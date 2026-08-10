# 项目状态（唯一源）

> 本文件是 OpenNeck TWIST2 + Dynamixel 适配的唯一状态源。最近更新：2026-08-10。

## 当前阶段

**software phase-1（backend 抽象骨架）已并入 fork `FAST-CERN/OpenNeck:main`（本地快进，不走 PR，零行为变化）。software phase-2（config-extension）已完成（TDD，31 passed）。下一步 software phase-3（dynamixel-backend）。** 各阶段计划见 [`plan/`](plan/)。

## 工作概述

为 OpenNeck 引入 Dynamixel 后端（vendored `dynamixel_easy_sdk`）并适配 TWIST2 NECK 机械结构，保留 Feetech 后端，公共 API 不变。详见 [`knowledge/twist2-dynamixel-design.md`](knowledge/twist2-dynamixel-design.md)。

## 组件与阶段进度

| 组件 | 阶段 | 状态 | 计划 | 进度 |
|---|---|---|---|---|
| software | phase-1 backend-skeleton | ✅ 完成 (已合入 fork main) | [`plan/software/README.md`](plan/software/README.md) | [`progress/software/phase-1-backend-skeleton.md`](progress/software/phase-1-backend-skeleton.md) |
| software | phase-2 config-extension | ✅ 完成 | 同上 | [`progress/software/phase-2-config-extension.md`](progress/software/phase-2-config-extension.md) |
| software | phase-3 dynamixel-backend | 未开始 | 同上 | 同上 |
| software | phase-4 sdk-wiring | 未开始 | 同上 | 同上 |
| software | phase-5 docs-calibration | 未开始 | 同上 | 同上 |
| hardware | phase-1 twist2-meshes | 未开始 | [`plan/hardware/README.md`](plan/hardware/README.md) | [`progress/hardware/`](progress/hardware/) |
| hardware | phase-2 twist2-sim-models | 未开始 | 同上 | 同上 |

## 关键决策

见设计文档 [§11 决策记录](knowledge/twist2-dynamixel-design.md#11-决策记录)。

## 开放问题

见设计文档 [§12 风险与开放问题](knowledge/twist2-dynamixel-design.md#12-风险与开放问题)。
