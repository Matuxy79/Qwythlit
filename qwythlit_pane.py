"""Qwythlit Ask Lane: styling and markup for the single-column knowledge layer.

The lane is one 600px column: brand line, heading, suggested prompts, the
composer and the latest answer. The composer's top rail is the retrieval
pipeline (Parse, Retrieve, Weave). Its segments light up while a query runs and
stay grey otherwise. The Streamlit widgets live in app.py; this module supplies
their markup and CSS, plus the animated media background.
"""

from __future__ import annotations

import html
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
QWYTHLIT_POSTER_URL = "/app/static/qwyth.png"
QWYTHLIT_VIDEO_URL = "/app/static/qwythlit-intro.mp4?v=starless-1"

# Pipeline stages, in order. The composer rail has one segment per stage.
LANE_STAGES = ("Parse", "Retrieve", "Weave")

# Empty-state prompts. Clicking one fills the composer; it does not send.
LANE_SUGGESTIONS = (
    "How does the Fano lattice route domains?",
    "Summarize the SSM symmetry doc",
    "What changed in the canon this week?",
)

# The one key status shown in the composer: label and tone class.
KEY_STATUS = {
    "missing": ("Key missing", "warn"),
    "set": ("Key set", "ok"),
    "verified": ("Key verified", "ok"),
    "failed": ("Key failed", "bad"),
    "off": ("Generation off", "muted"),
}


def render_qwythlit_media_background(context: str = "home") -> str:
    """Return a fixed video background with a still-image fallback."""
    if context not in {"home", "ask_lane"}:
        raise ValueError(f"Unsupported Qwythlit background context: {context}")

    return f"""
<style>
.stApp:has(.qwythlit-media-bg) {{
    isolation: isolate;
    background: transparent !important;
}}
.stApp:has(.qwythlit-media-bg) div[data-testid="stAppViewContainer"],
.stApp:has(.qwythlit-media-bg) section[data-testid="stMain"] {{
    background: transparent !important;
}}
.stApp:has(.qwythlit-media-bg) div[data-testid="stMainBlockContainer"] {{
    position: relative;
    z-index: 1;
}}
.qwythlit-media-bg {{
    position: fixed;
    inset: 0;
    z-index: 0;
    overflow: hidden;
    pointer-events: none;
    background: #111716 url("{QWYTHLIT_POSTER_URL}") center center / cover no-repeat;
}}
.qwythlit-media-bg video {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center center;
    opacity: 1;
}}
.qwythlit-media-scrim {{
    position: absolute;
    inset: 0;
    background:
        linear-gradient(180deg, rgba(5, 8, 9, 0.38), rgba(5, 8, 9, 0.62)),
        linear-gradient(90deg, rgba(5, 8, 9, 0.56), rgba(5, 8, 9, 0.18) 55%, rgba(5, 8, 9, 0.38));
}}
.qwythlit-media-bg[data-context="ask_lane"] .qwythlit-media-scrim {{
    background:
        linear-gradient(180deg, rgba(4, 7, 9, 0.68), rgba(4, 7, 9, 0.82)),
        linear-gradient(90deg, rgba(5, 10, 11, 0.64), rgba(5, 10, 11, 0.38) 55%, rgba(5, 10, 11, 0.66));
}}
@media (max-width: 700px) {{
    .qwythlit-media-bg {{ background-position: 44% center; }}
    .qwythlit-media-bg video {{ object-position: 48% center; }}
}}
@media (prefers-reduced-motion: reduce) {{
    .qwythlit-media-bg video {{ display: none; }}
}}
</style>
<div class="qwythlit-media-bg" data-context="{context}" aria-hidden="true">
    <video autoplay muted loop playsinline preload="metadata" poster="{QWYTHLIT_POSTER_URL}" tabindex="-1" disablepictureinpicture>
        <source src="{QWYTHLIT_VIDEO_URL}" type="video/mp4">
    </video>
    <div class="qwythlit-media-scrim"></div>
</div>
""".strip()


QWYTHLIT_PANE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --q-bg: #0b0f10;
    --q-panel: rgba(14, 18, 20, 0.86);
    --q-line: rgba(255, 255, 255, 0.12);
    --q-ink: #f4f7f6;
    --q-muted: #9aa6a3;
    --q-faint: #66726f;
    --q-cyan: #62d3bc;
    --q-amber: #f0b429;
    --q-red: #f07178;
}

