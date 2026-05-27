"""Unit tests for the retrieval helpers in ``rag_query.py``.

Covers the pure functions: query tokenization and hybrid reranking.
No Ollama, ChromaDB, or network access is required.
"""

from rag_query import _tokenize, rerank

# --- _tokenize ------------------------------------------------------------

def test_tokenize_lowercases_and_splits():
    assert _tokenize("NWD vs IoU") == {"nwd", "vs", "iou"}


def test_tokenize_drops_single_chars_and_punctuation():
    assert _tokenize("a, b! 3D-model") == {"3d", "model"}


# --- rerank ---------------------------------------------------------------

def _hit(text, score):
    return {"text": text, "score": score}


def test_rerank_boosts_lexical_overlap():
    hits = [
        _hit("nomic embedding model", 0.50),   # higher cosine, no overlap
        _hit("sahi slicing inference", 0.40),  # lower cosine, full overlap
    ]
    ranked = rerank("sahi slicing", hits, alpha=0.7)
    # The lexically-matching hit should win despite its lower cosine score.
    assert ranked[0]["text"] == "sahi slicing inference"
    assert ranked[0]["score"] > ranked[1]["score"]


def test_rerank_is_sorted_descending():
    hits = [_hit("alpha beta", 0.30), _hit("alpha gamma", 0.90)]
    ranked = rerank("alpha", hits)
    scores = [h["score"] for h in ranked]
    assert scores == sorted(scores, reverse=True)


def test_rerank_no_query_tokens_returns_unchanged():
    hits = [_hit("foo bar", 0.50), _hit("baz qux", 0.60)]
    out = rerank("!!! ??", hits)
    assert out is hits  # untouched when the query has no usable tokens
    assert [h["score"] for h in out] == [0.50, 0.60]
