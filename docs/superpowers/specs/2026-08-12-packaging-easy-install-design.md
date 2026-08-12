# Packaging & easy-install improvements

**Date:** 2026-08-12
**Status:** Approved (design), pending implementation
**Scope:** Lower the friction of installing OpenNeck (and migrating its runtime
parameters) into a new or existing environment such as the teleop stack.

## Problem

Migrating OpenNeck into a new environment today requires three loosely-coupled
manual steps, and the runtime parameters do not travel with `pip install`:

1. `active_vision_config.json` is gitignored (`.gitignore:27`) and not shipped
   in the wheel, so the whole parameter set (backend choice, IDs, calibration,
   PID gains) must be hand-copied. There is no in-repo template to start from.
2. The Dynamixel SDK is a git submodule that is **not** declared in
   `pyproject.toml`; it needs a separate `pip install -e thirdparty/...` step.
3. `OpenNeckController.__init__` only accepts `config` (a path) and `port`
   (`api.py:41-49`), so a host program cannot select the backend in code
   without maintaining a JSON file or reaching into the private `_config`.

## Goals

- One-command install of the Dynamixel variant: `pip install ".[dynamixel]"`.
- Two in-repo example configs (feetech + dynamixel) that `cp` into place.
- A host program can pick the backend and common hardware params purely in
  code via `OpenNeckController(...)`.

## Non-goals

- No changes to the CLI (it already has `--servo-backend`).
- No kwarg exposure for PID / profile fields (those stay JSON-only).
- No refactor of `_controller_from_config` or the backend protocol.

---

## Change 1 — Optional dependency for the Dynamixel SDK

**File:** `pyproject.toml`

Add an extras section pointing at the vendored, pinned submodule:

```toml
[project.optional-dependencies]
dynamixel = ["dynamixel-sdk @ file:thirdparty/DynamixelSDK/python"]
```

- Distribution name confirmed `dynamixel-sdk` v4.0.5
  (`thirdparty/DynamixelSDK/python/pyproject.toml:6`).
- The `file:` direct reference is non-editable, which is the correct semantic
  for a read-only submodule pinned to a release tag.
- Pure-Feetech installs (`pip install .`) are unaffected and still pull only
  `pyserial` + `ftservo-python-sdk`.

**Known risk to verify in implementation:** the relative `file:` reference must
resolve against the project root on the target pip version. Implementation
**must** validate by running `pip install ".[dynamixel]"` in a clean virtualenv
and confirming `python -c "from dynamixel_easy_sdk import Connector"` imports.
If the relative form fails, fallback (in priority order): an absolute `file:///`
reference generated at install time is **not** acceptable (non-portable); the
fallback is a `requirements-dynamixel.txt` containing
`-e thirdparty/DynamixelSDK/python`, documented alongside the extra. Modern pip
is expected to handle the relative `file:` form.

**Docs:** update `docs/en/software.md` and `docs/zh-CN/software.md` install
sections to show `pip install ".[dynamixel]"` as the primary Dynamixel install,
keeping the manual `pip install -e thirdparty/...` as the editable/debug
alternative. Keep the `--no-build-isolation` proxy note.

## Change 2 — Two example config templates

**New files** (the `*.example.json` suffix is not matched by the
`active_vision_config.json` gitignore line):

- `active_vision_config.feetech.example.json` — exactly the `Config()` defaults
  (`servo_backend: "feetech"`, `yaw_id`/`pitch_id` 1/2, centers 2048, etc.).
- `active_vision_config.dynamixel.example.json` — full Dynamixel field set
  (`servo_backend: "dynamixel"`, `operating_mode: 3`, `profile_velocity` /
  `profile_acceleration: 0`, PID gains `0` = leave untouched). Calibration
  steps use safe defaults with a top-of-file comment path documented in the
  install guide noting these must be re-run via `openneck calibrate` when the
  physical mechanism changes.

Because JSON has no comments, the "re-run calibrate" guidance lives in the
install section of `software.md` (both languages), not inline in the JSON.

**Test:** add a case to `tests/test_config.py` that loads each example file
through `Config(**json.load(...))` (or `load_config(path)`), asserting it
validates. This guards the templates against silent drift when `Config` fields
change.

## Change 3 — `OpenNeckController` constructor kwargs

**File:** `openneck/api.py` (replace `__init__`, lines 41-51)

New keyword-only args, mirroring how `port` already flows through
`_replace_config`, so validation reuses `Config.__post_init__` for free:

```python
def __init__(
    self,
    config: str | Path | None = None,
    *,
    port: str | None = None,
    servo_backend: str | None = None,
    baudrate: int | None = None,
    operating_mode: int | None = None,
) -> None:
    loaded = _load_config(config)
    changes = {}
    for key, value in (
        ("port", port),
        ("servo_backend", servo_backend),
        ("baudrate", baudrate),
        ("operating_mode", operating_mode),
    ):
        if value is not None:
            changes[key] = value
    if changes:
        loaded = _replace_config(loaded, **changes)
    self._config = loaded
    self._backend = _make_backend(loaded)
```

- `servo_backend` is the primary switch; `baudrate` and `operating_mode` are
  the two hardware params most commonly set at construction time (port speed;
  Dynamixel motion mode). Deeper fields stay in JSON.
- Invalid values (e.g. `servo_backend="foo"`, `operating_mode=2`) raise via
  `Config.__post_init__` — no new validation code.
- Public API surface (`openneck/__init__.py`) is unchanged; the class signature
  gains kwargs only.

**Tests** (`tests/test_api.py`, matching existing style):
1. `servo_backend="dynamixel"` override produces a `DynamixelBackend` instance
   (with a fake SDK injected, as the existing dynamixel tests do).
2. `baudrate` / `operating_mode` overrides land on `controller._config`.
3. Invalid `servo_backend` raises `ValueError`.
4. No-kwargs call is unchanged (regression).

---

## Test plan (whole change)

- `pytest -q` stays green (baseline 43 passing as of 2026-08-12); new cases
  raise the count.
- Clean-venv install check for Change 1 (above).
- Manual: `cp active_vision_config.dynamixel.example.json
  active_vision_config.json` loads cleanly via `openneck config`.

## Order of implementation

1. Change 3 (api.py + tests) — smallest, highest isolation.
2. Change 2 (two example JSONs + config test).
3. Change 1 (pyproject extra + clean-venv verify + docs).
