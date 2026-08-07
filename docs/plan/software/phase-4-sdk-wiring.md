# Phase 4: Vendored SDK Wiring — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Make the vendored `dynamixel_easy_sdk` importable from the OpenNeck environment, then run a human-supervised real-hardware smoke test.

**Architecture:** The submodule is installed editable (`pip install -e thirdparty/DynamixelSDK/python`), which exposes `dynamixel_sdk` and `dynamixel_easy_sdk` plus the `.model` control-table data it depends on. A hard relative path-dependency is intentionally NOT added to `pyproject.toml` (relative `file:` URLs are fragile across pip versions); the editable install is the documented, reproducible mechanism (covered in phase-5 docs). Resolves open item **R4**: package `dynamixel-sdk` v4.0.5, setuptools backend, `package-dir = src`.

**Tech Stack:** `pip`, `dynamixel_easy_sdk`, real Dynamixel hardware (Task 2 only).

## Global Constraints

- Task 1 is automated and offline; it must not change behavior — `pytest -q` stays green.
- Task 2 touches real hardware: AGENTS.md rule 5 — human approval + operator present; first motion is center-only, then a small ≤5° move.
- Do not modify `thirdparty/DynamixelSDK/` (editable install only).

## File Structure

- No production source changes this phase (driver code is complete from phase 3).
- Modify (docs, if a quick pointer is added): `docs/en/software.md`, `docs/zh-CN/software.md` — full treatment is phase 5; here only the install command is confirmed.
- Progress record: `docs/progress/software/phase-4-sdk-wiring.md`.

---

### Task 1: Editable-install the submodule and smoke-test imports (offline)

- [ ] **Step 1: Ensure the submodule is present**

Run: `git submodule status thirdparty/DynamixelSDK`
Expected: prints `2ded684... thirdparty/DynamixelSDK (4.0.5)` (no `+`/`-` prefix). If missing: `git submodule update --init --recursive`.

- [ ] **Step 2: Editable-install**

Run: `pip install -e thirdparty/DynamixelSDK/python`
Expected: builds `dynamixel-sdk` 4.0.5 and installs `dynamixel_sdk` + `dynamixel_easy_sdk` (with `.model` data under `.../control_table/`).

- [ ] **Step 3: Import smoke test**

Run:
```bash
python -c "import dynamixel_sdk; from dynamixel_easy_sdk import Connector, Motor, GroupExecutor, OperatingMode; from dynamixel_easy_sdk.control_table import ControlTable; print('import ok')"
```
Expected: prints `import ok` (proves both packages and the control-table module load).

- [ ] **Step 4: Confirm the unit suite is unaffected**

Run: `pytest -q`
Expected: all PASS (tests inject fakes; the real SDK install does not change them).

- [ ] **Step 5: Record progress + commit (if any tracked file changed)**

If no tracked files changed, commit is a no-op; still record commands/exit codes in `docs/progress/software/phase-4-sdk-wiring.md`. (The editable install lives in the environment, not the repo.)

---

### Task 2: Real-hardware smoke test (human-supervised)

**Prerequisite:** TWIST2 (or any Dynamixel X-series) gimbal wired on the bus; both servo IDs match the config; operator present.

- [ ] **Step 1: Write a throwaway dynamixel config**

Create `active_vision_config.json` (gitignored) in the working directory:
```json
{
  "port": "COM3",
  "baudrate": 57600,
  "servo_backend": "dynamixel",
  "operating_mode": 3,
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
  "profile_velocity": 0,
  "profile_acceleration": 0
}
```
Adjust `port`, `baudrate`, IDs, signs to the actual hardware. Confirm the mechanism is clear to move.

- [ ] **Step 2: Read voltage + angles (no torque enabled)**

Run: `openneck voltage`
Expected: prints yaw/pitch angles and voltages without error. Confirms ping, present-position read, and voltage read against the real model's control table (resolves **R2** for the target hardware).

- [ ] **Step 3: Center, then a small yaw move**

Run: `openneck center --hold-s 2 && openneck test yaw --angle-deg 5`
Expected: gimbal centers, then moves yaw +5°, −5°, back to 0. Confirms `setOperatingMode` + `GroupExecutor` goal write on real hardware.

- [ ] **Step 4: Record results**

Append to `docs/progress/software/phase-4-sdk-wiring.md`: actual port/baudrate/model numbers seen, voltage readings, whether center/test moved correctly, any errors. Note final resolution of **R1** (model control table worked) and **R2** (voltage key worked).
