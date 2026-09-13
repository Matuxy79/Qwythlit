"""Chainlit Ask Lane — a streaming RAG/CAG chat over the shared backend.

Run:  chainlit run chat_lane.py -w        (or ./scripts/launch_chat.sh)

Single-pass answer design:
  Instant grounded answer from the RAG/CAG engine, no LLM wait.
  Formatted markdown bullets with match badge (exact / close / loose / cached)
  and source chips attached.  This is always the source of truth.

The retrieval / CAG / embedder engine is reused unchanged from jls_service and
jls_backend — this file is only the Chainlit view.
"""

from __future__ import annotations

import os

import chainlit as cl
from chainlit.input_widget import Select

from jls_config import APP_VERSION, KEYWORD_ONLY_RETRIEVAL, RESEARCH_SCOPES, RETRIEVAL_ONLY
from jls_backend.query_repair import repair_query
from jls_service import ask_manual


def _match_badge(result: dict) -> str:
    """Advertise the instant grounded layer's confidence."""
    if result.get("from_cache"):
        return "⚡ exact match · cached"
    rows = result.get("rows") or []
    score = rows[0]["score"] if rows else 0.0
    label = "exact match" if score >= 0.9 else "close match" if score >= 0.6 else "loose match"
    return f"● {label} · {score:.2f}"


def _grounded_bullets(answer: list[str]) -> str:
    return "\n".join(f"- {s.split(' [Source:')[0].strip()}" for s in answer)


def _sources(rows: list[dict]) -> list[str]:
    seen: set = set()
    items: list[str] = []
    for row in rows:
        meta = row.get("metadata", {}) or {}
        src = str(meta.get("source", "")).rsplit(".", 1)[0]
        page = meta.get("page")
        key = (src, page)
        if src and key not in seen:
            seen.add(key)
            items.append(f"{src}" + (f" · p{page}" if page else ""))
    return items


_STREAMLIT_URL = os.getenv("JLS_STREAMLIT_URL") or os.getenv("JS_STREAMLIT_URL") or os.getenv("CLS_STREAMLIT_URL", "http://localhost:8501")


@cl.on_chat_start
async def start():
    scopes = list(RESEARCH_SCOPES.keys())
    await cl.ChatSettings(
        [Select(id="scope", label="Research scope", values=scopes, initial_index=0)]
    ).send()
    cl.user_session.set("scope", scopes[0])
    await cl.Message(
        content=(
            f"### 🐉 Qwythlit Ask Lane · John's Synchrotron `{APP_VERSION}`\n"
            "**Ask the knowledge layer** — instant cited answers from your indexed documents with pulse retrieval. "
            + (
                "Temporary retrieval-only mode is active; no model answer will run."
                if RETRIEVAL_ONLY
                else "The grounded evidence is the source of truth."
            )
        ),
    ).send()


@cl.on_settings_update
async def update_settings(settings: dict):
    cl.user_session.set("scope", settings.get("scope"))


@cl.on_message
async def on_message(message: cl.Message):
    query = message.content.strip()
    if not query:
        return

    scope = cl.user_session.get("scope") or "All"
    mfilter = RESEARCH_SCOPES.get(scope)

    # ── 01 · Parse (intent + context) ───────────────────────────
    async with cl.Step(name="01 · Parse", type="tool") as step1:
        repaired = repair_query(query)
        search = repaired["search"]
        step1.output = f"intent + context parsed (search: '{search}', scope: {scope})"

    # ── 02 · Retrieve (graph + chunks) ──────────────────────────
    async with cl.Step(name="02 · Retrieve", type="tool") as step2:
        result = await cl.make_async(ask_manual)(
            search,
            top_k=16,
            metadata_filter=mfilter,
            keyword_only=KEYWORD_ONLY_RETRIEVAL,
        )
        rows   = result.get("rows") or []
        answer = result.get("answer") or []
        step2.output = f"retrieved {len(rows)} evidence chunks from synchrotron store"

    if not rows:
        await cl.Message(content="_Nothing relevant found in synchrotron evidence — try rephrasing._").send()
        return

    # ── 03 · Weave (grounded answer) ────────────────────────────
    badge   = _match_badge(result)
    sources = _sources(rows)
    async with cl.Step(name="03 · Weave", type="tool") as step3:
        step3.output = f"grounded answer lattice woven ({badge})"

    p1 = cl.Message(content=f"**{badge}**\n\n{_grounded_bullets(answer)}")
    if sources:
        p1.elements = [
            cl.Text(
                name="Sources",
                content="\n".join(f"📄 {s}" for s in sources),
                display="inline",
            )
        ]
    await p1.send()
