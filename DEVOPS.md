# DevOps Pipeline

A full CI/CD chain wrapped around the RAG app, used as a DevOps showcase
(the app is small; the pipeline demonstrates the toolchain end to end).

```
git push
  -> Jenkins
       Lint (ruff)
       Test (pytest + coverage)
       SonarQube scan + Quality Gate   (fail build if gate is red)
       Build Docker image
       Push image to Nexus registry
       Deploy to the Jetson Orin edge device
```

| Tool | Role |
|------|------|
| **Jenkins** | Pipeline orchestrator (`Jenkinsfile`, declarative) |
| **SonarQube** | Static analysis + coverage gate (`sonar-project.properties`) |
| **Nexus 3** | Docker image registry (artifact store) |
| **Jetson Orin** | Edge deploy target ("prod") |

GitHub Actions (`.github/workflows/ci.yml`) stays as the lightweight PR check;
Jenkins is the full release pipeline.

## 1. Bring up the toolchain

Run on a workstation/server (not the Jetson - these are heavy JVM apps):

```bash
docker compose -f docker-compose.devops.yml up -d
# Jenkins   http://localhost:8080
# SonarQube http://localhost:9000   (admin/admin)
# Nexus     http://localhost:8081   (Docker registry on :8082)
```

## 2. One-time config

- **Nexus**: create a `docker (hosted)` repo, expose it on port `8082`.
- **SonarQube**: create project `personal-rag`, generate a token, register the
  server in Jenkins as `sonarqube`.
- **Jenkins credentials**: `nexus` (username/password), `dgx-ssh` (SSH key for
  the Jetson). Install Docker, SonarQube Scanner, and SSH Agent plugins.
- Point a Jenkins pipeline job at this repo (uses the `Jenkinsfile`).

## 3. Run the parts locally

```bash
# lint + test + coverage (what the pipeline runs)
pip install -r requirements-dev.txt
ruff check src tests
pytest -q --cov=src --cov-report=xml --junitxml=junit.xml

# build + run the image (Ollama must run on the host)
docker build -t personal-rag .
docker run --rm -it \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -e LITELLM_BASE_URL=http://host.docker.internal:11434/v1 \
  -v "$PWD/chroma_db:/data/chroma_db" \
  personal-rag --query "What is SAHI?"
```

> The container ships the code + corpus only. Ollama runs on the host, and the
> vector index lives in the mounted `chroma_db` volume (build it once with
> `python src/data_update.py --rebuild`). Nothing leaves the host.
