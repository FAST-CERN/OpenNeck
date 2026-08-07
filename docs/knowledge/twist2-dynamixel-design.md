# TWIST2 NECK + Dynamixel 适配设计（工程合同）

> 权威设计文档。本文件是 OpenNeck 适配 **TWIST2 NECK 机械结构** 与 **Dynamixel 舵机（git 子模块 SDK）** 的唯一设计源。
> 硬性规则见根 [`AGENTS.md`](../../AGENTS.md)；文档结构约定见 [`ref/doc-conventions.md`](ref/doc-conventions.md)。
> 项目状态见 [`../STATUS.md`](../STATUS.md)；阶段计划见 [`../plan/`](../plan/)。

- 日期：2026-08-07
- 状态：设计已批准，待编写实现计划（writing-plans）
- 适用版本：openneck 0.2.x → 0.3.x

## 1. 背景与目标

当前 `openneck/` 是基于角度的 2-DoF（yaw + pitch）颈部驱动，后端为 **Feetech SCS** 舵机（`scservo_sdk`/`sms_sts`，12 位 0..4095）。本次目标：

1. 引入 `thirdparty/DynamixelSDK`（**git 子模块**，ROBOTIS 官方仓库 @ `2ded684` / v4.0.5），新增 **Dynamixel** 后端（基于高层 `dynamixel_easy_sdk`）。
2. 适配 **TWIST2 NECK** 新机械结构（运动学仍为 2-DoF yaw+pitch），含 `mesh待转换` 的 mesh 转换。
3. **保留** Feetech 后端，通过 config 选择 backend（非破坏式）。

公共 API 表面（`NeckAngles` / `OpenNeckController.move_deg(yaw, pitch)` 等）**保持不变**。

## 2. 范围与非目标

**范围**：`openneck/_backends/` 后端抽象、Dynamixel 后端实现、Config 扩展、vendored SDK 接线、TWIST2 mesh 转换与 sim 模型更新、文档与校准流程。

**非目标**：不改 `_angles.py` 的角度换算数学；不引入第三个 backend；不替换原 `hardware/`（Feetech 设计原样保留）；不改公共 API 形状（yaw_deg/pitch_deg）。

## 3. 总体架构

后端抽象位于"寄存器级"：`ServoBackend` 只进出原始 step 整数（0..4095）。`_config.py` / `_angles.py` 的轴系换算在两个 backend 间**完全复用、不改**。

```
openneck/
  _config.py        # 新增 servo_backend / operating_mode / profile_velocity / profile_acceleration（默认保兼容）
  _angles.py        # 不变
  _backends/
    protocol.py     # ServoBackend Protocol（寄存器级契约）
    feetech.py      # 现 _driver.py 的 scservo_sdk 逻辑迁入（torque_addr=40 / voltage_addr=62 成为内部常量）
    dynamixel.py    # 新：dynamixel_easy_sdk Connector + Motor + GroupExecutor
    factory.py      # make_backend(config) -> ServoBackend，按 config.servo_backend 选择
  api.py            # OpenNeckController 持有 ServoBackend（经 factory），API 表面不变
  cli.py            # 经 factory 使用 backend
  tools/            # scan / change_servo_id / calibrate 适配两协议；_servo_bus 抽象总线发现
```

数据流（不变部分）：
`上层角度(deg)` → `_angles.angle_to_step(center/min/max/sign)` → `step(0..4095)` → `ServoBackend.write_positions({id:step})` → 寄存器。

## 4. ServoBackend 契约

两个 backend 都实现该 Protocol：

```python
class ServoBackend(Protocol):
    def connect(self) -> None: ...
    def close(self) -> None: ...
    def ping(self, servo_id: int) -> int: ...                       # 返回 model number
    def read_positions(self) -> dict[int, int]: ...
    def write_positions(self, targets: dict[int, int]) -> None: ... # 校验 0..4095
    def read_voltage(self, servo_id: int) -> float: ...             # 0.1V → V
    def enable_torque(self, servo_id: int) -> None: ...
    def release_torque(self) -> None: ...
```

- `connect()` 失败需回滚已使能的扭矩（沿用现有 `_rollback_torque_after_failed_connect` 语义）。
- `close()` 只关串口，不改扭矩状态（沿用现有语义）。
- Protocol 让 `api.py` / `cli.py` 测试可注入 `FakeBackend`，**无需真实舵机/串口**。

