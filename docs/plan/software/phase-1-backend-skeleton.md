# Phase 1: Backend Abstraction Skeleton — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Introduce a `ServoBackend` abstraction and route the controller/CLI through a `make_backend` factory, with the existing Feetech logic migrated unchanged into `FeetechBackend`. Zero behavior change.

**Architecture:** New `openneck/_backends/` package holds a `ServoBackend` Protocol, a `make_backend(config)` factory (returns `FeetechBackend` only, this phase), shared port discovery, and the migrated Feetech driver. `api.py` and `cli.py` stop importing `ServoDriver` directly and call `make_backend`. Feetech maintenance tools (`tools/_servo_bus.py`) are out of scope and unchanged.

**Tech Stack:** Python ≥3.10, `unittest` + `pytest`, `ftservo-python-sdk` (scservo_sdk), `pyserial`.

## Global Constraints

- Python ≥3.10; tests run with `pytest` from repo root.
- Every task ends with `pytest` green and a commit; record results in `docs/progress/software/phase-1-backend-skeleton.md` (AGENTS.md rule 1).
- Do **not** modify `thirdparty/DynamixelSDK/` (submodule, read-only).
- Do **not** change Feetech behavior this phase — pure refactor. Existing tests must stay green unchanged in intent.
- Code, paths, identifiers in English; progress-record narrative in Chinese.

## File Structure

- Create: `openneck/_backends/__init__.py` — package exports (`ServoBackend`, `make_backend`).
- Create: `openneck/_backends/protocol.py` — `ServoBackend` Protocol (consumer contract).
- Create: `openneck/_backends/_port.py` — `find_servo_port()` shared serial discovery.
- Create: `openneck/_backends/factory.py` — `make_backend(config, *, enable_torque_on_connect=True) -> ServoBackend`.
- Create: `openneck/_backends/feetech.py` — `FeetechBackend` (migrated from `_driver.py`).
- Modify: `openneck/api.py` — use `make_backend`; rename `self._driver` → `self._backend`.
- Modify: `openneck/cli.py` — `cmd_calibrate` + `record_axis_limits` use `make_backend`/`ServoBackend`.
- Delete: `openneck/_driver.py`.
- Move: `tests/test_driver.py` → `tests/test_backends/test_feetech_backend.py`.
- Modify: `tests/test_api.py` — patch `openneck.api._make_backend`; rename `FakeServoDriver` → `FakeBackend`.

**Interfaces:**
- Produces (used by later phases): `openneck._backends.ServoBackend` (Protocol), `openneck._backends.make_backend(config, *, enable_torque_on_connect=True) -> ServoBackend`, `openneck._backends.feetech.FeetechBackend`.

---

### Task 1: Backend package, Protocol, port helper, factory (Feetech only)

**Files:**
- Create: `openneck/_backends/__init__.py`, `protocol.py`, `_port.py`, `factory.py`
- Test: `tests/test_backends/__init__.py`, `tests/test_backends/test_factory.py`

**Interfaces:**
- Produces: `make_backend(config, *, enable_torque_on_connect=True) -> ServoBackend`; `ServoBackend` Protocol.

- [ ] **Step 1: Write the failing test**

`tests/test_backends/__init__.py` is empty. `tests/test_backends/test_factory.py`:

```python
from __future__ import annotations
import unittest
from openneck._config import Config
from openneck._backends import make_backend, ServoBackend
from openneck._backends.feetech import FeetechBackend


class MakeBackendTests(unittest.TestCase):
    def test_default_backend_is_feetech(self) -> None:
        backend = make_backend(Config(port="/dev/fake"))
        self.assertIsInstance(backend, FeetechBackend)

    def test_feetech_backend_satisfies_protocol(self) -> None:
        backend = make_backend(Config(port="/dev/fake"))
        self.assertIsInstance(backend, ServoBackend)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_backends/test_factory.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'openneck._backends'`.

- [ ] **Step 3: Write the modules**

`openneck/_backends/protocol.py`:

```python
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
```

`openneck/_backends/_port.py`:

