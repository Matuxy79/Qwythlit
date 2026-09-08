"""FastAPI shared bridge — an *optional* HTTP layer in front of the RAG+CAG backend.

This API is only active when the environment variable ``CLS_USE_API=1`` is set.
By default the Streamlit UI (``app.py``) and the Chainlit Ask Lane (``chat_lane.py``)
import ``cls_service`` directly; no HTTP hop is needed for local single-machine use.

Route groups:

    GET  /
        Service index. Browsers get a short HTML page; API clients get JSON.
        The Streamlit UI is not served here.

    GET  /health
        Liveness plus Chroma counts. Railway's healthcheck uses this path.

    POST /v1/ingest/default
        Index ``data/training_corpus/test_books`` (or ``CLS_DEFAULT_DOCUMENTS_DIR``)
        into this process's Chroma store.

    POST /v1/query
        Structured retrieval request.  Returns grounded evidence rows and the
        assembled extractive answer.  The schema mirrors OpenAI where sensible
        so existing tooling can point at this endpoint with minimal changes.

    POST /v1/chat/completions
        OpenAI-compatible chat endpoint.  Wraps the same retrieval backend so
        any OpenAI-compatible client (LangChain, LlamaIndex, curl, etc.) can
        drive the CLS knowledge base without code changes.

    POST /v1/dllm/chat
        Thin proxy to the configured generative carrier (OpenRouter by default,
        Ollama for offline use).  Only reachable when ``CLS_RETRIEVAL_ONLY=0``.

CORS is restricted to localhost origins; no external traffic is expected in the
current prototype deployment.

Start standalone:  ./scripts/launch_api.sh
"""

from __future__ import annotations

import logging
import os
import threading
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from cls_config import APP_VERSION, DEFAULT_DLLM_MODEL, KEYWORD_ONLY_RETRIEVAL, RETRIEVAL_ONLY
from cls_service import (
    answer_text,
    ask_manual,
    call_dllm_api,
    dllm_status,
    ingest_default_corpus,
    service_status,
)

