# OpenNeck 硬件准备

[主页](../../README.md) · [软件](./software.md) · [硬件](./hardware.md) · [装配](./assembly.md) · [English](../en/hardware.md) · **中文**

本页汇总 OpenNeck 的机械资源、采购清单、紧固件和 3D 打印文件。

## 机械资源

- [3D 打印文件](../../hardware/3d_prints/)：可直接切片的 STL 模型和可编辑的 STEP 模型。
- [仿真模型](../../hardware/simulation/)：独立的 URDF、MuJoCo 模型及共用网格。
- [机械装配](./assembly.md)：带示意图的简明安装步骤。

## 采购清单

以下数量可组装一套完整的两自由度 OpenNeck。目前只列出中国大陆采购链接。价格以人民币计，仅供参考，可能随供应商和所选规格变化。

每种[打印件](#3d-打印)各打印 1 个；下表合计不含打印费用。

### 一套 OpenNeck 所需零件

| 零件 | 数量 | 单价（人民币） | 中国大陆购买链接 |
|---|---:|---:|---|
| Feetech `ST-3032-C062` 舵机，12 V | 2 | ¥188.00 | [淘宝](https://e.tb.cn/h.8aarOVldDyPmC7d?tk=9oH5gqVNnVN) |
| Feetech `FE-URT2-C001` 舵机控制板 | 1 | ¥40.00 | [淘宝](https://e.tb.cn/h.8bgrsMrQFWgc4Bu?tk=fTrsgqVpd49) |
| XT30 公头尾线，18 AWG，20 cm | 2 | ¥4.58 | [淘宝](https://e.tb.cn/h.8bgsvNociqhA1rM?tk=PMr2gqVqhDb) |
| DC 5.5 × 2.1 mm 母座转螺丝端子 | 2 | ¥2.33 | [淘宝](https://e.tb.cn/h.8aauTw6872kQeXT?tk=c8MVgqVK6il) |
| 12 V 2 A 电源适配器 | 1 | ¥10.50 | [淘宝](https://e.tb.cn/h.8ZCVsDbeUsrlQYd?tk=Ifu1gqVIeB9) |
| 12 V 2.5 A / 3 A 自恢复保险丝 | 2 | ¥0.18 | [淘宝](https://e.tb.cn/h.8aDYFYCkvzOViZA?tk=wJfwgqVsDQW) |
| 两芯线 | 1 | ¥4.99 | [淘宝](https://e.tb.cn/h.8ZCkGY0SdN1LYgS?tk=LHhUgq4akyX) |
| Intel RealSense `D415` 深度相机 | 1 | — | — |
| USB Type-C 数据线 | 1 | ¥21.00 | [京东](https://3.cn/2Vt2Q-om?jkl=@X2ZyIE9EpMwX@) |
| 热缩管 | 1 | ¥3.80 | [淘宝](https://e.tb.cn/h.8bTq6aqF5lUGayT?tk=9j6bgq4MPNt) |
| 扎带 | 1 | ¥2.02 | [淘宝](https://m.tb.cn/h.8Zy2pTr?tk=olBMgq4qepp) |
| 杜邦线 | 1 | ¥3.66 | [淘宝](https://e.tb.cn/h.8bTE4jGComVkq4r?tk=DZcqgq4GnL1) |
| **已知合计（不含 D415 和 3D 打印）** | — | **¥476.15** | — |

舵机附带 2 个舵盘和 1 块转接板，下单前请确认配件齐全。

### 紧固件

| 紧固件 | 数量 | 用途 |
|---|---:|---|
| `GB/T 845-1985 ST2.2 × 4.5 C-H` 自攻螺丝 | 12 | 固定两个舵机和转接板 |
| `GB/T 818-2000 M6 × 8` 螺丝 | 1 | 固定 RealSense D415 |
| `GB/T 818-2000 M3 × 6` 螺丝 | 2 | 固定摄像头支架 |
| `GB/T 818-2000 M3 × 12` 螺丝 | 2 | 固定舵机控制板 |
| `GB/T 6174-2000 M3` 薄六角螺母 | 2 | 与 M3 × 12 螺丝配合使用 |

## 3D 打印

每个打印件均提供 STL 和 STEP 两种格式：

| 零件 | STL | STEP |
|---|---|---|
| 底座 | [base_mount.stl](../../hardware/3d_prints/base_mount.stl) | [base_mount.step](../../hardware/3d_prints/base_mount.step) |
| 俯仰支架 | [pitch_mount.stl](../../hardware/3d_prints/pitch_mount.stl) | [pitch_mount.step](../../hardware/3d_prints/pitch_mount.step) |
| 摄像头支架 | [camera_mount.stl](../../hardware/3d_prints/camera_mount.stl) | [camera_mount.step](../../hardware/3d_prints/camera_mount.step) |
| 俯仰从动轴 | [pitch_pivot.stl](../../hardware/3d_prints/pitch_pivot.stl) | [pitch_pivot.step](../../hardware/3d_prints/pitch_pivot.step) |

切片和打印时使用 STL；需要查看尺寸、安装孔位或修改结构时使用 STEP。每种零件打印 1 个。
