"""Backward-compatibility shim for cls_backend -> jls_backend."""

from jls_backend import *  # noqa: F401, F403
import jls_backend as _jls_backend

__all__ = [name for name in dir(_jls_backend) if not name.startswith("__")]
