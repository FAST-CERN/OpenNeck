# AGENTS.md — 工作区约束（适用于所有 AI Agent）

本仓库进行 **TWIST2 NECK + Dynamixel 适配**工作。权威设计见 [`docs/knowledge/twist2-dynamixel-design.md`](docs/knowledge/twist2-dynamixel-design.md)，项目状态见 [`docs/STATUS.md`](docs/STATUS.md)，文档结构约定见 [`docs/knowledge/ref/doc-conventions.md`](docs/knowledge/ref/doc-conventions.md)。

## 硬性规则

1. **进度记录（强制）**：每个阶段的全部新增/修改都必须在 `docs/progress/<组件>/phase-*.md` 记录（组件 = `software` / `hardware`）——改了哪些文件、跑了什么命令（含退出码）、结果与偏离。**未记录视为未完成**。同名文件按日期追加，不新建。
2. **plan ↔ progress 一一对应**：`docs/plan/<组件>/phase-X.md` 写「打算怎么做」，`docs/progress/<组件>/phase-X.md` 写「实际做了什么」。
3. **单一事实源（去重靠链接，不复制）**：测试数字、版本号、机器路径、量程等只在一处写；其余位置只链接。
4. **每阶段必须** 实现 → `pytest` 全绿 → 记录；失败先修复，**不跳阶段**。
5. **真机调试**：每次需人批准且人在场；默认先用 `FakeBackend` / mock 与仿真验证。
6. **不修改** `thirdparty/DynamixelSDK/` 子模块源码（子模块只读指向上游 commit）；Dynamixel 适配层全部放在 `openneck/_backends/`。
7. **保留 Feetech 后端**：不删除现有 `scservo_sdk` 实现；backend 由 config 的 `servo_backend` 字段选择。
8. **对话语言**：所有对话、解释、进度记录用**中文**；代码、路径、协议字段、命令、标识符保持英文。
9. **不进 Git**：虚拟环境、build 产物、`active_vision_config.json`（见 `.gitignore`）。`thirdparty/DynamixelSDK/` 为 git 子模块（ROBOTIS 官方，Apache-2.0）；克隆主仓需 `--recurse-submodules`，更新子模块用 `git submodule update --recursive`。

## 流程

每阶段：①查 `docs/plan/<组件>/phase-*.md` → ②实现 → ③`pytest`（必要时 configure/build/test）→ ④把过程与结果写入 `docs/progress/<组件>/phase-*.md` → ⑤报告真实命令、退出码、结果。
