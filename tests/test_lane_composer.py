"""Ask Lane composer support: the one key status, model choices and the sidebar key panel."""

from __future__ import annotations

import unittest
from unittest.mock import patch

import openrouter_client as client
from provider_settings import _fingerprint, key_status


class KeyStatusTests(unittest.TestCase):
    def test_each_state(self):
        self.assertEqual(key_status({}, {}), "missing")
        self.assertEqual(key_status({"api_key": "   "}, {}), "missing")
        self.assertEqual(key_status({"api_key": "k", "enabled": False}, {}), "off")
        self.assertEqual(key_status({"api_key": "k", "enabled": True}, {}), "set")
        self.assertEqual(
            key_status({"api_key": "k", "enabled": True}, {"fingerprint": _fingerprint("k"), "ok": True}),
            "verified",
        )
        self.assertEqual(
            key_status({"api_key": "k", "enabled": True}, {"fingerprint": _fingerprint("k"), "ok": False, "error": "no"}),
            "failed",
        )

    def test_test_result_for_another_key_is_ignored(self):
        self.assertEqual(
            key_status({"api_key": "k", "enabled": True}, {"fingerprint": _fingerprint("other"), "ok": True}),
            "set",
        )


class KeyPanelTests(unittest.TestCase):
    def test_sidebar_panel_carries_no_status_of_its_own(self):
        from streamlit.testing.v1 import AppTest

        with patch.object(client, "model_catalog", return_value=[]):
            app = AppTest.from_string(
                "from provider_settings import render_key_panel\nrender_key_panel()"
            ).run()
            self.assertFalse(app.exception)
            text = " ".join(m.value for m in app.markdown)
            captions = " ".join(c.value for c in app.caption)
            self.assertNotIn("Not connected", text)
            self.assertNotIn("Connected", text)
            self.assertNotIn("Untested", captions)
            self.assertNotIn("Key verified", captions)
            self.assertEqual(app.text_input[0].value, "")
            self.assertTrue(app.checkbox[0].value)

    def test_panel_leads_with_the_brand_header(self):
        from streamlit.testing.v1 import AppTest

        with patch.object(client, "model_catalog", return_value=[]):
            app = AppTest.from_string(
                "from provider_settings import render_key_panel\nrender_key_panel()"
            ).run()
            self.assertFalse(app.exception)
            self.assertIn("Qwythlit", " ".join(m.value for m in app.markdown))

    def test_save_stores_key_and_generation_switch(self):
        from streamlit.testing.v1 import AppTest

        with patch.object(client, "model_catalog", return_value=[]):
            app = AppTest.from_string(
                "from provider_settings import render_key_panel\nrender_key_panel()"
            ).run()
            app.text_input[0].set_value("session-key").run()
            next(b for b in app.button if b.label == "Save").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["openrouter_settings"]["api_key"], "session-key")
            self.assertTrue(app.session_state["openrouter_settings"]["enabled"])
            app.checkbox[0].uncheck().run()
            next(b for b in app.button if b.label == "Save").click().run()
            self.assertFalse(app.session_state["openrouter_settings"]["enabled"])

    def test_save_refuses_generation_without_key(self):
        from streamlit.testing.v1 import AppTest

        with patch.object(client, "model_catalog", return_value=[]):
            app = AppTest.from_string(
                "import streamlit as st\n"
                "st.session_state['openrouter_settings'] = {'api_key': 'k', 'model': 'openrouter/auto', 'enabled': True}\n"
                "from provider_settings import render_key_panel\n"
                "render_key_panel()\n"
            ).run()
            app.text_input[0].set_value("").run()
            next(b for b in app.button if b.label == "Save").click().run()
            self.assertFalse(app.exception)
            self.assertIn("Enter an API key", " ".join(e.value for e in app.error))
            self.assertEqual(app.session_state["openrouter_settings"]["api_key"], "k")


class ModelChoiceTests(unittest.TestCase):
    def test_auto_first_then_catalog_then_current_custom_model(self):
        from streamlit.testing.v1 import AppTest

        catalog = [{"id": "meta/llama", "name": "Llama", "context_length": 8192}]
        with patch.object(client, "model_catalog", return_value=catalog):
            app = AppTest.from_string(
                "import streamlit as st\n"
                "from provider_settings import model_options, model_chip_label\n"
                "opts = model_options('custom/x')\n"
                "st.session_state['opts'] = opts\n"
                "st.session_state['labels'] = [model_chip_label(o) for o in opts]\n"
            ).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["opts"], ["openrouter/auto", "meta/llama", "custom/x"])
            self.assertEqual(app.session_state["labels"], ["Auto", "Llama", "custom/x"])

    def test_remember_model_keeps_key_and_switch(self):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_string(
            "import streamlit as st\n"
            "from provider_settings import remember_model\n"
            "st.session_state['openrouter_settings'] = {'api_key': 'k', 'model': 'a/b', 'enabled': False}\n"
            "remember_model('c/d')\n"
        ).run()
        self.assertFalse(app.exception)
        self.assertEqual(
            app.session_state["openrouter_settings"],
            {"api_key": "k", "model": "c/d", "enabled": False},
        )


if __name__ == "__main__":
    unittest.main()
