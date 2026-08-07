# 项目状态（唯一源）

> 本文件是 OpenNeck TWIST2 + Dynamixel 适配的唯一状态源。最近更新：2026-08-07。

## 当前阶段

**设计已批准，实现计划已编写完成（writing-plans），待执行。** 尚未进入代码实现。各阶段计划见 [`plan/`](plan/)；执行方式待选（subagent-driven 或 inline）。

## 工作概述

为 OpenNeck 引入 Dynamixel 后端（vendored `dynamixel_easy_sdk`）并适配 TWIST2 NECK 机械结构，保留 Feetech 后端，公共 API 不变。详见 [`knowledge/twist2-dynamixel-design.md`](knowledge/twist2-dynamixel-design.md)。

## 组件与阶段进度

| 组件 | 阶段 | 状态 | 计划 | 进度 |
|---|---|---|---|---|
| software | phase-1 backend-skeleton | 未开始 | [`plan/software/README.md`](plan/software/README.md) | [`progress/software/`](progress/software/) |
| software | phase-2 config-extension | 未开始 | 同上 | 同上 |
| software | phase-3 dynamixel-backend | 未开始 | 同上 | 同上 |
| software | phase-4 sdk-wiring | 未开始 | 同上 | 同上 |
| software | phase-5 docs-calibration | 未开始 | 同上 | 同上 |
| hardware | phase-1 twist2-meshes | 未开始 | [`plan/hardware/README.md`](plan/hardware/README.md) | [`progress/hardware/`](progress/hardware/) |
| hardware | phase-2 twist2-sim-models | 未开始 | 同上 | 同上 |

## 关键决策

见设计文档 [§11 决策记录](knowledge/twist2-dynamixel-design.md#11-决策记录)。

## 开放问题

见设计文档 [§12 风险与开放问题](knowledge/twist2-dynamixel-design.md#12-风险与开放问题)。
