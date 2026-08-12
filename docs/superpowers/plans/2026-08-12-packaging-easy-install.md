# Packaging & easy-install improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lower the friction of installing OpenNeck into a new environment by adding a `dynamixel` install extra, two in-repo example configs, and `servo_backend`/`baudrate`/`operating_mode` kwargs on `OpenNeckController`.

**Architecture:** Pure-additive changes. (1) A PEP 508 `file:` direct reference in `pyproject.toml` exposes the vendored SDK as an optional extra. (2) Two committed `*.example.json` files (not matched by the existing gitignore line) give a copy-and-edit starting point. (3) The controller constructor gains keyword-only overrides that flow through the existing `_replace_config` path, reusing `Config.__post_init__` validation.

**Tech Stack:** Python ≥3.10, `unittest` + `pytest`, setuptools/pyproject, JSON config.

## Global Constraints

- Python ≥3.10; tests run with `pytest` from repo root. Baseline is **43 passing** as of 2026-08-12; every task keeps pytest green and the count only rises.
- Conversation/progress-record narrative in Chinese; code, paths, fields, commands, identifiers in English (AGENTS.md rule 8).
- Do **not** modify `thirdparty/DynamixelSDK/` (read-only submodule).
- `.gitignore` line 27 is the exact name `active_vision_config.json`; it does **not** match `*.example.json`, so example files can be committed.
- The Dynamixel backend imports `dynamixel_easy_sdk` lazily inside `connect()` (`openneck/_backends/dynamixel.py:49`); constructing a `DynamixelBackend` does **not** require the SDK to be importable. This is relied on by Task 1's tests.
- No new public exports from `openneck/__init__.py` (still only `NeckAngles`, `OpenNeckController`).

---

### Task 1: `OpenNeckController` constructor kwargs

**Files:**
- Modify: `openneck/api.py:41-51` (the `__init__` method)
- Test: `tests/test_api.py` (append a new test class)

