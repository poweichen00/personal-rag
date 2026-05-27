# Personal RAG - runtime image (CLI). Ollama runs on the HOST, not in here.
FROM python:3.11-slim

WORKDIR /app

# deps first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# app code + bundled corpus
COPY src/ ./src/
COPY data/ ./data/

# Point at the host's Ollama at runtime (override with -e / --env-file).
# On Linux hosts use the host IP or --network host instead of host.docker.internal.
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434 \
    LITELLM_BASE_URL=http://host.docker.internal:11434/v1 \
    LITELLM_API_KEY=ollama \
    DEFAULT_LLM_MODEL=llama3.1 \
    EMBEDDING_MODEL=nomic-embed-text \
    CHROMA_PERSIST_DIR=/data/chroma_db

# Index lives in a mounted volume (built once via data_update.py), not baked in
# (building it needs a running Ollama, unavailable at image-build time).
VOLUME ["/data/chroma_db"]

ENTRYPOINT ["python", "src/rag_query.py"]
CMD ["--help"]
