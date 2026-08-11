#!/usr/bin/env python3
"""OpenNeck 机械限位测试脚本。

两段式：

1. 离线裁剪验证（默认运行，不连硬件）——用 `active_vision_config.json`
   的 `center/min/max/step_sign` 调 `angle_to_step`，验证超限角度被裁到
   `min_step`/`max_step`。
2. 真机渐进逼近（需 `--real`，操作员在场）——`OpenNeckController` 连真机，
   对每个限位按 30/60/90/100% 渐进，每步操作员回车确认，Ctrl-C 中止。

读 cwd 的 `active_vision_config.json`。真机段遵循 AGENTS.md 规则 5
（操作员在场）。用法：

    python scripts/test_limits.py            # 仅离线裁剪验证
    python scripts/test_limits.py --real     # 加真机渐进逼近
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openneck import OpenNeckController
from openneck._angles import angle_to_step
from openneck._config import Config, load_config


# 限位（deg，相对中位）。顺序：先 yaw 再 pitch，每轴先正后负。
LIMITS: list[tuple[str, float]] = [
    ("yaw", 50.0),
    ("yaw", -50.0),
    ("pitch", 90.0),
    ("pitch", -10.0),
]
RATIOS = [0.3, 0.6, 0.9, 1.0]


def settle_read(
    neck: OpenNeckController,
    axis: str,
    *,
    timeout: float = 5.0,
    tol_deg: float = 0.3,
    interval: float = 0.15,
) -> tuple[float, bool]:
    """轮询 read_deg 直到位置收敛（连续两次差 < tol）或超时。

    OpenNeck 的 write_positions 是异步下目标、不等到位；调用方要测稳态
    必须自己等。返回 (收敛角度, 是否在超时前收敛)。
    """
    prev = getattr(neck.read_deg(), f"{axis}_deg")
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(interval)
        cur = getattr(neck.read_deg(), f"{axis}_deg")
        if abs(cur - prev) < tol_deg:
            return cur, True
        prev = cur
    return prev, False


def verify_clamp(cfg: Config) -> bool:
    """离线验证：两个方向的超限请求应分别裁到 min_step 与 max_step。

    不依赖 step_sign 的方向——只要求两个端点都被命中。
    """
    axes = [
        ("yaw", cfg.yaw_center_step, cfg.yaw_min_step, cfg.yaw_max_step, cfg.yaw_step_sign),
        ("pitch", cfg.pitch_center_step, cfg.pitch_min_step, cfg.pitch_max_step, cfg.pitch_step_sign),
    ]
    all_pass = True
    for axis, center, lo, hi, sign in axes:
        over_pos = angle_to_step(360.0, center_step=center, min_step=lo, max_step=hi, step_sign=sign)
        over_neg = angle_to_step(-360.0, center_step=center, min_step=lo, max_step=hi, step_sign=sign)
        hit_endpoints = {over_pos, over_neg} == {lo, hi}
        all_pass = all_pass and hit_endpoints
        status = "PASS" if hit_endpoints else "FAIL"
        print(
            f"  [{status}] {axis}: +360°→{over_pos}, -360°→{over_neg} "
            f"(期望端点 {{{lo}, {hi}}})"
        )
    return all_pass


def run_real() -> None:
    """真机渐进逼近每个限位。每步操作员 Enter；Ctrl-C 中止并释放扭矩。"""
    print("\n=== 真机渐进限位 ===")
    print("操作员请看住云台。每步回车继续，Ctrl-C 立即中止（会释放扭矩再关端口）。")

    results: list[tuple[str, float, float, float]] = []
    neck = OpenNeckController()
    neck.connect()
    try:
        print("[center] 回中")
        neck.center()
        for axis, limit_deg in LIMITS:
            for ratio in RATIOS:
                target = limit_deg * ratio
                pct = int(ratio * 100)
                print(f"\n即将移动: {axis} 限位 {limit_deg:+.0f}° @ {pct}% = {target:+.1f}°")
                try:
                    input("  Enter 继续，Ctrl-C 中止 ... ")
                except EOFError:
                    print("\n[abort] 无终端输入，中止。")
                    return
                applied = neck._move_axis_deg(axis, target)
                actual, settled = settle_read(neck, axis)
                delta = actual - applied
                flag = "" if settled else " (未收敛)"
                print(f"  applied={applied:+.2f}°  readback={actual:+.2f}°  偏差={delta:+.2f}°{flag}")
                results.append((f"{axis} {limit_deg:+.0f}@{pct}%", target, applied, actual))
            print(f"[center] {axis} 测完，回中")
            neck.center()

        print("\n=== 真机汇总 ===")
        for label, target, applied, actual in results:
            print(f"  {label:>18}  target={target:+.1f}°  applied={applied:+.2f}°  readback={actual:+.2f}°")
        print("[done] 全部完成")
    except KeyboardInterrupt:
        print("\n[abort] 收到 Ctrl-C，中止")
    finally:
        try:
            neck.release_torque()
        except Exception as exc:
            print(f"[warn] release_torque: {exc!r}")
        neck.close()


def main() -> None:
    cfg = load_config()
    print("配置（来自 active_vision_config.json）:")
    print(f"  backend={cfg.servo_backend}  yaw_id={cfg.yaw_id}  pitch_id={cfg.pitch_id}")
    print(
        f"  yaw   center={cfg.yaw_center_step} min={cfg.yaw_min_step} "
        f"max={cfg.yaw_max_step} sign={cfg.yaw_step_sign}"
    )
    print(
        f"  pitch center={cfg.pitch_center_step} min={cfg.pitch_min_step} "
        f"max={cfg.pitch_max_step} sign={cfg.pitch_step_sign}"
    )

    print("\n=== 离线裁剪验证 ===")
    clamp_ok = verify_clamp(cfg)
    print(f"裁剪验证: {'全 PASS' if clamp_ok else '有 FAIL — 检查 Config 的 min/max/sign'}")

    if "--real" not in sys.argv:
        print("\n真机段未开启（需 --real，且操作员在场）。结束。")
        return
    if cfg.servo_backend != "dynamixel":
        print(f"\n真机段仅对 dynamixel 后端验证（当前 {cfg.servo_backend}），跳过。")
        return
    run_real()


if __name__ == "__main__":
    main()
