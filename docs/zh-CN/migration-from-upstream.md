# 从上游 BotRunner64 OpenNeck 升级

[主页](../../README.md) · [软件](./software.md) · [硬件](./hardware.md) · [装配](./assembly.md) · [部署](./deployment-teleopit.md) · [迁移](./migration-from-upstream.md) · [English](../en/migration-from-upstream.md) · **中文**

## 目录

- [一览](#一览)
- [公开 API 变化](#公开-api-变化)
- [下游代码需要改哪些地方](#下游代码需要改哪些地方)
- [配置 schema 变化](#配置-schema-变化)
- [CLI 变化](#cli-变化)
- [打包变化](#打包变化)
- [使用时要注意的行为差异](#使用时要注意的行为差异)
- [迁移清单](#迁移清单)
- [参考](#参考)

本 fork 相对原始 BotRunner64 OpenNeck 的 API 变化、更新到当前版本时需要改哪些地方、以及使用时要注意的行为差异。装进具体环境的步骤见 [`deployment-teleopit.md`](deployment-teleopit.md)；完整字段参考见 [`software.md`](software.md)。

**基线：** 对比的基准是与 `upstream`（`BotRunner64/OpenNeck`）的 git merge-base，提交 `145e6bf`——即本 fork 分叉的精确位置。下文"原始版本"指该状态。

## 一览

| 面 | 结论 |
|---|---|
| `from openneck import OpenNeckController, NeckAngles` + 公开方法 | **向后兼容**——无需改动 |
| `OpenNeckController.__init__` | 兼容——新增 3 个*可选* kwarg，旧调用不变 |
| `openneck._driver.ServoDriver`（私有） | **已移除**——由 `openneck._backends`（`make_backend`、`ServoBackend`）取代 |
| `controller._driver` 属性 | 改名为 `controller._backend`（私有） |
| 配置文件 | 仅新增——新可选字段；`yaw_id`/`pitch_id` 现允许 `0` |
| CLI 子命令 | 不变（`ports`、`config`、`voltage`、`calibrate`、`center`、`test`） |
| CLI flag | 仅新增可选 flag；旧 flag 不变 |
| `pyproject.toml` | 新增 `dynamixel` extra；依赖不变；**版本 bump 到 `0.3.0`**（上游为 `0.2.0`） |

**结论：** 如果你的下游代码只用公开 API（`OpenNeckController` / `NeckAngles`），**什么都不用改**。唯一的硬性破坏是导入了私有的 `ServoDriver`。

## 公开 API 变化

包导出不变：

```python
# openneck/__init__.py —— 导出不变；版本自上游 0.2.0 bump
__all__ = ["NeckAngles", "OpenNeckController"]
__version__ = "0.3.0"
```

`OpenNeckController` 的每个公开方法签名都保持不变：
`connect()`、`move_deg(yaw_deg, pitch_deg) -> NeckAngles`、`center()`、
`read_deg() -> NeckAngles`、`read_voltage() -> dict[str, float]`、
`release_torque()`、`close()`，以及上下文管理器协议。

构造函数新增三个**可选、keyword-only** 覆盖参数（默认都是 `None`，省略即复现原始行为）：

```python
OpenNeckController(
    config=None,            # str | Path | None （不变）
    *,
    port=None,              # 不变
    servo_backend=None,     # 新增： "feetech" | "dynamixel"
    baudrate=None,          # 新增
    operating_mode=None,    # 新增（仅 Dynamixel）
)
```

`NeckAngles`（frozen dataclass：`yaw_deg`、`pitch_deg`）不变。

## 下游代码需要改哪些地方

1. **只用过公开 API 的**——无需改动，旧代码照常工作：
   ```python
   from openneck import OpenNeckController
   with OpenNeckController("active_vision_config.json", port="/dev/ttyUSB0") as neck:
       neck.move_deg(5.0, 0.0)
   ```

2. **导入过私有 driver 的**——迁移：
   ```python
   # 之前（已坏——模块移除）：
   from openneck._driver import ServoDriver
   driver = ServoDriver(cfg)

   # 之后：
   from openneck._backends import make_backend      # 按 config.servo_backend 选择
   driver = make_backend(cfg)
   # 或仅需要契约（仅用于类型）：
   from openneck._backends import ServoBackend       # Protocol
   ```
   尽量走 `OpenNeckController` 或 `make_backend(config)`，不要直接实例化某个 backend 类——factory 读 `config.servo_backend`，代码即可与具体后端解耦。

3. **访问过 `controller._driver` 的**——改名为 `controller._backend`。（私有属性，只有越过公开 API 才会涉及。）

4. **配置里用过舵机 ID `0` 的**——现在能通过校验（之前因 "must be 1..253" 被拒）。无需处理；这是为 Dynamixel（ID 含 0）刻意放宽。

5. **（可选）启用 Dynamixel 后端**——三种等价方式：
   - 配置字段：`"servo_backend": "dynamixel"`
   - CLI flag：`--servo-backend dynamixel`
   - 代码 kwarg：`OpenNeckController(servo_backend="dynamixel", baudrate=57600)`

   并安装 SDK：`python -m pip install ".[dynamixel]"`。

## 配置 schema 变化

仅新增。原始字段（port、baudrate、ID、`*_center_step`/`*_min_step`/`*_max_step`/`*_step_sign`、`speed`、`acceleration`）不变，原样加载。新增可选字段：

| 字段 | 默认 | 含义 |
|---|---|---|
| `servo_backend` | `"feetech"` | `"feetech"` 或 `"dynamixel"` |
| `operating_mode` | `3`（POSITION） | 仅 Dynamixel；Feetech 忽略 |
| `profile_velocity` | `0` | Dynamixel；`0` = 不动 |
| `profile_acceleration` | `0` | Dynamixel；`0` = 不动 |
| `yaw_kp` / `yaw_ki` / `yaw_kd` | `0` | Dynamixel 位置 PID；`0` = 不动 |
| `pitch_kp` / `pitch_ki` / `pitch_kd` | `0` | Dynamixel 位置 PID；`0` = 不动 |

校验变化：
- **放宽：** `yaw_id` / `pitch_id` 下限现为 `0`（原为 `1`）。
- **不变：** 未知字段仍被拒，因此带 merge-base 之前已移除字段的配置仍会报错。来自*更早* normalized-amplitude schema 的配置不会自动转换——需重跑 `openneck calibrate`。

## CLI 变化

子命令完全相同：`ports`、`config`、`voltage`、`calibrate`、`center`、`test`。新增可选 flag（默认都不设，旧行为不变）：`--servo-backend`、`--operating-mode`、`--profile-velocity`、`--profile-acceleration`、`--yaw-kp/ki/kd`、`--pitch-kp/ki/kd`。

## 打包变化

- `pyproject.toml` 依赖不变（`pyserial`、`ftservo-python-sdk`）。
- 新增可选 extra：`pip install ".[dynamixel]"` 拉取内置 Dynamixel SDK 子模块。纯 Feetech 的 `pip install .` 不变。
- **版本：** fork 报告 `0.3.0`；上游报告 `0.2.0`。可用 `openneck.__version__` 判断是否在 fork 上。对于仍报告 `0.2.0` 的旧 fork 构建，退回 `_backends` 探测或安装位置：
  ```bash
  python -c "import openneck; print(openneck.__version__)"   # 0.3.0 = fork, 0.2.0 = 上游
  python -c "import importlib.util as u; print(bool(u.find_spec('openneck._backends')))"
  pip show openneck | grep Location
  ```

## 使用时要注意的行为差异

- **后端选择现在是显式的。** 原始版本只有 Feetech。默认仍是 Feetech，但换后端只差一个配置字段 / flag / kwarg——跨机器搬运配置时务必核对 `servo_backend`。
- **Dynamixel 专属字段会被 Feetech 忽略**（安全 no-op），因此一份配置可同时携带两族的设置。
- **校验对未知字段更严、对 ID 更松。** 之前被拒的 ID-0 配置现在能加载；带拼写错误或已移除字段的配置仍会显式报错。
- **运动语义无破坏性变化。** `move_deg` / 限位 clamp / 符号处理不变；`openneck._angles` 的步进↔角度换算未动。

## 迁移清单

- [ ] 更新包（`pip install -U .` 或 `pip install ".[dynamixel]"`）。
- [ ] 在代码库里 `grep -rn "_driver\|ServoDriver"`——按"需要改哪些地方"#2/#3 替换任何私有导入。
- [ ] 重跑现有 `OpenNeckController` 冒烟测试——应原样通过。
- [ ] 若启用 Dynamixel：设 `servo_backend`、装 extra、在真实机构上 `openneck calibrate`。
- [ ] 确认装上的确实是 fork（`openneck.__version__` 应为 `0.3.0`；或用 `_backends` 探测）。

## 参考

- 安装 + 完整配置字段参考：[`software.md`](software.md)
- 配置数据流（加载/校验/override/后端选择）：[`../knowledge/config-dataflow.md`](../knowledge/config-dataflow.md)
- 装进具体环境：[`deployment-teleopit.md`](deployment-teleopit.md)
- 后端设计合同（为何 `_driver` → `_backends`）：[`../knowledge/twist2-dynamixel-design.md`](../knowledge/twist2-dynamixel-design.md)