```python
"""Shared serial-port discovery for servo backends."""

from __future__ import annotations


def find_servo_port() -> str:
    from serial.tools import list_ports

    ports = list(list_ports.comports())
    preferred = [
        port.device
        for port in ports
        if "ttyACM" in port.device
        or "ttyUSB" in port.device
        or port.device.startswith("COM")
    ]
    if preferred:
        return preferred[0]
    if ports:
        return ports[0].device
    raise RuntimeError("no serial ports found; pass port explicitly")
```

`openneck/_backends/factory.py`:

```python
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
```

`openneck/_backends/__init__.py`:

```python
"""Servo backend abstraction for OpenNeck.

Backends speak one servo family's register-level protocol. The controller and
CLI use the ``ServoBackend`` protocol and :func:`make_backend`; they never
import a specific SDK.
"""

from __future__ import annotations

from .factory import make_backend
from .protocol import ServoBackend

__all__ = ["ServoBackend", "make_backend"]
```

- [ ] **Step 4: Run test to verify it passes**

`feetech.py` does not exist yet, so this will still fail on import — that is expected; Task 2 creates `feetech.py`. Defer the green run to the end of Task 2. Commit nothing yet.

---

### Task 2: Migrate `ServoDriver` → `FeetechBackend`; move its tests

**Files:**
- Create: `openneck/_backends/feetech.py` (content migrated from `openneck/_driver.py`)
- Move: `tests/test_driver.py` → `tests/test_backends/test_feetech_backend.py`
- Delete: `openneck/_driver.py` is deleted in Task 5 (kept until api.py/cli.py stop importing it).

**Interfaces:**
- Produces: `FeetechBackend(config, *, enable_torque_on_connect=True)` implementing `ServoBackend`, with the same public methods as the old `ServoDriver`.

- [ ] **Step 1: Create `feetech.py` from `_driver.py`**

Copy `openneck/_driver.py` verbatim into `openneck/_backends/feetech.py` with these changes:
- Module docstring: `"""Feetech SCS servo backend (scservo_sdk)."""`.
- `from ._config import ...` → `from .._config import Config, SERVO_MAX_STEP, SERVO_MIN_STEP`.
- `from serial.tools import list_ports` block (the `find_servo_port` body) → replace the local `find_servo_port` definition with `from ._port import find_servo_port`.
- Rename `class ServoDriver` → `class FeetechBackend`. Keep every method and private helper (`connect`, `close`, `ping`, `read_positions`, `read_position`, `read_voltage`, `enable_torque`, `release_torque`, `write_positions`, `_set_torque`, `_rollback_torque_after_failed_connect`, `_packet_call`, `_reset_sdk_busy`, `_ensure_connected`, `_ensure_connected_or_opened`, `_check`, `__enter__`, `__exit__`) and the module constants `TORQUE_ENABLE_ADDR`, `PRESENT_VOLTAGE_ADDR` unchanged.
- In `connect()`, the `from scservo_sdk import COMM_SUCCESS, PortHandler, sms_sts` import stays inside the method.

- [ ] **Step 2: Move and adapt the driver tests**

Create `tests/test_backends/test_feetech_backend.py` from `tests/test_driver.py` with these changes:
- `from openneck._driver import ServoDriver` → `from openneck._backends.feetech import FeetechBackend`.
- `driver = ServoDriver(Config(port="/dev/fake"))` → `driver = FeetechBackend(Config(port="/dev/fake"))` (3 occurrences).
- `patch("openneck._driver.time.sleep", ...)` → `patch("openneck._backends.feetech.time.sleep", ...)`.
- Rename the test class `ServoDriverTests` → `FeetechBackendTests`.
- Keep the `make_fake_sdk()` helper and all three test methods unchanged in logic.
- Delete `tests/test_driver.py`.

- [ ] **Step 3: Run the migrated tests**

Run: `pytest tests/test_backends/test_feetech_backend.py tests/test_backends/test_factory.py -v`
Expected: PASS (4 tests).

- [ ] **Step 4: Commit**

```bash
git add openneck/_backends/ tests/test_backends/ tests/test_driver.py
git commit -m "refactor: extract _backends package and migrate Feetech driver to FeetechBackend"
```

---

