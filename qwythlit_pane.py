"""Qwythlit animated pane — cinematic micro-stub for the Ask Lane.

Renders the chromatic familiar, dynamic synchrotron beam pulse, lifecycle
state indicators (01 · Parse, 02 · Retrieve, 03 · Weave), and floating 'Q' launcher.
"""

from __future__ import annotations

import base64
import html
import os
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
_DRAGON_PATH = APP_ROOT / "animator" / "qwythlit-dragon-stub" / "public" / "qwythlit-dragon.jpg"
if not _DRAGON_PATH.exists():
    _DRAGON_PATH = APP_ROOT / "animator" / "GreatGreenTransformer.jpg"

_DRAGON_B64 = ""
if _DRAGON_PATH.exists():
    try:
        _DRAGON_B64 = base64.b64encode(_DRAGON_PATH.read_bytes()).decode("ascii")
    except Exception:
        _DRAGON_B64 = ""

QWYTHLIT_PANE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --q-bg: #060814;
    --q-card-bg: rgba(11, 14, 38, 0.88);
    --q-card-border: rgba(255, 255, 255, 0.12);
    --q-ink: #f7f7ff;
    --q-muted: #8c93ad;
    --q-faint: #59617d;
    --q-cyan: #00f4d2;
    --q-magenta: #d946ef;
    --q-amber: #ffbe0b;
    --q-orange: #ff5e36;
    --q-indigo: #7a5cff;
}

html, body, #root {
    background: var(--q-bg) !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    color: var(--q-ink) !important;
}

.stApp,
div[data-testid="stAppViewContainer"],
section[data-testid="stMain"] {
    background:
        radial-gradient(circle at 72% 30%, rgba(122, 92, 255, 0.16), transparent 38rem),
        radial-gradient(circle at 18% 75%, rgba(0, 244, 210, 0.08), transparent 34rem),
        radial-gradient(circle at 50% 10%, rgba(255, 94, 54, 0.06), transparent 28rem),
        var(--q-bg) !important;
    color: var(--q-ink) !important;
}

/* Sidebar — deep dark glassmorphism */
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

/* BaseWeb Controls in Sidebar */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-baseweb="base-input"] {
    background: rgba(18, 22, 54, 0.8) !important;
    border-color: rgba(255, 255, 255, 0.12) !important;
    border-radius: 12px !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] input {
    color: #ffffff !important;
    background: transparent !important;
}
section[data-testid="stSidebar"] div[data-baseweb="tag"] {
    background: rgba(122, 92, 255, 0.25) !important;
    border: 1px solid rgba(122, 92, 255, 0.5) !important;
    color: #e2d9ff !important;
    border-radius: 999px !important;
}

/* Popover dropdown */
div[data-baseweb="popover"] div[data-baseweb="menu"],
ul[role="listbox"] {
    background: #0d102b !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 12px !important;
    box-shadow: 0 16px 40px rgba(0,0,0,0.6) !important;
}
li[role="option"] {
    color: #e2e8f0 !important;
    background: transparent !important;
}
li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
    background: rgba(122, 92, 255, 0.3) !important;
    color: #ffffff !important;
}

/* Hero */
.qwythlit-hero {
    max-width: 680px;
    margin: 1.2rem auto 2.2rem;
    text-align: left;
    padding: 0 0.5rem;
}
.qwythlit-hero h1 {
    font-family: 'Outfit', 'Inter', sans-serif !important;
    font-size: clamp(2.4rem, 4.8vw, 3.8rem) !important;
    font-weight: 800 !important;
    line-height: 1.05 !important;
    letter-spacing: -0.04em !important;
    color: #ffffff !important;
    margin: 0 0 1rem !important;
}
.qwythlit-hero p {
    font-size: 1.05rem !important;
    color: var(--q-muted) !important;
    line-height: 1.65 !important;
    margin: 0 !important;
    max-width: 580px;
}

/* The Qwythlit Card */
.qwythlit-card {
    max-width: 680px;
    margin: 0 auto 2.5rem;
    background: var(--q-card-bg);
    border: 1px solid var(--q-card-border);
    border-radius: 28px;
    padding: 2rem 2.2rem 2rem;
    box-shadow:
        0 24px 70px rgba(0, 0, 0, 0.75),
        0 0 60px rgba(122, 92, 255, 0.14);
    backdrop-filter: blur(28px);
    position: relative;
    overflow: hidden;
}

