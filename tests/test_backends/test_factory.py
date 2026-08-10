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

    def test_dynamixel_backend_not_implemented(self) -> None:
        # Phase 2 wires only Feetech; Dynamixel lands in phase-3. Using
        # "dynamixel" (valid to Config) ensures this exercises the factory
        # branch, not Config's own validation.
        with self.assertRaises(ValueError):
            make_backend(Config(port="/dev/fake", servo_backend="dynamixel"))


if __name__ == "__main__":
    unittest.main()
