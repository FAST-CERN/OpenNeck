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

## Task 2：真机冒烟（待操作员/硬件，未自动执行）

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

## 状态

- Task 1（离线）：✅ 完成。
- Task 2（真机）：⏳ 待硬件/操作员。