/* Card Topbar */
.qwythlit-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.6rem;
}
.qwythlit-brand {
    display: flex;
    align-items: center;
    gap: 0.65rem;
}
.qwythlit-mark-badge {
    width: 22px;
    height: 22px;
    border-radius: 6px;
    background: linear-gradient(135deg, #ff5e36, #ffbe0b 35%, #00f4d2 70%, #7a5cff);
    display: inline-block;
    box-shadow: 0 0 12px rgba(0, 244, 210, 0.5);
}
.qwythlit-brand-title {
    font-family: 'Outfit', sans-serif;
    font-size: 0.84rem;
    font-weight: 800;
    letter-spacing: 0.16em;
    color: #ffffff;
}
.qwythlit-status {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.qwythlit-status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--q-cyan);
    box-shadow: 0 0 10px var(--q-cyan);
    animation: qDotPulse 2s ease-in-out infinite;
}
.qwythlit-status-text {
    color: var(--q-cyan);
}

@keyframes qDotPulse {
    0%, 100% { opacity: 0.7; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.3); }
}

/* Animated Visual Area */
.qwythlit-visual {
    position: relative;
    height: 190px;
    margin: 0.5rem 0 1.6rem;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    border-radius: 20px;
    background: radial-gradient(ellipse at center, rgba(30, 25, 75, 0.45) 0%, transparent 75%);
}

.qwythlit-halo {
    position: absolute;
    width: 220px;
    height: 220px;
    border-radius: 50%;
    background: conic-gradient(from 30deg, #ff5e36, #ffbe0b, #00f4d2, #3a86ff, #a855f7, #ff5e36);
    filter: blur(55px);
    opacity: 0.18;
    animation: qHaloSpin 16s linear infinite;
}
@keyframes qHaloSpin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Dragon subtle watermark backdrop */
.qwythlit-dragon-bg {
    position: absolute;
    width: 240px;
    height: 160px;
    opacity: 0.22;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    filter: drop-shadow(0 0 24px rgba(122, 92, 255, 0.6));
    mix-blend-mode: screen;
    pointer-events: none;
    animation: qDragonFloat 6s ease-in-out infinite;
}
@keyframes qDragonFloat {
    0%, 100% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-6px) scale(1.03); }
}

/* Chromatic particles */
.q-particle {
    position: absolute;
    border-radius: 50%;
    pointer-events: none;
    animation: qParticleMotion var(--duration, 3.5s) var(--delay, 0s) ease-in-out infinite;
}
@keyframes qParticleMotion {
    0%, 100% {
        transform: translate(0, 0) scale(1);
        opacity: var(--base-op, 0.35);
    }
    50% {
        transform: translate(var(--dx, 10px), var(--dy, -12px)) scale(1.4);
        opacity: 0.95;
    }
}

/* Rainbow Synchrotron Spectral Beam */
.qwythlit-beam-wrap {
    position: relative;
    width: 82%;
    height: 14px;
    z-index: 10;
}
.qwythlit-beam-glow {
    position: absolute;
    inset: -6px -4px;
    border-radius: 999px;
    background: linear-gradient(90deg, #ff5e36 0%, #ffbe0b 25%, #00f4d2 50%, #3a86ff 75%, #a855f7 100%);
    filter: blur(14px);
    opacity: 0.72;
    animation: qBeamBreathe 3s ease-in-out infinite alternate;
}
.qwythlit-beam-core {
    position: relative;
    width: 100%;
    height: 14px;
    border-radius: 999px;
    background: linear-gradient(90deg, #ff5e36 0%, #ffbe0b 22%, #00f4d2 48%, #3a86ff 72%, #a855f7 100%);
    overflow: hidden;
    box-shadow: 0 0 20px rgba(0, 244, 210, 0.5), 0 0 35px rgba(122, 92, 255, 0.4);
}
.qwythlit-beam-pulse {
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.95) 50%, transparent 100%);
    width: 40%;
    transform: translateX(-100%);
    animation: qBeamPulse 2.2s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}
@keyframes qBeamPulse {
    0% { transform: translateX(-120%); }
    100% { transform: translateX(350%); }
}
@keyframes qBeamBreathe {
    0% { opacity: 0.55; filter: blur(12px); transform: scaleY(0.9); }
    100% { opacity: 0.95; filter: blur(20px); transform: scaleY(1.15); }
}

/* Title & Description */
.qwythlit-heading h2 {
    font-family: 'Outfit', 'Inter', sans-serif !important;
    font-size: 1.55rem !important;
    font-weight: 750 !important;
    color: #ffffff !important;
    margin: 0 0 0.35rem !important;
    letter-spacing: -0.02em;
}
.qwythlit-heading p {
    font-size: 0.88rem !important;
    color: var(--q-muted) !important;
    margin: 0 !important;
    line-height: 1.5;
}

