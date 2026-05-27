#!/usr/bin/env python3
"""
data_update.py - UAV Small Object Detection RAG Data Pipeline

Pipeline:
  data/raw/ (.md, .txt, .pdf)
    -> clean text -> data/processed/ (.txt)
    -> chunk -> embed (Ollama nomic-embed-text)
    -> upsert into ChromaDB

Features:
  --rebuild   : Clear data/processed/ + wipe ChromaDB, then reindex all files
  default     : Incremental update via MD5 hash cache (only changed files)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Configuration (overridable via env or CLI flags)
# ---------------------------------------------------------------------------
DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
HASH_CACHE_FILE = DATA_DIR / ".file_hashes.json"

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "uav_detection")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
EMBEDDING_DIM = 768  # nomic-embed-text output dimension

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "600"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

SUPPORTED_SUFFIXES = {".md", ".markdown", ".txt", ".pdf"}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Hash cache helpers (incremental update)
# ---------------------------------------------------------------------------

def load_hash_cache() -> dict[str, str]:
    if HASH_CACHE_FILE.exists():
        with open(HASH_CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_hash_cache(cache: dict[str, str]) -> None:
    with open(HASH_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def file_md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def extract_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)
    except ImportError:
        log.warning("pypdf not installed - skipping %s", path.name)
        return ""
    except Exception as e:
        log.error("PDF extraction failed for %s: %s", path.name, e)
        return ""


def extract_text(path: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        raw = extract_pdf(path)
    elif suffix in (".md", ".markdown", ".txt"):
        raw = path.read_text(encoding="utf-8", errors="replace")
    else:
        return None
    return raw if raw.strip() else None


# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Normalize newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse 3+ blank lines -> 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse spaces on each line
    text = re.sub(r"[ \t]{2,}", " ", text)
    # Strip trailing whitespace per line
    lines = [ln.rstrip() for ln in text.split("\n")]
    return "\n".join(lines).strip()


# ---------------------------------------------------------------------------
# Chunking  (paragraph-aware + fixed-size fallback)
# ---------------------------------------------------------------------------

def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """
    Strategy:
      1. Split on double newlines (paragraph boundaries).
      2. Accumulate paragraphs until we hit chunk_size.
      3. When flushing, keep the last paragraph as overlap context.
      4. If a single paragraph exceeds chunk_size, hard-split it by chars.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    def flush() -> list[str]:
        """Flush current buffer and return overlap seed."""
        if current:
            chunks.append("\n\n".join(current))
            # keep last paragraph as overlap context
            last = current[-1]
            return [last] if len(last) <= overlap else []
        return []

    for para in paragraphs:
        plen = len(para)

        # Long single paragraph -> hard-split then continue
        if plen > chunk_size:
            current = flush()
            current_len = sum(len(p) for p in current)
            for i in range(0, plen, chunk_size - overlap):
                sub = para[i : i + chunk_size].strip()
                if sub:
                    chunks.append(sub)
            continue

        if current_len + plen + 2 > chunk_size and current:
            current = flush()
            current_len = sum(len(p) for p in current)

        current.append(para)
        current_len += plen + 2  # +2 for the "\n\n" separator

    flush()
    return [c for c in chunks if len(c) > 20]


