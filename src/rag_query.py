#!/usr/bin/env python3
"""Query interface for the UAV small-object-detection RAG knowledge base.

RAG pipeline per query:
  1. Embed the user question (Ollama nomic-embed-text)
  2. Retrieve candidate chunks from ChromaDB and hybrid-rerank them
  3. Assemble a prompt with the retrieved context + citations
  4. Call an OpenAI-compatible LLM endpoint
  5. Print the answer + source references

Usage:
  python rag_query.py                              # interactive multi-turn
  python rag_query.py --query "your question"      # single query
  python rag_query.py --query "..." --top-k 8 --model my-model
"""

from __future__ import annotations

import argparse
import os
import re
import sys

from dotenv import load_dotenv

load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "uav_detection")
RAG_DOMAIN = os.getenv("RAG_DOMAIN", "UAV (Unmanned Aerial Vehicle) small object detection")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

LITELLM_API_KEY = os.getenv("LITELLM_API_KEY", "")
LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "")
DEFAULT_MODEL = os.getenv("DEFAULT_LLM_MODEL", "openai/gpt-oss-20b")

DEFAULT_TOP_K = 5
MAX_HISTORY_TURNS = 6  # keep last 6 messages (3 turns)

# Reranking: fetch more candidates by cosine, then re-score with a hybrid of
# cosine similarity and lexical (token) overlap with the query.
RERANK_FETCH_MULTIPLIER = 3
RERANK_ALPHA = 0.7  # weight on cosine vs. lexical overlap


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

def embed_query(text: str) -> list[float]:
    import requests

    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={"model": EMBEDDING_MODEL, "prompt": text},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["embedding"]
    except Exception as e:
        print(f"[ERROR] Embedding failed: {e}", file=sys.stderr)
        print("[HINT] Make sure Ollama is running: ollama serve", file=sys.stderr)
        print(f"[HINT] And the model is pulled: ollama pull {EMBEDDING_MODEL}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Retrieval + reranking
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]{2,}", text.lower()))


def rerank(question: str, hits: list[dict], alpha: float = RERANK_ALPHA) -> list[dict]:
    """Hybrid rerank: alpha * cosine + (1 - alpha) * lexical overlap.

    Boosts chunks that share concrete tokens with the query (acronyms,
    dataset/metric names) without adding any dependency. Degrades to pure
    cosine ordering when the query has no usable tokens.
    """
    q_tokens = _tokenize(question)
    if not q_tokens:
        return hits
    for h in hits:
        overlap = len(q_tokens & _tokenize(h["text"])) / len(q_tokens)
        h["score"] = round(alpha * h["score"] + (1 - alpha) * overlap, 4)
    return sorted(hits, key=lambda h: h["score"], reverse=True)


def retrieve(
    query_vector: list[float],
    top_k: int = DEFAULT_TOP_K,
    question: str | None = None,
) -> list[dict]:
    """Query ChromaDB, then hybrid-rerank, and return top-k with metadata."""
    import chromadb

    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception:
        print(
            "[ERROR] Vector DB collection not found.\n"
            "[HINT]  Run: python data_update.py --rebuild",
            file=sys.stderr,
        )
        sys.exit(1)

    if collection.count() == 0:
        print("[ERROR] Collection is empty. Run: python data_update.py --rebuild", file=sys.stderr)
        sys.exit(1)

    fetch_n = min(top_k * RERANK_FETCH_MULTIPLIER, collection.count())
    results = collection.query(
        query_embeddings=[query_vector],
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
        hits.append(
            {
                "text": doc,
                "source": meta.get("source", "unknown"),
                "chunk_index": meta.get("chunk_index", 0),
                "chunk_total": meta.get("chunk_total", 1),
                "score": round(1.0 - dist, 4),  # cosine similarity
            }
        )

    if question:
        hits = rerank(question, hits)
    return hits[:top_k]


# ---------------------------------------------------------------------------
# Prompt assembly
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = f"""\
You are an expert research assistant specializing in {RAG_DOMAIN}. You have access to \
a curated knowledge base of documents on this topic.

When answering:
1. Base your answer primarily on the provided context passages.
2. Always cite your sources using [Source: filename, chunk N/M] format inline.
3. If the context doesn't fully cover the question, say so explicitly.
4. Be precise and technical - the user is a domain expert.
5. Structure longer answers with clear headings or bullet points.
"""


def build_user_prompt(question: str, hits: list[dict]) -> str:
    context_blocks = []
    for i, hit in enumerate(hits, 1):
        context_blocks.append(
            f"[{i}] Source: {hit['source']} | Chunk {hit['chunk_index'] + 1}/{hit['chunk_total']} "
            f"| Similarity: {hit['score']}\n"
            f"{hit['text']}"
        )
    context_str = "\n\n---\n\n".join(context_blocks)

    return (
        f"## Retrieved Context\n\n"
        f"{context_str}\n\n"
        f"---\n\n"
        f"## Question\n\n"
        f"{question}\n\n"
        f"Please answer the question based on the context above. "
        f"Cite sources inline as [Source: filename, chunk N]."
    )


# ---------------------------------------------------------------------------
# LLM call via OpenAI-compatible SDK
# ---------------------------------------------------------------------------

def call_llm(messages: list[dict], model: str) -> str:
    from openai import OpenAI

    if not LITELLM_BASE_URL or not LITELLM_API_KEY:
        return (
            "[LLM Error] LITELLM_BASE_URL or LITELLM_API_KEY not set.\n"
            "Please fill in your .env file."
        )

    client = OpenAI(
        api_key=LITELLM_API_KEY,
        base_url=LITELLM_BASE_URL,
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"[LLM Error] {e}\n\nHint: Check LITELLM_API_KEY and LITELLM_BASE_URL in .env"


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_sources(hits: list[dict]) -> None:
    print("\n\033[36m── Sources ──────────────────────────────────────\033[0m")
    for i, h in enumerate(hits, 1):
        print(
            f"  [{i}] {h['source']}  "
            f"chunk {h['chunk_index'] + 1}/{h['chunk_total']}  "
            f"(similarity={h['score']})"
        )
    print("\033[36m─────────────────────────────────────────────────\033[0m\n")


def print_answer(text: str) -> None:
    print(f"\n\033[92m[Assistant]\033[0m {text}\n")


# ---------------------------------------------------------------------------
# Single-query flow
# ---------------------------------------------------------------------------

def single_query(question: str, top_k: int, model: str) -> None:
    print("[INFO] Embedding query ...")
    qvec = embed_query(question)

    print(f"[INFO] Retrieving top-{top_k} chunks ...")
    hits = retrieve(qvec, top_k=top_k, question=question)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(question, hits)},
    ]

    print("[INFO] Generating answer ...\n")
    answer = call_llm(messages, model)
    print_answer(answer)
    print_sources(hits)


