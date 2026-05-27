#!/usr/bin/env python3
"""Generate ``skill.md`` from the UAV small-object-detection RAG knowledge base.

The builder probes the knowledge base with seed questions (covering Concepts,
Trends, and Entities), retrieves and reranks context for each, then asks an LLM
to synthesise a structured agent-skill specification.

If the LLM endpoint is unavailable or errors, it falls back to a deterministic,
retrieval-only generator, so ``skill.md`` is always produced with the required
section structure.

Usage:
    python3 skill_builder.py [--output skill.md] [--top-k 5] [--verbose]
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import textwrap
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OLLAMA_BASE_URL   = os.getenv("OLLAMA_BASE_URL",   "http://localhost:11434")
EMBEDDING_MODEL   = os.getenv("EMBEDDING_MODEL",   "nomic-embed-text")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME   = os.getenv("COLLECTION_NAME",   "uav_detection")
RAG_DOMAIN        = os.getenv("RAG_DOMAIN",        "UAV small object detection")
LITELLM_API_KEY   = os.getenv("LITELLM_API_KEY",   "")
LITELLM_BASE_URL  = os.getenv("LITELLM_BASE_URL",  "")
DEFAULT_MODEL     = os.getenv("DEFAULT_LLM_MODEL", "openai/gpt-oss-20b")

LLM_ERROR_PREFIX = "[LLM Error]"

# Reranking: combine dense cosine similarity with lexical overlap.
RERANK_FETCH_MULTIPLIER = 3
RERANK_ALPHA = 0.7  # weight on cosine vs. lexical overlap

# Built-in seed questions (UAV small object detection example). To use the
# template for your own domain, point SEED_QUESTIONS_FILE at a JSON file with
# the same {"concepts": [...], "trends": [...], "entities": [...]} structure.
_DEFAULT_SEED_QUESTIONS: dict[str, list[str]] = {
    "concepts": [
        "What are the main challenges of small object detection in UAV images?",
        "What datasets are commonly used for UAV small object detection evaluation?",
        "How do label assignment strategies like NWD and RFLA improve tiny object detection?",
        "What are the key transformer-based detectors used for UAV small object detection?",
        "How does SAHI slicing improve inference on small objects?",
        "What attention mechanisms are effective for UAV small object detection?",
        "What are the state-of-the-art lightweight models for UAV detection?",
        "How does a feature pyramid network (FPN) help multi-scale object detection?",
    ],
    "trends": [
        "How have label-assignment and matching metrics evolved from IoU toward "
        "Gaussian or Wasserstein distances over time?",
        "What is the trend from anchor-based to anchor-free to transformer/query-based "
        "detectors in this field?",
        "How has the field shifted toward lightweight, edge-deployable UAV detectors?",
    ],
    "entities": [
        "Which benchmark datasets, detector families, and backbones are central to "
        "UAV small object detection research?",
        "What evaluation metrics are used to measure small object detection performance?",
    ],
}


def _load_seed_questions() -> dict[str, list[str]]:
    """Load seed questions from SEED_QUESTIONS_FILE if set, else built-in defaults."""
    path = os.getenv("SEED_QUESTIONS_FILE", "").strip()
    if not path:
        return _DEFAULT_SEED_QUESTIONS
    try:
        import json
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not all(isinstance(v, list) for v in data.values()):
            raise ValueError("expected {category: [questions...]} structure")
        return data
    except Exception as e:
        print(f"[WARN] SEED_QUESTIONS_FILE={path} failed to load ({e}); using built-in defaults.", file=sys.stderr)
        return _DEFAULT_SEED_QUESTIONS


SEED_QUESTIONS: dict[str, list[str]] = _load_seed_questions()


# ---------------------------------------------------------------------------
# Embedding (Ollama)
# ---------------------------------------------------------------------------
def embed_query(text: str) -> list[float]:
    import requests
    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/embeddings",
        json={"model": EMBEDDING_MODEL, "prompt": text},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]


# ---------------------------------------------------------------------------
# ChromaDB retrieval + reranking
# ---------------------------------------------------------------------------
def get_collection():
    import chromadb
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return client.get_collection(name=COLLECTION_NAME)


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]{2,}", text.lower()))


def rerank(query: str, hits: list[dict], alpha: float = RERANK_ALPHA) -> list[dict]:
    """Hybrid rerank: alpha * cosine + (1 - alpha) * lexical overlap."""
    q_tokens = _tokenize(query)
    if not q_tokens:
        return hits
    for h in hits:
        d_tokens = _tokenize(h["text"])
        overlap = len(q_tokens & d_tokens) / len(q_tokens)
        h["rerank_score"] = alpha * h["similarity"] + (1 - alpha) * overlap
    return sorted(hits, key=lambda h: h["rerank_score"], reverse=True)


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    collection = get_collection()
    vec = embed_query(query)
    fetch_n = min(top_k * RERANK_FETCH_MULTIPLIER, max(collection.count(), 1))
    results = collection.query(
        query_embeddings=[vec],
        n_results=fetch_n,
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
        strict=False,
    ):
        hits.append({
            "text": doc,
            "source": meta.get("source", "unknown"),
            "chunk_index": meta.get("chunk_index", 0),
            "total_chunks": meta.get("chunk_total", 0),
            "similarity": round(1 - dist, 4),
        })
    return rerank(query, hits)[:top_k]


# ---------------------------------------------------------------------------
# LLM call
# ---------------------------------------------------------------------------
def llm_available() -> bool:
    return bool(LITELLM_BASE_URL and LITELLM_API_KEY)


def call_llm(messages: list[dict], model: str = DEFAULT_MODEL) -> str:
    from openai import OpenAI
    if not llm_available():
        return f"{LLM_ERROR_PREFIX} LITELLM_BASE_URL or LITELLM_API_KEY not set."
    client = OpenAI(api_key=LITELLM_API_KEY, base_url=LITELLM_BASE_URL)
    try:
        response = client.chat.completions.create(model=model, messages=messages)
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"{LLM_ERROR_PREFIX} {e}"


# ---------------------------------------------------------------------------
# Q&A generation per seed question
# ---------------------------------------------------------------------------
def _extractive_answer(hits: list[dict]) -> str:
    """Deterministic fallback answer: stitch the top retrieved snippets."""
    if not hits:
        return "_(No relevant context retrieved.)_"
    parts = []
    for h in hits[:2]:
        snippet = " ".join(h["text"].split())[:280]
        parts.append(f"{snippet} (Source: {h['source']})")
    return " ".join(parts)


def answer_seed(question: str, top_k: int, model: str, verbose: bool) -> dict:
    """Retrieve context and generate an answer for one seed question.

    Returns a dict with the question, answer, and the hits used (so the
    fallback generator can cite sources without re-querying).
    """
    if verbose:
        print(f"  [seed] {question[:60]}...", flush=True)
    hits = retrieve(question, top_k=top_k)

    answer = ""
    if llm_available():
        context_parts = [
            f"[{i}] ({h['source']}) {h['text'][:300]}"
            for i, h in enumerate(hits, 1)
        ]
        context = "\n\n".join(context_parts)
        messages = [
            {"role": "system", "content": (
                "Answer the question concisely (2-4 sentences) using ONLY the "
                "provided context. Do not invent facts."
            )},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ]
        answer = call_llm(messages, model)

    # Fall back to an extractive answer if the LLM is unavailable or errored.
    if not llm_available() or answer.startswith(LLM_ERROR_PREFIX):
        answer = _extractive_answer(hits)

    return {"question": question, "answer": answer, "hits": hits}


def collect_papers() -> list[str]:
    """List unique paper names from ChromaDB metadata."""
    collection = get_collection()
    results = collection.get(include=["metadatas"])
    sources = sorted({m.get("source", "") for m in results["metadatas"]})
    return [s for s in sources if s]


# ---------------------------------------------------------------------------
# Synthesis prompt (LLM path)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = textwrap.dedent(f"""\
    You are a technical writer creating a concise agent-skill specification.
    You will be given question-answer pairs produced by a RAG system whose
    knowledge base covers {RAG_DOMAIN}.
    Synthesise them into a structured Markdown skill description that another
    AI agent could use to understand what this skill knows and how to invoke it.
    Use the EXACT section headings requested. Keep it focused and under 1200 words.
