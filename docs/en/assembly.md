# OpenNeck Mechanical Assembly

[Home](../../README.md) · [Software](./software.md) · [Hardware](./hardware.md) · [Assembly](./assembly.md) · [Deployment](./deployment-teleopit.md) · [Migration](./migration-from-upstream.md) · **English** · [中文](../zh-CN/assembly.md)

Keep the system powered off throughout assembly. First identify three directions: the D415 lenses face forward, the yaw servo output shaft points up, and the pitch servo output shaft is horizontal.

![OpenNeck exploded view](../images/assembly-exploded.jpg)

## Preparation

Print one copy of each part: `base_mount`, `pitch_mount`, `camera_mount`, and `pitch_pivot`. You also need two ST-3032 servos, two servo horns, a D415, a URT-2, and a servo adapter board; see [Hardware Preparation](./hardware.md) for the complete list.

Remove supports and burrs from the printed parts, then sort the screws by purpose:

| Screw | Quantity | Purpose |
|---|---:|---|
| ST2.2 × 4.5 self-tapping screw | 12 | Both servos and the servo adapter board |
| M6 × 8 | 1 | D415 |
| M3 × 6 | 2 | Camera mount |
| M3 × 12 + M3 thin hex nut | 2 each | URT-2 |

## 1. Assemble the Base

1. Place the yaw servo in the rear recess of `base_mount`, with its output shaft pointing up, and secure it with four ST2.2 × 4.5 screws.
2. Install the servo adapter board outside the recess, with its connectors facing outward, and secure it with four ST2.2 × 4.5 screws.
3. Fit the yaw servo horn onto the output shaft, but do not fully tighten it yet.
4. Install the URT-2 underneath the front of the base with two M3 × 12 screws and two M3 thin hex nuts.

## 2. Assemble the Upper Module

1. Place the pitch servo horizontally in `pitch_mount` and secure it with the remaining four ST2.2 × 4.5 screws.
2. Place the D415 on `camera_mount` with its lenses facing forward, then insert one M6 × 8 screw from underneath.
3. Place `camera_mount` between the two arms of `pitch_mount`: install the servo horn on the servo side and insert `pitch_pivot` from the other side.
4. After confirming that both sides are coaxial, secure the camera mount with two M3 × 6 screws. Do not fully tighten the pitch servo horn yet.

![OpenNeck upper-module orientation](../images/assembly-upper-module.jpg)

## 3. Join the Modules

1. Keep the lenses facing forward and position the upper module directly above the yaw servo.
2. Align the yaw servo horn with the bottom mounting hole, keep the upper module level, and press it straight down.
3. Once both mounting surfaces are flush, tighten the supplied fasteners on the yaw and pitch servo horns.

![Joining the OpenNeck modules](../images/assembly-join.jpg)

## 4. Check the Assembly

With the power off, slowly move the yaw and pitch axes by hand:

- Both axes should move smoothly without collisions, scraping, or binding.
- The D415 should be centered with an unobstructed view.
- The servos, servo horns, and both circuit boards should be secure.
- The cables should not become taut or pinched anywhere in the full motion range.

![Completed OpenNeck assembly](../images/assembly-finished.jpg)

> Tighten self-tapping screws only until their heads make contact; overtightening can crack the printed parts. Use only an M6 × 8 screw for the D415—do not substitute a longer screw.
