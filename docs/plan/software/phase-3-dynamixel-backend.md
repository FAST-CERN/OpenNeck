# Phase 3: Dynamixel Backend — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Implement `DynamixelBackend` over the vendored `dynamixel_easy_sdk`, register it in the factory, and cover it with offline (mocked-SDK) tests.

**Architecture:** `DynamixelBackend` implements the `ServoBackend` Protocol using `Connector` + `Motor`. `connect()` pings both IDs, sets `OperatingMode` (torque off → set → re-enable), and holds `Motor` objects. `write_positions` uses `GroupExecutor` for an atomic two-axis goal write; reads use per-motor `getPresentPosition()`; voltage uses the `Present Input Voltage` control-table item. All `dynamixel_easy_sdk` errors are translated to `RuntimeError` (the SDK's `DxlRuntimeError` subclasses `Exception`, not `RuntimeError`).

**Tech Stack:** `dynamixel_easy_sdk` (`Connector`, `Motor`, `GroupExecutor`, `OperatingMode`), `unittest` + `pytest`, `sys.modules` fakes.

## Global Constraints

- Same as prior phases; in addition, `dynamixel_easy_sdk` and `dynamixel_sdk` must be importable — wiring is phase 4, so this phase's tests inject a fake `dynamixel_easy_sdk` module via `patch.dict(sys.modules, ...)` and never import the real SDK at module load (only inside method bodies).
- Do not modify `thirdparty/DynamixelSDK/`.
- Step range and angle math are unchanged: positions are 0..4095; `_angles`/`_config` are reused as-is.

## File Structure

- Create: `openneck/_backends/dynamixel.py` — `DynamixelBackend` + `_translate`.
- Modify: `openneck/_backends/factory.py` — add `"dynamixel"` branch.
- Test: `tests/test_backends/test_dynamixel_backend.py`.

**Interfaces:**
- Consumes: `Config` (`.operating_mode`, `.baudrate`, `.port`, `.yaw_id`, `.pitch_id`), `find_servo_port`.
- Produces: `DynamixelBackend(config, *, enable_torque_on_connect=True)` implementing `ServoBackend`; factory returns it for `servo_backend == "dynamixel"`.

---

### Task 1: Backend class with connect / close / torque / ping

**Files:** Create `openneck/_backends/dynamixel.py`; Test `tests/test_backends/test_dynamixel_backend.py`.

- [ ] **Step 1: Write the failing tests (connect + error translation)**

`tests/test_backends/test_dynamixel_backend.py`:

```python
from __future__ import annotations
import sys
import types
import unittest
from unittest.mock import patch

from openneck._config import Config


def make_fake_easy_sdk():
    """Minimal fake of dynamixel_easy_sdk exercising the backend paths."""
    state = {
        "port": None,
        "baudrate": None,
        "motors": {},          # id -> FakeMotor
        "fail_create": None,   # id whose createMotor raises
        "closed": False,
        "writes": [],          # list of {id: position}
        "positions": {},       # id -> present position
    }

    class OperatingMode:
        POSITION = 3
        EXTENDED_POSITION = 4

    class StagedCommand:
        def __init__(self, command_type, id_, address, length, data, *rest):
            self.command_type = command_type
            self.id = id_
            self.address = address
            self.length = length
            self.data = data

    class FakeMotor:
        def __init__(self, motor_id, connector):
            self.id = motor_id
            self.connector = connector
            self.torque_status = 0
            self.operating_mode_status = OperatingMode.POSITION

        def disableTorque(self):
            self.torque_status = 0

        def enableTorque(self):
            self.torque_status = 1

        def setOperatingMode(self, mode):
            self.operating_mode_status = mode

        def getPresentPosition(self):
            return state["positions"].get(self.id, 2048)

        def _getControlTableItem(self, name):
            class _Item:
                def __init__(self, address, size):
                    self.address = address
                    self.size = size
            return _Item({"Present Input Voltage": 144}.get(name, 0), 1)

        def _readData(self, dxl_id, address, length):
            return 121  # 12.1 V

        def stageSetGoalPosition(self, position):
            return StagedCommand("write", self.id, 116, 4, [position])

    class GroupExecutor:
        def __init__(self, connector):
            self.cmds = []

        def addCmd(self, command):
            self.cmds.append(command)

        def executeWrite(self):
            for cmd in self.cmds:
                state["writes"].append({cmd.id: cmd.data[0]})

        def executeRead(self):
            return [None for _ in self.cmds]

    class Connector:
        def __init__(self, port_name, baud_rate):
            state["port"] = port_name
            state["baudrate"] = baud_rate

        def createMotor(self, motor_id):
            if motor_id == state["fail_create"]:
                raise RuntimeError("simulated createMotor failure")
            motor = FakeMotor(motor_id, self)
            state["motors"][motor_id] = motor
            return motor

        def ping(self, motor_id):
            return 1180  # model number

        def createGroupExecutor(self):
            return GroupExecutor(self)

        def closePort(self):
            state["closed"] = True

    module = types.ModuleType("dynamixel_easy_sdk")
    module.Connector = Connector
    module.Motor = FakeMotor
    module.GroupExecutor = GroupExecutor
    module.OperatingMode = OperatingMode
    module.StagedCommand = StagedCommand
    return module, state


class DynamixelBackendTests(unittest.TestCase):
    def _config(self, **kw):
        return Config(port="/dev/fake", servo_backend="dynamixel", **kw)

    def test_connect_creates_motors_and_enables_torque(self):
        sdk, state = make_fake_easy_sdk()
        with patch.dict(sys.modules, {"dynamixel_easy_sdk": sdk}):
            from openneck._backends.dynamixel import DynamixelBackend
            backend = DynamixelBackend(self._config())
            backend.connect()
            self.assertEqual(set(state["motors"]), {1, 2})
            self.assertTrue(all(m.torque_status == 1 for m in state["motors"].values()))
            backend.close()
        self.assertTrue(state["closed"])

    def test_connect_failure_is_translated_to_runtime_error(self):
        sdk, state = make_fake_easy_sdk()
        state["fail_create"] = 2
        with patch.dict(sys.modules, {"dynamixel_easy_sdk": sdk}):
            from openneck._backends.dynamixel import DynamixelBackend
            backend = DynamixelBackend(self._config())
            with self.assertRaisesRegex(RuntimeError, "ping servo 2"):
                backend.connect()
        self.assertTrue(state["closed"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_backends/test_dynamixel_backend.py -v`
Expected: FAIL — `ModuleNotFoundError: openneck._backends.dynamixel`.

- [ ] **Step 3: Write `openneck/_backends/dynamixel.py`**

```python
"""Dynamixel servo backend (dynamixel_easy_sdk)."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any

from .._config import Config, SERVO_MAX_STEP, SERVO_MIN_STEP
from ._port import find_servo_port


@contextmanager
def _translate(action: str):
    """Convert easy_sdk errors to RuntimeError (the ServoBackend contract)."""
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
                    self._motors[servo_id] = self._connector.createMotor(servo_id)
            mode = OperatingMode(self.config.operating_mode)
            for servo_id in self.ids:
                motor = self._motors[servo_id]
                with _translate(f"configure servo {servo_id}"):
                    motor.disableTorque()
                    motor.setOperatingMode(mode)
            if self.enable_torque_on_connect:
                for servo_id in self.ids:
                    self.enable_torque(servo_id)
        except BaseException:
            try:
                self.close()
            except Exception:
                pass
            raise
        self._connected = True

    def close(self) -> None:
        connector = self._connector
        self._connected = False
        self._motors = {}
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

    def _ensure_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("OpenNeck is not connected")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_backends/test_dynamixel_backend.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add openneck/_backends/dynamixel.py tests/test_backends/test_dynamixel_backend.py
git commit -m "feat(backends): add DynamixelBackend connect/close/torque"
```

---

### Task 2: Position read/write + voltage

**Files:** Modify `openneck/_backends/dynamixel.py`; Test `tests/test_backends/test_dynamixel_backend.py`.

- [ ] **Step 1: Write the failing tests**

Append to `DynamixelBackendTests`:

```python
    def test_write_positions_uses_group_executor(self):
        sdk, state = make_fake_easy_sdk()
        with patch.dict(sys.modules, {"dynamixel_easy_sdk": sdk}):
            from openneck._backends.dynamixel import DynamixelBackend
            backend = DynamixelBackend(self._config())
            backend.connect()
            backend.write_positions({1: 1024, 2: 3072})
        self.assertEqual(state["writes"], [{1: 1024}, {2: 3072}])

    def test_write_positions_rejects_out_of_range(self):
        sdk, state = make_fake_easy_sdk()
        with patch.dict(sys.modules, {"dynamixel_easy_sdk": sdk}):
            from openneck._backends.dynamixel import DynamixelBackend
            backend = DynamixelBackend(self._config())
            backend.connect()
            with self.assertRaises(ValueError):
                backend.write_positions({1: 5000})

    def test_read_positions_and_voltage(self):
        sdk, state = make_fake_easy_sdk()
        state["positions"] = {1: 1500, 2: 2500}
        with patch.dict(sys.modules, {"dynamixel_easy_sdk": sdk}):
            from openneck._backends.dynamixel import DynamixelBackend
            backend = DynamixelBackend(self._config())
            backend.connect()
            self.assertEqual(backend.read_positions(), {1: 1500, 2: 2500})
            self.assertAlmostEqual(backend.read_voltage(1), 12.1)
```

- [ ] **Step 2: Run to verify they fail**

Run: `pytest tests/test_backends/test_dynamixel_backend.py -k "write_positions or read_positions" -v`
Expected: FAIL — `AttributeError: ... has no attribute 'write_positions'`.

- [ ] **Step 3: Add the methods to `dynamixel.py`**

```python
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
            item = motor._getControlTableItem("Present Input Voltage")
            raw = motor._readData(servo_id, item.address, item.size)
        return float(raw) / 10.0
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_backends/test_dynamixel_backend.py -v`
Expected: PASS (6 tests).

- [ ] **Step 5: Commit**

```bash
git add openneck/_backends/dynamixel.py tests/test_backends/test_dynamixel_backend.py
git commit -m "feat(backends): Dynamixel position sync-write/read and voltage"
```

---

### Task 3: Register Dynamixel in the factory

**Files:** Modify `openneck/_backends/factory.py`; Test `tests/test_backends/test_factory.py`.

- [ ] **Step 1: Write the failing test**

Append to `MakeBackendTests`:

```python
    def test_dynamixel_backend_is_selected(self) -> None:
        from openneck._backends.dynamixel import DynamixelBackend
        backend = make_backend(Config(port="/dev/fake", servo_backend="dynamixel"))
        self.assertIsInstance(backend, DynamixelBackend)
        self.assertIsInstance(backend, ServoBackend)
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest tests/test_backends/test_factory.py -v`
Expected: FAIL — `ValueError: unknown servo_backend: 'dynamixel'`.

- [ ] **Step 3: Add the branch to `factory.py`**

```python
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
```

- [ ] **Step 4: Run full suite**

Run: `pytest -q`
Expected: all PASS.

- [ ] **Step 5: Commit + record progress**

```bash
git add openneck/_backends/factory.py tests/test_backends/test_factory.py
git commit -m "feat(backends): select DynamixelBackend from factory"
```
Append findings to `docs/progress/software/phase-3-dynamixel-backend.md`. Note resolution of open item **R2**: the `Present Input Voltage` control-table key works on the target model (confirm on real hardware in phase 4).
