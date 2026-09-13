"""Central configuration for John's Light Source (JLS).

All runtime behaviour is controlled through environment variables so the same
codebase can run in fast prototype mode (defaults) or with a live LLM carrier,
without touching source code. Set values in ``jls.env`` (gitignored) before
launching; the launch scripts source that file automatically.

Key environment variables
-------------------------
JLS_RETRIEVAL_ONLY       1 = hard-disable the generative carrier entirely
                         (default: 0 — generation is on; the Streamlit
                         "Generate via OpenRouter" toggle is the only
                         retrieval-only switch for the UIs)
JLS_KEYWORD_ONLY         1 = skip vector search, use lexical term overlap only (default: 1)
JLS_DLLM_API_KEY         API key for the generative carrier (OpenRouter)
JLS_DLLM_API_URL         Base URL for the carrier (default: https://openrouter.ai/api/v1)
JLS_DLLM_MODEL           Model name passed to the carrier (default: openai/gpt-oss-120b)
JLS_API_URL              Internal FastAPI bridge URL (default: http://127.0.0.1:8010)
JLS_CHROMA_DIR           On-disk Chroma persistent path (default: <app>/chroma_store)
JLS_BOOTSTRAP_CORPUS     1 = index DEFAULT_DOCUMENTS_DIR when the store is empty
                         (default: 1 on Railway, 0 locally)

Discipline scopes (RESEARCH_SCOPES)
------------------------------------
Each entry maps a human-readable discipline name to a ChromaDB metadata filter dict.
Passing ``None`` as the filter returns the entire corpus (All).
The dict keys (e.g. ``"physics"``) also serve as folder names under
``data/corpus/`` for batch ingest via ``scripts/ingest_corpus.py``.

To add a new discipline: append one entry to RESEARCH_SCOPES and create the
corresponding sub-folder under ``data/corpus/``.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path


def _env_get(suffix: str, default: str = "") -> str:
    for prefix in ("JLS_", "JS_"):
        val = os.getenv(prefix + suffix)
        if val is not None:
            return val
    return default


def _env_flag(suffix: str, default: bool = False) -> bool:
    for prefix in ("JLS_", "JS_"):
        val = os.getenv(prefix + suffix)
        if val is not None:
            return val.strip().lower() in {"1", "true", "yes", "on"}
    return default


APP_ROOT = Path(__file__).resolve().parent
MANUAL_DIR = APP_ROOT / "data" / "training_corpus"
_default_doc_dir = str(MANUAL_DIR / "test_books") if (MANUAL_DIR / "test_books").exists() else str(MANUAL_DIR)
DEFAULT_DOCUMENTS_DIR = Path(_env_get("DEFAULT_DOCUMENTS_DIR", _default_doc_dir))
DEFAULT_DOCUMENT_DOMAIN = _env_get("DEFAULT_DOCUMENT_DOMAIN", "")
CHROMA_DIR = Path(_env_get("CHROMA_DIR") or str(APP_ROOT / "chroma_store"))

COLLECTION_NAME = "jls_v2_evidence"            # Evidence Store (384d, MiniLM)
CACHE_COLLECTION_NAME = "jls_v2_cag_cache"   # CAG Layer (384d, MiniLM)
CHUNK_TARGET_CHARS = 1100
CHUNK_OVERLAP_CHARS = 180

APP_VERSION = "v1.3"

# Research scopes — one lane per discipline. Shared by every frontend (Streamlit,
# Chainlit). None bypasses the Chroma metadata filter; any other value is passed as
# metadata_filter={"domain": ...}. The domain slugs double as the folder names under
# data/corpus/ that scripts/ingest_corpus.py reads (it derives its valid-domain set
# from this map), so a lane only returns evidence once docs are ingested under its slug.
RESEARCH_SCOPES = {
    "All":              None,
    "Science":          {"domain": "science"},
    "Maths":            {"domain": "maths"},
    "Physics":          {"domain": "physics"},
    "Chemistry":        {"domain": "chemistry"},
    "Biology":          {"domain": "biology"},
    "Computer Science": {"domain": "computer_science"},
}

# Admin-added scopes are layered on top of the built-ins above and persisted here
# so they survive restarts and are shared by every session/frontend. The built-in
# names stay the source of truth in code; only runtime additions go to disk.
CUSTOM_SCOPES_PATH = APP_ROOT / "data" / "custom_scopes.json"
_BUILTIN_SCOPE_NAMES = frozenset(RESEARCH_SCOPES)


def _slugify_domain(value: str) -> str:
    """Normalise free text into a corpus folder slug (lowercase, a-z0-9 and _)."""
    return re.sub(r"[^a-z0-9]+", "_", (value or "").strip().lower()).strip("_")


def _load_custom_scopes() -> dict[str, dict | None]:
    """Read admin-added scopes from disk; tolerate a missing or corrupt file."""
    if not CUSTOM_SCOPES_PATH.exists():
        return {}
    try:
        raw = json.loads(CUSTOM_SCOPES_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(raw, dict):
        return {}
    return {
        name.strip(): mfilter
        for name, mfilter in raw.items()
        if isinstance(name, str) and name.strip()
    }


def _persist_custom_scopes() -> None:
    """Write every non-built-in scope back to CUSTOM_SCOPES_PATH as JSON."""
    custom = {
        name: mfilter
        for name, mfilter in RESEARCH_SCOPES.items()
        if name not in _BUILTIN_SCOPE_NAMES
    }
    CUSTOM_SCOPES_PATH.parent.mkdir(parents=True, exist_ok=True)
    CUSTOM_SCOPES_PATH.write_text(
        json.dumps(custom, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def add_research_scope(name: str, domain: str = "") -> tuple[str, dict]:
    """Register a new discipline scope and persist it so it survives restarts.

    Mutates RESEARCH_SCOPES in place so any frontend holding a reference to the
    dict picks the new lane up on its next rerun, then saves the custom subset to
    disk. ``domain`` defaults to a slug derived from ``name``. The slug doubles as
    the folder name under ``data/corpus/`` that ingest reads, so a new lane stays
    empty until documents are ingested under that slug.

    Returns ``(display_name, metadata_filter)``. Raises ``ValueError`` on empty or
    duplicate input.
    """
    name = (name or "").strip()
    slug = _slugify_domain(domain or name)
    if not name:
        raise ValueError("Scope name cannot be empty.")
    if not slug:
        raise ValueError("Domain slug must contain at least one letter or digit.")
    if name in RESEARCH_SCOPES:
        raise ValueError(f"A scope named \u201c{name}\u201d already exists.")
    existing_slugs = {
        f["domain"] for f in RESEARCH_SCOPES.values()
        if isinstance(f, dict) and "domain" in f
    }
    if slug in existing_slugs:
        raise ValueError(f"The domain \u201c{slug}\u201d is already used by another scope.")
    mfilter = {"domain": slug}
    RESEARCH_SCOPES[name] = mfilter
    _persist_custom_scopes()
    return name, mfilter


# Layer any previously saved admin scopes on top of the built-ins, in place, so
# existing references to RESEARCH_SCOPES stay valid.
for _scope_name, _scope_filter in _load_custom_scopes().items():
    RESEARCH_SCOPES.setdefault(_scope_name, _scope_filter)

DEFAULT_API_URL = _env_get("API_URL", "http://127.0.0.1:8010")

# Generation is on by default: the Streamlit "Generate via OpenRouter" toggle is
# the only retrieval-only switch for the UIs. Set JLS_RETRIEVAL_ONLY=1 to
# hard-disable carrier synthesis/cleanup/proxy calls in headless paths too.
RETRIEVAL_ONLY = _env_flag("RETRIEVAL_ONLY", default=False)

# Temporary keyword-first mode: skip semantic embedding/CAG cache lookup on queries and
# rank directly by lexical term overlap. Set JLS_KEYWORD_ONLY=0 to restore hybrid
# semantic+lexical retrieval.
KEYWORD_ONLY_RETRIEVAL = _env_flag("KEYWORD_ONLY", default=True)

# Default generative carrier: OpenRouter + openai/gpt-oss-120b (one key, 100+ models).
# Plug-and-play — paste JLS_DLLM_API_KEY into jls.env (gitignored) and launch.
DEFAULT_DLLM_API_URL = _env_get("DLLM_API_URL", "https://openrouter.ai/api/v1").rstrip("/")
DEFAULT_DLLM_API_KEY = _env_get("DLLM_API_KEY", "")
DEFAULT_DLLM_MODEL = _env_get("DLLM_MODEL", "openai/gpt-oss-120b")
