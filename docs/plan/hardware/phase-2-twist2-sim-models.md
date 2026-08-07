# Hardware Phase 2: TWIST2 Simulation Models — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Produce `twist2.urdf` and `twist2.xml` (MuJoCo) that reuse the OpenNeck yaw+pitch kinematic template but consume the TWIST2 meshes and the measured joint ranges.

**Architecture:** Copy `hardware/simulation/openneck.urdf` and `openneck.xml` into `hardware/twist2/simulation/`, then edit mesh asset paths to the TWIST2 STLs and set the yaw/pitch joint limits from the values measured in hardware phase 1 (open item **R3**). The body hierarchy (`yaw_horn_link` → `pitch_horn_link`) and joint axes are unchanged because the kinematics match.

**Tech Stack:** URDF, MuJoCo MJCF, optional `mujoco` Python package for a load smoke test.

## Global Constraints

- Do not modify the original `hardware/simulation/openneck.{urdf,xml}` (Feetech design preserved).
- Keep mesh asset `name=` values stable so existing `<geom mesh=...>` references stay valid; only the `file=` paths change.
- Joint ranges come from the R3 measurement; do not invent them. If unavailable, use the OpenNeck defaults (`-1.5708 1.5708` rad) and flag for update.
- Progress record: `docs/progress/hardware/phase-2-twist2-sim-models.md`.

## File Structure

- Create: `hardware/twist2/simulation/twist2.urdf` (adapted from `openneck.urdf`).
- Create: `hardware/twist2/simulation/twist2.xml` (adapted from `openneck.xml`).

---

### Task 1: Create `twist2.xml` (MuJoCo)

- [ ] **Step 1: Copy and relocate**

Run: `cp hardware/simulation/openneck.xml hardware/twist2/simulation/twist2.xml`

- [ ] **Step 2: Repoint mesh assets**

In `hardware/twist2/simulation/twist2.xml`, for every `<mesh ... file="meshes/<name>.stl" .../>`, change `<name>.stl` to the matching TWIST2 STL produced in hardware phase 1. Meshes live in the same relative location (`meshes/`), so the `meshes/` prefix stays; only filenames change. Keep each `name=` attribute unchanged.

- [ ] **Step 3: Set joint ranges from R3**

Find the `yaw_joint` and `pitch_joint` elements. Set each `range="lo hi"` to the radian equivalents of the measured safe range from hardware phase 1 (e.g., if yaw is ±90°, keep `range="-1.5708 1.5708"`). Leave the `axis` values unchanged.

- [ ] **Step 4: Verify referenced meshes exist**

Run:
```bash
python - <<'PY'
import re
from pathlib import Path
xml = Path("hardware/twist2/simulation/twist2.xml").read_text(encoding="utf-8")
base = Path("hardware/twist2/simulation")
missing = []
for m in re.finditer(r'file="([^"]+\.stl)"', xml):
    p = base / m.group(1)
    if not p.exists():
        missing.append(str(p))
assert not missing, f"missing meshes: {missing}"
print("twist2.xml: all mesh references resolve")
PY
```
Expected: `twist2.xml: all mesh references resolve`.

- [ ] **Step 5: Commit**

```bash
git add hardware/twist2/simulation/twist2.xml
git commit -m "hw(twist2): add MuJoCo model from TWIST2 meshes"
```

---

### Task 2: Create `twist2.urdf` and optional MuJoCo load smoke

- [ ] **Step 1: Copy and edit**

Run: `cp hardware/simulation/openneck.urdf hardware/twist2/simulation/twist2.urdf`

In `twist2.urdf`, repoint every `<mesh filename="...">` to the matching TWIST2 STL (mirror the path style used by `openneck.urdf` — typically relative `../meshes/<name>.stl` or `package://...`; adjust the filename only). Update the yaw/pitch joint `<limit lower="..." upper="..."/>` to the R3 radian values.

- [ ] **Step 2: Verify URDF mesh references**

Run:
```bash
python - <<'PY'
import re
from pathlib import Path
urdf = Path("hardware/twist2/simulation/twist2.urdf").read_text(encoding="utf-8")
base = Path("hardware/twist2/simulation")
missing = []
for m in re.finditer(r'filename="([^"]+\.stl)"', urdf):
    ref = m.group(1).replace("package://openneck/", "")
    p = (base / ref).resolve()
    if not p.exists():
        missing.append(str(p))
assert not missing, f"missing meshes: {missing}"
print("twist2.urdf: all mesh references resolve")
PY
```
Expected: `twist2.urdf: all mesh references resolve`. (If `openneck.urdf` uses a different path scheme, adjust the `replace(...)` normalization accordingly and re-run.)

- [ ] **Step 3: Optional MuJoCo load smoke**

If `mujoco` is installed:
```bash
python -c "import mujoco; mujoco.MjModel.from_xml_path('hardware/twist2/simulation/twist2.xml'); print('mujoco load ok')"
```
Expected: `mujoco load ok`. If `mujoco` is not installed, skip and note it in the progress record.

- [ ] **Step 4: Commit + record**

```bash
git add hardware/twist2/simulation/twist2.urdf
git commit -m "hw(twist2): add URDF model from TWIST2 meshes"
```
Record in `docs/progress/hardware/phase-2-twist2-sim-models.md`: the final yaw/pitch joint limits applied, mesh count, and the MuJoCo load result. Hardware component phases 1–2 are complete when both sim models parse and all meshes resolve.
