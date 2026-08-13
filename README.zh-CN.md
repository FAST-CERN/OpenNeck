# OpenNeck

<p align="center">
  <img src="docs/images/twist2neck-cad-render.png" alt="OpenNeck 二自由度颈部云台 CAD 渲染图" width="58%">
  <img src="docs/images/twist2neck-on-robot.jpg" alt="OpenNeck 二自由度颈部云台装机实拍" width="40%">
</p>

<p align="center">
  <a href="LICENSE"><img alt="version" src="https://img.shields.io/badge/version-0.3.0-blue"></a>
  <a href="LICENSE"><img alt="license" src="https://img.shields.io/badge/license-Apache--2.0-green"></a>
  <img alt="python" src="https://img.shields.io/badge/python-%3E%3D3.10-blue">
  <img alt="servos" src="https://img.shields.io/badge/servos-Feetech%20%7C%20Dynamixel-orange">
</p>

<p align="center">
  <strong>语言：</strong>
  <a href="README.md">English</a> · <strong>中文</strong>
</p>

OpenNeck 是一个开源的二自由度机器人颈部云台。本仓库提供可 3D 打印的机械零件、基于物理角度的软件驱动，以及独立的 URDF 和 MuJoCo 仿真模型。

## 特性

- **机械硬件**：可编辑的 STEP 模型、可直接打印的 STL 模型、采购清单和装配说明。
- **软件驱动**：Python API、命令行工具、舵机维护工具，以及居中 / 机械限位标定。通过 `servo_backend` 配置字段同时支持 Feetech 和 Dynamixel 舵机。
- **仿真模型**：独立的 URDF 和 MuJoCo XML 模型及其配套 mesh。

## 快速开始

```bash
git clone --recurse-submodules https://github.com/FAST-CERN/OpenNeck.git
cd OpenNeck
pip install ".[dynamixel]"   # Feetech + Dynamixel；仅 Feetech 用 `pip install .`
```

随后按 [软件驱动文档](docs/zh-CN/software.md) 分配舵机 ID 并完成标定。

## 文档

| 主题 | English | 中文 |
|---|---|---|
| 软件 —— 安装、标定、配置、CLI、API | [Software](docs/en/software.md) | [软件](docs/zh-CN/software.md) |
| 硬件 —— 采购与 3D 打印 | [Hardware](docs/en/hardware.md) | [硬件](docs/zh-CN/hardware.md) |
| 机械装配 | [Assembly](docs/en/assembly.md) | [装配](docs/zh-CN/assembly.md) |
| 部署到既有环境（如 `teleopit`） | [Deployment](docs/en/deployment-teleopit.md) | [部署](docs/zh-CN/deployment-teleopit.md) |
| 从上游 BotRunner64 升级（API 变化） | [Migration](docs/en/migration-from-upstream.md) | [迁移](docs/zh-CN/migration-from-upstream.md) |
| URDF 模型 | [openneck.urdf](hardware/simulation/openneck.urdf) | — |
| MuJoCo 模型 | [openneck.xml](hardware/simulation/openneck.xml) | — |

## 上手指南

克隆时加 `--recurse-submodules` 以拉取 Dynamixel SDK，或克隆后执行 `git submodule update --init --recursive`。

首次搭建 OpenNeck 时，按顺序参考以下文档：

1. 用 [硬件准备](docs/zh-CN/hardware.md) 采购元件并打印结构件。
2. 按 [机械装配](docs/zh-CN/assembly.md) 组装云台。
3. 按 [软件驱动](docs/zh-CN/software.md) 安装驱动、分配舵机 ID 并完成标定。

## 开发者

内部文档索引（设计合同、计划、进度、状态）：[`docs/README.md`](docs/README.md)。

## 致谢

OpenNeck 的硬件设计与实现由 [zc-xzc](https://github.com/zc-xzc) 完成。

## 许可证

本项目基于 [Apache License 2.0](LICENSE) 授权。