/* 3 Lifecycle Stage Cards */
.qwythlit-stages {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 1.4rem 0 1.2rem;
}
.qwythlit-stage {
    background: rgba(18, 22, 54, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 0.85rem 0.95rem;
    display: flex;
    flex-direction: column;
    gap: 3px;
    transition: all 0.3s ease;
}
.qwythlit-stage strong {
    font-size: 0.86rem;
    color: #f7f7ff;
    letter-spacing: 0.02em;
}
.qwythlit-stage small {
    font-size: 0.72rem;
    color: var(--q-muted);
}
.qwythlit-stage.is-active {
    background: rgba(24, 30, 75, 0.95);
    border-color: var(--q-cyan);
    box-shadow: 0 0 20px rgba(0, 244, 210, 0.25);
}
.qwythlit-stage.is-active strong {
    color: var(--q-cyan);
}
.qwythlit-stage.is-complete {
    background: rgba(22, 27, 68, 0.85);
    border-color: rgba(122, 92, 255, 0.5);
    box-shadow: 0 0 15px rgba(122, 92, 255, 0.15);
}
.qwythlit-stage.is-complete strong {
    color: #9d87ff;
}

/* Response Container */
.qwythlit-response {
    background: rgba(14, 18, 46, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 1.15rem 1.3rem;
    color: #e3e6f5;
    font-size: 0.92rem;
    line-height: 1.6;
    margin-top: 1rem;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.3);
}
.qwythlit-response-query {
    color: var(--q-cyan);
    font-weight: 600;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.qwythlit-response-bullets {
    margin: 0.4rem 0 0.4rem 1.2rem;
    padding: 0;
}
.qwythlit-response-bullets li {
    margin-bottom: 0.4rem;
    color: #e2e8f5;
}

/* Source Chips */
.qwythlit-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 0.8rem;
}
.qwythlit-chip {
    font-size: 0.74rem;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(122, 92, 255, 0.18);
    border: 1px solid rgba(122, 92, 255, 0.38);
    color: #c9c1ff;
    white-space: nowrap;
}

/* Chat Input Styling */
div[data-testid="stChatInput"] {
    background: rgba(14, 18, 44, 0.92) !important;
    border: 1px solid rgba(255, 255, 255, 0.16) !important;
    border-radius: 999px !important;
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.55) !important;
    backdrop-filter: blur(20px) !important;
    padding: 2px !important;
}
div[data-testid="stChatInput"]:focus-within {
    border-color: rgba(0, 244, 210, 0.6) !important;
    box-shadow: 0 0 30px rgba(0, 244, 210, 0.25) !important;
}
div[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    background: transparent !important;
    caret-color: var(--q-cyan) !important;
    font-size: 0.95rem !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
    color: var(--q-faint) !important;
}
button[data-testid="stChatInputSubmitButton"] {
    border-radius: 50% !important;
    background: linear-gradient(135deg, #ff5e36, #ffbe0b 35%, #00f4d2 70%, #7a5cff) !important;
    border: 0 !important;
    box-shadow: 0 0 18px rgba(0, 244, 210, 0.45) !important;
    transition: transform 0.2s ease, filter 0.2s ease !important;
}
button[data-testid="stChatInputSubmitButton"]:hover {
    transform: scale(1.08) !important;
    filter: brightness(1.18) !important;
}
button[data-testid="stChatInputSubmitButton"] svg {
    fill: #060814 !important;
    color: #060814 !important;
}

/* Floating 'Q' Launcher Widget Button */
.q-launcher-wrap {
    position: fixed;
    bottom: 26px;
    right: 26px;
    z-index: 99999;
}
.q-launcher-btn {
    width: 54px;
    height: 54px;
    border-radius: 17px;
    background: #090c22;
    border: 2px solid transparent;
    background-image: linear-gradient(#090c22, #090c22), conic-gradient(from 180deg, #ff5e36, #ffbe0b, #00f4d2, #3a86ff, #a855f7, #ff5e36);
    background-origin: border-box;
    background-clip: content-box, border-box;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 28px rgba(122, 92, 255, 0.45), 0 8px 24px rgba(0,0,0,0.6);
    color: #ffffff;
    font-family: 'Outfit', sans-serif;
    font-size: 1.35rem;
    font-weight: 850;
    cursor: pointer;
    text-decoration: none;
    transition: transform 0.22s ease, box-shadow 0.22s ease;
}
.q-launcher-btn:hover {
    transform: scale(1.08) translateY(-2px);
    box-shadow: 0 0 40px rgba(122, 92, 255, 0.75), 0 12px 30px rgba(0,0,0,0.7);
}

/* Native chat message cards in lane */
div[data-testid="stChatMessage"] {
    background: rgba(14, 18, 46, 0.78) !important;
    border: 1px solid rgba(255, 255, 255, 0.09) !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35) !important;
    margin-bottom: 0.8rem !important;
}
div[data-testid="stChatMessage"] * {
    color: #e3e6f5 !important;
}

/* Main content padding */
section[data-testid="stMain"] .block-container,
div[data-testid="stMainBlockContainer"] {
    padding-bottom: 130px !important;
    max-width: 900px !important;
}

div[data-testid="stBottom"] {
    background: transparent !important;
    border-top: 0 !important;
}
div[data-testid="stBottom"] > div {
    background: transparent !important;
}
</style>
"""

# Pre-computed 22 chromatic particles with varied positions, sizes, and animations
_PARTICLES = [
    {"top": 28, "left": 40, "size": 6, "color": "#00f4d2", "dx": "14px", "dy": "-18px", "dur": "3.2s", "delay": "0s", "op": 0.5},
    {"top": 35, "left": 55, "size": 4, "color": "#ffbe0b", "dx": "-12px", "dy": "-15px", "dur": "2.8s", "delay": "-0.5s", "op": 0.45},
    {"top": 24, "left": 70, "size": 8, "color": "#7a5cff", "dx": "10px", "dy": "14px", "dur": "4.1s", "delay": "-1.2s", "op": 0.6},
    {"top": 42, "left": 25, "size": 5, "color": "#d946ef", "dx": "-10px", "dy": "-12px", "dur": "3.5s", "delay": "-0.8s", "op": 0.4},
    {"top": 68, "left": 35, "size": 7, "color": "#ff5e36", "dx": "12px", "dy": "-14px", "dur": "3.0s", "delay": "-1.5s", "op": 0.55},
    {"top": 72, "left": 65, "size": 4, "color": "#00f4d2", "dx": "-15px", "dy": "10px", "dur": "3.8s", "delay": "-0.3s", "op": 0.45},
    {"top": 30, "left": 80, "size": 5, "color": "#ffbe0b", "dx": "8px", "dy": "-16px", "dur": "2.9s", "delay": "-1.9s", "op": 0.5},
    {"top": 62, "left": 82, "size": 6, "color": "#3a86ff", "dx": "-14px", "dy": "-10px", "dur": "3.6s", "delay": "-0.7s", "op": 0.4},
    {"top": 20, "left": 48, "size": 3, "color": "#ffffff", "dx": "6px", "dy": "12px", "dur": "2.5s", "delay": "-1.1s", "op": 0.65},
    {"top": 75, "left": 50, "size": 5, "color": "#d946ef", "dx": "15px", "dy": "8px", "dur": "4.0s", "delay": "-2.1s", "op": 0.45},
    {"top": 48, "left": 18, "size": 4, "color": "#ffbe0b", "dx": "-8px", "dy": "15px", "dur": "3.3s", "delay": "-1.4s", "op": 0.4},
    {"top": 58, "left": 75, "size": 6, "color": "#00f4d2", "dx": "10px", "dy": "-12px", "dur": "3.1s", "delay": "-0.9s", "op": 0.5},
    {"top": 32, "left": 30, "size": 7, "color": "#7a5cff", "dx": "-12px", "dy": "14px", "dur": "3.7s", "delay": "-1.7s", "op": 0.5},
    {"top": 65, "left": 22, "size": 3, "color": "#ffffff", "dx": "8px", "dy": "-10px", "dur": "2.7s", "delay": "-0.4s", "op": 0.6},
    {"top": 26, "left": 62, "size": 5, "color": "#ff5e36", "dx": "-14px", "dy": "-8px", "dur": "3.4s", "delay": "-2.0s", "op": 0.45},
    {"top": 78, "left": 72, "size": 6, "color": "#ffbe0b", "dx": "12px", "dy": "10px", "dur": "3.9s", "delay": "-1.3s", "op": 0.5},
    {"top": 45, "left": 86, "size": 4, "color": "#00f4d2", "dx": "-10px", "dy": "12px", "dur": "3.0s", "delay": "-0.6s", "op": 0.4},
]


def render_qwythlit_header_card(
    *,
    status: str = "READY",
    status_active: bool = False,
    stage_idx: int = 0,
    latest_query: str = "",
    latest_answer: list[str] | None = None,
    latest_chips: str = "",
    augmentation: str | None = None,
) -> str:
    """Generate the HTML markup for the cinematic Qwythlit animated pane."""
    particles_html = "".join(
        f'<div class="q-particle" style="'
        f'top:{p["top"]}%;left:{p["left"]}%;width:{p["size"]}px;height:{p["size"]}px;'
        f'background:{p["color"]};box-shadow:0 0 {p["size"]*2.5}px {p["color"]};'
        f'--dx:{p["dx"]};--dy:{p["dy"]};--duration:{p["dur"]};--delay:{p["delay"]};--base-op:{p["op"]};'
        f'"></div>'
        for p in _PARTICLES
    )

    dragon_bg_html = ""
    if _DRAGON_B64:
        dragon_bg_html = f'<div class="qwythlit-dragon-bg" style="background-image:url(data:image/jpeg;base64,{_DRAGON_B64});"></div>'

    s1_class = "is-complete" if stage_idx > 1 else ("is-active" if stage_idx == 1 else "")
    s2_class = "is-complete" if stage_idx > 2 else ("is-active" if stage_idx == 2 else "")
    s3_class = "is-complete" if stage_idx >= 3 else ("is-active" if stage_idx == 3 else "")

    status_dot_color = "var(--q-cyan)" if not status_active else "var(--q-amber)"
    status_text = status.upper()

    response_content = ""
    if latest_answer or latest_query:
        query_line = f'<div class="qwythlit-response-query">🔍 {html.escape(latest_query)}</div>' if latest_query else ""
        chips_line = latest_chips if latest_chips else ""
        bullets = ""
        if latest_answer:
            bullets = '<ul class="qwythlit-response-bullets">' + "".join(
                f"<li>{html.escape(s.split(' [Source:')[0].strip())}</li>"
                for s in latest_answer if s.strip()
            ) + "</ul>"
        aug_line = f'<div style="margin-top:0.6rem;padding-top:0.6rem;border-top:1px solid rgba(255,255,255,0.08);color:#d1d5f0;"><em>{html.escape(augmentation)}</em></div>' if augmentation else ""
        response_content = f"""
        <div class="qwythlit-response">
            {query_line}
            {chips_line}
            {bullets}
            {aug_line}
        </div>
        """
    else:
        response_content = """
        <div class="qwythlit-response" style="color:#7b84a6;text-align:center;padding:1.4rem 1rem;">
            Ready to query the knowledge layer. Type any question about beamlines, instrumentation, or contacts below.
        </div>
        """

    return f"""
    <div class="qwythlit-shell">
        <div class="qwythlit-hero">
            <h1>Knowledge, retrieved with a pulse.</h1>
            <p>A cinematic micro-stub for Qwythlit: chromatic familiar, retrieval state, and a compact launcher mounted over the existing app shell.</p>
        </div>

        <div class="qwythlit-card">
            <div class="qwythlit-topbar">
                <div class="qwythlit-brand">
                    <span class="qwythlit-mark-badge"></span>
                    <span class="qwythlit-brand-title">Q W Y T H L I T</span>
                </div>
                <div class="qwythlit-status">
                    <span class="qwythlit-status-dot" style="background:{status_dot_color};box-shadow:0 0 10px {status_dot_color};"></span>
                    <span class="qwythlit-status-text" style="color:{status_dot_color};">{status_text}</span>
                </div>
            </div>

            <div class="qwythlit-visual">
                <div class="qwythlit-halo"></div>
                {dragon_bg_html}
                {particles_html}
                <div class="qwythlit-beam-wrap">
                    <div class="qwythlit-beam-glow"></div>
                    <div class="qwythlit-beam-core">
                        <div class="qwythlit-beam-pulse"></div>
                    </div>
                </div>
            </div>

            <div class="qwythlit-heading">
                <h2>Ask the knowledge layer.</h2>
                <p>Stubbed retrieval lifecycle. Wire the events below into the real RAG/CAG pipeline.</p>
            </div>

            <div class="qwythlit-stages">
                <div class="qwythlit-stage {s1_class}">
                    <strong>01 · Parse</strong>
                    <small>intent + context</small>
                </div>
                <div class="qwythlit-stage {s2_class}">
                    <strong>02 · Retrieve</strong>
                    <small>graph + chunks</small>
                </div>
                <div class="qwythlit-stage {s3_class}">
                    <strong>03 · Weave</strong>
                    <small>grounded answer</small>
                </div>
            </div>

            {response_content}
        </div>
    </div>
    """
