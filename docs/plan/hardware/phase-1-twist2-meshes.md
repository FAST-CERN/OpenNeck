# Hardware Phase 1: TWIST2 Mesh Conversion — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Establish the `hardware/twist2/` tree, bring in the TWIST2 NECK source CAD, and export the STLs needed for both 3D printing and simulation.

**Architecture:** TWIST2 keeps the OpenNeck 2-DoF yaw+pitch kinematics, so the mesh *set* mirrors the existing role-based names (`base_mount`, `yaw_horn`, `pitch_horn`, `pitch_mount`, `pitch_pivot`, `camera_mount`, …). CAD source goes under `cad/`, print STLs under `3d_prints/`, simulation STLs under `simulation/meshes/`. This phase produces files only; the URDF/MuJoCo that consume them is hardware phase 2.

**Tech Stack:** Any CAD tool that exports STEP/STL (Fusion 360, SolidWorks, FreeCAD); optional `trimesh` for STL sanity checks.

## Global Constraints

- Do not modify the original `hardware/` tree (Feetech design is preserved).
- Mesh filenames are lowercase, underscore-separated, role-based, and end in `.stl` (match the convention in `hardware/simulation/meshes/`).
- Each STL committed once; binary STL is fine. Keep source CAD under `cad/` (STEP preferred).
- Progress record: `docs/progress/hardware/phase-1-twist2-meshes.md`.

## File Structure

- Create dir: `hardware/twist2/cad/` — source CAD (STEP/STL) provided by the user.
- Create dir: `hardware/twist2/3d_prints/` — print-ready STLs.
- Create dir: `hardware/twist2/simulation/meshes/` — simulation visual (and optional collision) STLs.
- Create: `hardware/twist2/README.md` — what TWIST2 is, mesh inventory, source-of-truth link to the design contract.

---

### Task 1: Create the directory tree and README

- [ ] **Step 1: Create directories**

Run: `mkdir -p hardware/twist2/cad hardware/twist2/3d_prints hardware/twist2/simulation/meshes`

- [ ] **Step 2: Write `hardware/twist2/README.md`**

```markdown
# TWIST2 NECK hardware

TWIST2 NECK is the 2-DoF (yaw + pitch) mechanism adapted for the Dynamixel
build. Kinematics match OpenNeck; meshes and ranges differ.

- `cad/` — source CAD (STEP), authoritative geometry.
- `3d_prints/` — print-ready STLs.
- `simulation/meshes/` — STLs consumed by `simulation/twist2.urdf` / `twist2.xml`.

Mesh inventory (fill in as parts are exported):

| File | Role |
|---|---|
| `base_mount.stl` | base structure |
| `yaw_servo.stl` / `yaw_horn.stl` | yaw axis servo + horn |
| `pitch_servo.stl` / `pitch_horn.stl` | pitch axis servo + horn |
| `pitch_mount.stl` / `pitch_pivot.stl` | pitch structure |
| `camera_mount.stl` / `camera.stl` | camera payload |
| `adapter_board.stl` / `servo_controller.stl` | electronics (sim only) |

Design contract: [`../../docs/knowledge/twist2-dynamixel-design.md`](../../docs/knowledge/twist2-dynamixel-design.md).
```

- [ ] **Step 3: Commit the scaffold**

```bash
git add hardware/twist2/README.md
git commit -m "hw(twist2): add directory tree and mesh inventory"
```

---

### Task 2: Bring in source CAD and export STLs

- [ ] **Step 1: Place source CAD**

Copy the TWIST2 STEP (and any native CAD) files into `hardware/twist2/cad/`. At minimum one STEP representing the full assembly, or per-part STEPs.

- [ ] **Step 2: Export print STLs**

In the CAD tool, export each structural/printable part as binary STL into `hardware/twist2/3d_prints/` using the inventory names (e.g., `base_mount.stl`, `pitch_mount.stl`, `pitch_pivot.stl`, `camera_mount.stl`). Use the build orientation; no supports baked in.

- [ ] **Step 3: Export simulation STLs**

Export every part needed for the sim model into `hardware/twist2/simulation/meshes/` in the **assembly coordinate frame** (so meshes line up without per-mesh transforms). Include servos, horns, electronics for visual fidelity. For collision meshes, export simplified convex shapes with a `_collision` suffix if desired (optional).

- [ ] **Step 4: Verify STLs are non-empty**

Run:
```bash
python - <<'PY'
from pathlib import Path
meshes = sorted(Path("hardware/twist2/simulation/meshes").glob("*.stl"))
prints = sorted(Path("hardware/twist2/3d_prints").glob("*.stl"))
assert meshes, "no sim meshes exported"
for p in meshes + prints:
    assert p.stat().st_size > 1_000, f"{p} looks empty"
print(f"sim meshes: {len(meshes)}; print stls: {len(prints)}")
PY
```
Expected: counts > 0 and no "looks empty" assertion errors. (Optional: replace the size check with `trimesh.load(str(p))` if `trimesh` is installed, to confirm each is a valid mesh.)

- [ ] **Step 5: Commit CAD + STLs**

```bash
git add hardware/twist2/cad hardware/twist2/3d_prints hardware/twist2/simulation/meshes
git commit -m "hw(twist2): add source CAD and exported print/sim STLs"
```

- [ ] **Step 6: Record progress**

Append to `docs/progress/hardware/phase-1-twist2-meshes.md`: the part list actually exported, any deviations from the inventory, the measured raw yaw/pitch step ranges observed on the mechanism (input to hardware phase 2's joint limits and to software calibration — open item **R3**).
