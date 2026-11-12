"""Tests for the Qwythlit Ask Lane pane module."""

from __future__ import annotations

import unittest
from pathlib import Path

from qwythlit_pane import (
    KEY_STATUS,
    LANE_STAGES,
    LANE_SUGGESTIONS,
    QWYTHLIT_PANE_CSS,
    QWYTHLIT_POSTER_URL,
    QWYTHLIT_VIDEO_URL,
    composer_rail_html,
    composer_status_html,
    render_lane_heading,
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

    def test_css_defines_single_column_lane_and_composer(self):
        self.assertIn("--q-bg", QWYTHLIT_PANE_CSS)
        self.assertIn("max-width: 600px", QWYTHLIT_PANE_CSS)
        self.assertIn(".st-key-lane_suggest", QWYTHLIT_PANE_CSS)
        self.assertIn('div[data-testid="stForm"]:has(.q-rail)', QWYTHLIT_PANE_CSS)
        self.assertIn(".q-seg.is-lit", QWYTHLIT_PANE_CSS)
        self.assertIn(".st-key-lane_clear_chat", QWYTHLIT_PANE_CSS)
        self.assertIn("stPageLink-NavLink", QWYTHLIT_PANE_CSS)

    def test_heading_has_no_placeholder_copy(self):
        heading = render_lane_heading()
        self.assertIn("Ask the knowledge layer", heading)
        for leftover in ("Ready to query", "beamline", "instrumentation", "Stubbed", "Wire the events"):
            self.assertNotIn(leftover, heading)

    def test_three_suggested_prompts(self):
        self.assertEqual(len(LANE_SUGGESTIONS), 3)
        self.assertEqual(len(set(LANE_SUGGESTIONS)), 3)

    def test_rail_has_one_segment_per_stage_and_lights_progressively(self):
        self.assertEqual(LANE_STAGES, ("Parse", "Retrieve", "Weave"))
        for active, lit in ((0, 0), (1, 1), (2, 2), (3, 3)):
            html = composer_rail_html(active)
            self.assertEqual(html.count('class="q-seg'), len(LANE_STAGES))
            self.assertEqual(html.count("is-lit"), lit)

    def test_rail_labels_the_current_stage(self):
        self.assertIn("Pipeline idle", composer_rail_html(0))
        self.assertIn("Pipeline: Parse", composer_rail_html(1))
        self.assertIn("Pipeline: Retrieve", composer_rail_html(2))
        self.assertIn("Pipeline: Weave", composer_rail_html(3))

    def test_rail_clamps_out_of_range_stages(self):
        self.assertEqual(composer_rail_html(9).count("is-lit"), len(LANE_STAGES))
        self.assertEqual(composer_rail_html(-1).count("is-lit"), 0)

    def test_status_row_shows_one_key_signal(self):
        html = composer_status_html("Ready", "missing")
        self.assertIn("Ready", html)
        self.assertIn("Key missing", html)
        self.assertIn("is-warn", html)
        for state, (label, _tone) in KEY_STATUS.items():
            self.assertIn(label, composer_status_html("Ready", state))

    def test_status_text_is_escaped(self):
        html = composer_status_html("<script>x</script>", "set")
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_markup_is_one_line_so_markdown_does_not_treat_it_as_code(self):
        for html in (
            render_lane_heading(),
            composer_rail_html(2),
            composer_status_html("Parsing…", "verified"),
        ):
            self.assertNotIn("\n", html)


if __name__ == "__main__":
    unittest.main()
