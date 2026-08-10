# 待办 / 未采纳点子

[文档索引](../README.md) · [状态](../STATUS.md)

唯一待办与未采纳点子汇总。已纳入计划的项不在此重复（见 [状态](../STATUS.md) 与 [计划](../plan/README.md)）。

## 待办

- （暂无）

## 已闭环

- M1（phase-3 闭环）：`ping`/`enable_torque` **不**纳入 `ServoBackend` Protocol——两个后端都实现了二者，但仅内部/具体类使用；Protocol 只保留 `connect/close/read_positions/read_position/write_positions/read_voltage/release_torque`。详见 [`progress/software/phase-3-dynamixel-backend.md`](progress/software/phase-3-dynamixel-backend.md)。

## 未采纳 / 延后

- （暂无）

## 开放问题（来自设计文档 §12）

- R1：easy_sdk 是否收录目标 Dynamixel 型号控制表？→ software phase-4 ping 冒烟确认
- R2：`Present Input Voltage` 在 easy_sdk 的确切 item key？→ software phase-3 核对
- R3：TWIST2 实际机械量程（yaw/pitch ±角度）需 hardware phase-1 / 校准时实测
- R4：vendored SDK 的 pyproject 构建后端与包名 → software phase-4 确认
