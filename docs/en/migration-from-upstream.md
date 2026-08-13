# Upgrading from upstream BotRunner64 OpenNeck

[Home](../../README.md) · [Software](./software.md) · [Hardware](./hardware.md) · [Assembly](./assembly.md) · [Deployment](./deployment-teleopit.md) · [Migration](./migration-from-upstream.md) · **English** · [中文](../zh-CN/migration-from-upstream.md)

## Contents

- [At a glance](#at-a-glance)
- [Public API changes](#public-api-changes)
- [What you must change in downstream code](#what-you-must-change-in-downstream-code)
- [Config schema changes](#config-schema-changes)
- [CLI changes](#cli-changes)
- [Packaging changes](#packaging-changes)
- [Behavioral differences to watch](#behavioral-differences-to-watch)
- [Migration checklist](#migration-checklist)
- [Reference](#reference)

What changed in this fork's API versus the original BotRunner64 OpenNeck, what
you must change in downstream code when updating, and behavioral differences
to watch. For install/config migration into a specific environment see
[`deployment-teleopit.md`](deployment-teleopit.md); for the full field
reference see [`software.md`](software.md).

**Baseline:** the comparison base is the git merge-base with `upstream`
(`BotRunner64/OpenNeck`), commit `145e6bf` — i.e. the exact point this fork
diverged. "Original" below means that state.

## At a glance

| Surface | Verdict |
|---|---|
| `from openneck import OpenNeckController, NeckAngles` + public methods | **Backward compatible** — no changes required |
| `OpenNeckController.__init__` | Compatible — 3 new *optional* kwargs, old calls work unchanged |
| `openneck._driver.ServoDriver` (private) | **Removed** — replaced by `openneck._backends` (`make_backend`, `ServoBackend`) |
| `controller._driver` attribute | Renamed to `controller._backend` (private) |
| Config file | Additive — new optional fields; `yaw_id`/`pitch_id` now allow `0` |
| CLI subcommands | Unchanged (`ports`, `config`, `voltage`, `calibrate`, `center`, `test`) |
| CLI flags | New optional flags added; old flags unchanged |
| `pyproject.toml` | New `dynamixel` extra; deps unchanged; **version bumped to `0.3.0`** (upstream is `0.2.0`) |

**Bottom line:** if your downstream code used only the public API
(`OpenNeckController` / `NeckAngles`), you need to change **nothing**. The only
hard break is importing the private `ServoDriver`.

## Public API changes

The package exports are unchanged:

```python
# openneck/__init__.py — exports unchanged; version bumped from upstream's 0.2.0
__all__ = ["NeckAngles", "OpenNeckController"]
__version__ = "0.3.0"
```

`OpenNeckController` keeps every public method with the same signature:
`connect()`, `move_deg(yaw_deg, pitch_deg) -> NeckAngles`, `center()`,
`read_deg() -> NeckAngles`, `read_voltage() -> dict[str, float]`,
`release_torque()`, `close()`, and the context-manager protocol.

The constructor gains three **optional, keyword-only** overrides (all default
`None`, so omitting them reproduces the original behavior):

```python
OpenNeckController(
    config=None,            # str | Path | None  (unchanged)
    *,
    port=None,              # unchanged
    servo_backend=None,     # NEW: "feetech" | "dynamixel"
    baudrate=None,          # NEW
    operating_mode=None,    # NEW (Dynamixel only)
)
```

`NeckAngles` (frozen dataclass: `yaw_deg`, `pitch_deg`) is unchanged.

## What you must change in downstream code

1. **If you used only the public API** — nothing. Existing code keeps working:
   ```python
   from openneck import OpenNeckController
   with OpenNeckController("active_vision_config.json", port="/dev/ttyUSB0") as neck:
       neck.move_deg(5.0, 0.0)
   ```

2. **If you imported the private driver** — migrate it:
   ```python
   # BEFORE (broken — module removed):
   from openneck._driver import ServoDriver
   driver = ServoDriver(cfg)

   # AFTER:
   from openneck._backends import make_backend      # factory by config.servo_backend
   driver = make_backend(cfg)
   # or, if you only need the contract:
   from openneck._backends import ServoBackend       # Protocol (typing only)
   ```
   Prefer routing through `OpenNeckController` or `make_backend(config)` rather
   than instantiating a backend class directly — the factory reads
   `config.servo_backend` so your code stays backend-agnostic.

3. **If you touched `controller._driver`** — rename to `controller._backend`.
   (Private attribute; only relevant if you reached past the public API.)

4. **If you had a config that used servo ID `0`** — it now validates (previously
   rejected with "must be 1..253"). No action needed; this is an intentional
   relaxation for Dynamixel, whose IDs include `0`.

5. **(Optional) Adopt the Dynamixel backend** — three equivalent ways:
   - config field: `"servo_backend": "dynamixel"`
   - CLI flag: `--servo-backend dynamixel`
   - code kwarg: `OpenNeckController(servo_backend="dynamixel", baudrate=57600)`

   And install the SDK: `python -m pip install ".[dynamixel]"`.

## Config schema changes

Additive only. The original schema (port, baudrate, IDs, `*_center_step` /
`*_min_step` / `*_max_step` / `*_step_sign`, `speed`, `acceleration) is
unchanged and loads as-is. New optional fields:

| Field | Default | Meaning |
|---|---|---|
| `servo_backend` | `"feetech"` | `"feetech"` or `"dynamixel"` |
| `operating_mode` | `3` (POSITION) | Dynamixel only; ignored by Feetech |
| `profile_velocity` | `0` | Dynamixel; `0` = leave untouched |
| `profile_acceleration` | `0` | Dynamixel; `0` = leave untouched |
| `yaw_kp` / `yaw_ki` / `yaw_kd` | `0` | Dynamixel Position PID; `0` = untouched |
| `pitch_kp` / `pitch_ki` / `pitch_kd` | `0` | Dynamixel Position PID; `0` = untouched |

Validation changes:
- **Relaxed:** `yaw_id` / `pitch_id` minimum is now `0` (was `1`).
- **Unchanged:** unknown fields are still rejected, so any config carrying
  fields removed before the merge-base will still error. Configs from the
  *very* old normalized-amplitude schema are not auto-converted — re-run
  `openneck calibrate`.

## CLI changes

Subcommands are identical: `ports`, `config`, `voltage`, `calibrate`,
`center`, `test`. New optional flags (all default unset, so old command lines
behave identically): `--servo-backend`, `--operating-mode`,
`--profile-velocity`, `--profile-acceleration`, `--yaw-kp/ki/kd`,
`--pitch-kp/ki/kd`.

## Packaging changes

- `pyproject.toml` dependencies are unchanged (`pyserial`, `ftservo-python-sdk`).
- New optional extra: `pip install ".[dynamixel]"` pulls the vendored
  Dynamixel SDK submodule. Plain `pip install .` (Feetech) is unchanged.
- **Version:** the fork reports `0.3.0`; upstream reports `0.2.0`. Detect the
  fork with `openneck.__version__`. For older fork builds that still reported
  `0.2.0`, fall back to the `_backends` probe or install location:
  ```bash
  python -c "import openneck; print(openneck.__version__)"   # 0.3.0 = fork, 0.2.0 = upstream
  python -c "import importlib.util as u; print(bool(u.find_spec('openneck._backends')))"
  pip show openneck | grep Location
  ```

## Behavioral differences to watch

- **Backend selection is now explicit.** The original was Feetech-only. The
  default is still Feetech, but a different backend is one config field / flag
  / kwarg away — verify `servo_backend` when porting a config between machines.
- **Dynamixel-only fields are ignored by Feetech** (safe no-op), so a single
  config file can carry both families' settings.
- **Validation is stricter on unknown fields, looser on IDs.** A previously-
  rejected ID-0 config now loads; a config with typos / removed fields still
  errors loudly.
- **No breaking change to motion semantics.** `move_deg` / clamping / sign
  handling are unchanged; the step↔angle math in `openneck._angles` is
  untouched.

## Migration checklist

- [ ] Update the package (`pip install -U .` or `pip install ".[dynamixel]"`).
- [ ] `grep -rn "_driver\|ServoDriver"` your codebase — replace any private
      import per "What you must change" #2/#3.
- [ ] Re-run your existing `OpenNeckController` smoke test — it should pass
      unchanged.
- [ ] If adopting Dynamixel: set `servo_backend`, install the extra, run
      `openneck calibrate` on the real mechanism.
- [ ] Confirm the fork is actually installed (`openneck.__version__` should
      be `0.3.0`; or use the `_backends` probe).

## Reference

- Install + full config field reference: [`software.md`](software.md)
- Config dataflow (load / validate / override / backend selection): [`../knowledge/config-dataflow.md`](../knowledge/config-dataflow.md)
- Deploy into a specific environment: [`deployment-teleopit.md`](deployment-teleopit.md)
- Backend design contract (why `_driver` → `_backends`): [`../knowledge/twist2-dynamixel-design.md`](../knowledge/twist2-dynamixel-design.md)
