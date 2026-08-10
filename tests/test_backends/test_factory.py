from __future__ import annotations
import unittest
from openneck._config import Config
from openneck._backends import make_backend, ServoBackend
from openneck._backends.feetech import FeetechBackend


class MakeBackendTests(unittest.TestCase):
    def test_default_backend_is_feetech(self) -> None:
        backend = make_backend(Config(port="/dev/fake"))
        self.assertIsInstance(backend, FeetechBackend)

    def test_feetech_backend_satisfies_protocol(self) -> None:
        backend = make_backend(Config(port="/dev/fake"))
        self.assertIsInstance(backend, ServoBackend)

    def test_dynamixel_backend_is_selected(self) -> None:
        from openneck._backends.dynamixel import DynamixelBackend

        backend = make_backend(
            Config(port="/dev/fake", servo_backend="dynamixel")
        )
        self.assertIsInstance(backend, DynamixelBackend)
        self.assertIsInstance(backend, ServoBackend)


if __name__ == "__main__":
    unittest.main()
