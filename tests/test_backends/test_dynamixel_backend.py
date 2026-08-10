from __future__ import annotations

import sys
import types
import unittest
from enum import IntEnum
from unittest.mock import patch

from openneck._config import Config


def make_fake_easy_sdk():
    """Minimal fake of dynamixel_easy_sdk exercising the backend paths.

    Mirrors the surface of the vendored real SDK (see
    thirdparty/DynamixelSDK/python/src/dynamixel_easy_sdk/): Connector,
    Motor, GroupExecutor, and OperatingMode as an IntEnum.
    """
    state = {
        "port": None,
        "baudrate": None,
        "motors": {},          # id -> FakeMotor
        "fail_create": None,   # id whose createMotor raises
        "closed": False,
        "writes": [],          # list of {id: position}
        "positions": {},       # id -> present position
    }

    class OperatingMode(IntEnum):
        CURRENT = 0
        VELOCITY = 1
        POSITION = 3
        EXTENDED_POSITION = 4
        CURRENT_BASED_POSITION = 5
        PWM = 16

    class StagedCommand:
        def __init__(self, command_type, id_, address, length, data, *rest):
            self.command_type = command_type
            self.id = id_
            self.address = address
            self.length = length
            self.data = data

    class FakeMotor:
        def __init__(self, motor_id, connector):
            self.id = motor_id
            self.connector = connector
            self.torque_status = 0
            self.operating_mode_status = OperatingMode.POSITION

        def disableTorque(self):
            self.torque_status = 0

        def enableTorque(self):
            self.torque_status = 1

        def setOperatingMode(self, mode):
            self.operating_mode_status = mode

        def getPresentPosition(self):
            return state["positions"].get(self.id, 2048)

        def _getControlTableItem(self, name):
            class _Item:
                def __init__(self, address, size):
                    self.address = address
                    self.size = size

            return _Item({"Present Input Voltage": 144}.get(name, 0), 1)

        def _readData(self, dxl_id, address, length):
            return 121  # 12.1 V

        def stageSetGoalPosition(self, position):
            return StagedCommand("write", self.id, 116, 4, [position])

    class GroupExecutor:
        def __init__(self, connector):
            self.cmds = []

        def addCmd(self, command):
            self.cmds.append(command)

        def executeWrite(self):
            for cmd in self.cmds:
                state["writes"].append({cmd.id: cmd.data[0]})

        def executeRead(self):
            return [None for _ in self.cmds]

    class Connector:
        def __init__(self, port_name, baud_rate):
            state["port"] = port_name
            state["baudrate"] = baud_rate

        def createMotor(self, motor_id):
            if motor_id == state["fail_create"]:
                raise RuntimeError("simulated createMotor failure")
            motor = FakeMotor(motor_id, self)
            state["motors"][motor_id] = motor
            return motor

        def ping(self, motor_id):
            return 1180  # model number

        def createGroupExecutor(self):
            return GroupExecutor(self)

        def closePort(self):
            state["closed"] = True

    module = types.ModuleType("dynamixel_easy_sdk")
    module.Connector = Connector
    module.Motor = FakeMotor
    module.GroupExecutor = GroupExecutor
    module.OperatingMode = OperatingMode
    module.StagedCommand = StagedCommand
    return module, state


class DynamixelBackendTests(unittest.TestCase):
    def _config(self, **kw):
        return Config(port="/dev/fake", servo_backend="dynamixel", **kw)

    def test_connect_creates_motors_and_enables_torque(self):
        sdk, state = make_fake_easy_sdk()
        with patch.dict(sys.modules, {"dynamixel_easy_sdk": sdk}):
            from openneck._backends.dynamixel import DynamixelBackend

            backend = DynamixelBackend(self._config())
            backend.connect()
            self.assertEqual(set(state["motors"]), {1, 2})
            self.assertTrue(
                all(m.torque_status == 1 for m in state["motors"].values())
            )
            backend.close()
        self.assertTrue(state["closed"])

    def test_connect_failure_is_translated_to_runtime_error(self):
        sdk, state = make_fake_easy_sdk()
        state["fail_create"] = 2
        with patch.dict(sys.modules, {"dynamixel_easy_sdk": sdk}):
            from openneck._backends.dynamixel import DynamixelBackend

            backend = DynamixelBackend(self._config())
            with self.assertRaisesRegex(RuntimeError, "ping servo 2"):
                backend.connect()
        self.assertTrue(state["closed"])


if __name__ == "__main__":
    unittest.main()
