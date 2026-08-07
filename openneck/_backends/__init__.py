"""Servo backend abstraction for OpenNeck.

Backends speak one servo family's register-level protocol. The controller and
CLI use the ``ServoBackend`` protocol and :func:`make_backend`; they never
import a specific SDK.
"""

from __future__ import annotations

from .factory import make_backend
from .protocol import ServoBackend

__all__ = ["ServoBackend", "make_backend"]
