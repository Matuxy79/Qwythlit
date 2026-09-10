"""Compatibility shim / alias for test_jls_dllm."""

from tests.test_jls_dllm import *  # noqa: F401, F403
import unittest

if __name__ == "__main__":
    unittest.main()
