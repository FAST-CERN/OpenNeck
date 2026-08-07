"""Select a servo backend from configuration."""

from __future__ import annotations

from .._config import Config
from .protocol import ServoBackend


def make_backend(
    config: Config,
    *,
    enable_torque_on_connect: bool = True,
) -> ServoBackend:
    """Build the servo backend for ``config``.

    Phase 1 returns the Feetech backend unconditionally; later phases branch on
    ``config.servo_backend``.
    """
    from .feetech import FeetechBackend

    return FeetechBackend(
        config, enable_torque_on_connect=enable_torque_on_connect
    )
