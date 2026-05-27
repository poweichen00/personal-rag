"""Unit tests for the text-processing helpers in ``data_update.py``.

These cover the pure functions only — no Ollama or ChromaDB required.
"""

from data_update import chunk_text, clean_text

# --- clean_text -----------------------------------------------------------

def test_clean_text_strips_html_tags():
    assert clean_text("<p>hello</p>") == "hello"


def test_clean_text_collapses_blank_lines():
    assert clean_text("a\n\n\n\n\nb") == "a\n\nb"


def test_clean_text_collapses_inline_spaces():
    assert clean_text("a      b") == "a b"


def test_clean_text_trims_trailing_whitespace_per_line():
    assert clean_text("a   \nb   ") == "a\nb"


def test_clean_text_normalizes_crlf():
    assert clean_text("a\r\nb") == "a\nb"


# --- chunk_text -----------------------------------------------------------

def test_chunk_text_empty_returns_no_chunks():
    assert chunk_text("   \n\n  ", chunk_size=100, overlap=20) == []


def test_chunk_text_short_text_is_single_chunk():
    text = "This is a single short paragraph well under the size limit."
    chunks = chunk_text(text, chunk_size=600, overlap=100)
    assert chunks == [text]


def test_chunk_text_respects_max_size():
    # 5 paragraphs of 120 chars each must split into several <=200-char chunks.
    para = "x" * 120
    text = "\n\n".join([para] * 5)
    chunks = chunk_text(text, chunk_size=200, overlap=40)
    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)


def test_chunk_text_hard_splits_long_paragraph_with_overlap():
    # One 250-char paragraph (no blank lines) is hard-split by characters.
    text = "".join(chr(ord("a") + (i % 26)) for i in range(250))
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) >= 3
    assert all(len(c) <= 100 for c in chunks)
    # Consecutive chunks share `overlap` characters.
    assert chunks[0][-20:] == chunks[1][:20]


def test_chunk_text_drops_tiny_fragments():
    # A trailing <20-char fragment should be filtered out of the result.
    chunks = chunk_text("y" * 80 + "\n\n" + "tiny", chunk_size=60, overlap=10)
    assert "tiny" not in chunks
    assert all(len(c) > 20 for c in chunks)
