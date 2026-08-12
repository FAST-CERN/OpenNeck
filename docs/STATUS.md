# 项目状态（唯一源）

> 本文件是 OpenNeck TWIST2 + Dynamixel 适配的唯一状态源。最近更新：2026-08-12。

## 当前阶段

**software 组件 phase-1～5 全部完成**（已并入 fork `FAST-CERN/OpenNeck:main`，本地快进、不走 PR）。phase-4 真机冒烟通过（2026-08-11，Dynamixel XC330-T288 ×2，R1–R4 闭环）；真机 smoke 后暴露的 5 个软件 gap（G1–G5：servo ID 0、`profile`/PID 写入、超 `Max/Min Position Limit` 显式报错、profile 取整）全部闭环（2026-08-12）。**下一步：hardware phase-1（twist2-meshes）。** 各阶段计划见 [`plan/`](plan/)。

## 工作概述

为 OpenNeck 引入 Dynamixel 后端（vendored `dynamixel_easy_sdk`）并适配 TWIST2 NECK 机械结构，保留 Feetech 后端，公共 API 不变。详见 [`knowledge/twist2-dynamixel-design.md`](knowledge/twist2-dynamixel-design.md)。

## 组件与阶段进度

| 组件 | 阶段 | 状态 | 计划 | 进度 |
|---|---|---|---|---|
| software | phase-1 backend-skeleton | ✅ 完成 (已合入 fork main) | [`plan/software/README.md`](plan/software/README.md) | [`progress/software/phase-1-backend-skeleton.md`](progress/software/phase-1-backend-skeleton.md) |
| software | phase-2 config-extension | ✅ 完成 | 同上 | [`progress/software/phase-2-config-extension.md`](progress/software/phase-2-config-extension.md) |
| software | phase-3 dynamixel-backend | ✅ 完成 | 同上 | [`progress/software/phase-3-dynamixel-backend.md`](progress/software/phase-3-dynamixel-backend.md) |
| software | phase-4 sdk-wiring | ✅ 完成 | 同上 | [`progress/software/phase-4-sdk-wiring.md`](progress/software/phase-4-sdk-wiring.md) |
| software | phase-5 docs-calibration | ✅ 完成 | 同上 | [`progress/software/phase-5-docs-calibration.md`](progress/software/phase-5-docs-calibration.md) |
| hardware | phase-1 twist2-meshes | 未开始 | [`plan/hardware/README.md`](plan/hardware/README.md) | [`progress/hardware/`](progress/hardware/) |
| hardware | phase-2 twist2-sim-models | 未开始 | 同上 | 同上 |

## 关键决策

见设计文档 [§11 决策记录](knowledge/twist2-dynamixel-design.md#11-决策记录)。

## 开放问题

见设计文档 [§12 风险与开放问题](knowledge/twist2-dynamixel-design.md#12-风险与开放问题)。