html, body, #root {
    background: var(--q-bg) !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    color: var(--q-ink) !important;
}

.stApp,
div[data-testid="stAppViewContainer"],
section[data-testid="stMain"] {
    background: var(--q-bg) !important;
    color: var(--q-ink) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(10, 13, 34, 0.95) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(20px) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--q-ink) !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255, 255, 255, 0.08) !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-baseweb="base-input"] {
    background: rgba(18, 22, 54, 0.8) !important;
    border-color: rgba(255, 255, 255, 0.12) !important;
    border-radius: 12px !important;
}

/* Sidebar nav rows (Home, Clear chat) — ghost buttons so global light .stButton rules
   and Streamlit's default white surfaces do not bleed through on the dark lane. */
section[data-testid="stSidebar"] .st-key-ask_lane_home_btn button,
section[data-testid="stSidebar"] .st-key-full_app_home_btn button,
section[data-testid="stSidebar"] .st-key-lane_clear_chat button,
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {
    background: transparent !important;
    border: 0.5px solid transparent !important;
    color: #A9AEC4 !important;
    justify-content: flex-start !important;
    border-radius: 8px !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .st-key-ask_lane_home_btn button:hover,
section[data-testid="stSidebar"] .st-key-full_app_home_btn button:hover,
section[data-testid="stSidebar"] .st-key-lane_clear_chat button:hover,
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {
    background: rgba(255, 255, 255, 0.06) !important;
    color: #E6E8F0 !important;
}
section[data-testid="stSidebar"] .st-key-lane_clear_chat button:hover {
    border-color: rgba(244, 63, 94, 0.45) !important;
}
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] {
    background: rgba(93, 202, 165, 0.14) !important;
    color: #5DCAA5 !important;
}
section[data-testid="stSidebar"] .st-key-ask_lane_home_btn button p,
section[data-testid="stSidebar"] .st-key-full_app_home_btn button p,
section[data-testid="stSidebar"] .st-key-lane_clear_chat button p,
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] span {
    color: inherit !important;
}

/* Sidebar brand: teal Q mark + wordmark, echoing the lane's main-column brand. */
.q-side-brand {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.1rem 0.15rem 0.85rem;
}
.q-side-mark {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(93, 202, 165, 0.13);
    border: 1px solid rgba(93, 202, 165, 0.45);
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    font-size: 0.98rem;
    color: #5DCAA5;
}
.q-side-word {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 1.22rem;
    letter-spacing: 0.01em;
    color: #E6E8F0 !important;
}

/* On the lane, Home is the current page: tint the ghost row like stPageLink[aria-current]. */
section[data-testid="stSidebar"] .st-key-ask_lane_home_btn button {
    background: rgba(93, 202, 165, 0.13) !important;
    border-color: rgba(93, 202, 165, 0.30) !important;
    color: #5DCAA5 !important;
    font-weight: 600;
}
section[data-testid="stSidebar"] .st-key-ask_lane_home_btn button:hover {
    background: rgba(93, 202, 165, 0.22) !important;
    color: #5DCAA5 !important;
}

/* Teal links and quiet captions anywhere in the lane sidebar. */
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] a {
    color: #5DCAA5 !important;
}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: #8b90a8 !important;
}

/* Dropdown menus (composer chips open these) */
div[data-baseweb="popover"]:has(ul[role="listbox"]) {
    min-width: 260px !important;
}
div[data-baseweb="popover"] div[data-baseweb="menu"],
ul[role="listbox"] {
    background: #0d1214 !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 12px !important;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6) !important;
}
li[role="option"] {
    color: #e2e8f0 !important;
    background: transparent !important;
}
li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
    background: rgba(98, 211, 188, 0.2) !important;
    color: #ffffff !important;
}

/* One column, 600px, left edge shared by heading, prompts and composer */
div[data-testid="stMainBlockContainer"] {
    max-width: 600px !important;
    padding: 2.6rem 16px 5rem !important;
}

