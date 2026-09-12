"""Tests for Qwythlit animated pane module."""

from __future__ import annotations

import unittest
from pathlib import Path

from qwythlit_pane import (
    _DRAGON_B64,
    _PARTICLES,
    QWYTHLIT_POSTER_URL,
    QWYTHLIT_PANE_CSS,
    QWYTHLIT_VIDEO_URL,
    render_qwythlit_header_card,
    render_qwythlit_media_background,
)


class TestQwythlitPane(unittest.TestCase):
    def test_media_assets_exist(self):
        static_dir = Path(__file__).resolve().parents[1] / "static"
        self.assertGreater((static_dir / "qwyth.png").stat().st_size, 1_000_000)
        self.assertGreater((static_dir / "qwythlit-intro.mp4").stat().st_size, 1_000_000)

    def test_render_media_background(self):
        markup = render_qwythlit_media_background("ask_lane")
        self.assertIn(f'poster="{QWYTHLIT_POSTER_URL}"', markup)
        self.assertIn(f'src="{QWYTHLIT_VIDEO_URL}"', markup)
        self.assertIn('data-context="ask_lane"', markup)
        self.assertIn("autoplay muted loop playsinline", markup)
        self.assertIn("prefers-reduced-motion: reduce", markup)
        with self.assertRaises(ValueError):
            render_qwythlit_media_background("unsupported")

    def test_css_tokens(self):
        self.assertIn("--q-bg", QWYTHLIT_PANE_CSS)
        self.assertIn("qwythlit-card", QWYTHLIT_PANE_CSS)
        self.assertIn("qwythlit-beam-pulse", QWYTHLIT_PANE_CSS)
        self.assertIn("q-launcher-btn", QWYTHLIT_PANE_CSS)

    def test_particles_defined(self):
        self.assertGreaterEqual(len(_PARTICLES), 10)
        for p in _PARTICLES:
            self.assertIn("top", p)
            self.assertIn("left", p)
            self.assertIn("color", p)

    def test_dragon_asset_loaded(self):
        self.assertTrue(len(_DRAGON_B64) > 1000, "Dragon image base64 should be populated")

    def test_render_empty_card(self):
        html = render_qwythlit_header_card(status="READY", status_active=False, stage_idx=0)
        self.assertNotIn("\n", html)
        self.assertEqual(html.count('class="qwythlit-dragon-bg'), 2)
        self.assertIn("is-left", html)
        self.assertIn("is-right", html)
        self.assertIn("Q W Y T H L I T", html)
        self.assertIn("READY", html)
        self.assertIn("01 · Parse", html)
        self.assertIn("02 · Retrieve", html)
        self.assertIn("03 · Weave", html)
        self.assertIn("qwythlit-beam-pulse", html)

    def test_render_answered_card(self):
        html = render_qwythlit_header_card(
            status="READY",
            status_active=False,
            stage_idx=3,
            latest_query="What is the beam energy?",
            latest_answer=["The beam energy is 2.9 GeV [Source: spec.pdf]."],
            latest_chips='<div class="qwythlit-chips"><span class="qwythlit-chip">spec</span></div>',
            augmentation="AI summary: storage ring operates at 2.9 GeV.",
        )
        self.assertIn("What is the beam energy?", html)
        self.assertIn("The beam energy is 2.9 GeV", html)
        self.assertIn("spec", html)
        self.assertIn("AI summary: storage ring operates at 2.9 GeV.", html)
        self.assertIn("is-complete", html)


if __name__ == "__main__":
    unittest.main()