# ---------------------------------------------------------------------------
# Embedding via Ollama REST API
# ---------------------------------------------------------------------------

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Call Ollama /api/embeddings for each text."""
    import requests as req

    embeddings: list[list[float]] = []
    for text in texts:
        try:
            resp = req.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json={"model": EMBEDDING_MODEL, "prompt": text},
                timeout=60,
            )
            resp.raise_for_status()
            embeddings.append(resp.json()["embedding"])
        except Exception as e:
            log.error("Embedding failed: %s", e)
            embeddings.append([0.0] * EMBEDDING_DIM)
    return embeddings


# ---------------------------------------------------------------------------
# ChromaDB helpers
# ---------------------------------------------------------------------------

def get_collection(client=None):
    import chromadb

    if client is None:
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    return client, collection


def drop_collection() -> None:
    import chromadb

    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    try:
        client.delete_collection(COLLECTION_NAME)
        log.info("Dropped ChromaDB collection: %s", COLLECTION_NAME)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Indexing a single file
# ---------------------------------------------------------------------------

def index_file(collection, filepath: Path, text: str) -> int:
    # Pass the (possibly CLI-overridden) globals explicitly: chunk_text's
    # default args are bound at import time, so reading them here keeps
    # --chunk-size / --chunk-overlap effective.
    chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
    if not chunks:
        log.warning("No chunks generated from %s", filepath.name)
        return 0

    log.info("  Embedding %d chunks from %s ...", len(chunks), filepath.name)
    vectors = embed_texts(chunks)

    stem = filepath.stem
    ids = [f"{stem}::chunk{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "source": filepath.name,
            "chunk_index": i,
            "chunk_total": len(chunks),
        }
        for i in range(len(chunks))
    ]

    # upsert is idempotent - safe to re-run
    collection.upsert(ids=ids, embeddings=vectors, documents=chunks, metadatas=metadatas)
    return len(chunks)


# ---------------------------------------------------------------------------
# Main update pipeline
# ---------------------------------------------------------------------------

def run_update(rebuild: bool = False) -> None:
    # Ensure directories exist
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if rebuild:
        log.info("=== FULL REBUILD MODE ===")
        # Clear processed text files
        for f in PROCESSED_DIR.glob("*.txt"):
            f.unlink()
        log.info("Cleared data/processed/")
        drop_collection()
        hash_cache: dict[str, str] = {}
    else:
        log.info("=== INCREMENTAL UPDATE MODE ===")
        hash_cache = load_hash_cache()

    _, collection = get_collection()

    # Discover raw files
    raw_files = sorted(
        f for f in RAW_DIR.rglob("*")
        if f.is_file() and f.suffix.lower() in SUPPORTED_SUFFIXES
    )

    if not raw_files:
        log.warning("No supported files found in %s", RAW_DIR)
        return

    log.info("Found %d raw file(s)", len(raw_files))

    total_chunks = 0
    n_updated = 0
    n_skipped = 0
    new_cache = dict(hash_cache)

    for filepath in raw_files:
        cache_key = str(filepath.relative_to(DATA_DIR))
        current_hash = file_md5(filepath)

        if not rebuild and hash_cache.get(cache_key) == current_hash:
            log.debug("Unchanged, skipping: %s", filepath.name)
            n_skipped += 1
            continue

        log.info("Processing: %s", filepath.name)

        raw_text = extract_text(filepath)
        if raw_text is None:
            log.warning("  No text extracted, skipping.")
            continue

        cleaned = clean_text(raw_text)

        # Save processed text
        processed_path = PROCESSED_DIR / (filepath.stem + ".txt")
        processed_path.write_text(cleaned, encoding="utf-8")

        # Index into ChromaDB
        n = index_file(collection, filepath, cleaned)
        total_chunks += n
        n_updated += 1
        new_cache[cache_key] = current_hash

    save_hash_cache(new_cache)

    total_in_db = collection.count()
    log.info("=== DONE ===")
    log.info(
        "Updated: %d | Skipped: %d | New chunks: %d | Total in DB: %d",
        n_updated, n_skipped, total_chunks, total_in_db,
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="data_update.py",
        description=(
            "UAV Small Object Detection RAG - Data Update Pipeline\n"
            "\n"
            "Reads raw files from data/raw/, cleans them, saves to data/processed/,\n"
            "chunks and embeds with Ollama (nomic-embed-text), then upserts into ChromaDB."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python data_update.py                     # incremental update\n"
            "  python data_update.py --rebuild           # full rebuild\n"
            "  python data_update.py --rebuild -v        # rebuild with debug logs\n"
            "  python data_update.py --chunk-size 800 --chunk-overlap 150\n"
        ),
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Clear data/processed/ and rebuild the vector index from scratch.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=None,
        metavar="N",
        help=f"Max characters per chunk (default: {CHUNK_SIZE}, env: CHUNK_SIZE)",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=None,
        metavar="N",
        help=f"Overlap characters between chunks (default: {CHUNK_OVERLAP}, env: CHUNK_OVERLAP)",
    )
    parser.add_argument(
        "--embedding-model",
        type=str,
        default=None,
        metavar="MODEL",
        help=f"Ollama embedding model (default: {EMBEDDING_MODEL})",
    )
    parser.add_argument(
        "--ollama-url",
        type=str,
        default=None,
        metavar="URL",
        help=f"Ollama base URL (default: {OLLAMA_BASE_URL})",
    )
    parser.add_argument(
        "--chroma-dir",
        type=str,
        default=None,
        metavar="DIR",
        help=f"ChromaDB persist directory (default: {CHROMA_PERSIST_DIR})",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Apply CLI overrides to globals
    global CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, OLLAMA_BASE_URL, CHROMA_PERSIST_DIR
    if args.chunk_size is not None:
        CHUNK_SIZE = args.chunk_size
    if args.chunk_overlap is not None:
        CHUNK_OVERLAP = args.chunk_overlap
    if args.embedding_model is not None:
        EMBEDDING_MODEL = args.embedding_model
    if args.ollama_url is not None:
        OLLAMA_BASE_URL = args.ollama_url
    if args.chroma_dir is not None:
        CHROMA_PERSIST_DIR = args.chroma_dir

    run_update(rebuild=args.rebuild)


if __name__ == "__main__":
    main()
