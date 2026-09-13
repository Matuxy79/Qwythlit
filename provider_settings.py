"""Compact, session-owned OpenRouter configuration surface."""
import hashlib

import streamlit as st

import openrouter_client


CSS = """
<style>
.st-key-provider_panel {
  --provider-muted: #a9b7dc;
  --panel:#171d36; --ink:#eef0ff; --line:#39365f;
  padding: 18px; border: 1px solid #263456; border-radius: 18px;
  background: linear-gradient(145deg, #10152d, #080f1b 65%);
  color: #f4f3ff; max-height: calc(100dvh - 150px); overflow-y:auto;
}
section[data-testid="stSidebar"]:has(.st-key-provider_panel) { width:360px !important; min-width:0 !important; }
section[data-testid="stSidebar"]:has(.st-key-provider_panel) [data-testid="stSidebarUserContent"] { padding:16px !important; }
.st-key-provider_panel [data-testid="stVerticalBlock"] { gap: .65rem; }
.st-key-provider_panel p, .st-key-provider_panel label { color: #eef0ff !important; }
.st-key-provider_panel [data-testid="stCaptionContainer"] p { color: #a9b7dc !important; font-size: .78rem; }
.st-key-provider_panel a { color: #a398ff !important; }
.st-key-provider_panel [data-baseweb="input"],
.st-key-provider_panel [data-baseweb="base-input"],
.st-key-provider_panel [data-baseweb="select"] > div {
  background: #10192c !important; color: #f4f3ff !important;
  border-color: #334268 !important; border-radius: 10px;
}
.st-key-provider_panel [data-testid="stTextInput"] input,
.st-key-provider_panel [data-testid="stTextInput"] [data-baseweb],
.st-key-provider_panel [data-testid="stTextInputRootElement"] { color: #f4f3ff !important; background:#10192c !important; border-color:#334268 !important; }
.st-key-provider_panel button[data-testid], .st-key-provider_panel button[data-testid]:hover {
  background: #171d36 !important; color: #eef0ff !important; border: 1px solid #39365f !important;
  border-radius: 10px; font-size: .82rem;
}
.st-key-provider_panel button[kind="primary"],
.st-key-provider_panel button[data-testid="stBaseButton-primary"],
.st-key-provider_panel button[data-testid="stBaseButton-segmented_controlActive"],
.st-key-provider_panel button[data-testid="stBaseButton-pillsActive"],
.st-key-provider_panel button[kind="segmented_controlActive"],
.st-key-provider_panel button[kind="pillsActive"],
.st-key-provider_panel button[aria-pressed="true"] {
  background: linear-gradient(115deg, #6b72fa, #593dde) !important;
  border-color: #9788ff !important; color: white !important;
}
.st-key-provider_panel button:focus-visible { outline: 2px solid #a398ff; outline-offset: 2px; }
.st-key-provider_panel button:disabled { opacity:.5; box-shadow:none !important; }
.st-key-provider_panel input::placeholder { color:#8e9cbf !important; }
.st-key-provider_panel a { color:#a398ff !important; }
.st-key-provider_panel [data-testid="stCheckbox"] label > span { background:#7558ed !important; }
@media(max-width:600px) {
  .stApp:has(.st-key-provider_panel) button[data-testid="stBaseButton-headerNoPadding"],
  .stApp:has(.st-key-provider_panel) [data-testid="stSidebarCollapsedControl"] { display:flex !important; }
}
.provider-header { display:flex; align-items:center; justify-content:space-between; gap:8px; margin-bottom:10px; }
.provider-header strong { font: 600 24px Georgia, serif; color:#f4f3ff; }
.provider-pill { font: 500 11px system-ui; padding:6px 9px; border:1px solid #423148; border-radius:99px; color:#f5a8bd; white-space:nowrap; }
.provider-pill.connected { color:#38dfa0; border-color:#225345; background:#0e2825; }
.provider-label { font:600 11px system-ui; letter-spacing:.12em; color:#a9b7dc; margin:10px 0 3px; }
.st-key-provider_panel hr { margin: .4rem 0; border-color:#263456; }
.st-key-provider_panel [data-testid="stExpander"] details { background:#10192c !important; border-color:#334268; }
.st-key-provider_actions { position:sticky; bottom:-18px; background:#0c1324; padding:12px 0 18px; border-top:1px solid #263456; z-index:2; }
@media(max-width:600px) { .st-key-provider_panel { padding:12px; } }
</style>
"""


