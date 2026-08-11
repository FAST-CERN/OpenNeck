# software phase-4-sdk-wiring 进度

[计划](../../plan/software/phase-4-sdk-wiring.md) · [状态](../../STATUS.md) · [设计合同](../../knowledge/twist2-dynamixel-design.md)

执行方式：环境接线 + 真机冒烟。分支 `feat/phase4-sdk-wiring`，基线 1347897（已并入 fork `FAST-CERN/OpenNeck:main`）。

> 本阶段无生产代码改动（驱动代码 phase-3 已完成）；仅环境安装 + 真机验证。

## Task 1：离线接线（已完成 2026-08-10）

| 步骤 | 命令 | 结果 |
|---|---|---|
| 子模块就位 | `git submodule status thirdparty/DynamixelSDK` | `2ded684... (4.0.5)`，无 `+`/`-` |
| 可编辑安装 | `python -m pip install -e thirdparty/DynamixelSDK/python --no-build-isolation` | `Successfully installed dynamixel-sdk-4.0.5 pyserial-3.5` |
| 导入冒烟 | `python -c "import dynamixel_sdk; from dynamixel_easy_sdk import Connector, Motor, GroupExecutor, OperatingMode; from dynamixel_easy_sdk.control_table import ControlTable; ..."` | `import ok`；`OperatingMode.POSITION = 3` |
| 单测回归 | `pytest -q` | **36 passed**（测试注入 fake，真 SDK 安装不影响） |

**R4（闭环）**：vendored SDK 包 `dynamixel-sdk` v4.0.5，setuptools 构建后端，`package-dir = src`，含 `control_table/*.model` 数据。可编辑安装即暴露 `dynamixel_sdk` + `dynamixel_easy_sdk`。

**偏离**：计划用裸 `pip install -e ...`，构建隔离会从 PyPI 拉 setuptools/wheel，受本机代理故障影响。环境已具备 setuptools 80.9 / wheel 0.45，故加 `--no-build-isolation` 规避网络跳，行为等价。

**对 phase-3 的回溯验证**：真 SDK 的 `OperatingMode.POSITION == 3`，与 phase-3 fake 的 `IntEnum` 取值一致——fake 忠实反映了真 API。

## Task 2 前置：G1 代码修复（2026-08-11）

真机配置（见 [`knowledge/twist2-servo-config.md`](../../knowledge/twist2-servo-config.md)）暴露 yaw_id=0，而 `Config` 校验 `yaw_id`/`pitch_id` `minimum=1` 拒绝 ID 0（G1）。

- 改动：`openneck/_config.py` 把 `yaw_id`/`pitch_id` 下限 `1` → `0`（`maximum=253` 不变；Dynamixel ID 0..252 合法，Feetech 同样适用）。
- TDD：`tests/test_config.py::test_servo_id_zero_is_allowed`（RED `yaw_id must be 1..253, got 0` → GREEN）。
- `pytest -q` → 37 passed。
- 提交 `e125512`。

其余 gap（G2 profile 未应用 / G3 acc 取整 / G4 PID 不管理）smoke 阶段先用舵机 EEPROM 现值绕过，跑通后再决定是否扩展。

## Task 2：真机冒烟（已完成 2026-08-11）

> **前置**：TWIST2（或任意 Dynamixel X 系列）云台接在总线上；双舵机 ID 与配置一致；操作员在场。AGENTS.md 规则 5：首次仅 center，再 ≤5° 小幅运动。

**Runbook：**

1. 工作目录建 `active_vision_config.json`（已 gitignore）：
   ```json
   {
     "port": "COM3", "baudrate": 57600, "servo_backend": "dynamixel",
     "operating_mode": 3, "yaw_id": 1, "pitch_id": 2,
     "yaw_center_step": 2048, "yaw_min_step": 1024, "yaw_max_step": 3072, "yaw_step_sign": 1,
     "pitch_center_step": 2048, "pitch_min_step": 1365, "pitch_max_step": 2731, "pitch_step_sign": 1,
     "profile_velocity": 0, "profile_acceleration": 0
   }
   ```
   按实际硬件调整 `port`/`baudrate`/ID/sign。

2. `openneck voltage` —— 不使能力矩下读电压 + 角度。**闭环 R2**（目标型号电压 item key）+ R1（ping/控制表）。
3. `openneck center --hold-s 2 && openneck test yaw --angle-deg 5` —— 回中后 yaw ±5°。验证 `setOperatingMode` + `GroupExecutor` 真机写入。

**完成后在此追加**：实际 port/baudrate/型号、电压读数、center/test 是否正常、任何报错；最终闭环 **R1**（型号控制表可用）与 **R2**（电压 key 可用）。

**实际结果（2026-08-11，操作员在场）：**

- 硬件：Dynamixel **XC330-T288** ×2（model_number 1220），ID 0=yaw / 1=pitch；总线 COM3 @57600；独立供电。
- 只读扫描 `Connector.broadcastPing()` → 发现 ID {0,1}，`model_name` 解析为 `xc330_t288` → easy_sdk 收录该型号控制表，**R1 闭环**。
- `openneck voltage`（不使能力矩）→ yaw 12.6V / pitch 12.5V，角度 yaw -3.52° / pitch -0.62°。`Present Input Voltage` 读取成功，**R2 闭环**。
- `openneck center --hold-s 2` → 使能力矩 + 写目标 (0,0)，pitch 回到 0°；yaw 稳态偏 -1.93°（≈22 step，舵机/机械侧 POSITION 模式带载稳态误差，非软件 bug，操作员确认可接受）。
- `openneck test yaw --angle-deg 5` → 发送 +5.01° / -5.01° / 0° 目标，`yaw_step_sign=1` 方向一致、运动平顺，操作员确认物理方向正确。
- 整条链路（`connect`/ping/位置读写/电压/`GroupExecutor` 同步写/`center`/`test`）在真机 XC330-T288 上可用；`setOperatingMode(POSITION)` 与未使能力矩行为符合预期。
- 遗留（非阻塞）：yaw ~1.93° 稳态偏差，属舵机 PID/机械特性；profile/PID 用 EEPROM 现值（G2/G4 延后）。

## 状态

- Task 1（离线）：✅ 完成。
- Task 2（真机）：✅ 完成（2026-08-11，XC330-T288）。**R1/R2 闭环**。

## 配套工具：`scripts/test_limits.py`（2026-08-11）

机械限位测试脚本，诞生于真机 smoke 阶段。两段式：

- **离线裁剪验证**（默认运行，不连硬件）：`openneck._angles.angle_to_step` 对 ±360° 超限请求应裁到 `min_step`/`max_step`。已跑通：yaw 端点 `{2616, 3754}`、pitch 端点 `{1251, 2389}`，全 PASS。
- **真机渐进逼近**（`--real`，操作员在场）：对 yaw ±50°、pitch -10°/+90° 按 30/60/90/100% 渐进，每步 `input()` 人工门（Enter 继续 / Ctrl-C 中止并 `release_torque`）。

真机段为交互式（人工安全门），需操作员在终端 `python scripts/test_limits.py --real` 自跑；非交互环境（如 AI agent 的 Bash）会在首个 `input()` 收到 EOF 退出。
