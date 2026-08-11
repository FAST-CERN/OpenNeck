# TWIST2 舵机配置（twist2-servo-config）

[状态](../../STATUS.md) · [配置数据流](config-dataflow.md) · [设计合同](twist2-dynamixel-design.md)

TWIST2 云台两个 Dynamixel 舵机的硬件配置事实（ID、零位、限位、控制参数），由操作员从舵机配置工具读取，作为 `openneck calibrate` 与 `active_vision_config.json` 的真机基准。操作员提供于 2026-08-11。

**型号**：Dynamixel **XC330-T288**（model_number 1220）。2026-08-11 真机 smoke 验证：`broadcastPing` 解析出 `xc330_t288`，easy_sdk 控制表收录该型号。

## 舵机配置（原值）

| 舵机 ID | 自由度 | 零位角度 | 运动限位（相对零位） | 控制参数 |
|---|---|---|---|---|
| 0 | yaw | 280° | [-50°, +50°] | kp=800 kd=5 ki=5；profile_velocity=600 profile_acceleration≈12016 |
| 1 | pitch | 120° | [-10°, +90°] | （用舵机默认） |

- 零位角度 = 机械正前方（yaw）/ 水平（pitch）时舵机报告的角度。Dynamixel POSITION 模式下 0..360° ↔ 0..4095 step。
- pitch 限位不对称（-10°..+90°），偏向上。
- `operating_mode` = POSITION（3）。
- PID 与 profile 由配置工具写入舵机 EEPROM。

## 到 `Config` 的映射（step 待真机标定确认）

换算：`step = round(angle / 360 × 4095)`（每 step = 360/4095 ≈ 0.0879°）。

| `Config` 字段 | yaw（ID 0） | pitch（ID 1） |
|---|---|---|
| `*_id` | 0 | 1 |
| `*_center_step` | 3185（280°） | 1365（120°） |
| `*_min_step` | 2616（230°） | 1251（110°） |
| `*_max_step` | 3754（330°） | 2389（210°） |
| `*_step_sign` | 现场定（先 1） | 现场定（先 1） |
| `servo_backend` | `dynamixel` | `dynamixel` |
| `operating_mode` | 3 | 3 |
| `profile_velocity` | 600 | 600（或舵机默认） |
| `profile_acceleration` | 12016（原 12016.3，取整） | 默认 |

step 值按线性映射换算，**最终以 `openneck calibrate` 真机读取为准**；`*_step_sign` 需通电后发小角度试方向。2026-08-11 smoke 用上表值已可加载与运动（yaw `sign=1` 物理方向正确）；center 时 yaw 有 ~1.93° 稳态偏差，正式标定建议重跑 `openneck calibrate`。

## 与当前 OpenNeck 的差异（gap，真机 smoke 前处理）

1. **ID 0 被 `Config` 拒绝**：`openneck/_config.py` 校验 `yaw_id`/`pitch_id` `minimum=1`，硬件 yaw_id=0 不通过。`Config(yaw_id=0)` 抛 `ValueError`。需把下限放开到 0，或改硬件 ID。
2. **profile 字段未应用**：`Config` 有 `profile_velocity`/`profile_acceleration`，但 `DynamixelBackend.connect()` 只设 `operating_mode`，不写 profile 寄存器。
3. **PID 无字段、无写入**：OpenNeck 不管理 PID gain，依赖舵机 EEPROM 已存值。
4. **profile_acceleration 浮点**：`Config.profile_*` 经 `_require_int` 只收 int，`12016.3` 取整为 `12016`。

这些 gap 的处置见 [`../todo/todolist.md`](../todo/todolist.md)。
