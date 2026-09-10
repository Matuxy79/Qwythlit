"""Backward-compatibility shim for cls_config -> jls_config."""

from jls_config import *  # noqa: F401, F403
import jls_config as _jls

# Re-export module globals
__all__ = [name for name in dir(_jls) if not name.startswith("__")]
