from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from openneck._config import Config, load_config


class ConfigTests(unittest.TestCase):
    def test_loads_only_current_schema(self) -> None:
        data = {
            "port": "/dev/test",
            "baudrate": 1_000_000,
            "yaw_id": 3,
            "pitch_id": 4,
            "yaw_center_step": 2000,
            "yaw_min_step": 1000,
            "yaw_max_step": 3000,
            "yaw_step_sign": -1,
            "pitch_center_step": 2100,
            "pitch_min_step": 1200,
            "pitch_max_step": 2800,
            "pitch_step_sign": 1,
            "speed": 20,
            "acceleration": 10,
            "servo_backend": "dynamixel",
            "operating_mode": 4,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            config = load_config(path)

        self.assertEqual(config.yaw_center_step, 2000)
        self.assertEqual(config.yaw_step_sign, -1)
        self.assertEqual(config.pitch_id, 4)
        self.assertEqual(config.servo_backend, "dynamixel")

    def test_unknown_fields_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text('{"obsolete_field": true}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "obsolete_field"):
                load_config(path)

    def test_explicit_missing_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.json"
            with self.assertRaises(FileNotFoundError):
                load_config(path)

    def test_axis_direction_and_bounds_are_validated(self) -> None:
        with self.assertRaises(ValueError):
            Config(yaw_step_sign=0)
        with self.assertRaises(ValueError):
            Config(yaw_step_sign=True)
        with self.assertRaises(ValueError):
            Config(yaw_min_step=3000, yaw_center_step=2000)
        with self.assertRaises(ValueError):
            Config(yaw_id=2, pitch_id=2)

    def test_servo_id_zero_is_allowed(self) -> None:
        # Dynamixel IDs are 0..252; ID 0 is valid (TWIST2 yaw uses it).
        cfg = Config(yaw_id=0, pitch_id=1)
        self.assertEqual(cfg.yaw_id, 0)
        cfg_pitch_zero = Config(yaw_id=1, pitch_id=0)
        self.assertEqual(cfg_pitch_zero.pitch_id, 0)

    def test_motion_packet_fields_are_range_checked(self) -> None:
        Config(speed=65_535, acceleration=255)
        with self.assertRaises(ValueError):
            Config(speed=65_536)
        with self.assertRaises(ValueError):
            Config(acceleration=256)

    def test_backend_defaults_to_feetech(self) -> None:
        self.assertEqual(Config().servo_backend, "feetech")
        self.assertEqual(Config().operating_mode, 3)

    def test_backend_field_is_validated(self) -> None:
        with self.assertRaises(ValueError):
            Config(servo_backend="bogus")

    def test_operating_mode_is_validated(self) -> None:
        Config(operating_mode=4)
        with self.assertRaises(ValueError):
            Config(operating_mode=2)
        with self.assertRaises(ValueError):
            Config(operating_mode=True)  # bool must be rejected

    def test_profile_fields_are_non_negative(self) -> None:
        Config(profile_velocity=0, profile_acceleration=0)
        with self.assertRaises(ValueError):
            Config(profile_velocity=-1)
        with self.assertRaises(ValueError):
            Config(profile_acceleration=-1)

    def test_pid_fields_default_zero_and_validated(self) -> None:
        self.assertEqual(Config().yaw_kp, 0)
        self.assertEqual(Config().pitch_kd, 0)
        Config(yaw_kp=800, yaw_ki=5, yaw_kd=5, pitch_kp=640, pitch_ki=0, pitch_kd=1600)
        with self.assertRaises(ValueError):
            Config(yaw_kp=-1)
        with self.assertRaises(ValueError):
            Config(pitch_ki=99999)  # > 16383 (Dynamixel gain range)


if __name__ == "__main__":
    unittest.main()
