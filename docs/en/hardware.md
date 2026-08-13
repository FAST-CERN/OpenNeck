# OpenNeck Hardware Preparation

[Home](../../README.md) · [Software](./software.md) · [Hardware](./hardware.md) · [Assembly](./assembly.md) · [Deployment](./deployment-teleopit.md) · [Migration](./migration-from-upstream.md) · **English** · [中文](../zh-CN/hardware.md)

This page collects OpenNeck's mechanical resources, sourcing list, fasteners, and 3D-printing files.

## Mechanical Resources

- [3D-printing files](../../hardware/3d_prints/): print-ready STL models and editable STEP models.
- [Simulation models](../../hardware/simulation/): standalone URDF and MuJoCo models with their shared meshes.
- [Mechanical Assembly](./assembly.md): concise installation steps with diagrams.

## Sourcing List

The quantities below build one complete 2-DoF OpenNeck. Only mainland China sourcing links are currently listed. Prices are reference prices in RMB and may change with the supplier and selected specifications.

Print one copy of each [3D-printed part](#3d-printing); printing costs are not included in the subtotal below.

### Parts for One OpenNeck

| Part | Quantity | Unit Price (RMB) | Buy in Mainland China |
|---|---:|---:|---|
| Feetech `ST-3032-C062` servo, 12 V | 2 | ¥188.00 | [Taobao](https://e.tb.cn/h.8aarOVldDyPmC7d?tk=9oH5gqVNnVN) |
| Feetech `FE-URT2-C001` servo control board | 1 | ¥40.00 | [Taobao](https://e.tb.cn/h.8bgrsMrQFWgc4Bu?tk=fTrsgqVpd49) |
| XT30 male pigtail, 18 AWG, 20 cm | 2 | ¥4.58 | [Taobao](https://e.tb.cn/h.8bgsvNociqhA1rM?tk=PMr2gqVqhDb) |
| DC 5.5 × 2.1 mm barrel jack to screw-terminal adapter | 2 | ¥2.33 | [Taobao](https://e.tb.cn/h.8aauTw6872kQeXT?tk=c8MVgqVK6il) |
| 12 V 2 A power adapter | 1 | ¥10.50 | [Taobao](https://e.tb.cn/h.8ZCVsDbeUsrlQYd?tk=Ifu1gqVIeB9) |
| 12 V 2.5 A / 3 A resettable fuse | 2 | ¥0.18 | [Taobao](https://e.tb.cn/h.8aDYFYCkvzOViZA?tk=wJfwgqVsDQW) |
| Two-core wire | 1 | ¥4.99 | [Taobao](https://e.tb.cn/h.8ZCkGY0SdN1LYgS?tk=LHhUgq4akyX) |
| Intel RealSense `D415` depth camera | 1 | — | — |
| USB Type-C data cable | 1 | ¥21.00 | [JD](https://3.cn/2Vt2Q-om?jkl=@X2ZyIE9EpMwX@) |
| Heat-shrink tubing | 1 | ¥3.80 | [Taobao](https://e.tb.cn/h.8bTq6aqF5lUGayT?tk=9j6bgq4MPNt) |
| Cable ties | 1 | ¥2.02 | [Taobao](https://m.tb.cn/h.8Zy2pTr?tk=olBMgq4qepp) |
| Dupont jumper wires | 1 | ¥3.66 | [Taobao](https://e.tb.cn/h.8bTE4jGComVkq4r?tk=DZcqgq4GnL1) |
| **Known subtotal (excluding D415 and 3D printing)** | — | **¥476.15** | — |

The servos include two servo horns and one adapter board. Confirm that all accessories are included before ordering.

### Fasteners

| Fastener | Quantity | Purpose |
|---|---:|---|
| `GB/T 845-1985 ST2.2 × 4.5 C-H` self-tapping screw | 12 | Secure both servos and the adapter board |
| `GB/T 818-2000 M6 × 8` screw | 1 | Secure the RealSense D415 |
| `GB/T 818-2000 M3 × 6` screw | 2 | Secure the camera mount |
| `GB/T 818-2000 M3 × 12` screw | 2 | Secure the servo control board |
| `GB/T 6174-2000 M3` thin hex nut | 2 | Use with the M3 × 12 screws |

## 3D Printing

Each printable part is provided in STL and STEP formats:

| Part | STL | STEP |
|---|---|---|
| Base mount | [base_mount.stl](../../hardware/3d_prints/base_mount.stl) | [base_mount.step](../../hardware/3d_prints/base_mount.step) |
| Pitch mount | [pitch_mount.stl](../../hardware/3d_prints/pitch_mount.stl) | [pitch_mount.step](../../hardware/3d_prints/pitch_mount.step) |
| Camera mount | [camera_mount.stl](../../hardware/3d_prints/camera_mount.stl) | [camera_mount.step](../../hardware/3d_prints/camera_mount.step) |
| Passive pitch pivot | [pitch_pivot.stl](../../hardware/3d_prints/pitch_pivot.stl) | [pitch_pivot.step](../../hardware/3d_prints/pitch_pivot.step) |

Use the STL files for slicing and printing. Use the STEP files to inspect dimensions or mounting features, or to modify the structure. Print one copy of each part.
