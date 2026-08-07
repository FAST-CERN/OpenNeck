# Phase 2: Config Extension — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Add backend-selection and Dynamixel-tuning fields to `Config`, route the factory through `config.servo_backend`, and expose the new fields on the CLI. Default stays Feetech (non-breaking).

**Architecture:** `Config` gains `servo_backend` (`"feetech"` default), `operating_mode`, `profile_velocity`, `profile_acceleration`, all validated in `__post_init__`. `make_backend` branches on `servo_backend` (Feetech only this phase; unknown raises). CLI gains matching override flags.

**Tech Stack:** Python ≥3.10, `unittest` + `pytest`.

## Global Constraints

- Same as phase-1 (pytest green + commit + progress record per task; do not modify the submodule).
- Backward compatible: a config file with no new fields still loads and selects Feetech.
- Unknown-field rejection must still hold (adding fields to the dataclass extends the known set automatically).

## File Structure

- Modify: `openneck/_config.py` — 4 new fields + validation.
- Modify: `openneck/_backends/factory.py` — branch on `config.servo_backend`.
- Modify: `openneck/cli.py` — 4 new override flags in `add_common` + `with_overrides`.
- Test: `tests/test_config.py`, `tests/test_backends/test_factory.py`.

**Interfaces:**
- Produces: `Config.servo_backend`, `Config.operating_mode`, `Config.profile_velocity`, `Config.profile_acceleration`; `make_backend` now reads `config.servo_backend`.

---

### Task 1: Add config fields and validation

**Files:** Modify `openneck/_config.py`; Test `tests/test_config.py`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_config.py` (`ConfigTests`):

```python
    def test_backend_defaults_to_feetech(self) -> None:
        self.assertEqual(Config().servo_backend, "feetech")
        self.assertEqual(Config().operating_mode, 3)

    def test_backend_field_is_validated(self) -> None:
        with self.assertRaises(ValueError):
            Config(servo_backend="bogus")

    def test_operating_mode_is_validated(self) -> None:
        Config(operating_mode=4)
        with self.assertRaises(ValueError):
            Config(operating_mode=2)
        with self.assertRaises(ValueError):
            Config(operating_mode=True)  # bool must be rejected

    def test_profile_fields_are_non_negative(self) -> None:
        Config(profile_velocity=0, profile_acceleration=0)
        with self.assertRaises(ValueError):
            Config(profile_velocity=-1)
        with self.assertRaises(ValueError):
            Config(profile_acceleration=-1)
```

Also extend `test_loads_only_current_schema` so the `data` dict includes `"servo_backend": "dynamixel", "operating_mode": 4`, and assert `config.servo_backend == "dynamixel"`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_config.py -v`
Expected: FAIL — `TypeError: __init__() got an unexpected keyword argument 'servo_backend'`.

- [ ] **Step 3: Add fields and validation**

In `openneck/_config.py`, add fields after `acceleration: int = 0`:

```python
    servo_backend: str = "feetech"
    operating_mode: int = 3
    profile_velocity: int = 0
    profile_acceleration: int = 0
```

In `__post_init__`, after the `acceleration` check, add:

```python
        if self.servo_backend not in ("feetech", "dynamixel"):
            raise ValueError(
                "servo_backend must be 'feetech' or 'dynamixel', "
                f"got {self.servo_backend!r}"
            )
        if isinstance(self.operating_mode, bool) or self.operating_mode not in (
            0,
            1,
            3,
            4,
            5,
            16,
        ):
            raise ValueError(
                "operating_mode must be one of 0,1,3,4,5,16, "
                f"got {self.operating_mode!r}"
            )
        _require_int("profile_velocity", self.profile_velocity, minimum=0)
        _require_int(
            "profile_acceleration", self.profile_acceleration, minimum=0
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_config.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add openneck/_config.py tests/test_config.py
git commit -m "feat(config): add servo_backend and Dynamixel profile fields"
```

---

### Task 2: Route the factory through `servo_backend`

**Files:** Modify `openneck/_backends/factory.py`; Test `tests/test_backends/test_factory.py`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_backends/test_factory.py`:

```python
    def test_unknown_backend_raises(self) -> None:
        from openneck._config import Config
        with self.assertRaises(ValueError):
            make_backend(Config(port="/dev/fake", servo_backend="bogus"))
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest tests/test_backends/test_factory.py::MakeBackendTests::test_unknown_backend_raises -v`
Expected: FAIL — `make_backend` still returns Feetech unconditionally.

- [ ] **Step 3: Update `factory.py`**

```python
def make_backend(
    config: Config,
    *,
    enable_torque_on_connect: bool = True,
) -> ServoBackend:
    name = config.servo_backend
    if name == "feetech":
        from .feetech import FeetechBackend

        return FeetechBackend(
            config, enable_torque_on_connect=enable_torque_on_connect
        )
    raise ValueError(f"unknown servo_backend: {name!r}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_backends/test_factory.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add openneck/_backends/factory.py tests/test_backends/test_factory.py
git commit -m "feat(backends): select backend by config.servo_backend"
```

---

### Task 3: Expose the new fields on the CLI

**Files:** Modify `openneck/cli.py`; Test `tests/test_cli.py` (existing must stay green).

- [ ] **Step 1: Add CLI flags**

In `add_common`, after the `--acceleration` argument:

```python
    parser.add_argument(
        "--servo-backend", choices=["feetech", "dynamixel"], default=None
    )
    parser.add_argument(
        "--operating-mode", type=int, choices=[0, 1, 3, 4, 5, 16], default=None
    )
    parser.add_argument("--profile-velocity", type=int, default=None)
    parser.add_argument("--profile-acceleration", type=int, default=None)
```

- [ ] **Step 2: Thread the overrides**

In `with_overrides`, extend the key list with `"servo_backend"`, `"operating_mode"`, `"profile_velocity"`, `"profile_acceleration"`.

- [ ] **Step 3: Run CLI tests + a manual parse check**

Run: `pytest tests/test_cli.py -v && python -c "import openneck.cli as c; p=c.build_parser(); a=p.parse_args(['config','--servo-backend','dynamixel','--operating-mode','3']); assert a.servo_backend=='dynamixel' and a.operating_mode==3; print('ok')"`
Expected: tests PASS and `ok` printed.

- [ ] **Step 4: Commit**

```bash
git add openneck/cli.py
git commit -m "feat(cli): add backend and profile override flags"
```

- [ ] **Step 5: Record progress** in `docs/progress/software/phase-2-config-extension.md`.