# ---------------------------------------------------------------------------
# Interactive multi-turn mode
# ---------------------------------------------------------------------------

def interactive_mode(top_k: int, model: str) -> None:
    print(f"\033[1m=== Personal RAG: {RAG_DOMAIN} ===\033[0m")
    print(f"Model: {model} | Embedding: {EMBEDDING_MODEL} | Top-K: {top_k}")
    print("Type 'exit' or 'quit' to leave. 'clear' to reset conversation.\n")

    history: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            question = input("\033[93m[You]\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit", "bye"}:
            print("Bye!")
            break
        if question.lower() == "clear":
            history = [{"role": "system", "content": SYSTEM_PROMPT}]
            print("[Conversation cleared]\n")
            continue

        # Embed + retrieve
        qvec = embed_query(question)
        hits = retrieve(qvec, top_k=top_k, question=question)

        # Build this turn's user message (with context)
        user_msg = build_user_prompt(question, hits)
        history.append({"role": "user", "content": user_msg})

        # Trim history to keep last MAX_HISTORY_TURNS messages (+ system)
        if len(history) > MAX_HISTORY_TURNS + 1:
            history = [history[0]] + history[-(MAX_HISTORY_TURNS):]

        # LLM call
        answer = call_llm(history, model)
        history.append({"role": "assistant", "content": answer})

        print_answer(answer)
        print_sources(hits)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rag_query.py",
        description=(
            "UAV Small Object Detection RAG - Query Interface\n"
            "\n"
            "Embeds your question with Ollama, retrieves and reranks relevant\n"
            "paper chunks from ChromaDB, then generates an answer via an\n"
            "OpenAI-compatible LLM endpoint."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python rag_query.py\n"
            "  python rag_query.py --query 'What is SAHI?'\n"
            "  python rag_query.py --query 'Compare NWD vs IoU for tiny objects' --top-k 8\n"
            "  python rag_query.py --query '...' --model gemini-2.5-flash\n"
        ),
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        default=None,
        metavar="TEXT",
        help="Single question to answer (omit for interactive mode).",
    )
    parser.add_argument(
        "--top-k", "-k",
        type=int,
        default=DEFAULT_TOP_K,
        metavar="N",
        help=f"Number of chunks to retrieve (default: {DEFAULT_TOP_K}).",
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=DEFAULT_MODEL,
        metavar="MODEL",
        help=f"LLM model name (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--embedding-model",
        type=str,
        default=None,
        metavar="MODEL",
        help=f"Ollama embedding model (default: {EMBEDDING_MODEL}).",
    )
    parser.add_argument(
        "--ollama-url",
        type=str,
        default=None,
        metavar="URL",
        help=f"Ollama base URL (default: {OLLAMA_BASE_URL}).",
    )
    parser.add_argument(
        "--chroma-dir",
        type=str,
        default=None,
        metavar="DIR",
        help=f"ChromaDB persist directory (default: {CHROMA_PERSIST_DIR}).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Apply CLI overrides
    global EMBEDDING_MODEL, OLLAMA_BASE_URL, CHROMA_PERSIST_DIR
    if args.embedding_model:
        EMBEDDING_MODEL = args.embedding_model
    if args.ollama_url:
        OLLAMA_BASE_URL = args.ollama_url
    if args.chroma_dir:
        CHROMA_PERSIST_DIR = args.chroma_dir

    if args.query:
        single_query(args.query, top_k=args.top_k, model=args.model)
    else:
        interactive_mode(top_k=args.top_k, model=args.model)


if __name__ == "__main__":
    main()