### Task 3: Route `api.py` through `make_backend`; update its tests

**Files:**
- Modify: `openneck/api.py`
- Test: `tests/test_api.py`

**Interfaces:**
- Consumes: `make_backend(config, *, enable_torque_on_connect=True) -> ServoBackend` (Task 1).
- Produces: `OpenNeckController` whose backend is obtained via `openneck.api._make_backend`.

- [ ] **Step 1: Write the failing test (update the existing patch target)**

In `tests/test_api.py`:
- Rename `class FakeServoDriver` → `class FakeBackend` and update the two references (`FakeServoDriver.instances` → `FakeBackend.instances`; `self.driver_patch = patch("openneck.api._ServoDriver", FakeServoDriver)` → `patch("openneck.api._make_backend", FakeBackend)`). `FakeBackend` keeps the same methods and the `__init__(self, config, *, enable_torque_on_connect=True)` signature — which matches `make_backend`'s, so the patch stands in for the factory directly.
- Replace `FakeServoDriver.instances[-1]` references inside the test bodies with `FakeBackend.instances[-1]`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_api.py -v`
Expected: FAIL — `AttributeError: module 'openneck.api' has no attribute '_make_backend'` (the patch target does not exist yet).

- [ ] **Step 3: Edit `api.py`**

- Replace `from ._driver import ServoDriver as _ServoDriver` with `from ._backends import make_backend as _make_backend`.
- In `OpenNeckController.__init__`: `self._driver = _ServoDriver(loaded)` → `self._backend = _make_backend(loaded)`.
- In `_controller_from_config`: `controller._driver = _ServoDriver(config, enable_torque_on_connect=enable_torque_on_connect)` → `controller._backend = _make_backend(config, enable_torque_on_connect=enable_torque_on_connect)`.
- Rename every `self._driver.` use site to `self._backend.` (methods `connect`, `write_positions`, `read_positions`, `read_voltage`, `release_torque`, `close`). There are 6 call sites.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_api.py -v`
Expected: PASS (7 tests).

- [ ] **Step 5: Commit**

```bash
git add openneck/api.py tests/test_api.py
git commit -m "refactor: obtain controller backend via make_backend factory"
```

---

### Task 4: Route `cli.py` calibration through `make_backend`

**Files:**
- Modify: `openneck/cli.py`
- Test: `tests/test_cli.py` (existing; should stay green).

**Interfaces:**
- Consumes: `make_backend`, `ServoBackend`.

- [ ] **Step 1: Edit `cli.py` imports and calibration sites**

- Line 26 import: `from ._driver import ServoDriver` → `from ._backends import ServoBackend, make_backend`.
- `cmd_calibrate` (line ~90): `with ServoDriver(cfg, enable_torque_on_connect=False) as driver:` → `with make_backend(cfg, enable_torque_on_connect=False) as driver:`.
- `record_axis_limits` signature: `def record_axis_limits(driver: ServoDriver, motor_id: int, name: str)` → `def record_axis_limits(driver: ServoBackend, motor_id: int, name: str)`.

- [ ] **Step 2: Run CLI tests**

Run: `pytest tests/test_cli.py -v`
Expected: PASS (existing tests).

- [ ] **Step 3: Commit**

```bash
git add openneck/cli.py
git commit -m "refactor: route CLI calibration through make_backend"
```

---

### Task 5: Delete `_driver.py`; full suite green

**Files:**
- Delete: `openneck/_driver.py`

- [ ] **Step 1: Delete the old module**

```bash
git rm openneck/_driver.py
```

- [ ] **Step 2: Confirm nothing else imports it**

Run: `grep -rn "_driver" openneck/ tests/ || true`
Expected: no matches (all references moved in Tasks 3–4).

- [ ] **Step 3: Run the full suite**

Run: `pytest -q`
Expected: all tests PASS.

- [ ] **Step 4: Commit**

```bash
git commit -m "refactor: remove legacy _driver.py after backend extraction"
```

- [ ] **Step 5: Record progress**

Append to `docs/progress/software/phase-1-backend-skeleton.md`: files touched, commands run (with exit codes), result, any deviations from this plan.