## 5. Config 扩展（严格校验、向后兼容）

`_config.Config` 新增字段，默认值不破坏现有 Feetech 用户；未知字段仍报错：

| 字段 | 默认 | 说明 |
|---|---|---|
| `servo_backend` | `"feetech"` | 校验 ∈ {"feetech","dynamixel"}；TWIST2 配置写 `"dynamixel"` |
| `operating_mode` | `3`（POSITION） | 校验 ∈ {0,1,3,4,5,16}；仅 Dynamixel 使用 |
| `profile_velocity` | `0` | 0 = 最大；仅 Dynamixel |
| `profile_acceleration` | `0` | 0 = 最大；仅 Dynamixel |

既有 `speed` / `acceleration` 保留，仅 Feetech 使用。

## 6. Dynamixel 后端要点

- `Connector(port, baudrate)` → 对每个 id `createMotor(id)`；model number 自动解析控制表（**型号无关**，支持 easy_sdk 已收录的型号）。
- `connect()` 顺序：ping → `setOperatingMode(POSITION)` → `enableTorque()`（`setGoalPosition` 会校验模式，必须先设）。
- `write_positions` / `read_positions`：用 `Connector.createGroupExecutor()` + `stageSetGoalPosition` / `stageGetPresentPosition` 做**两轴同步读写**（消除 Feetech 顺序写的 yaw/pitch 微错位）。
- `read_voltage`：经控制表项 `Present Input Voltage`（或 `Connector.read1ByteData`），0.1V 单位，与 Feetech 一致（实现阶段确认 easy_sdk 中的确切 item key）。
- **复用** `step_sign` + `_angles.py` 做方向翻转；**不**用 easy_sdk `setDirection`（保证两 backend 角度数学统一）。

## 7. TWIST2 NECK mesh 转换（`mesh待转换`）

TWIST2 仍为 2-DoF yaw+pitch，**URDF/MuJoCo 运动学骨架不变**，只换 mesh 与量程。新增 `hardware/twist2/`（与原 `hardware/` 并列，保留原始 Feetech 设计）：

```
hardware/twist2/
  cad/                     # 源 CAD（STEP/原生），由用户提供
  3d_prints/               # 导出的打印件 STL
  simulation/
    meshes/                # 视觉 / 碰撞 STL
    twist2.urdf            # 复用 yaw_joint/pitch_joint 模板，更新 mesh 引用与 range
    twist2.xml             # MuJoCo，同上
```

转换链：CAD 各零件 → STL（打印件 + sim 视觉 mesh，必要时简化碰撞 mesh）→ 以现有 yaw/pitch 模板更新 mesh 引用与 joint range。本阶段产物清单见 [`../plan/hardware/README.md`](../plan/hardware/README.md)。

## 8. 依赖与打包

`pyproject.toml`：

- 保留 `pyserial`、`ftservo-python-sdk==2.0.0`（Feetech 仍在）。
- 新增 Dynamixel SDK（git 子模块，官方 `ROBOTIS-GIT/DynamixelSDK` @ `2ded684` / v4.0.5）：`pip install -e thirdparty/DynamixelSDK/python`（提供 `dynamixel_sdk` 与 `dynamixel_easy_sdk`），在 pyproject 中以路径依赖固化（实现阶段确认包名与构建后端）。
- `thirdparty/DynamixelSDK/` 为 git 子模块（Apache-2.0，与本项目兼容）；**不修改其源码**（子模块只读指向上游 commit），适配层全部放在 `openneck/_backends/`。克隆主仓需 `git clone --recurse-submodules`，或之后 `git submodule update --init --recursive`。

## 9. 测试策略

- `tests/test_backends/test_feetech_backend.py`：mock `scservo_sdk`，由现有 `tests/test_driver.py` 迁移。
- `tests/test_backends/test_dynamixel_backend.py`：mock `dynamixel_easy_sdk` 的 `Connector` / `Motor` / `GroupExecutor`。
- `tests/test_api.py` / `test_cli.py` / `test_config.py`：注入 `FakeBackend`（实现 `ServoBackend`）做无硬件回归；新增 Config 新字段的校验用例。
- 门禁：每阶段必须 `pytest` 全绿（沿用现有测试纪律）。

## 10. 阶段划分（plan 组件）