.q-brand {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 0 0 1.4rem;
}
.q-mark {
    width: 20px;
    height: 20px;
    border-radius: 6px;
    background: linear-gradient(135deg, #285e59, #72b7a7 52%, #557184);
    box-shadow: 0 0 12px rgba(0, 244, 210, 0.45);
}
.q-wordmark {
    font-family: 'Outfit', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    color: var(--q-muted);
}
.q-heading h1 {
    font-family: 'Outfit', 'Inter', sans-serif !important;
    font-size: clamp(1.9rem, 4vw, 2.4rem) !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em !important;
    line-height: 1.12 !important;
    color: #ffffff !important;
    margin: 0 0 0.5rem !important;
}
.q-heading p {
    font-size: 1rem !important;
    color: var(--q-muted) !important;
    line-height: 1.5 !important;
    margin: 0 0 1.5rem !important;
}

/* Suggested prompts: pills that fill the composer */
.st-key-lane_suggest {
    gap: 0.5rem;
    margin-bottom: 1.2rem;
}
.st-key-lane_suggest button {
    justify-content: flex-start !important;
    text-align: left !important;
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid var(--q-line) !important;
    border-radius: 999px !important;
    color: var(--q-ink) !important;
    font-size: 0.92rem !important;
    padding: 0.5rem 1.1rem !important;
}
.st-key-lane_suggest button:hover {
    border-color: rgba(98, 211, 188, 0.6) !important;
    color: #ffffff !important;
}
.st-key-lane_suggest button:hover p {
    color: #ffffff !important;
}
.st-key-lane_suggest button p {
    color: var(--q-ink) !important;
}
/* Streamlit paints a focused or pressed button white; keep the pill dark after a click. */
.st-key-lane_suggest button:focus,
.st-key-lane_suggest button:active {
    background: rgba(98, 211, 188, 0.12) !important;
    border-color: rgba(98, 211, 188, 0.6) !important;
    color: #ffffff !important;
}
.st-key-lane_suggest button:focus p,
.st-key-lane_suggest button:active p {
    color: #ffffff !important;
}

/* Composer: one bordered form holding rail, question, settings chips and send */
div[data-testid="stForm"]:has(.q-rail) {
    position: relative !important;
    background: var(--q-panel) !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 18px !important;
    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.5) !important;
    backdrop-filter: blur(18px);
    overflow: hidden;
    padding: 1.1rem 1rem 0.8rem !important;
}
.q-rail {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    display: flex;
    gap: 2px;
    pointer-events: none;
}
.q-seg {
    flex: 1;
    background: rgba(255, 255, 255, 0.1);
    transition: background 0.35s ease, box-shadow 0.35s ease;
}
.q-seg.is-lit {
    background: linear-gradient(90deg, #285e59, #62d3bc);
    box-shadow: 0 0 12px rgba(98, 211, 188, 0.55);
}

div[data-testid="stForm"]:has(.q-rail) div[data-baseweb="textarea"],
div[data-testid="stForm"]:has(.q-rail) div[data-baseweb="base-input"] {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}
div[data-testid="stForm"]:has(.q-rail) textarea,
div[data-testid="stForm"]:has(.q-rail) textarea:focus {
    resize: none !important;
    border: 0 !important;
    outline: none !important;
    box-shadow: none !important;
    background: transparent !important;
    color: var(--q-ink) !important;
    font-size: 1.02rem !important;
    line-height: 1.5 !important;
    caret-color: var(--q-cyan) !important;
    padding: 0.2rem 0 !important;
}
div[data-testid="stForm"]:has(.q-rail) textarea::placeholder {
    color: var(--q-faint) !important;
}

/* Settings chips: small dropdowns for corpus and model */
div[data-testid="stForm"]:has(.q-rail) div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    min-height: 32px !important;
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid var(--q-line) !important;
    border-radius: 999px !important;
}
div[data-testid="stForm"]:has(.q-rail) div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
    font-size: 0.84rem !important;
    color: var(--q-ink) !important;
}

/* Single status row: pipeline state, then the key dot */
.q-status-row {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 0.7rem;
    min-height: 32px;
    font-size: 0.8rem;
    color: var(--q-muted);
    white-space: nowrap;
}
.q-pipeline {
    margin-right: auto;
}
.q-key {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-weight: 600;
}
.q-key i {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
    background: currentColor;
    box-shadow: 0 0 8px currentColor;
}
.q-key.is-warn { color: var(--q-amber); }
.q-key.is-ok { color: var(--q-cyan); }
.q-key.is-bad { color: var(--q-red); }
.q-key.is-muted { color: var(--q-faint); }

/* Send button */
div[data-testid="stForm"]:has(.q-rail) button[kind="primaryFormSubmit"],
div[data-testid="stForm"]:has(.q-rail) button[data-testid="stBaseButton-primaryFormSubmit"] {
    width: 38px !important;
    min-width: 38px !important;
    height: 38px !important;
    padding: 0 !important;
    border: 0 !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #285e59, #72b7a7 55%, #557184) !important;
    color: #06201d !important;
    font-size: 1.1rem !important;
    font-weight: 800 !important;
    box-shadow: 0 0 18px rgba(0, 244, 210, 0.35) !important;
}

