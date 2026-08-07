# software 组件计划

[计划路由](../README.md) · [设计合同](../../knowledge/twist2-dynamixel-design.md) · [进度](../../progress/software/README.md) · [状态](../../STATUS.md)

`openneck/` Python 包的 TWIST2 + Dynamixel 适配。阶段按序，每阶段须 `pytest` 全绿并记录。

| 阶段 | 主题 | 状态 |
|---|---|---|
| `phase-1-backend-skeleton` | 建 `_backends/{protocol,factory}.py`；`_driver.py` → `feetech.py`；`api/cli/tools` 走 factory；零行为变化 | 未开始 |
| `phase-2-config-extension` | Config 加 `servo_backend/operating_mode/profile_velocity/profile_acceleration` 字段与校验；默认 `feetech` | 未开始 |
| `phase-3-dynamixel-backend` | `_backends/dynamixel.py`（Connector+Motor+GroupExecutor 同步读写 + 电压）；mock 单测 | 未开始 |
| `phase-4-sdk-wiring` | vendored SDK 可编辑安装 + pyproject 路径依赖；导入冒烟；真机 ping 冒烟（需人/硬件） | 未开始 |
| `phase-5-docs-calibration` | `docs/{en,zh-CN}/software.md` 增 backend 选择与 Dynamixel 配置/校准；CLI 帮助 | 未开始 |

各阶段详情见同目录 `phase-*.md`（由 writing-plans 产出）。
