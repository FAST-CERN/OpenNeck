# hardware 组件计划

[计划路由](../README.md) · [设计合同](../../knowledge/twist2-dynamixel-design.md) · [进度](../../progress/hardware/README.md) · [状态](../../STATUS.md)

`hardware/` 的 TWIST2 NECK 机械结构与仿真模型。保留原 `hardware/`（Feetech 设计），新增 `hardware/twist2/`。

| 阶段 | 主题 | 状态 |
|---|---|---|
| `phase-1-twist2-meshes` | 建 `hardware/twist2/{cad,3d_prints,simulation/meshes}`；CAD→STL（打印件 + 视觉/碰撞 mesh） | 未开始 |
| `phase-2-twist2-sim-models` | 复用 yaw/pitch 运动学模板更新 `twist2.urdf` / `twist2.xml`（mesh 引用 + joint range）；MuJoCo 加载冒烟 | 未开始 |

产物清单（mesh 转换）：

- `hardware/twist2/cad/*.step` — 源 CAD（用户提供）
- `hardware/twist2/3d_prints/*.stl` — 打印件
- `hardware/twist2/simulation/meshes/*.stl` — 视觉 / 碰撞 mesh
- `hardware/twist2/simulation/twist2.urdf` / `twist2.xml` — 仿真模型

各阶段详情见同目录 `phase-*.md`（由 writing-plans 产出）。
