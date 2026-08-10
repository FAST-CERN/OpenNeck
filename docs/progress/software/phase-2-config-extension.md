# software phase-2-config-extension 进度

[计划](../../plan/software/phase-2-config-extension.md) · [状态](../../STATUS.md) · [设计合同](../../knowledge/twist2-dynamixel-design.md)

执行方式：TDD（红→绿→提交）。分支 `feat/phase2-config-extension`，基线 3e86420（已并入 fork `FAST-CERN/OpenNeck:main`）。

## 改动概览

- `openneck/_config.py`：`Config` 新增 `servo_backend`（默认 `"feetech"`）、`operating_mode`（默认 3）、`profile_velocity`、`profile_acceleration`（均默认 0）；`__post_init__` 增校验（`servo_backend ∈ {feetech, dynamixel}`；`operating_mode ∈ {0,1,3,4,5,16}` 且拒绝 `bool`；`profile_*` 经 `_require_int` 非负）。默认值保证旧配置零变化、向后兼容。
- `openneck/_backends/factory.py`：`make_backend` 按 `config.servo_backend` 分支（feetech 接通，其余抛 `ValueError`）；docstring 同步更新（原 phase-1 "无条件返回 Feetech" 措辞作废）。
- `openneck/cli.py`：`add_common` 增 4 个 override flag（`--servo-backend`/`--operating-mode`/`--profile-velocity`/`--profile-acceleration`，均 `default=None`）；`with_overrides` 键列表同步追加 4 个键。
- 测试：`tests/test_config.py`（+4 测试 + 扩展 schema 加载测试）、`tests/test_backends/test_factory.py`（+1）、`tests/test_cli.py`（+2）。

## 命令与结果

- `pytest -q` → **31 passed**（基线 24 → 31）。
- 手动解析检查 `python -c "import openneck.cli as c; ... --servo-backend dynamixel ..."` → `ok`。

## 提交

- 3e86420 → c1039c3：Task 1 `7f71309`（config 字段 + 校验）、Task 2 `f987ffa`（factory 分支）、Task 3 `c1039c3`（CLI override flag）。

## 偏离

- **Task 2 测试值**：计划用 `servo_backend="bogus"`，但 Task 1 落地后 `Config` 已在构造期拒绝 `bogus`，该测试会"立即通过"（ValueError 来自 Config 校验而非 factory），无法驱动 factory 改动——属 TDD 反模式。改为 `servo_backend="dynamixel"`（Config 合法、phase-2 factory 尚未实现），真正覆盖 factory 分支。**phase-3 落地 `DynamixelBackend` 后此测试需相应更新**（dynamixel 将不再抛错）。
- **Task 3 测试**：计划仅做手动 parse 检查；补为两个单测（flag 解析 + `with_overrides` 线程化），回归保护更强。

## 与设计文档的接口确认

- 本阶段产生：`Config.{servo_backend, operating_mode, profile_velocity, profile_acceleration}`；`make_backend` 读取 `config.servo_backend` 分支；CLI 4 个 override flag。
- 开放问题 R2（`Present Input Voltage` 在 easy_sdk 的 item key）仍留待 phase-3 核对，本阶段未触及。
