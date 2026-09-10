"""Backward-compatibility shim for cls_service -> jls_service."""

from jls_service import *  # noqa: F401, F403
import jls_service as _jls_service

__all__ = [name for name in dir(_jls_service) if not name.startswith("__")]
