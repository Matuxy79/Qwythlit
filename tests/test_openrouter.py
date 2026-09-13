import ast
import json
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
import urllib.error

import openrouter_client as client


class OpenRouterTests(unittest.TestCase):
    def test_selected_model_and_session_key_are_sent(self):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(
            {"choices": [{"message": {"content": "Cited answer [1]"}}]}
        ).encode()
        with patch.object(client.urllib.request, "urlopen", return_value=response) as send:
            self.assertEqual(client.chat([{"role": "user", "content": "Question"}],
                                        api_key="session-key", model="provider/chosen"), "Cited answer [1]")
        request = send.call_args.args[0]
        self.assertEqual(request.full_url, client.BASE_URL + "/chat/completions")
        self.assertEqual(request.get_header("Authorization"), "Bearer session-key")
        self.assertEqual(json.loads(request.data)["model"], "provider/chosen")

    def test_catalog_filters_non_text_models(self):
        with patch.object(client, "request", return_value={"data": [
            {"id": "a/text", "architecture": {"output_modalities": ["text"]}},
            {"id": "b/image", "architecture": {"output_modalities": ["image"]}},
        ]}):
            self.assertEqual(client.model_ids(), ["a/text"])

    def test_error_does_not_echo_credentials(self):
        error = urllib.error.HTTPError("url", 401, "secret-key", {}, None)
        with patch.object(client.urllib.request, "urlopen", side_effect=error):
            with self.assertRaisesRegex(RuntimeError, "HTTP 401") as caught:
                client.request("/key", api_key="secret-key")
        self.assertNotIn("secret-key", str(caught.exception))

    def test_setup_save_disable_and_clear(self):
        from streamlit.testing.v1 import AppTest
        source = Path("app.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        names = {"_openrouter_settings", "dllm_api_status", "render_openrouter_setup"}
        functions = [ast.get_source_segment(source, node) for node in tree.body
                     if isinstance(node, ast.FunctionDef) and node.name in names]
        app = AppTest.from_string("import streamlit as st\nimport openrouter_client\n" +
                                  "\n\n".join(functions) + "\nrender_openrouter_setup()")
        app.run()
        app.text_input[0].set_value("session-key")
        app.run()
        next(button for button in app.button if button.label == "Save").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["openrouter_settings"]["api_key"], "session-key")
        app.checkbox[0].uncheck()
        app.run()
        next(button for button in app.button if button.label == "Save").click().run()
        self.assertFalse(app.session_state["openrouter_settings"]["enabled"])
        next(button for button in app.button if button.label == "Clear API key").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.text_input[0].value, "")
        self.assertNotIn("openrouter_settings", app.session_state)

    def test_drafts_reset_and_key_test_identity(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_string("from provider_settings import render_provider_settings\nrender_provider_settings({'All': None, 'Maths': {}})").run()
        app.text_input[0].set_value("test-key").run()
        self.assertNotIn("openrouter_settings", app.session_state)
        with patch.object(client, "request", return_value={"data": {}}):
            next(b for b in app.button if b.label == "Test").click().run()
        self.assertTrue(app.session_state["provider_test"]["ok"])
        next(b for b in app.button if b.label == "Save").click().run()
        app.text_input[0].set_value("different-key").run()
        self.assertIn("Not connected", " ".join(m.value for m in app.markdown))
        next(b for b in app.button if b.label == "Reset").click().run()
        self.assertEqual(app.text_input[0].value, "test-key")
        self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
