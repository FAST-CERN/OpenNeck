# 待办 / 未采纳点子

[文档索引](../README.md) · [状态](../STATUS.md)

唯一待办与未采纳点子汇总。已纳入计划的项不在此重复（见 [状态](../STATUS.md) 与 [计划](../plan/README.md)）。

## 待办

- M1（software phase-3 处理）：`ServoBackend` Protocol 是否纳入 `ping`/`enable_torque`（设计 §4 已列），还是在设计文档里标为内部？phase-3 落地 `DynamixelBackend` 时定（当前 `FeetechBackend` 已实现二者，仅内部使用，向后兼容，不阻塞）。

## 未采纳 / 延后

- （暂无）

## 开放问题（来自设计文档 §12）

- R1：easy_sdk 是否收录目标 Dynamixel 型号控制表？→ software phase-4 ping 冒烟确认
- R2：`Present Input Voltage` 在 easy_sdk 的确切 item key？→ software phase-3 核对
- R3：TWIST2 实际机械量程（yaw/pitch ±角度）需 hardware phase-1 / 校准时实测
- R4：vendored SDK 的 pyproject 构建后端与包名 → software phase-4 确认
