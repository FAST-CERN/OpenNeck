"""Shared serial-port discovery for servo backends."""

from __future__ import annotations


def find_servo_port() -> str:
    from serial.tools import list_ports

    ports = list(list_ports.comports())
    preferred = [
        port.device
        for port in ports
        if "ttyACM" in port.device
        or "ttyUSB" in port.device
        or port.device.startswith("COM")
    ]
    if preferred:
        return preferred[0]
    if ports:
        return ports[0].device
    raise RuntimeError("no serial ports found; pass port explicitly")