def render_provider_settings(scopes=None):
    state = st.session_state
    saved = state.get("openrouter_settings", {})
    defaults = {"api_key": "", "model": "openrouter/auto", "enabled": True}
    baseline = {**defaults, **saved}
    state.setdefault("provider_key", baseline["api_key"])
    state.setdefault("provider_mode", "Auto" if baseline["model"] == "openrouter/auto" else "Custom")
    state.setdefault("provider_custom", "" if baseline["model"] == "openrouter/auto" else baseline["model"])
    state.setdefault("provider_enabled", baseline["enabled"])
    state.setdefault("provider_scopes", list(state.get("lane_scopes", [])))
    # Keep drafts when a rerun occurs before a widget or while its section is hidden.
    for name in ("provider_mode", "provider_custom", "provider_enabled", "provider_scopes"):
        state[name] = state[name]

    def reset():
        for key in ("provider_key", "provider_mode", "provider_custom", "provider_enabled", "provider_scopes"):
            state.pop(key, None)

    def clear_key():
        state.pop("openrouter_settings", None)
        state.pop("provider_test", None)
        state.pop("last_synth", None)
        state.pop("last_dllm", None)
        reset()

    def fingerprint(key):
        return hashlib.sha256(key.encode()).hexdigest()

    st.markdown(CSS, unsafe_allow_html=True)
    with st.container(key="provider_panel"):
        key = state.provider_key.strip()
        tested = state.get("provider_test", {})
        verified = bool(key and tested.get("fingerprint") == fingerprint(key) and tested.get("ok"))
        pill = "connected" if verified else ""
        status = "Connected" if verified else "Not connected"
        st.markdown(f'<div class="provider-header"><strong>Qwythlit</strong><span class="provider-pill {pill}">● {status}</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="provider-label">PROVIDER KEY</div>', unsafe_allow_html=True)
        api_key = st.text_input("OpenRouter API key", type="password", key="provider_key", placeholder="sk-or-v1-…", label_visibility="collapsed")
        st.caption("Kept only in this Streamlit session.")
        left, right = st.columns([1, 2])
        if left.button("Test", disabled=not api_key.strip(), use_container_width=True):
            try:
                openrouter_client.request("/key", api_key=api_key.strip())
                state.provider_test = {"fingerprint": fingerprint(api_key.strip()), "ok": True}
            except RuntimeError as exc:
                state.provider_test = {"fingerprint": fingerprint(api_key.strip()), "ok": False, "error": str(exc)}
            st.rerun()
        right.caption("Key verified" if verified else "Untested" if tested.get("fingerprint") != fingerprint(api_key.strip()) else "Test failed")
        if tested.get("fingerprint") == fingerprint(api_key.strip()) and tested.get("error"):
            st.error(tested["error"])
        st.markdown("[Create a key ↗](https://openrouter.ai/settings/keys)")
        st.divider()
        st.markdown('<div class="provider-label">MODEL</div>', unsafe_allow_html=True)
        mode = st.segmented_control("Model mode", ["Auto", "Custom"], key="provider_mode", selection_mode="single", required=True, label_visibility="collapsed")
        if mode == "Custom":
            st.text_input("Custom model ID", key="provider_custom", placeholder="provider/model")
            models = state.get("openrouter_models", [])
            if models:
                def choose_model():
                    if state.provider_catalog:
                        state.provider_custom = state.provider_catalog
                st.selectbox("Model catalog", models, index=None, key="provider_catalog", on_change=choose_model, placeholder="Search models…")
        model = "openrouter/auto" if mode == "Auto" else state.provider_custom.strip()
        st.caption(f"Resolves → {model or 'Enter a model ID'}")

        if scopes is not None:
            st.divider()
            count = len(state.provider_scopes)
            st.markdown(f'<div class="provider-label">RETRIEVAL FILTER · {count} ON</div>', unsafe_allow_html=True)
            st.pills("Retrieval disciplines", [s for s in scopes if s != "All"], selection_mode="multi", key="provider_scopes", label_visibility="collapsed")
            st.button("Clear filters", on_click=lambda: state.update(provider_scopes=[]))
            st.caption("No filters = all disciplines.")

        st.divider()
        enabled = st.checkbox("Generate via OpenRouter", key="provider_enabled")
        st.caption("Off = retrieval-only")
        with st.expander("Quick actions"):
            if st.button("Refresh models", use_container_width=True):
                try:
                    state.openrouter_models = openrouter_client.model_ids()
                    st.success(f"Loaded {len(state.openrouter_models)} models. Choose Custom to browse.")
                except RuntimeError as exc:
                    st.error(str(exc))
            st.button("Clear API key", disabled=not (api_key or saved.get("api_key")), on_click=clear_key, use_container_width=True)
            st.markdown("[View models ↗](https://openrouter.ai/models)")

        draft = {"api_key": api_key.strip(), "model": model, "enabled": enabled}
        dirty = draft != baseline or (scopes is not None and state.provider_scopes != state.get("lane_scopes", []))
        with st.container(key="provider_actions"):
            st.caption("● Unsaved changes" if dirty else "✓ Settings saved" if saved else "No configuration saved")
            left, right = st.columns(2)
            left.button("Reset", on_click=reset, disabled=not dirty, use_container_width=True)
            if right.button("Save", type="primary", disabled=not dirty, use_container_width=True):
                if enabled and (not draft["api_key"] or not model or "/" not in model or any(c.isspace() for c in model)):
                    st.error("Enter an API key and a model ID in provider/model format.")
                else:
                    state.openrouter_settings = draft
                    if scopes is not None:
                        state.lane_scopes = list(state.provider_scopes)
                    state.pop("last_synth", None)
                    state.pop("last_dllm", None)
                    st.rerun()
    return state.get("lane_scopes", [])
