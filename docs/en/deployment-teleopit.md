# Deploying OpenNeck into an existing environment (e.g. `teleopit`)

[Home](../../README.md) · [Software](./software.md) · [Hardware](./hardware.md) · [Assembly](./assembly.md) · [Deployment](./deployment-teleopit.md) · [Migration](./migration-from-upstream.md) · **English** · [中文](../zh-CN/deployment-teleopit.md)

## Contents

- [Why this guide exists](#why-this-guide-exists)
- [Step 0 — Confirm the target interpreter](#step-0--confirm-the-target-interpreter)
- [Step 1 — Get the code with the Dynamixel submodule](#step-1--get-the-code-with-the-dynamixel-submodule)
- [Step 2 — Install the package](#step-2--install-the-package)
- [Step 3 — Migrate the runtime config](#step-3--migrate-the-runtime-config)
- [Step 4 — Verify on real hardware](#step-4--verify-on-real-hardware)
- [Integration patterns](#integration-patterns)
- [Troubleshooting](#troubleshooting)
- [Reference](#reference)

A migration runbook for installing this OpenNeck build (`0.3.0`, with the
optional Dynamixel backend) into a Python environment you already run — for
example the `teleopit` conda env. It covers fresh installs and upgrades, on
both Linux and Windows.

For the full config-field reference and the calibration workflow, see
[`software.md`](software.md). This guide only links to those values; it does
not repeat them.

---

## Why this guide exists

`pip install` does **not** carry OpenNeck's runtime parameters. The config
file `active_vision_config.json` is gitignored and resolved relative to your
**current working directory** at runtime, not the install location. So
migrating OpenNeck into a new environment is three independent concerns:

| # | What | Travels with `pip install`? |
|---|------|------------------------------|
| 1 | The Python package (with your backend changes) | yes — from the repo |
| 2 | The Dynamixel SDK (for `servo_backend: "dynamixel"`) | only if you install the `dynamixel` extra |
| 3 | The runtime config `active_vision_config.json` | **no** — you migrate it by hand |

## Step 0 — Confirm the target interpreter

OpenNeck and the SDK must land in **the same interpreter that imports
`openneck`**. A bare `pip` often binds to a different env. Always use
`python -m pip` after activating the target env.

```bash
# Activate your env first, e.g.:
conda activate teleopit          # conda
# or:  source .venv/bin/activate   # Linux venv
# or:  .venv\Scripts\activate      # Windows venv / cmd
# or:  .venv\Scripts\Activate.ps1  # Windows PowerShell

# Confirm THIS is the interpreter teleopit will use:
python -c "import sys; print(sys.executable); print(sys.prefix)"
```

On Windows, `where python` (cmd) or `Get-Command python` (PowerShell) lists
every `python` on `PATH` — make sure the first entry is inside the target env.

## Step 1 — Get the code with the Dynamixel submodule

```bash
# Fresh clone (the SDK is a submodule — --recurse-submodules is required):
git clone --recurse-submodules <repo>
cd OpenNeck

# Already cloned? Make sure the submodule is present and up to date:
git submodule update --init --recursive

# Upgrading an existing checkout to this build:
git pull
git submodule update --recursive
```

## Step 2 — Install the package

Install with the interpreter confirmed in Step 0:

```bash
# Feetech only (pulls pyserial + ftservo-python-sdk automatically):
python -m pip install .

# Dynamixel build — one command, pulls the vendored SDK too:
python -m pip install ".[dynamixel]"

# Editable / development install:
python -m pip install -e .
python -m pip install -e thirdparty/DynamixelSDK/python   # SDK editable
```

`".[dynamixel]"` is quoted so the brackets are not globbed by your shell;
this form is safe on both POSIX shells and Windows cmd.

**Behind a proxy?** If pip's build isolation cannot reach PyPI, add
`--no-build-isolation` (the host env must already have `setuptools` + `wheel`).

**Linux serial permission** (robot host): add your user to the dialout group
and re-login, or install a udev rule:

```bash
sudo usermod -aG dialout "$USER"   # then log out and back in
```

**Verify the install:**

```bash
python -c "import openneck; print(openneck.__version__)"      # -> 0.3.0
# Dynamixel build only:
python -c "from dynamixel_easy_sdk import Connector; print('sdk ok')"
```

## Step 3 — Migrate the runtime config

Copy whichever template matches your hardware, then edit it:

```bash
# Linux / macOS:
cp active_vision_config.dynamixel.example.json active_vision_config.json
# Windows cmd:
copy active_vision_config.dynamixel.example.json active_vision_config.json
# Windows PowerShell:
Copy-Item active_vision_config.dynamixel.example.json active_vision_config.json
```

Then distinguish two kinds of fields inside the file:

- **Reusable across machines** (same hardware assembly) — copy as-is:
  `servo_backend`, `baudrate`, `yaw_id`, `pitch_id`, `yaw_step_sign`,
  `pitch_step_sign`, `operating_mode`, `profile_velocity`,
  `profile_acceleration`, `yaw_kp`/`ki`/`kd`, `pitch_kp`/`ki`/`kd`.
- **Mechanism-specific** — these come from calibrating *that physical unit*;
  do **not** trust copied values across necks:
  `yaw_center_step`, `yaw_min_step`, `yaw_max_step`, `pitch_center_step`,
  `pitch_min_step`, `pitch_max_step`. Re-run, against the actual mechanism:

  ```bash
  openneck calibrate --port /dev/ttyUSB0      # Linux
  openneck calibrate --port COM3              # Windows
  ```

**Where the file must live:** the default loader reads
`./active_vision_config.json` relative to the host program's **current working
directory**. If `teleopit` does not run from a fixed CWD, prefer one of the
explicit patterns in [Integration patterns](#integration-patterns) instead of
relying on CWD.

> Upgrading from 0.1.x? The old normalized-amplitude fields cannot be
> converted to the current angle-direction system (`0.3.0`); run
> `openneck calibrate` again. See [`software.md`](software.md).

## Step 4 — Verify on real hardware

With the env activated (so the `openneck` console script is on `PATH`):

```bash
openneck config                       # prints the loaded config
openneck ports                        # lists serial ports
openneck voltage --port /dev/ttyUSB0  # non-motion smoke test: voltage + angles
```

`openneck voltage` does not move the mechanism, so it is a safe first check
on hardware.

## Integration patterns

How `teleopit` (or any host) consumes OpenNeck. The public API is
`OpenNeckController`; backend selection is the only thing that differs.

```python
from openneck import OpenNeckController

# Pattern A — JSON file in the host program's CWD (default lookup path):
with OpenNeckController(port="/dev/ttyUSB0") as neck:
    neck.center()
    neck.move_deg(5.0, 0.0)

# Pattern B — explicit config path (does not depend on CWD):
with OpenNeckController(
    config="/etc/openneck/active_vision_config.json",
    port="/dev/ttyUSB0",
) as neck:
    neck.move_deg(5.0, 0.0)

# Pattern C — code-only, no JSON file at all (backend selected in code):
with OpenNeckController(
    servo_backend="dynamixel",
    baudrate=57600,
    port="/dev/ttyUSB0",
) as neck:
    neck.center()
```

`servo_backend`, `baudrate`, and `operating_mode` are keyword-only overrides;
invalid values raise via the same validation as the config file. Deeper
fields (PID gains, profile velocity/acceleration) stay in the JSON.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `import openneck` still loads an old version | Wrong interpreter. Re-check `sys.executable`, then reinstall with `python -m pip install ...` in that env. |
| `ModuleNotFoundError: dynamixel_easy_sdk` | You installed Feetech-only. Reinstall with `python -m pip install ".[dynamixel]"`. |
| `PermissionError` opening the serial port (Linux) | User not in `dialout` group (see Step 2), or the port is held by another process. |
| pip fails to fetch setuptools/wheel behind a proxy | Add `--no-build-isolation` (host env must already have `setuptools` + `wheel`). |
| Mechanism points the wrong way / angles off after migrating | The copied calibration steps do not match this unit. Re-run `openneck calibrate`. |
| `active_vision_config.json` "not found" | The host runs from a CWD with no config file. Use Pattern B (explicit path) or Pattern C (code-only). |

## Reference

- Install + full config-field reference + calibration: [`software.md`](software.md)
- Why the config is CWD-relative and how override/backend selection works:
  [`../knowledge/config-dataflow.md`](../knowledge/config-dataflow.md)
- TWIST2 servo hardware values (IDs, centers, limits): [`../knowledge/twist2-servo-config.md`](../knowledge/twist2-servo-config.md)
