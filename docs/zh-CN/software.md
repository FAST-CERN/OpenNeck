# OpenNeck 软件驱动

[主页](../../README.md) · [软件](./software.md) · [硬件](./hardware.md) · [装配](./assembly.md) · [部署](./deployment-teleopit.md) · [迁移](./migration-from-upstream.md) · [English](../en/software.md) · **中文**

## 目录

- [安装](#安装) — `pip install .` / Dynamixel extra
- [舵机设置与标定](#舵机设置与标定) — 分配 ID、中位、安全范围
- [配置](#配置) — 配置 schema、`*_step_sign`、升级说明
- [舵机后端](#舵机后端) — Feetech 与 Dynamixel
- [其他命令](#其他命令) — `config`、`voltage`、CLI flags
- [Python API](#python-api) — `OpenNeckController`、`move_deg`

OpenNeck 软件驱动负责把目标角度转换为舵机位置，并执行标定后的机械限位。主要控制 API 只接受相对机械中位的角度：

- `yaw_deg = 0`：正前方
- `yaw_deg > 0`：向左
- `yaw_deg < 0`：向右
- `pitch_deg = 0`：水平
- `pitch_deg > 0`：向上
- `pitch_deg < 0`：向下

Teleopit 负责把人体姿态转换为机器人目标角度；OpenNeck 只负责执行目标角度。

## 安装

```bash
pip install .
```

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

Linux 没有串口权限时：

```bash
sudo usermod -a -G dialout $USER
```

重新登录后生效。临时调试可以使用：

```bash
sudo chmod 666 /dev/ttyACM0
```

将 OpenNeck 部署到既有环境（如 `teleopit`）见[部署](./deployment-teleopit.md)。

## 舵机设置与标定

机械部分先按[机械装配](./assembly.md)完成。以下步骤用于设置舵机 ID、中位和安全活动范围。

1. 确认云台断电时能在安全范围内手动活动，没有卡死、撞限位或拉线。

2. 查找串口：

```bash
openneck ports
export OPENNECK_PORT=/dev/ttyACM0
```

3. 只连接 yaw 电机并设置 ID 为 1：

```bash
openneck-change-servo-id --port "$OPENNECK_PORT" --new-id 1
```

4. 只连接 pitch 电机并设置 ID 为 2：

```bash
openneck-change-servo-id --port "$OPENNECK_PORT" --new-id 2
```

5. 同时连接两个电机并检查 ID 与电压：

```bash
openneck-scan-servos --port "$OPENNECK_PORT"
```

6. 将两个轴摆到硬件中位并写入舵机内部的 2048 中位：

```bash
openneck-calibrate-middle --port "$OPENNECK_PORT" --ids 1 2
```

7. 标定 OpenNeck 的逻辑中位和安全机械范围，并按安装方向指定符号：

```bash
openneck calibrate \
  --port "$OPENNECK_PORT" \
  --yaw-step-sign 1 \
  --pitch-step-sign 1
```

该命令把结果写入 `active_vision_config.json`。原始位置读写只存在于这些包内维护与标定工具中。

8. 回中并做小角度验证：

```bash
openneck center --port "$OPENNECK_PORT" --hold-s 2
openneck test yaw --port "$OPENNECK_PORT" --angle-deg 5
openneck test pitch --port "$OPENNECK_PORT" --angle-deg 5
```

`openneck calibrate` 流程（逻辑中位 + 安全范围）对两种后端都一样，因为它只读取当前位置。`openneck-calibrate-middle` 工具仅适用于 Feetech（它写入舵机内部的硬件中位）。Dynamixel 请用 `openneck calibrate` 对齐逻辑中位；如需平移内部中位，请直接在电机上设置硬件 homing offset（超出本驱动范围）。

## 配置

默认从当前目录的 `active_vision_config.json` 读取配置，也可以在 API 或 CLI 中指定其他文件：

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

Dynamixel 构建请选择后端并设置 Dynamixel 专属字段（以下为默认值；`profile_velocity` / `profile_acceleration` 为 `0` 表示最大）：

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

按你的硬件选择对应模板——`active_vision_config.feetech.example.json` 或 `active_vision_config.dynamixel.example.json`——复制为 `active_vision_config.json`，再按实际安装修改 `port`、舵机 ID 与 `*_step_sign`。标定步进值（`*_center_step` / `*_min_step` / `*_max_step`）为安全默认；请在真实机构上运行 `openneck calibrate` 重新记录。

`yaw_step_sign` 和 `pitch_step_sign` 只允许为 `1` 或 `-1`：

- 逻辑正角度使舵机 step 增大时填 `1`。
- 逻辑正角度使舵机 step 减小时填 `-1`。

机械安装方向完全由这两个字段吸收，上层调用始终使用相同的左正、上正约定。配置包含未知字段时会直接报错，避免错误配置被静默接受。

从 `0.1.x` 升级时需要重新运行 `openneck calibrate`。旧配置中的归一化幅度和姿态反向字段不能安全推导新的物理角度方向，因此当前版本（`0.3.0`）不会自动转换旧配置；请先备份或移走旧文件，再按实际安装方向设置两个 `*_step_sign` 字段。

从 `0.2.x` 升级到 `0.3.0` 无需改动配置——schema 为增量扩展（新增的 `servo_backend` / `operating_mode` / `profile_*` / `*_kp,ki,kd` 字段均为可选），且 `yaw_id` / `pitch_id` 现在接受 `0`。若要使用 Dynamixel，设置 `servo_backend` 并安装 `dynamixel` extra。完整的 API/配置/CLI 变化清单见[从上游升级](./migration-from-upstream.md)。

## 舵机后端

OpenNeck 支持两类舵机，由 `servo_backend` 字段选择：

- `"feetech"`（默认）—— 经 `scservo_sdk` 驱动 Feetech SCS/STS。
- `"dynamixel"` —— 经内置 `dynamixel_easy_sdk` 驱动 Dynamixel X 系列。

Dynamixel 专属字段：`operating_mode`（默认 `3`，POSITION）；`profile_velocity` / `profile_acceleration`（默认 `0` = 不写入，保留舵机值）；以及 per-axis 位置 PID `yaw_kp`/`yaw_ki`/`yaw_kd`/`pitch_kp`/`pitch_ki`/`pitch_kd`（默认 `0` = 不写入）。Feetech 后端忽略它们。完整模型见[设计合同](../knowledge/twist2-dynamixel-design.md)。

## 其他命令

```bash
openneck config
openneck voltage --port "$OPENNECK_PORT"
```

`openneck-calibrate-middle` 修改舵机内部的非易失硬件中位；`openneck calibrate` 只更新 OpenNeck 的 JSON 运行配置。

每个配置字段都可在命令行用 `--<字段名>` 覆盖（下划线转连字符），例如 `--port`、`--yaw-id`、`--servo-backend`。`0.3.0` 新增的 flag 与新配置字段一一对应：`--servo-backend {feetech,dynamixel}`、`--operating-mode {0,1,3,4,5,16}`、`--profile-velocity`、`--profile-acceleration`，以及 per-axis PID `--yaw-kp/ki/kd` / `--pitch-kp/ki/kd`。默认均不设置，故既有命令行行为不变。完整列表见[从上游升级](./migration-from-upstream.md#cli-变化)。

## Python API

包根目录只公开 `NeckAngles` 和 `OpenNeckController`：

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

`move_deg()` 返回经过机械限位裁剪和舵机整数 step 量化后的实际目标角度。它表示已发送的目标，不是位置回读；需要当前位置时调用 `read_deg()`。

不使用上下文管理器时，可以显式管理连接：

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

`close()` 只关闭串口，不改变当前扭矩状态；需要释放保持力时应显式调用 `release_torque()`。
