# software phase-3-dynamixel-backend 进度

[计划](../../plan/software/phase-3-dynamixel-backend.md) · [状态](../../STATUS.md) · [设计合同](../../knowledge/twist2-dynamixel-design.md)

执行方式：TDD（红→绿→提交），fake-SDK 离线测试。分支 `feat/phase3-dynamixel-backend`，基线 9910720（已并入 fork `FAST-CERN/OpenNeck:main`）。

## 改动概览

- 新增 `openneck/_backends/dynamixel.py`：`DynamixelBackend`（实现 `ServoBackend` Protocol）+ `_translate` 上下文管理器（把 `dynamixel_easy_sdk` 的 `DxlRuntimeError`——`Exception` 子类，非 `RuntimeError`——统一翻译成 `RuntimeError`，对齐后端契约）。
  - `connect()`：开端口 → 逐 ID `createMotor`（内含 ping）→ `OperatingMode(config.operating_mode)`（先 `disableTorque` 再 set，满足 SDK 的 torque-off 前置约束）→ 可选逐轴使能扭矩。
  - `write_positions`：经 `GroupExecutor` 批量 `stageSetGoalPosition` + `executeWrite`（原子双轴写入），越界抛 `ValueError`。
  - `read_position(s)`：`getPresentPosition()`，超 `0..4095` 抛 `RuntimeError`。
  - `read_voltage`：`Present Input Voltage` 控制表项（见下 R2）。
- `openneck/_backends/factory.py`：`make_backend` 增 `"dynamixel"` 分支，返回 `DynamixelBackend`；docstring 同步。
- 测试：`tests/test_backends/test_dynamixel_backend.py`（新增，5 测试，`patch.dict(sys.modules, ...)` 注入 fake SDK，绝不导入真 SDK）；`tests/test_backends/test_factory.py`（替换 1 测试）。

## 命令与结果

- `pytest -q` → **36 passed**（基线 31 → 36）。
- Fake SDK 对照真实 vendored 源码（`thirdparty/DynamixelSDK/python/src/dynamixel_easy_sdk/`）核对：`Connector(port, baud)`、`createMotor`→`Motor`、`enableTorque/disableTorque/setOperatingMode`（torque-off 前置）、`getPresentPosition`、`stageSetGoalPosition`、`GroupExecutor.addCmd/executeWrite`、`OperatingMode` 为 `IntEnum`。

## 提交

- 9910720 → c1d9833：Task 1 `bf6245a`（connect/close/torque）、Task 2 `12f28bb`（位置读写 + 电压）、Task 3 `c1d9833`（factory 注册）。

## 偏离 / 计划修正

- **Fake `OperatingMode`**：计划写为裸类，但 `connect()` 调 `OperatingMode(config.operating_mode)`（构造式）。真实 SDK 中 `OperatingMode` 是 `IntEnum`（`POSITION=3`…），裸类会 `TypeError`。修正为 `IntEnum`，与 vendored 源码一致。
- **`connect()` 使能扭矩路径（计划 bug）**：计划在 `connect()` 内调 `self.enable_torque(id)`，但 `enable_torque` 的 `_ensure_connected()` 守卫会在 `_connected=True`（connect 末尾才置位）之前就抛 "not connected"，计划的测试无法通过。改为在 `connect()` 内**内联**使能扭矩（绕过守卫），保留 `enable_torque()` 的守卫供连接后外部调用。等价于 FeetechBackend 用更弱的 `_ensure_connected_or_opened` 的做法。
- **Task 3 测试替换**：phase-2 的 `test_dynamixel_backend_not_implemented`（断言 dynamixel 抛错）与 phase-3 的 `test_dynamixel_backend_is_selected`（断言返回实例）是同一场景的相反预期，互斥。按 phase-2 进度文档预告，用后者**替换**前者。
- **`read_voltage` 耦合 Motor 私有方法**：真 SDK 未暴露 `getPresentInputVoltage()` 公开方法，故用 `motor._getControlTableItem("Present Input Voltage")` + `motor._readData(...)`。属对私有 API 的耦合，phase-4 真机核对时留意。

## 关键决策 / 开放问题闭环

- **M1（已闭环）**：`ping`/`enable_torque` **不**纳入 `ServoBackend` Protocol。两个后端都实现了二者，但仅内部/具体类使用，Protocol 只保留 `connect/close/read_positions/read_position/write_positions/read_voltage/release_torque`。向后兼容、不阻塞，与 [[../../todo/todolist]] 中预留方向一致。
- **R2**：`Present Input Voltage` 经控制表读取（fake 中 address=144、size=1、单位 0.1V）。item key 在 fake 内自洽；**真机/真控制表覆盖待 phase-4 ping 冒烟确认**（见设计 §12 R1/R2）。
- **R1（型号控制表）**：`createMotor`→`Motor` 构造会 `ControlTable.getControlTable(model_number)`；目标型号是否被收录待 phase-4 真机 ping 确认。
