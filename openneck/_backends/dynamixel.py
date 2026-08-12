"""Dynamixel servo backend (dynamixel_easy_sdk)."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any

from .._config import Config, SERVO_MAX_STEP, SERVO_MIN_STEP
from ._port import find_servo_port


@contextmanager
def _translate(action: str):
    """Convert easy_sdk errors to RuntimeError (the ServoBackend contract).

    ``dynamixel_easy_sdk`` raises ``DxlRuntimeError`` (a plain ``Exception``
    subclass, not ``RuntimeError``); the backend contract requires
    ``RuntimeError`` so callers catch one family.
    """
    try:
        yield
    except Exception as exc:
        raise RuntimeError(f"{action}: {exc}") from exc


class DynamixelBackend:
    """Register-level Dynamixel access via the high-level easy SDK."""

    def __init__(
        self, config: Config, *, enable_torque_on_connect: bool = True
    ) -> None:
        self.config = config
        self.ids: tuple[int, ...] = (config.yaw_id, config.pitch_id)
        self.enable_torque_on_connect = enable_torque_on_connect
        self.port_name: str | None = config.port
        self._connector: Any = None
        self._motors: dict[int, Any] = {}
        self._position_limits: dict[int, tuple[int, int]] = {}
        self._connected = False

    def __enter__(self) -> "DynamixelBackend":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def connect(self) -> None:
        from dynamixel_easy_sdk import Connector, OperatingMode

        if self._connected:
            return
        self.port_name = self.config.port or find_servo_port()
        with _translate(f"open port {self.port_name}"):
            self._connector = Connector(self.port_name, self.config.baudrate)
        try:
            for servo_id in self.ids:
                with _translate(f"ping servo {servo_id}"):
                    self._motors[servo_id] = self._connector.createMotor(
                        servo_id
                    )
            for servo_id in self.ids:
                motor = self._motors[servo_id]
                with _translate(f"read position limits servo {servo_id}"):
                    lo = int(motor.getMinPositionLimit())
                    hi = int(motor.getMaxPositionLimit())
                self._position_limits[servo_id] = (lo, hi)
            mode = OperatingMode(self.config.operating_mode)
            for servo_id in self.ids:
                motor = self._motors[servo_id]
                axis = "yaw" if servo_id == self.config.yaw_id else "pitch"
                with _translate(f"configure servo {servo_id}"):
                    motor.disableTorque()
                    motor.setOperatingMode(mode)
                    self._write_profile(motor, servo_id)
                    self._write_pid(motor, servo_id, axis)
            if self.enable_torque_on_connect:
                for servo_id in self.ids:
                    with _translate(f"enable torque servo {servo_id}"):
                        self._motors[servo_id].enableTorque()
        except BaseException:
            try:
                self.close()
            except Exception:
                pass
            raise
        self._connected = True

    def _write_profile(self, motor: Any, servo_id: int) -> None:
        """Apply Config profile_velocity / profile_acceleration to RAM.

        Profile Velocity/Acceleration are RAM registers writable while torque
        is off (written inside the configure step, before torque enable). A
        config value of 0 means "leave the servo's current value untouched".
        """
        if self.config.profile_velocity:
            item = motor._getControlTableItem("Profile Velocity")
            motor._writeData(
                servo_id, item.address, item.size, self.config.profile_velocity
            )
        if self.config.profile_acceleration:
            item = motor._getControlTableItem("Profile Acceleration")
            motor._writeData(
                servo_id, item.address, item.size, self.config.profile_acceleration
            )

    def _write_pid(self, motor: Any, servo_id: int, axis: str) -> None:
        """Apply per-axis Position P/I/D Gain to RAM (torque off).

        A config value of 0 leaves the gain untouched.
        """
        for suffix, gain in (
            ("_kp", "Position P Gain"),
            ("_ki", "Position I Gain"),
            ("_kd", "Position D Gain"),
        ):
            value = getattr(self.config, f"{axis}{suffix}")
            if value:
                item = motor._getControlTableItem(gain)
                motor._writeData(servo_id, item.address, item.size, value)

    def close(self) -> None:
        connector = self._connector
        self._connected = False
        self._motors = {}
        self._position_limits = {}
        self._connector = None
        if connector is not None:
            with _translate("close port"):
                connector.closePort()

    def ping(self, servo_id: int) -> int:
        self._ensure_connected()
        with _translate(f"ping servo {servo_id}"):
            return int(self._connector.ping(servo_id))

    def enable_torque(self, servo_id: int) -> None:
        self._ensure_connected()
        with _translate(f"enable torque servo {servo_id}"):
            self._motors[servo_id].enableTorque()

    def release_torque(self) -> None:
        self._ensure_connected()
        for servo_id in self.ids:
            with _translate(f"disable torque servo {servo_id}"):
                self._motors[servo_id].disableTorque()

    def read_positions(self) -> dict[int, int]:
        self._ensure_connected()
        return {servo_id: self.read_position(servo_id) for servo_id in self.ids}

    def read_position(self, servo_id: int) -> int:
        self._ensure_connected()
        with _translate(f"read servo {servo_id}"):
            position = int(self._motors[servo_id].getPresentPosition())
        if position < SERVO_MIN_STEP or position > SERVO_MAX_STEP:
            raise RuntimeError(f"read servo {servo_id}: invalid position {position}")
        return position

    def write_positions(self, targets: dict[int, int]) -> None:
        from dynamixel_easy_sdk import GroupExecutor

        self._ensure_connected()
        normalized: dict[int, int] = {}
        for servo_id, position in targets.items():
            position = int(position)
            if position < SERVO_MIN_STEP or position > SERVO_MAX_STEP:
                raise ValueError(
                    f"servo {servo_id} target must be in "
                    f"{SERVO_MIN_STEP}..{SERVO_MAX_STEP}, got {position}"
                )
            lo, hi = self._position_limits[int(servo_id)]
            if position < lo or position > hi:
                raise ValueError(
                    f"servo {servo_id} target {position} exceeds hardware "
                    f"position limit [{lo}, {hi}]"
                )
            normalized[int(servo_id)] = position
        with _translate("write positions"):
            group: GroupExecutor = self._connector.createGroupExecutor()
            for servo_id in self.ids:
                if servo_id in normalized:
                    group.addCmd(
                        self._motors[servo_id].stageSetGoalPosition(
                            normalized[servo_id]
                        )
                    )
            group.executeWrite()

    def read_voltage(self, servo_id: int) -> float:
        self._ensure_connected()
        motor = self._motors[servo_id]
        with _translate(f"read voltage servo {servo_id}"):
            # The SDK exposes no public getPresentInputVoltage(), so look up
            # the control-table item and read it directly.
            item = motor._getControlTableItem("Present Input Voltage")
            raw = motor._readData(servo_id, item.address, item.size)
        return float(raw) / 10.0

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("OpenNeck is not connected")
