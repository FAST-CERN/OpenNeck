# software phase-5-docs-calibration 进度

[计划](../../plan/software/phase-5-docs-calibration.md) · [状态](../../STATUS.md) · [设计合同](../../knowledge/twist2-dynamixel-design.md)

执行方式：纯文档（双语），无代码改动。分支 `feat/phase5-docs-calibration`，基线 3899d6e（已并入 fork `FAST-CERN/OpenNeck:main`）。

## 改动概览

- `docs/en/software.md` + `docs/zh-CN/software.md`（各 4 处）：
  1. 安装小节增 “Dynamixel 后端（可选）”：`--recurse-submodules` 克隆 + `pip install -e thirdparty/DynamixelSDK/python`。
  2. 新增 “Servo backend / 舵机后端” 章节：`servo_backend` 取值（feetech 默认 / dynamixel）、Dynamixel 专属字段（`operating_mode`、`profile_velocity`、`profile_acceleration`），指向设计合同而非复述。
  3. 配置小节增 Dynamixel JSON 示例。
  4. 标定小节增注：`openneck calibrate` 后端无关（只读当前位置）；`openneck-calibrate-middle` 仅 Feetech（写硬件中位）。
- `README.md`：Getting Started 增 `--recurse-submodules` 提示一行。

## 验证

- CLI `openneck config --help` 列出 `--servo-backend {feetech,dynamixel}`、`--operating-mode {0,1,3,4,5,16}`、`--profile-velocity`、`--profile-acceleration`。✅
- 无代码改动；`pytest -q` 仍 **36 passed**。

## 提交

- 3899d6e → …：`0340c07`（en+zh-CN software.md）、本提交（README + 本进度 + STATUS）。

## 软件组件收尾

software phases 1–5 全部完成。phase-4 Task 2（真机冒烟）仍待硬件/操作员，属独立硬件验证（闭环 R1/R2），不阻塞软件侧收尾。Dynamixel 后端从设计（design）→ 实现（phase-1/2/3）→ 接线（phase-4 离线）→ 文档（phase-5）全链路落地。
