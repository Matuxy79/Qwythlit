import os
import sys
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import Mock, patch

from cls_backend import bootstrap


class CorpusBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.env_patch = patch.dict(os.environ, {}, clear=True)
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)
        self.thread_patch = patch.object(bootstrap, "_bootstrap_thread", None)
        self.thread_patch.start()
        self.addCleanup(self.thread_patch.stop)
        self.service = SimpleNamespace(
            service_status=Mock(return_value={"indexed_chunks": 0}),
            ingest_default_corpus=Mock(return_value={"ok": True, "message": "indexed"}),
        )
        self.service_patch = patch.dict(sys.modules, {"cls_service": self.service})
        self.service_patch.start()
        self.addCleanup(self.service_patch.stop)

    def test_disabled_locally_without_opening_store(self):
        self.assertFalse(bootstrap.start_corpus_bootstrap())
        self.assertIsNone(bootstrap._bootstrap_thread)
        self.service.service_status.assert_not_called()

    def test_railway_defaults_and_explicit_overrides(self):
        for railway_var in ("RAILWAY_ENVIRONMENT", "RAILWAY_PUBLIC_DOMAIN"):
            with self.subTest(railway_var=railway_var), patch.dict(os.environ, {railway_var: "production"}):
                self.assertTrue(bootstrap.should_bootstrap_corpus())
                with patch.dict(os.environ, {"CLS_BOOTSTRAP_CORPUS": "0"}):
                    self.assertFalse(bootstrap.start_corpus_bootstrap())
        with patch.dict(os.environ, {"CLS_BOOTSTRAP_CORPUS": " TRUE "}):
            self.assertTrue(bootstrap.should_bootstrap_corpus())
        self.service.service_status.assert_not_called()

    def test_existing_store_is_preserved(self):
        self.service.service_status.return_value = {"indexed_chunks": 123}
        bootstrap._bootstrap_worker()
        self.service.ingest_default_corpus.assert_not_called()

    def test_concurrent_starts_return_without_waiting_and_ingest_only_once(self):
        os.environ["CLS_BOOTSTRAP_CORPUS"] = "1"
        entered = threading.Event()
        release = threading.Event()

        def blocking_ingest():
            entered.set()
            if not release.wait(timeout=5):
                raise TimeoutError("test did not release the bootstrap worker")
            return {"ok": True, "message": "indexed"}

        self.service.ingest_default_corpus.side_effect = blocking_ingest
        try:
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(bootstrap.start_corpus_bootstrap) for _ in range(8)]
                results = [future.result(timeout=2) for future in futures]
            self.assertEqual(results.count(True), 1)
            self.assertTrue(entered.wait(timeout=2))
            self.assertTrue(bootstrap._bootstrap_thread.daemon)
            self.assertTrue(bootstrap._bootstrap_thread.is_alive())
        finally:
            release.set()
            if bootstrap._bootstrap_thread is not None:
                bootstrap._bootstrap_thread.join(timeout=5)
        self.assertFalse(bootstrap._bootstrap_thread.is_alive())
        self.assertFalse(bootstrap.start_corpus_bootstrap())
        self.service.ingest_default_corpus.assert_called_once_with()

    def test_ingest_exception_is_logged_without_breaking_frontend(self):
        self.service.ingest_default_corpus.side_effect = RuntimeError("embedding unavailable")
        with self.assertLogs("cls.bootstrap", level="ERROR") as captured:
            bootstrap._bootstrap_worker()
        self.assertIn("application remains available", "\n".join(captured.output))
        self.assertIn("embedding unavailable", "\n".join(captured.output))

    def test_missing_corpus_is_reported(self):
        self.service.ingest_default_corpus.return_value = {
            "ok": False,
            "message": "Default documents directory not found",
        }
        with self.assertLogs("cls.bootstrap", level="WARNING") as captured:
            bootstrap._bootstrap_worker()
        self.assertIn("Default documents directory not found", "\n".join(captured.output))


if __name__ == "__main__":
    unittest.main()
