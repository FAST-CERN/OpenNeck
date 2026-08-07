"""Backend contract for register-level servo access."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ServoBackend(Protocol):
    """Register-level servo access shared by every backend.

    Positions are raw integer servo steps in ``SERVO_MIN_STEP..SERVO_MAX_STEP``
    (0..4095). Angle/step conversion and clamping live in ``openneck._angles``;
    backends only move and read raw steps.
    """

    ids: tuple[int, ...]

    def connect(self) -> None: ...
    def close(self) -> None: ...
    def read_positions(self) -> dict[int, int]: ...
    def read_position(self, servo_id: int) -> int: ...
    def write_positions(self, targets: dict[int, int]) -> None: ...
    def read_voltage(self, servo_id: int) -> float: ...
    def release_torque(self) -> None: ...