.q-hint {
    font-size: 0.78rem;
    color: var(--q-muted);
    margin: 0.6rem 0 0 0.25rem;
}

/* Answer: source chips and evidence bullets, dark theme */
.lane-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 0 0 0.7rem;
}
.lane-chip {
    font-size: 0.74rem;
    font-weight: 600;
    line-height: 1;
    padding: 5px 10px;
    border-radius: 999px;
    background: rgba(98, 211, 188, 0.1);
    border: 1px solid rgba(98, 211, 188, 0.32);
    color: #bfe9de;
    white-space: nowrap;
}
.lane-evidence {
    margin: 0.2rem 0 0.4rem 1.15rem;
    padding: 0;
}
.lane-evidence li {
    color: #e3ebe8 !important;
    font-size: 0.95rem !important;
    font-weight: 400 !important;
    line-height: 1.5;
    margin: 0 0 0.4rem;
}

/* The question above its answer, flush left with the heading */
.stApp div[data-testid="stMarkdownContainer"] p.lane-query {
    font-family: 'Outfit', 'Inter', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--q-ink) !important;
    margin: 0.4rem 0 0.7rem !important;
}
/* The app's global sheet paints markdown text dark (--ink), and the lane sits on a dark
   video, so the lane's text colours are set with the .stApp prefix to win that cascade. */
.stApp div[data-testid="stMarkdownContainer"] p,
.stApp div[data-testid="stMarkdownContainer"] li,
.stApp .lane-evidence li {
    color: #e3ebe8 !important;
}
.stApp div[data-testid="stMarkdownContainer"] p.q-hint {
    color: var(--q-muted) !important;
}
.stApp .q-heading h1 {
    color: #ffffff !important;
}
.stApp div[data-testid="stMarkdownContainer"] .q-heading p {
    color: var(--q-muted) !important;
}

@media (max-width: 700px) {
    div[data-testid="stMainBlockContainer"] {
        padding-top: 1.6rem !important;
    }
    .q-status-row {
        flex-wrap: wrap;
        justify-content: flex-start;
    }
    .q-pipeline {
        margin-right: 0;
    }
}
@media (prefers-reduced-motion: reduce) {
    .q-seg { transition: none; }
}
</style>
"""


def render_lane_heading() -> str:
    """Brand line, heading and subtitle. One block, left-aligned in the lane column."""
    return (
        '<div class="q-brand"><span class="q-mark"></span><span class="q-wordmark">qwythlit</span></div>'
        '<div class="q-heading"><h1>Ask the knowledge layer</h1>'
        '<p>Answers are grounded in your canon corpus, with sources.</p></div>'
    )


def render_sidebar_brand() -> str:
    """Sidebar brand row: teal Q mark + wordmark, matching the lane's main column."""
    return (
        '<div class="q-side-brand"><span class="q-side-mark">Q</span>'
        '<span class="q-side-word">Qwythlit</span></div>'
    )


def composer_rail_html(active_stage: int = 0) -> str:
    """The thin pipeline rail at the top of the composer.

    ``active_stage`` is 0 when idle (every segment grey). During a query it is
    the number of stages reached so far, so 1 lights Parse, 2 lights Parse and
    Retrieve, and 3 lights all three (Weave is running).
    """
    count = max(0, min(int(active_stage), len(LANE_STAGES)))
    segments = "".join(
        f'<span class="q-seg{" is-lit" if index < count else ""}"></span>'
        for index in range(len(LANE_STAGES))
    )
    label = "Pipeline idle" if count == 0 else f"Pipeline: {LANE_STAGES[count - 1]}"
    return f'<div class="q-rail" role="img" aria-label="{html.escape(label)}">{segments}</div>'


def composer_status_html(pipeline_text: str, key_state: str) -> str:
    """The composer's one status row: pipeline state on the left, key status on the right."""
    label, tone = KEY_STATUS.get(key_state, KEY_STATUS["missing"])
    return (
        '<div class="q-status-row">'
        f'<span class="q-pipeline">{html.escape(pipeline_text)}</span>'
        f'<span class="q-key is-{tone}"><i></i>{html.escape(label)}</span>'
        '</div>'
    )