CLS_RAG_MODEL = "cls-rag-cag-v1.0"
_LOG = logging.getLogger("cls.api")


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _on_railway() -> bool:
    return bool(os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PUBLIC_DOMAIN"))


def _should_bootstrap_corpus() -> bool:
    return _env_flag("CLS_BOOTSTRAP_CORPUS", default=_on_railway())


def _bootstrap_worker() -> None:
    try:
        status = service_status()
        if int(status.get("indexed_chunks") or 0) > 0:
            _LOG.info("Chroma already has %s chunks; skipping bootstrap ingest.", status["indexed_chunks"])
            return
        _LOG.info("Empty Chroma store — indexing default documents.")
        result = ingest_default_corpus()
        _LOG.info("Bootstrap ingest finished: %s", result.get("message"))
    except Exception:
        _LOG.exception("Bootstrap ingest failed; API will stay up with an empty store.")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if _should_bootstrap_corpus():
        threading.Thread(target=_bootstrap_worker, daemon=True, name="cls-bootstrap").start()
    yield


app = FastAPI(
    title="CLS RAG+CAG API",
    version=APP_VERSION,
    description="Shared RAG API plus inference carrier proxy for Streamlit, Chainlit, and OpenAI-compatible frontends.",
    lifespan=lifespan,
)
# CORS: local frontends always allowed; when deployed (Railway injects
# RAILWAY_PUBLIC_DOMAIN / the service URL), the platform's own origin and any
# https origin listed in CLS_CORS_ORIGINS are added so browser clients on the
# public domain are not blocked.
_EXTRA_ORIGINS = [o.strip() for o in os.getenv("CLS_CORS_ORIGINS", "").split(",") if o.strip()]
_RAILWAY_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN", "") or os.getenv("RAILWAY_DOMAIN", "")
if _RAILWAY_DOMAIN:
    _EXTRA_ORIGINS.append(f"https://{_RAILWAY_DOMAIN}")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_origins=_EXTRA_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(16, ge=1, le=24)
    cache_enabled: bool = True
    min_similarity: float = Field(0.80, ge=0.0, le=1.0)
    metadata_filter: dict | None = None
    debate_enabled: bool = False
    keyword_only: bool | None = None


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = CLS_RAG_MODEL
    messages: list[ChatMessage]
    stream: bool = False
    top_k: int = Field(16, ge=1, le=24)
    cache_enabled: bool = True
    min_similarity: float = Field(0.80, ge=0.0, le=1.0)
    metadata_filter: dict | None = None
    debate_enabled: bool = False
    keyword_only: bool | None = None


class DllmChatRequest(BaseModel):
    model: str = DEFAULT_DLLM_MODEL
    messages: list[ChatMessage]
    system: str | None = None


class IngestDefaultRequest(BaseModel):
    force: bool = False


def _service_index() -> dict[str, Any]:
    return {
        "service": "CLS RAG+CAG API",
        "version": APP_VERSION,
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
        "note": "This host is the FastAPI bridge, not the Streamlit UI. Open /docs or POST /v1/query.",
        "endpoints": [
            {"method": "GET", "path": "/health"},
            {"method": "GET", "path": "/v1/models"},
            {"method": "POST", "path": "/v1/query"},
            {"method": "POST", "path": "/v1/chat/completions"},
            {"method": "POST", "path": "/v1/ingest/default"},
            {"method": "GET", "path": "/v1/dllm/status"},
            {"method": "POST", "path": "/v1/dllm/chat"},
        ],
    }


def _query_payload(request: QueryRequest) -> dict[str, Any]:
    result = ask_manual(
        request.query,
        top_k=request.top_k,
        cache_enabled=request.cache_enabled,
        min_similarity=request.min_similarity,
        metadata_filter=request.metadata_filter,
        debate_enabled=request.debate_enabled,
        keyword_only=request.keyword_only,
    )
    return {
        "query": request.query,
        "answer": result["answer"],
        "answer_text": answer_text(result["answer"]),
        "category": result["category"],
        "from_cache": result["from_cache"],
        "similarity": result["similarity"],
        "retrieval_mode": result.get("retrieval_mode", "semantic"),
        "rows": result["rows"],
    }


def _last_user_message(messages: list[ChatMessage]) -> str:
    for message in reversed(messages):
        if message.role == "user" and message.content.strip():
            return message.content.strip()
    raise HTTPException(status_code=400, detail="At least one user message is required.")


@app.get("/", include_in_schema=False)
def root(request: Request):
    payload = _service_index()
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        links = "".join(
            f"<li><code>{item['method']}</code> <a href='{item['path']}'>{item['path']}</a></li>"
            if item["method"] == "GET"
            else f"<li><code>{item['method']}</code> {item['path']}</li>"
            for item in payload["endpoints"]
        )
        return HTMLResponse(
            f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{payload["service"]}</title>
  <style>
    body {{ font-family: sans-serif; max-width: 42rem; margin: 3rem auto; line-height: 1.45; }}
    code {{ background: #f2f2f2; padding: 0.1rem 0.35rem; }}
  </style>
</head>
<body>
  <h1>{payload["service"]}</h1>
  <p>{payload["note"]}</p>
  <p>Version <code>{payload["version"]}</code>. Interactive docs: <a href="/docs">/docs</a>. Health: <a href="/health">/health</a>.</p>
  <ul>{links}</ul>
</body>
</html>"""
        )
    return JSONResponse(payload)


@app.get("/health")
def health() -> dict[str, Any]:
    return {"version": APP_VERSION, "status": "ok", **service_status()}


@app.post("/v1/ingest/default")
def ingest_default(request: IngestDefaultRequest = IngestDefaultRequest()) -> dict[str, Any]:
    return ingest_default_corpus(force=request.force)


@app.get("/v1/models")
def models() -> dict[str, Any]:
    data = [
        {
            "id": CLS_RAG_MODEL,
            "object": "model",
            "created": 0,
            "owned_by": "cls",
        },
    ]
    if not RETRIEVAL_ONLY:
        data.append(
            {
                "id": DEFAULT_DLLM_MODEL,
                "object": "model",
                "created": 0,
                "owned_by": "dllm-api",
            }
        )
    return {
        "object": "list",
        "data": data,
        "retrieval_only": RETRIEVAL_ONLY,
        "keyword_only": KEYWORD_ONLY_RETRIEVAL,
    }


@app.post("/v1/query")
def query_manual(request: QueryRequest) -> dict[str, Any]:
    return _query_payload(request)


@app.post("/v1/chat/completions")
def chat_completions(request: ChatCompletionRequest) -> dict[str, Any]:
    if request.stream:
        raise HTTPException(status_code=400, detail="Streaming is not implemented for the RAG endpoint yet.")
    if request.model == DEFAULT_DLLM_MODEL:
        if RETRIEVAL_ONLY:
            raise HTTPException(
                status_code=403,
                detail="Retrieval-only mode is active; LLM chat completions are disabled.",
            )
        try:
            text = call_dllm_api(
                [message.model_dump() for message in request.messages],
                model=request.model,
            )
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Inference carrier model call failed: {exc}") from exc
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": text},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    payload = _query_payload(
        QueryRequest(
            query=_last_user_message(request.messages),
            top_k=request.top_k,
            cache_enabled=request.cache_enabled,
            min_similarity=request.min_similarity,
            metadata_filter=request.metadata_filter,
            debate_enabled=request.debate_enabled,
            keyword_only=request.keyword_only,
        )
    )
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": payload["answer_text"]},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        "cls_rag": payload,
    }


@app.get("/v1/dllm/status")
def dllm_status_endpoint() -> dict[str, Any]:
    return dllm_status()


@app.post("/v1/dllm/chat")
def dllm_chat(request: DllmChatRequest) -> dict[str, str]:
    if RETRIEVAL_ONLY:
        raise HTTPException(
            status_code=403,
            detail="Retrieval-only mode is active; LLM chat is disabled.",
        )
    try:
        text = call_dllm_api(
            [message.model_dump() for message in request.messages],
            system=request.system,
            model=request.model,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Inference carrier model call failed: {exc}") from exc
    return {"model": request.model, "content": text}
