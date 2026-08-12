# OpenNeck 文档索引

[返回根 README](../README.md) · [项目状态](./STATUS.md) · [English](../README.md)

本目录是 OpenNeck **TWIST2 NECK + Dynamixel 适配**工作的文档根。结构遵循 [`knowledge/ref/doc-conventions.md`](knowledge/ref/doc-conventions.md)。

> **获取代码（含 Dynamixel SDK 子模块）**：`git clone --recurse-submodules <repo>`，或克隆后 `git submodule update --init --recursive`。

## 目录布局

```
docs/
  README.md            本索引 + 权威源表（本文件）
  STATUS.md            唯一项目状态源
  knowledge/           长期参考：设计合同、机制说明、约定
    twist2-dynamixel-design.md   适配工程合同（权威设计）
    config-dataflow.md           配置数据流（加载/校验/override/后端选择）
    twist2-servo-config.md       TWIST2 舵机硬件配置（ID/零位/限位/参数）
    ref/                         约定样例（doc-conventions、AGENTS-ref）
  plan/                计划（打算怎么做）
    software/          openneck Python 包：phase-1..5
    hardware/          hardware/ 机械与仿真：phase-1..2
  progress/            进度（实际做了什么）
    software/
    hardware/
  todo/
    todolist.md        待办 / 未采纳点子汇总
  en/  zh-CN/  images/ 用户向说明文档（既有）
```

## 权威源表（单一事实源）

| 事实 | 唯一归属 |
|---|---|
| 适配设计 / 工程合同 | [`knowledge/twist2-dynamixel-design.md`](knowledge/twist2-dynamixel-design.md) |
| 配置数据流机制 | [`knowledge/config-dataflow.md`](knowledge/config-dataflow.md) |
| TWIST2 舵机硬件配置 | [`knowledge/twist2-servo-config.md`](knowledge/twist2-servo-config.md) |
| 项目状态 | [`STATUS.md`](STATUS.md) |
| 工作区硬性规则 | [`../AGENTS.md`](../AGENTS.md) |
| 文档结构约定 | [`knowledge/ref/doc-conventions.md`](knowledge/ref/doc-conventions.md) |
| 软件阶段计划 | [`plan/software/README.md`](plan/software/README.md) |
| 硬件阶段计划 | [`plan/hardware/README.md`](plan/hardware/README.md) |
| 待办 / 点子 | [`todo/todolist.md`](todo/todolist.md) |
| 软件使用说明 | [`en/software.md`](en/software.md) · [`zh-CN/software.md`](zh-CN/software.md) |
| 部署到既有环境（teleopit 等） | [`en/deployment-teleopit.md`](en/deployment-teleopit.md) · [`zh-CN/deployment-teleopit.md`](zh-CN/deployment-teleopit.md) |
| 从上游 BotRunner64 升级（API 变化） | [`en/migration-from-upstream.md`](en/migration-from-upstream.md) · [`zh-CN/migration-from-upstream.md`](zh-CN/migration-from-upstream.md) |

其余位置**只链接**，不抄写具体值（测试数字、版本号、量程、机器路径）。
