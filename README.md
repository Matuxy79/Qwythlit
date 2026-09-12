# John's Light Source (JLS) Research Query — RAG+CAG Prototype (1.5v)

A Retrieval-Augmented and Cache-Augmented Generation (RAG+CAG) system for the John's Light Source (JLS), built with Streamlit, FastAPI, and ChromaDB. Retrieval is gated by JLS beamline metadata so each beamline lane can be queried independently or together.

Temporary fast mode is enabled by default: generation is disabled and queries use deterministic keyword retrieval for millisecond lookups on the prototype corpus. Set `JLS_RETRIEVAL_ONLY=0` and `JLS_KEYWORD_ONLY=0` to restore hybrid semantic retrieval plus optional carrier synthesis.

## Beamline Scopes

The current app is beamline-scoped, not discipline-scoped. Uploaded documents are tagged from the **Assign a beamline** selector, and the same shared scope map drives both the Full App and Ask Lane.

Choose **All beamlines** to bypass the metadata filter and search the full indexed store. The named scopes currently cover BioXAS-Imaging, BioXAS-Spectroscopy, BMIT, BXDS, JLS@APS, CMCF, EIML, Far-IR, HXMA, IDEAS, Mid-IR, QMSC, REIXS, SGM, SM, SXRMB, SyLMAND, VESPERS, and VLS-PGM.

## Architecture

DocuSearch-inspired: retrieval is instant and primary. The grounded extractive answer from the RAG/CAG layer is always shown first. Optional generative carrier synthesis (default: OpenRouter · `openai/gpt-oss-120b`) is currently blocked by retrieval-only mode.

| # | Component | File |
| --- | --- | --- |
| 1 | Streamlit dual-UI (Full App + Ask Lane) | `app.py` |
| 2 | FastAPI shared bridge | `api.py` |
| 3 | RAG+CAG instant backend | `jls_service.py`, `jls_backend/pipeline.py` |
| 4 | Generative carrier | `jls_backend/dllm.py`, `/v1/dllm/*` |

## Two UIs

The landing page offers two entry points:

- **Full App** — Admin / User roles, corpus admin, upload, precision controls, graded eval, optional LLM synthesis.
- **Ask Lane** — cinematic Qwythlit animated knowledge layer for instant retrieval: paired western wyvern familiar, dynamic synchrotron energy pulse, 3-stage lifecycle (`01 · Parse`, `02 · Retrieve`, `03 · Weave`), grounded evidence bullets with source chips, and a persistent floating `Qq` launcher widget.

Both UIs share the same underlying retrieval backend.

## Quick Launch

```bash
./scripts/launch_jls.sh
```

Creates `.venv` if needed, installs packages, and opens the UI at `http://localhost:8501`. Does not start Ollama or pull any LLM.

Fast mode defaults:

```bash
export JLS_RETRIEVAL_ONLY=1
export JLS_KEYWORD_ONLY=1
```

### Carrier (optional, Full App synthesis)

Carrier calls are disabled while `JLS_RETRIEVAL_ONLY=1`. To test generation again, set `JLS_RETRIEVAL_ONLY=0` and `JLS_KEYWORD_ONLY=0` before launch.

The carrier is any OpenAI-compatible `/v1/chat/completions` endpoint. Pick one — no code change:

```bash
# Cloud (OpenRouter)
export JLS_DLLM_API_KEY="sk-or-..."
# export JLS_DLLM_API_URL="https://openrouter.ai/api/v1"   # default
# export JLS_DLLM_MODEL="openai/gpt-oss-120b"              # default

# Local llama.cpp (offline, no key) — run: llama-server -m model.gguf --port 8080
# export JLS_DLLM_API_URL="http://localhost:8080/v1"
# unset JLS_DLLM_API_KEY

# Local Ollama
# export JLS_DLLM_API_URL="http://localhost:11434/v1"
```

Without a carrier the app is fully offline: semantic retrieval + instant cited extraction. The **Ask Lane never uses the carrier** — it is retrieval-only by design.

## API + Dual Frontend

### Railway deployment

The default `railway.toml` serves the interactive Streamlit app at `/`, with
**Full App** and **Ask Lane** on its landing page. It binds to Railway's `PORT`
and uses `/_stcore/health` for deployment health checks. The start command sets
`JLS_USE_API=0` so queries, uploads, and corpus administration use the same
embedded backend.

Deploy this branch with Railway's Config File set to `/railway.toml`. If the
public URL still shows **JLS RAG+CAG API**, check the deployment's source branch
and config file: it is still starting `uvicorn main:app` instead of Streamlit.

Attach a persistent volume and set `JLS_CHROMA_DIR=/data/chroma_store` (adjust to
your volume mount). Keep an existing volume and its path to retain its index.
On the first UI session, an empty store is indexed in the background from
`JLS_DEFAULT_DOCUMENTS_DIR` (default: `data/training_corpus/test_books`). This is
enabled by default on Railway; `JLS_BOOTSTRAP_CORPUS=0` disables it. Give initial
indexing time to finish before searching, or use **Full App > Workspace > Corpus
admin** to index documents manually.

For a separate API deployment, select `/railway.api.toml` as that service's
Config File. That service exposes `/docs`, `/health`, and `/v1/*`; the Streamlit
service exposes the browser UI. Each service should have its own Chroma volume.

### Local API bridge

```bash
./scripts/launch_api.sh
JLS_USE_API=1 JLS_API_URL=http://127.0.0.1:8010 ./scripts/launch_jls.sh
```

Key endpoints:

```text
GET  /health
POST /v1/query
POST /v1/chat/completions   # cls-rag-cag-v1.0; JLS_DLLM_MODEL only when retrieval-only is off
GET  /v1/dllm/status
POST /v1/dllm/chat
```

Example:

```bash
curl http://127.0.0.1:8010/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"What is the sample mounting procedure?","top_k":16}'
```

## Indexing Documents

- **Workspace -> Corpus admin**: one-click index of the local literature test corpus (`data/training_corpus/test_books` by default; override with `JLS_DEFAULT_DOCUMENTS_DIR`).
- **Main page upload panel**: drag-and-drop batch upload of PDF, TXT, MD, DOCX, HTML, CSV, TSV, and JSON with beamline tagging.
- **`ingest_daemon.py`**: optional batch indexer for folder-watch experiments.

> **Upgrading from v1.1 to 1.5** The encoder changed to 384d MiniLM, so collections were renamed `cls_v2_*`. Open **Workspace**, hit **Reset Chroma index**, and re-index once.

## Prototype HUD

A fixed floating overlay (bottom-right) shows live session telemetry for dev use:

| Field | Meaning |
| --- | --- |
| `ui` | Current surface (Full App / Ask Lane) |
| `turn` | Query count this session |
| `score` | Top Chroma similarity score |
| `cache` | HIT (green) / MISS (orange) |

## Guide Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Inference carrier](docs/DLLM.md)
- [User guide](docs/USER_GUIDE.md)
