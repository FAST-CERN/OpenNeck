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

**真机渐进结果（2026-08-11，操作员终端跑 `--real`）：**

- 软件侧全对：离线裁剪 PASS；每步 `applied ≈ target`（量化误差 ≤0.03°），裁剪与发送正确。
- readback 解读：脚本 `move → 立即 read` + 每步 `input()` 间歇，使 `readback` 反映**上一步目标的稳态**（最后 @100 档的稳态未读到）。
- 关键发现：**yaw 正向物理极限 ~+30°**——@60%（30°）稳态能到 28.92°，@90%（45°）卡在 28.92°（写 45° 到不了）；远小于声明的 +50°。yaw 负向 -45° 能到（-43.77°）。pitch 正向 +81° 能到（+90° 本次未确认），负向 -9° 能到（-8.17°）。
- 结论：配置里基于声明角度换算的 `max_step`（yaw +50°/pitch +90°）超出真机正向可达范围（负向基本可达）。需 `openneck calibrate` 真机标定物理量程，或查 yaw 正向机械干涉/动力。
- 脚本可改进：`move` 后加 settle 延时再 `read`，直测每个 target 的稳态（当前 readback 滞后一步）；末档 @100 之后补一次延时 read 以测极限稳态。

**根因闭环（systematic-debugging，2026-08-11）：** 上面"yaw 正向物理极限 ~+30°"是**误判**（Wizard 确认可达 3640）。真因两层：

1. **center 换算偏**：声明零位 280° 不准，真机中位约 270°。改 `yaw_center_step`=3072（270°）后 ±25°、+33°、+42°、-50° 全部到位。
2. **`max_step` 超舵机 `Max Position Limit`**：yaw `Max Position Limit`=3640，而 +50° 从 270° 算到 step **3641**（超 1 step）。舵机对 `Goal Position` 3641 返回 `Data Limit Error`（easy_sdk 单包 `Motor.setGoalPosition` 抛 `SDK_ERRNUM_DATA_LIMIT(6): data value exceeds the limit`）。
3. **OpenNeck 静默缺陷（G5）**：`DynamixelBackend.write_positions` 用 `GroupSyncWrite`，协议不收集 per-device 错误，超限写入**静默失败**（舵机不动、不报错）——这是之前"看似卡 3528/29°"的真象。

修复：`yaw_center_step` 3185→3072、`yaw_max_step` 3641→3640（`yaw_min_step` 2503 = `Min Position Limit` 不变）。验证：写 3640 到 3619（Δ-21）、2503 到 2522（Δ+19），**yaw ±50° 双向可达**。详见 [`knowledge/twist2-servo-config.md`](../../knowledge/twist2-servo-config.md)；G5 进 [`todo/todolist.md`](../todo/todolist.md)。脚本已加 `settle_read`（move 后轮询 read_deg 到收敛）。

**G5 修复（2026-08-11，提交 a8e41ef）：** `DynamixelBackend.connect` 现读取并缓存每个 motor 的 `Max/Min Position Limit`；`write_positions` 写前校验 target ∈ `[min, max]`，超限抛 `ValueError`（不再靠 `GroupSyncWrite` 静默吞）。TDD：`test_write_positions_rejects_over_hardware_limit`（fake limit 3640，写 3641 → ValueError）。真机验证：写 3641 raise `exceeds hardware position limit [2503, 3640]`、写 3640 到位 3618。pitch 硬件 limit (1251, 2389) 恰等于 Config，一致。

**G2 修复（2026-08-11，提交 79035ff）：** `DynamixelBackend.connect` 现写 `Config.profile_velocity`/`profile_acceleration` 到每个 motor 的 RAM Profile Velocity/Acceleration 寄存器（在 torque-off 配置段，`setOperatingMode` 之后）；Config 值 0 = 不动（保留舵机值）。TDD：`test_connect_applies_profile_when_configured` + `test_connect_skips_profile_when_zero`。真机验证：yaw Profile Velocity 600 / Acceleration 12016 写入 RAM。
