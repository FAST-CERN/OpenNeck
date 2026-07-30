# OpenNeck Hardware

This directory contains the mechanical resources for OpenNeck:

- [`ASSEMBLY.md`](./ASSEMBLY.md): concise mechanical assembly guide with diagrams.
- [`3d_prints`](./3d_prints/): print-ready STL models and editable STEP models.
- [`simulation`](./simulation/): standalone URDF and MuJoCo models with their shared meshes.

## Sourcing Parts

The quantities below are for one complete 2-DOF OpenNeck assembly. Only China
sourcing links are listed. Prices are reference prices in RMB and may change
depending on the supplier and selected options.

Print one copy of each model listed in the
[3D-printing guide](./3d_prints/README.md). Printing costs are not included.

### Parts for One OpenNeck

| Part | Amount | Unit Cost (RMB) | Buy CN |
|---|---:|---:|---|
| Feetech `ST-3032-C062` servo, 12 V | 2 | ¥188.00 | [Taobao](https://e.tb.cn/h.8aarOVldDyPmC7d?tk=9oH5gqVNnVN) |
| Feetech `FE-URT2-C001` servo control board | 1 | ¥40.00 | [Taobao](https://e.tb.cn/h.8bgrsMrQFWgc4Bu?tk=fTrsgqVpd49) |
| XT30 male pigtail, 18 AWG, 20 cm | 2 | ¥4.58 | [Taobao](https://e.tb.cn/h.8bgsvNociqhA1rM?tk=PMr2gqVqhDb) |
| DC barrel jack screw-terminal adapter, 5.5 × 2.1 mm | 2 | ¥2.33 | [Taobao](https://e.tb.cn/h.8aauTw6872kQeXT?tk=c8MVgqVK6il) |
| Power adapter, 12 V 2 A | 1 | ¥10.50 | [Taobao](https://e.tb.cn/h.8ZCVsDbeUsrlQYd?tk=Ifu1gqVIeB9) |
| Resettable fuse, 12 V 2.5 A / 3 A | 2 | ¥0.18 | [Taobao](https://e.tb.cn/h.8aDYFYCkvzOViZA?tk=wJfwgqVsDQW) |
| Two-core wire | 1 | ¥4.99 | [Taobao](https://e.tb.cn/h.8ZCkGY0SdN1LYgS?tk=LHhUgq4akyX) |
| Intel RealSense `D415` depth camera | 1 | — | — |
| USB Type-C data cable | 1 | ¥21.00 | [JD](https://3.cn/2Vt2Q-om?jkl=@X2ZyIE9EpMwX@) |
| Heat-shrink tubing | 1 | ¥3.80 | [Taobao](https://e.tb.cn/h.8bTq6aqF5lUGayT?tk=9j6bgq4MPNt) |
| Cable ties | 1 | ¥2.02 | [Taobao](https://m.tb.cn/h.8Zy2pTr?tk=olBMgq4qepp) |
| Dupont jumper wires | 1 | ¥3.66 | [Taobao](https://e.tb.cn/h.8bTE4jGComVkq4r?tk=DZcqgq4GnL1) |
| **Known subtotal (excluding D415 and 3D printing)** | — | **¥476.15** | — |

Two servo horns and one adapter board are supplied with the servos. Confirm
that these accessories are included before ordering.

### Required Fasteners

| Fastener | Amount | Purpose |
|---|---:|---|
| `GB/T 845-1985 ST2.2 × 4.5 C-H` self-tapping screw | 12 | Secure both servos and the adapter board |
| `GB/T 818-2000 M6 × 8` screw | 1 | Secure the RealSense D415 |
| `GB/T 818-2000 M3 × 6` screw | 2 | Secure the camera mount |
| `GB/T 818-2000 M3 × 12` screw | 2 | Secure the servo control board |
| `GB/T 6174-2000 M3` thin hex nut | 2 | Used with the M3 × 12 screws |