""")

REQUIRED_SECTIONS = (
    "## Overview",
    "## Core Concepts",
    "## Key Trends",
    "## Key Entities",
    "## Methodology",
    "## Knowledge Gaps",
    "## Example Q&A",
    "## Source References",
)


def _synthesis_prompt(qa_by_cat: dict[str, list[dict]], papers: list[str]) -> str:
    paper_list = "\n".join(f"- {p}" for p in papers)

    def block(cat: str) -> str:
        return "\n\n".join(
            f"Q: {qa['question']}\nA: {qa['answer']}" for qa in qa_by_cat.get(cat, [])
        )

    return textwrap.dedent(f"""\
        The following Q&A pairs were generated by a RAG system over {len(papers)}
        documents covering {RAG_DOMAIN}.

        Sources in the knowledge base:
        {paper_list}

        [Concept Q&A]
        {block("concepts")}

        [Trend Q&A]
        {block("trends")}

        [Entity Q&A]
        {block("entities")}

        Write a Markdown skill specification using EXACTLY these section headings,
        in this order:

        # {RAG_DOMAIN} - Skill Specification
        ## Overview            - skill name, 2-3 sentence description, capabilities, limitations
        ## Core Concepts       - the key methods/ideas, grouped with bullets
        ## Key Trends          - how the field evolved over time (use the Trend Q&A)
        ## Key Entities        - datasets, methods, people, metrics (use the Entity Q&A)
        ## Methodology         - how this knowledge base / skill was built
        ## Knowledge Gaps      - what the skill cannot answer or may get wrong
        ## Example Q&A         - 3-4 grounded question/answer examples with source citations
        ## Source References   - the list of documents in the knowledge base
    """)


# ---------------------------------------------------------------------------
# Deterministic fallback generator (no LLM required)
# ---------------------------------------------------------------------------
def build_fallback_skill(qa_by_cat: dict[str, list[dict]], papers: list[str]) -> str:
    def qa_section(cat: str) -> str:
        lines = []
        for qa in qa_by_cat.get(cat, []):
            lines.append(f"**Q: {qa['question']}**\n\n{qa['answer']}\n")
        return "\n".join(lines) if lines else "_(No Q&A available.)_\n"

    paper_list = "\n".join(f"- {p}" for p in papers)
    example_qa = qa_section("concepts")

    return textwrap.dedent(f"""\
        # {RAG_DOMAIN} - Skill Specification

        ## Overview

        **Skill Name:** {RAG_DOMAIN} Knowledge

        This skill answers questions about **{RAG_DOMAIN}**, grounded in {len(papers)}
        curated documents in the knowledge base.

        **Capabilities:** answer concept, trend, and entity questions about the
        domain; cite specific source documents for every claim; surface knowledge
        gaps when the retrieved context is insufficient.

        **Limitations:** bounded to the {len(papers)}-document corpus; no
        information beyond what the retrieved passages contain.

        ## Core Concepts

        {qa_section("concepts")}
        ## Key Trends

        {qa_section("trends")}
        ## Key Entities

        {qa_section("entities")}
        ## Methodology

        Built from {len(papers)} documents: clean -> paragraph-aware chunking
        (600/100) -> Ollama `nomic-embed-text` (768-dim) -> ChromaDB cosine search ->
        Kx3 fetch + hybrid (cosine + lexical) rerank -> top-K. Seed questions span
        Concepts, Trends, and Entities; this document was generated by the
        deterministic retrieval-only fallback (no LLM endpoint was available).

        ## Knowledge Gaps

        - Limited to the {len(papers)} listed documents; anything outside this set is unknown
        - May miss the right passage when the retriever doesn't surface it
        - No external knowledge beyond the indexed corpus

        ## Example Q&A

        {example_qa}
        ## Source References

        ### Source Papers
        {paper_list}
    """)


# ---------------------------------------------------------------------------
# Build skill.md
# ---------------------------------------------------------------------------
def build_skill_md(top_k: int, model: str, verbose: bool) -> str:
    if verbose:
        print("[1/3] Gathering Q&A pairs from RAG ...", flush=True)

    qa_by_cat: dict[str, list[dict]] = {}
    for category, questions in SEED_QUESTIONS.items():
        qa_by_cat[category] = [
            answer_seed(q, top_k, model, verbose) for q in questions
        ]

    papers = collect_papers()

    if verbose:
        print("[2/3] Synthesising skill description ...", flush=True)

    skill_body = ""
    if llm_available():
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": _synthesis_prompt(qa_by_cat, papers)},
        ]
        skill_body = call_llm(messages, model)

    # Fall back to the deterministic generator if the LLM is unavailable,
    # errored, or returned output missing the required sections.
    needs_fallback = (
        not llm_available()
        or skill_body.startswith(LLM_ERROR_PREFIX)
        or any(sec not in skill_body for sec in REQUIRED_SECTIONS)
    )
    if needs_fallback:
        if verbose:
            print("  [fallback] Using deterministic retrieval-only generator.", flush=True)
        skill_body = build_fallback_skill(qa_by_cat, papers)

    if verbose:
        print("[3/3] Writing output file ...", flush=True)

    header = textwrap.dedent(f"""\
        <!-- Auto-generated by skill_builder.py on {datetime.now().strftime('%Y-%m-%d %H:%M')} -->
        <!-- Run `python3 skill_builder.py` to regenerate -->

    """)
    return header + skill_body


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate skill.md from the UAV RAG knowledge base.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--output", default="skill.md",
        help="Output path for the generated skill file",
    )
    parser.add_argument(
        "--top-k", type=int, default=5,
        help="Number of chunks to retrieve per seed question",
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help="LLM model to use for synthesis",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print progress messages",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Sanity checks
    try:
        get_collection()
    except Exception:
        print("[ERROR] ChromaDB collection not found.")
        print("[HINT]  Run: python3 data_update.py --rebuild")
        sys.exit(1)

    print(f"Building skill.md -> {args.output}")
    content = build_skill_md(top_k=args.top_k, model=args.model, verbose=args.verbose)

    Path(args.output).write_text(content, encoding="utf-8")
    print(f"Done. Skill file written to: {args.output}")


if __name__ == "__main__":
    main()
