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

    Selects the backend by ``config.servo_backend``: ``"feetech"`` or
    ``"dynamixel"``.
    """
    name = config.servo_backend
    if name == "feetech":
        from .feetech import FeetechBackend

        return FeetechBackend(
            config, enable_torque_on_connect=enable_torque_on_connect
        )
    if name == "dynamixel":
        from .dynamixel import DynamixelBackend

        return DynamixelBackend(
            config, enable_torque_on_connect=enable_torque_on_connect
        )
    raise ValueError(f"unknown servo_backend: {name!r}")
