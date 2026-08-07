# Phase 5: Documentation & Calibration Notes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Document the new backend selection, the Dynamixel install/config path, and how calibration behaves for each backend — in both English and Chinese, matching the existing bilingual docs.

**Architecture:** No code changes. `docs/en/software.md` and `docs/zh-CN/software.md` gain: submodule-aware install, a "servo backend" section, a Dynamixel config example, and calibration notes. The runtime `openneck calibrate` is backend-agnostic (it reads present positions via the backend), so the existing procedure carries over; only the Feetech-specific `openneck-calibrate-middle` is called out as Feetech-only.

**Tech Stack:** Markdown (bilingual).

## Global Constraints

- Match the existing doc voice and link style in `docs/en|zh-CN/software.md`.
- Code/paths/identifiers in English; Chinese narrative in the zh-CN file (per AGENTS.md rule 8).
- Single source of truth: link the design contract rather than restating decisions — `docs/knowledge/twist2-dynamixel-design.md`.

## File Structure

- Modify: `docs/en/software.md`, `docs/zh-CN/software.md`.
- Optionally modify: `README.md` (clone hint with `--recurse-submodules`).
- Progress record: `docs/progress/software/phase-5-docs-calibration.md`.

---

### Task 1: Add backend + Dynamixel sections to the software docs

**Files:** `docs/en/software.md`, `docs/zh-CN/software.md`.

- [ ] **Step 1: Update the Installation section (English)**

After the existing `pip install .` block in `docs/en/software.md`, add:

```markdown
### Dynamixel backend (optional)

The Dynamixel backend uses the vendored ROBOTIS SDK, included as a git
submodule. Install it editable after cloning with submodules:

```bash
git clone --recurse-submodules <repo>
pip install .
pip install -e thirdparty/DynamixelSDK/python
```
```

- [ ] **Step 2: Add a "Servo backend" subsection (English)**

Add after the Configuration section:

```markdown
## Servo backend

OpenNeck supports two servo families, selected by the `servo_backend` field:

- `"feetech"` (default) — Feetech SCS/STS via `scservo_sdk`.
- `"dynamixel"` — Dynamixel X-series via the vendored `dynamixel_easy_sdk`.

Dynamixel-only fields: `operating_mode` (default `3`, POSITION), and
`profile_velocity` / `profile_acceleration` (default `0`, meaning max). They
are ignored by the Feetech backend. See the
[design contract](../knowledge/twist2-dynamixel-design.md) for the full model.
```

- [ ] **Step 3: Add a Dynamixel config example (English)**

In the Configuration section, alongside the existing Feetech example:

```json
{
  "port": "/dev/ttyUSB0",
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
  "pitch_step_sign": 1
}
```

- [ ] **Step 4: Add calibration notes (English)**

In the Servo Setup and Calibration section, add:

```markdown
The `openneck calibrate` procedure (logical center + safe range) works the same
for both backends because it only reads present positions. The
`openneck-calibrate-middle` tool is Feetech-specific (it writes the servo's
internal hardware midpoint). For Dynamixel, align the logical center with
`openneck calibrate`; set a hardware homing offset directly on the motor only if
you need the internal midpoint shifted (out of scope for this driver).
```

- [ ] **Step 5: Mirror the four additions in `docs/zh-CN/software.md`**

Translate the same four blocks to Chinese narrative with English identifiers/paths/config keys, preserving the same code blocks and links.

- [ ] **Step 6: Commit**

```bash
git add docs/en/software.md docs/zh-CN/software.md
git commit -m "docs: document Dynamixel backend, config, and calibration"
```

---

### Task 2: README clone hint and CLI help check

**Files:** `README.md` (optional); verify CLI.

- [ ] **Step 1: Add a submodule clone hint**

In `README.md` Getting Started (or Project Contents), add one line:

```markdown
Clone with `--recurse-submodules` so the Dynamixel SDK is fetched, or run `git submodule update --init --recursive` after cloning.
```

- [ ] **Step 2: Verify CLI surfaces the new flags**

Run: `python -c "import openneck.cli as c; c.build_parser().parse_args(['config','--help'])"` (or `openneck config --help`).
Expected: `--servo-backend`, `--operating-mode`, `--profile-velocity`, `--profile-acceleration` all appear.

- [ ] **Step 3: Commit + record**

```bash
git add README.md
git commit -m "docs: note submodule clone in README"
```
Record in `docs/progress/software/phase-5-docs-calibration.md`. Software component phases 1–5 are complete when all commits land and `pytest -q` is green.
