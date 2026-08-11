# 待办 / 未采纳点子

[文档索引](../README.md) · [状态](../STATUS.md)

唯一待办与未采纳点子汇总。已纳入计划的项不在此重复（见 [状态](../STATUS.md) 与 [计划](../plan/README.md)）。

## 待办

- **phase-4 真机 smoke 前的 gap**（来自 [`knowledge/twist2-servo-config.md`](../knowledge/twist2-servo-config.md)）：
  - G1：`Config` 的 `yaw_id`/`pitch_id` 下限放开到 0（硬件 yaw_id=0，当前 `minimum=1` 拒绝）。
  - G2：`DynamixelBackend.connect()` 应用 `profile_velocity`/`profile_acceleration`（当前只设 `operating_mode`）。
  - G3：`profile_acceleration` 取整策略（`12016.3` → `12016`；`Config.profile_*` 只收 int）。
  - G4：决定 PID（kp/kd/ki）是否由 OpenNeck 管理（当前依赖舵机 EEPROM 已存值）。

## 已闭环

- M1（phase-3 闭环）：`ping`/`enable_torque` **不**纳入 `ServoBackend` Protocol——两个后端都实现了二者，但仅内部/具体类使用；Protocol 只保留 `connect/close/read_positions/read_position/write_positions/read_voltage/release_torque`。详见 [`progress/software/phase-3-dynamixel-backend.md`](progress/software/phase-3-dynamixel-backend.md)。
- R3（phase-4 真机配置闭环）：TWIST2 量程 yaw [-50°,+50°]、pitch [-10°,+90°]，零位 yaw 280°/pitch 120°。详见 [`knowledge/twist2-servo-config.md`](../knowledge/twist2-servo-config.md)。
- R4（phase-4 离线闭环）：vendored SDK = 包 `dynamixel-sdk` v4.0.5，setuptools 后端，`package-dir = src`。

## 未采纳 / 延后

- （暂无）

## 开放问题（来自设计文档 §12）

- R1：easy_sdk 是否收录目标 Dynamixel 型号控制表？→ phase-4 真机 ping 冒烟闭环（只读扫描即可验）。
- R2：`Present Input Voltage` 在 easy_sdk 的 item key？→ phase-3 fake 已用 `"Present Input Voltage"`（address 144），真机确认待 phase-4 smoke。
