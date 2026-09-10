"""Nonblocking empty-store corpus bootstrap shared by the deployed frontends."""

from __future__ import annotations

import logging
import os
import threading


_LOG = logging.getLogger("jls.bootstrap")
_START_LOCK = threading.Lock()
_bootstrap_thread: threading.Thread | None = None


def should_bootstrap_corpus() -> bool:
    """Enable on Railway by default, with an explicit environment override."""
    for var in ("JLS_BOOTSTRAP_CORPUS", "JS_BOOTSTRAP_CORPUS", "CLS_BOOTSTRAP_CORPUS"):
        value = os.getenv(var)
        if value is not None:
            return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PUBLIC_DOMAIN"))


def _bootstrap_worker() -> None:
    try:
        # Import only in the worker: starting the frontend must not wait for the
        # persistent store, embedding model, or corpus indexing to initialize.
        from jls_service import ingest_default_corpus, service_status

        status = service_status()
        if int(status.get("indexed_chunks") or 0) > 0:
            _LOG.info("Chroma already has %s chunks; skipping bootstrap ingest.", status["indexed_chunks"])
            return
        _LOG.info("Empty Chroma store; indexing default documents.")
        result = ingest_default_corpus()
        if not result.get("ok", True):
            _LOG.warning("Corpus bootstrap could not index documents: %s", result.get("message"))
        else:
            _LOG.info("Corpus bootstrap finished: %s", result.get("message"))
    except Exception:
        _LOG.exception("Corpus bootstrap failed; application remains available.")


def start_corpus_bootstrap() -> bool:
    """Start at most one background ingest per process; return whether started.

    A completed or failed attempt is not repeated on frontend reruns. Existing
    stores are retained, and manual indexing remains available after a failure.
    """
    global _bootstrap_thread
    if not should_bootstrap_corpus():
        return False
    with _START_LOCK:
        if _bootstrap_thread is not None:
            return False
        worker = threading.Thread(target=_bootstrap_worker, daemon=True, name="jls-bootstrap")
        worker.start()
        _bootstrap_thread = worker
        return True
