from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import call, patch

import openneck.cli as cli
from openneck import NeckAngles
from openneck._config import Config


class FakeController:
    def __init__(self) -> None:
        self.axis_moves: list[tuple[str, float]] = []

    def __enter__(self) -> "FakeController":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pass

    def read_voltage(self) -> dict[str, float]:
        return {"yaw": 12.1, "pitch": 12.2}

    def read_deg(self) -> NeckAngles:
        return NeckAngles(1.0, -2.0)

    def _move_axis_deg(self, axis: str, angle_deg: float) -> float:
        self.axis_moves.append((axis, angle_deg))
        return angle_deg


class AngleCliTests(unittest.TestCase):
    def test_motion_test_cli_accepts_angles(self) -> None:
        args = cli.build_parser().parse_args(
            ["test", "yaw", "--angle-deg", "6.5"]
        )
        self.assertEqual(args.angle_deg, 6.5)

    def test_voltage_connects_without_enabling_torque(self) -> None:
        args = cli.build_parser().parse_args(["voltage"])
        config = Config(port="/dev/fake")
        controller = FakeController()

        with (
            patch.object(cli, "with_overrides", return_value=config),
            patch.object(
                cli,
                "_controller_from_config",
                return_value=controller,
            ) as factory,
            redirect_stdout(io.StringIO()),
        ):
            cli.cmd_voltage(args)

        factory.assert_called_once_with(
            config, enable_torque_on_connect=False
        )

    def test_motion_test_commands_only_the_selected_axis(self) -> None:
        args = cli.build_parser().parse_args(
            ["test", "pitch", "--angle-deg", "6.5"]
        )
        config = Config(port="/dev/fake")
        controller = FakeController()

        with (
            patch.object(cli, "with_overrides", return_value=config),
            patch.object(
                cli,
                "_controller_from_config",
                return_value=controller,
            ),
            patch.object(cli.time, "sleep") as sleep,
            redirect_stdout(io.StringIO()),
        ):
            cli.cmd_test(args)

        self.assertEqual(
            controller.axis_moves,
            [
                ("pitch", 0.0),
                ("pitch", 6.5),
                ("pitch", -6.5),
                ("pitch", 0.0),
            ],
        )
        self.assertEqual(sleep.call_args_list, [call(1.0)] * 4)

    def test_backend_and_profile_flags_parse(self) -> None:
        args = cli.build_parser().parse_args(
            [
                "config",
                "--servo-backend",
                "dynamixel",
                "--operating-mode",
                "4",
                "--profile-velocity",
                "100",
                "--profile-acceleration",
                "10",
            ]
        )
        self.assertEqual(args.servo_backend, "dynamixel")
        self.assertEqual(args.operating_mode, 4)
        self.assertEqual(args.profile_velocity, 100)
        self.assertEqual(args.profile_acceleration, 10)

    def test_with_overrides_threads_backend_fields(self) -> None:
        args = cli.build_parser().parse_args(
            [
                "config",
                "--servo-backend",
                "dynamixel",
                "--profile-velocity",
                "100",
            ]
        )
        cfg = cli.with_overrides(args, allow_missing=True)
        self.assertEqual(cfg.servo_backend, "dynamixel")
        self.assertEqual(cfg.profile_velocity, 100)

    def test_pid_flags_parse_and_override(self) -> None:
        args = cli.build_parser().parse_args(
            ["config", "--yaw-kp", "800", "--pitch-kd", "1600"]
        )
        self.assertEqual(args.yaw_kp, 800)
        self.assertEqual(args.pitch_kd, 1600)
        cfg = cli.with_overrides(args, allow_missing=True)
        self.assertEqual(cfg.yaw_kp, 800)
        self.assertEqual(cfg.pitch_kd, 1600)


if __name__ == "__main__":
    unittest.main()