**Interfaces:**
- Consumes: `openneck._config.load_config`, `openneck._config.replace_config`, `openneck._backends.make_backend` (all unchanged).
- Produces: `OpenNeckController.__init__(config=None, *, port=None, servo_backend=None, baudrate=None, operating_mode=None)`. Later tasks do not consume this; it is the user-facing API.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_api.py` (new class — deliberately does **not** patch `_make_backend`, so the real factory runs and `servo_backend="dynamixel"` yields a real `DynamixelBackend`):

```python
class ControllerKwargTests(unittest.TestCase):
    """servo_backend / baudrate / operating_mode constructor kwargs.

    Does NOT patch openneck.api._make_backend: the real factory must run so
    that servo_backend="dynamixel" produces a real (unconnected)
    DynamixelBackend. connect() is never called, so no SDK import happens.
    """

    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.config_path = Path(self.directory.name) / "config.json"
        self.config_path.write_text(
            json.dumps(
                {
                    "port": "/dev/from-config",
                    "baudrate": 1_000_000,
                    "yaw_id": 7,
                    "pitch_id": 8,
                    "yaw_center_step": 2000,
                    "yaw_min_step": 1900,
                    "yaw_max_step": 2100,
                    "yaw_step_sign": 1,
                    "pitch_center_step": 1500,
                    "pitch_min_step": 1400,
                    "pitch_max_step": 1600,
                    "pitch_step_sign": -1,
                    "speed": 0,
                    "acceleration": 0,
                    "servo_backend": "feetech",
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.directory.cleanup()

    def test_servo_backend_kwarg_selects_dynamixel(self) -> None:
        from openneck._backends.dynamixel import DynamixelBackend

        neck = OpenNeckController(self.config_path, servo_backend="dynamixel")
        self.assertEqual(neck._config.servo_backend, "dynamixel")
        self.assertIsInstance(neck._backend, DynamixelBackend)

    def test_baudrate_and_operating_mode_kwargs_override_config(self) -> None:
        neck = OpenNeckController(
            self.config_path, baudrate=57600, operating_mode=4
        )
        self.assertEqual(neck._config.baudrate, 57600)
        self.assertEqual(neck._config.operating_mode, 4)
        # Untouched fields keep the file value.
        self.assertEqual(neck._config.servo_backend, "feetech")

    def test_invalid_servo_backend_kwarg_raises(self) -> None:
        with self.assertRaises(ValueError):
            OpenNeckController(self.config_path, servo_backend="bogus")

    def test_no_kwargs_keeps_loaded_config(self) -> None:
        neck = OpenNeckController(self.config_path)
        self.assertEqual(neck._config.servo_backend, "feetech")
        self.assertEqual(neck._config.baudrate, 1_000_000)
        # operating_mode was absent from the file -> Config default 3.
        self.assertEqual(neck._config.operating_mode, 3)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest tests/test_api.py::ControllerKwargTests -v`
Expected: FAIL — `OpenNeckController.__init__() got an unexpected keyword argument 'servo_backend'` (a `TypeError`), so the first three tests error. The fourth (`test_no_kwargs_keeps_loaded_config`) may pass already.

- [ ] **Step 3: Implement the constructor**

Replace the body of `OpenNeckController.__init__` in `openneck/api.py` (currently lines 41-51). The new signature and body:

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

- [ ] **Step 4: Run the full test suite to verify it passes**

Run: `pytest -q`
Expected: PASS — baseline 43 + 4 new = **47 passing**.

- [ ] **Step 5: Commit**

```bash
git add openneck/api.py tests/test_api.py
git commit -m "feat(api): add servo_backend/baudrate/operating_mode kwargs to OpenNeckController"
```

---

### Task 2: Example config templates + test + doc pointer

**Files:**
- Create: `active_vision_config.feetech.example.json` (repo root)
- Create: `active_vision_config.dynamixel.example.json` (repo root)
- Test: `tests/test_config.py` (append a new test class)
- Modify: `docs/en/software.md` and `docs/zh-CN/software.md` (one-line pointer near the existing config example)

**Interfaces:**
- Consumes: `openneck._config.load_config` (unchanged), the `Config` field set in `openneck/_config.py:17-47`.
- Produces: two committed JSON templates that validate against `Config(**data)`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_config.py`. `Path(__file__).resolve().parent.parent` is the repo root because `tests/` lives at repo root:

```python
REPO_ROOT = Path(__file__).resolve().parent.parent


class ExampleConfigTests(unittest.TestCase):
    def test_feetech_example_is_valid(self) -> None:
        path = REPO_ROOT / "active_vision_config.feetech.example.json"
        config = load_config(path)
        self.assertEqual(config.servo_backend, "feetech")
        self.assertEqual(config.baudrate, 1_000_000)

    def test_dynamixel_example_is_valid(self) -> None:
        path = REPO_ROOT / "active_vision_config.dynamixel.example.json"
        config = load_config(path)
        self.assertEqual(config.servo_backend, "dynamixel")
        self.assertEqual(config.baudrate, 57_600)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_config.py::ExampleConfigTests -v`
Expected: FAIL — `FileNotFoundError` for the two not-yet-created example files.

- [ ] **Step 3: Create the feetech example**

Create `active_vision_config.feetech.example.json` with exactly the `Config()` defaults (every field enumerated as a reference):

```json
{
  "port": null,
  "baudrate": 1000000,
  "yaw_id": 1,
  "pitch_id": 2,
  "yaw_center_step": 2048,
  "yaw_min_step": 1024,
  "yaw_max_step": 3072,
  "yaw_step_sign": 1,
  "pitch_center_step": 2048,
  "pitch_min_step": 1365,
  "pitch_max_step": 2731,
  "pitch_step_sign": 1,
  "speed": 0,
  "acceleration": 0,
  "servo_backend": "feetech",
  "operating_mode": 3,
  "profile_velocity": 0,
  "profile_acceleration": 0,
  "yaw_kp": 0,
  "yaw_ki": 0,
  "yaw_kd": 0,
  "pitch_kp": 0,
  "pitch_ki": 0,
  "pitch_kd": 0
}
```

- [ ] **Step 4: Create the dynamixel example**

Create `active_vision_config.dynamixel.example.json` — same field set, but `servo_backend: "dynamixel"` and `baudrate: 57600` (typical Dynamixel X-series default). Calibration steps use safe defaults and **must be re-run via `openneck calibrate` for the actual mechanism** (note goes in docs, not JSON):

```json
{
  "port": null,
  "baudrate": 57600,
  "yaw_id": 1,
  "pitch_id": 2,
  "yaw_center_step": 2048,
  "yaw_min_step": 1024,
  "yaw_max_step": 3072,
  "yaw_step_sign": 1,
  "pitch_center_step": 2048,
  "pitch_min_step": 1365,
  "pitch_max_step": 2731,
  "pitch_step_sign": 1,
  "speed": 0,
  "acceleration": 0,
  "servo_backend": "dynamixel",
  "operating_mode": 3,
  "profile_velocity": 0,
  "profile_acceleration": 0,
  "yaw_kp": 0,
  "yaw_ki": 0,
  "yaw_kd": 0,
  "pitch_kp": 0,
  "pitch_ki": 0,
  "pitch_kd": 0
}
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `pytest tests/test_config.py::ExampleConfigTests -v`
Expected: PASS — both files validate against `Config`.

- [ ] **Step 6: Add the doc pointer (English)**

In `docs/en/software.md`, immediately after the existing Dynamixel JSON example block (which ends around the line containing `"pitch_step_sign": 1` followed by the closing ` ``` `; the prose about `yaw_step_sign` follows), insert a one-sentence note before the `yaw_step_sign` paragraph. Concretely, find this prose line:

```
`yaw_step_sign` and `pitch_step_sign` accept only `1` or `-1`:
```

and insert above it:

```
Copy whichever template matches your hardware — `active_vision_config.feetech.example.json` or `active_vision_config.dynamixel.example.json` — to `active_vision_config.json` and edit the `port`, servo IDs, and `*_step_sign` for your installation. The calibration steps (`*_center_step` / `*_min_step` / `*_max_step`) are safe defaults; run `openneck calibrate` against the actual mechanism to record real values.

```

- [ ] **Step 7: Add the doc pointer (Chinese)**

In `docs/zh-CN/software.md`, find the matching prose line (the Chinese guide mirrors the English structure; locate the paragraph that discusses `yaw_step_sign` / `pitch_step_sign` 取值) and insert the equivalent note above it:

```
按你的硬件选择对应模板——`active_vision_config.feetech.example.json` 或 `active_vision_config.dynamixel.example.json`——复制为 `active_vision_config.json`，再按实际安装修改 `port`、舵机 ID 与 `*_step_sign`。标定步进值（`*_center_step` / `*_min_step` / `*_max_step`）为安全默认；请在真实机构上运行 `openneck calibrate` 重新记录。

```

- [ ] **Step 8: Run the full suite and commit**

Run: `pytest -q`
Expected: PASS — 47 + 2 new = **49 passing**.

```bash
git add active_vision_config.feetech.example.json \
        active_vision_config.dynamixel.example.json \
        tests/test_config.py docs/en/software.md docs/zh-CN/software.md
git commit -m "feat(config): add feetech + dynamixel example config templates"
```

---

### Task 3: `dynamixel` install extra + docs rewrite + clean-venv verify

**Files:**
- Modify: `pyproject.toml` (add `[project.optional-dependencies]`)
- Modify: `docs/en/software.md` and `docs/zh-CN/software.md` (rewrite the "Dynamixel backend (optional)" install subsection)

**Interfaces:**
- Consumes: the vendored SDK at `thirdparty/DynamixelSDK/python` (distribution name `dynamixel-sdk`, confirmed at `thirdparty/DynamixelSDK/python/pyproject.toml:6`).
- Produces: `pip install ".[dynamixel]"` as the one-command Dynamixel install.

- [ ] **Step 1: Add the optional-dependency section**

In `pyproject.toml`, immediately after the `[project] dependencies` array (lines 12-15), add:

```toml

[project.optional-dependencies]
dynamixel = ["dynamixel-sdk @ file:thirdparty/DynamixelSDK/python"]
```

- [ ] **Step 2: Rewrite the English install subsection**

In `docs/en/software.md`, replace the existing "### Dynamixel backend (optional)" block (the prose ending in the `git clone ... / pip install . / pip install -e thirdparty/DynamixelSDK/python` fenced block, currently around lines 22-31) with:

````markdown
### Dynamixel backend (optional)

The Dynamixel backend uses the ROBOTIS SDK vendored as a git submodule. After
cloning with `--recurse-submodules`, install OpenNeck with the `dynamixel`
extra, which pulls the SDK automatically:

```bash
git clone --recurse-submodules <repo>
pip install ".[dynamixel]"
```

For an editable SDK install (when debugging the SDK itself), use the manual
form instead:

```bash
pip install -e thirdparty/DynamixelSDK/python
```

If `pip`'s build isolation cannot reach PyPI through your proxy, add
`--no-build-isolation` (the host env must already have `setuptools` and `wheel`).
````

- [ ] **Step 3: Rewrite the Chinese install subsection**

In `docs/zh-CN/software.md`, replace the matching "### Dynamixel 后端（可选）" block (currently around lines 22-30, ending in the same three-command fenced block) with:

````markdown
### Dynamixel 后端（可选）

Dynamixel 后端使用以 git 子模块内置的 ROBOTIS SDK。带 `--recurse-submodules` 克隆后，用 `dynamixel` extra 安装，SDK 会自动拉取：

```bash
git clone --recurse-submodules <repo>
pip install ".[dynamixel]"
```

如需可编辑安装 SDK（调试 SDK 本身时），改用手动方式：

```bash
pip install -e thirdparty/DynamixelSDK/python
```

若 `pip` 构建隔离环境下经代理无法访问 PyPI，加 `--no-build-isolation`（宿主环境需已安装 `setuptools` 与 `wheel`）。
````

- [ ] **Step 4: Verify the metadata builds and the extra is declared**

Run from repo root:

```bash
python -m pip install --upgrade build >/dev/null 2>&1 || true
python -m build --wheel 2>&1 | tail -n 5
python -c "import pathlib, tomllib, email; d=pathlib.Path('dist').glob('openneck-*.whl'); p=sorted(d)[-1]; meta=email.message_from_bytes(p.read_bytes()); print([x for x in (meta.get_all('Provides-Extra'), meta.get_all('Requires-Dist'))])"
```

Expected: the build produces `dist/openneck-*.whl`, and the metadata lists `Provides-Extra: dynamixel` and a `Requires-Dist` entry containing `dynamixel-sdk @ file:thirdparty/DynamixelSDK/python`. If `python -m build` is unavailable or fails behind the proxy, fall back to `python -c "import tomllib; print(tomllib.loads(open('pyproject.toml',encoding='utf-8').read())['project']['optional-dependencies'])"` to at least confirm the section parses.

- [ ] **Step 5: Verify the extra actually installs the SDK (clean venv)**

This is the risk-verification step called out in the spec (relative `file:` reference portability). In a throwaway venv:

```bash
python -m venv /tmp/openneck-extra-check
/tmp/openneck-extra-check/Scripts/python -m pip install --upgrade pip
/tmp/openneck-extra-check/Scripts/python -m pip install ".[dynamixel]"
/tmp/openneck-extra-check/Scripts/python -c "from dynamixel_easy_sdk import Connector, OperatingMode; print('extra ok')"
```

Expected: final line prints `extra ok`.

**If the relative `file:` reference fails** (pip error mentioning the path), do **not** silently switch to an absolute path (non-portable). Instead apply the documented fallback: keep the extra out of `pyproject.toml`, create `requirements-dynamixel.txt` at repo root containing the single line `-e thirdparty/DynamixelSDK/python`, and rewrite the two install subsections to `pip install -r requirements-dynamixel.txt`. Record which path was taken in the progress note. (Modern pip is expected to handle the relative `file:` form; this branch is the contingency.)

On Windows the venv interpreter path is `…/Scripts/python`; on Linux/macOS use `…/bin/python`. Adjust accordingly.

- [ ] **Step 6: Run the full suite and commit**

Run: `pytest -q`
Expected: PASS — still **49 passing** (no test change this task).

```bash
git add pyproject.toml docs/en/software.md docs/zh-CN/software.md
git commit -m "build(pyproject): add dynamixel install extra; rewrite install docs"
```

---

## Self-review notes

- **Spec coverage:** Change 1 (extra) → Task 3; Change 2 (two templates) → Task 2; Change 3 (kwargs) → Task 1. The spec's "docs" and "test plan" items are folded into the tasks that own each deliverable. No spec requirement lacks a task.
- **Type consistency:** kwarg names (`servo_backend`, `baudrate`, `operating_mode`) are identical across the `api.py` edit, the Task 1 tests, and the spec. Example field names match `Config` exactly (`baudrate`, `servo_backend`, etc.). Dynamixel example `baudrate: 57600` is asserted in both the file and the Task 2 test.
- **Risks:** Task 3 Step 5 is the only step that needs network/build-isolation and may require `--no-build-isolation`; the contingency is written inline. All other steps are offline and deterministic.