### software 组件（`openneck/` Python 包）

| 阶段 | 主题 |
|---|---|
| `phase-1-backend-skeleton` | 建 `_backends/{protocol,factory}.py`，`_driver.py`→`feetech.py`，`api/cli/tools` 走 factory；零行为变化；测试全绿 |
| `phase-2-config-extension` | Config 加 4 个新字段与校验；默认 `feetech` |
| `phase-3-dynamixel-backend` | `_backends/dynamixel.py`（同步读写 + 电压）；mock 单测 |
| `phase-4-sdk-wiring` | vendored SDK 可编辑安装 + pyproject 路径依赖；导入冒烟；真机 ping 冒烟（需人/硬件） |
| `phase-5-docs-calibration` | `docs/{en,zh-CN}/software.md` 增 backend 选择与 Dynamixel 配置/校准；CLI 帮助 |

### hardware 组件（`hardware/`）

| 阶段 | 主题 |
|---|---|
| `phase-1-twist2-meshes` | `hardware/twist2/` 目录建立；CAD→STL（打印件 + 视觉/碰撞 mesh）；产物清单 |
| `phase-2-twist2-sim-models` | 复用 yaw/pitch 模板更新 `twist2.urdf` / `twist2.xml`；MuJoCo 加载冒烟 |

依赖：software 与 hardware 两个组件相互独立，可并行；`phase-4` 真机冒烟不依赖 hardware。

## 11. 决策记录

| # | 决策 | 选择 | 理由 |
|---|---|---|---|
| D1 | TWIST2 运动学 | 与现 OpenNeck 相同的 2-DoF yaw+pitch | 公共 API 形状不变，只换 mesh/量程 |
| D2 | mesh 来源 | 用户将 CAD/STL 放入 `hardware/` | 计划对实际文件做转换，非占位 |
| D3 | Dynamixel SDK 层 | `dynamixel_easy_sdk`（高层 Connector+Motor） | 样板少、协议 2.0、控制表按型号自动解析 |
| D4 | Feetech 后端去留 | 保留，通过 backend 抽象与 Dynamixel 并存 | 保留既有平台，config 选择 |
| D5 | 后端布局 | 方案 A（`openneck/_backends/` 包 + Protocol） | 单职责、强契约、便于注入 `FakeBackend` |
| D6 | TWIST2 文件位置 | `hardware/twist2/` 并列（不替换原 `hardware/`） | 与"两 backend 并存"对称，保留原始设计 |
| D7 | 默认 backend | `servo_backend="feetech"`（非破坏式） | 现有用户不受影响；TWIST2 配置显式写 `dynamixel` |
| D8 | thirdparty 取得方式 | git 子模块（官方 `2ded684` / v4.0.5），非 vendor 拷贝 | 上游 ROBOTIS 可追溯、不膨胀主仓历史；`dynamixel_easy_sdk` 在官方上游 |

## 12. 风险与开放问题

- **R1**：easy_sdk 是否收录目标 Dynamixel 型号的控制表？→ `phase-4` ping 冒烟时确认；型号经 `ping` 自动识别。
- **R2**：`Present Input Voltage` 在 easy_sdk 的确切 item key？→ `phase-3` 实现时核对（备选 `Connector.read1ByteData`）。
- **R3**：TWIST2 实际机械量程（yaw/pitch 的 ±角度）需在 `phase-1` 校准时实测写入 config 与 sim 的 `range`。
- **R4**：Dynamixel SDK 子模块的 pyproject 构建后端与包名需在 `phase-4` 确认后再固化路径依赖。

## 13. 参考与链接

- 文档约定：[`ref/doc-conventions.md`](ref/doc-conventions.md)
- 工作区硬性规则（参考样例）：[`ref/AGENTS-ref.md`](ref/AGENTS-ref.md)
- 现有软件驱动说明：[`../en/software.md`](../en/software.md)
- 仿真模型（原始）：[`../../hardware/simulation/openneck.urdf`](../../hardware/simulation/openneck.urdf)、[`../../hardware/simulation/openneck.xml`](../../hardware/simulation/openneck.xml)
- Dynamixel SDK 子模块：[`../../thirdparty/DynamixelSDK/python/`](../../thirdparty/DynamixelSDK/python/)（git submodule，官方 `ROBOTIS-GIT/DynamixelSDK`）
