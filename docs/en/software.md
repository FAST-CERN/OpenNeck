# OpenNeck Software Driver

[Home](../../README.md) · [Software](./software.md) · [Hardware](./hardware.md) · [Assembly](./assembly.md) · **English** · [中文](../zh-CN/software.md)

The OpenNeck software driver converts target angles into servo positions and applies the calibrated mechanical limits. The main control API accepts only angles relative to the mechanical center:

- `yaw_deg = 0`: straight ahead
- `yaw_deg > 0`: left
- `yaw_deg < 0`: right
- `pitch_deg = 0`: level
- `pitch_deg > 0`: up
- `pitch_deg < 0`: down

Teleopit converts human poses into robot target angles; OpenNeck only executes those target angles.

## Installation

```bash
pip install .
```

### Dynamixel backend (optional)

The Dynamixel backend uses the vendored ROBOTIS SDK, included as a git
submodule. Install it editable after cloning with submodules:

```bash
git clone --recurse-submodules <repo>
pip install .
pip install -e thirdparty/DynamixelSDK/python
```

If the current Linux user does not have serial-port permission:

```bash
sudo usermod -a -G dialout $USER
```

Log in again for the change to take effect. For temporary testing, you can use:

```bash
sudo chmod 666 /dev/ttyACM0
```

## Servo Setup and Calibration

Complete the [mechanical assembly](./assembly.md) first. The following steps assign servo IDs, set the center, and calibrate the safe motion range.

1. With the gimbal powered off, confirm that it moves by hand through a safe range without binding, hitting a limit, or pulling a cable.

2. Find the serial port:

```bash
openneck ports
export OPENNECK_PORT=/dev/ttyACM0
```

3. Connect only the yaw servo and assign ID 1:

```bash
openneck-change-servo-id --port "$OPENNECK_PORT" --new-id 1
```

4. Connect only the pitch servo and assign ID 2:

```bash
openneck-change-servo-id --port "$OPENNECK_PORT" --new-id 2
```

5. Connect both servos and check their IDs and voltage:

```bash
openneck-scan-servos --port "$OPENNECK_PORT"
```

6. Move both axes to their mechanical centers and write 2048 as the internal servo midpoint:

```bash
openneck-calibrate-middle --port "$OPENNECK_PORT" --ids 1 2
```

7. Calibrate OpenNeck's logical center and safe mechanical range, specifying the signs for the installation direction:

```bash
openneck calibrate \
  --port "$OPENNECK_PORT" \
  --yaw-step-sign 1 \
  --pitch-step-sign 1
```

This command writes the result to `active_vision_config.json`. Raw position reads and writes are available only through these package-internal maintenance and calibration tools.

8. Return to center and verify both axes with small movements:

```bash
openneck center --port "$OPENNECK_PORT" --hold-s 2
openneck test yaw --port "$OPENNECK_PORT" --angle-deg 5
openneck test pitch --port "$OPENNECK_PORT" --angle-deg 5
```

The `openneck calibrate` procedure (logical center + safe range) works the same
for both backends because it only reads present positions. The
`openneck-calibrate-middle` tool is Feetech-specific (it writes the servo's
internal hardware midpoint). For Dynamixel, align the logical center with
`openneck calibrate`; set a hardware homing offset directly on the motor only if
you need the internal midpoint shifted (out of scope for this driver).

## Configuration

By default, OpenNeck reads `active_vision_config.json` from the current directory. You can also specify another file through the API or CLI:

```json
{
  "port": "/dev/ttyACM0",
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
  "acceleration": 0
}
```

For a Dynamixel build, select the backend and set the Dynamixel-only fields
(defaults shown; `profile_velocity` / `profile_acceleration` of `0` mean max):

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

`yaw_step_sign` and `pitch_step_sign` accept only `1` or `-1`:

- Use `1` when a positive logical angle increases the servo step value.
- Use `-1` when a positive logical angle decreases the servo step value.

These two fields fully represent the mechanical installation direction, so upper-level callers always use the same left-positive and up-positive convention. A configuration containing unknown fields raises an error so that invalid settings are not silently accepted.

When upgrading from `0.1.x`, run `openneck calibrate` again. The normalized-amplitude and pose-inversion fields in an old configuration cannot safely determine the new physical angle directions, so `0.2.x` does not convert them automatically. Back up or move the old file first, then set both `*_step_sign` fields for the actual installation direction.

## Servo backend

OpenNeck supports two servo families, selected by the `servo_backend` field:

- `"feetech"` (default) — Feetech SCS/STS via `scservo_sdk`.
- `"dynamixel"` — Dynamixel X-series via the vendored `dynamixel_easy_sdk`.

Dynamixel-only fields: `operating_mode` (default `3`, POSITION);
`profile_velocity` / `profile_acceleration` (default `0` = leave the servo
untouched); and per-axis Position PID gains `yaw_kp` / `yaw_ki` / `yaw_kd` /
`pitch_kp` / `pitch_ki` / `pitch_kd` (default `0` = untouched). They are
ignored by the Feetech backend. See the
[design contract](../knowledge/twist2-dynamixel-design.md) for the full model.

## Other Commands

```bash
openneck config
openneck voltage --port "$OPENNECK_PORT"
```

`openneck-calibrate-middle` changes the servo's internal nonvolatile hardware midpoint; `openneck calibrate` only updates OpenNeck's JSON runtime configuration.

## Python API

The package root exposes only `NeckAngles` and `OpenNeckController`:

```python
from openneck import OpenNeckController

with OpenNeckController(
    config="active_vision_config.json",
    port="/dev/ttyACM0",
) as neck:
    applied = neck.move_deg(yaw_deg=30.0, pitch_deg=-15.0)
    print(applied)
    print(neck.read_deg())
    print(neck.read_voltage())
```

`move_deg()` returns the actual target angle after mechanical-limit clipping and integer servo-step quantization. It represents the target that was sent, not a position reading; call `read_deg()` when you need the current position.

Without a context manager, manage the connection explicitly:

```python
from openneck import OpenNeckController

neck = OpenNeckController(port="/dev/ttyACM0")
try:
    neck.connect()
    neck.center()
    neck.move_deg(yaw_deg=-20.0, pitch_deg=10.0)
    neck.release_torque()
finally:
    neck.close()
```

`close()` only closes the serial port and does not change the current torque state. Call `release_torque()` explicitly when the holding force should be released.
