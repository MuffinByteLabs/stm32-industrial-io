"""Small Modbus RTU codec. No broadcast writes, retries, or target register map."""
from __future__ import annotations

import struct
from typing import Protocol


class ProtocolError(ValueError):
    """A malformed, mismatched or corrupt frame."""


class DeviceException(ProtocolError):
    def __init__(self, function: int, code: int):
        self.function, self.code = function, code
        super().__init__(f"Modbus exception: function 0x{function:02x}, code 0x{code:02x}")


class Transport(Protocol):
    def exchange(self, request: bytes) -> bytes: ...
    def close(self) -> None: ...


def crc16(data: bytes) -> int:
    """Modbus CRC-16, polynomial 0xa001; transmitted low byte first."""
    crc = 0xffff
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0xa001 if crc & 1 else 0)
    return crc


def frame(address: int, function: int, payload: bytes) -> bytes:
    if not 1 <= address <= 247:
        raise ValueError("Unicast address must be 1..247; broadcasts are disabled")
    if not 1 <= function <= 255:
        raise ValueError("Function must be 1..255")
    body = bytes((address, function)) + payload
    if len(body) + 2 > 256:
        raise ValueError("RTU frame exceeds 256 bytes")
    return body + struct.pack("<H", crc16(body))


def decode_frame(data: bytes, address: int, function: int) -> bytes:
    if not 5 <= len(data) <= 256:
        raise ProtocolError("RTU frame length must be 5..256 bytes")
    if crc16(data[:-2]) != struct.unpack("<H", data[-2:])[0]:
        raise ProtocolError("RTU CRC mismatch")
    if data[0] != address:
        raise ProtocolError("Response address does not match request")
    if data[1] == (function | 0x80):
        if len(data) != 5:
            raise ProtocolError("Malformed Modbus exception")
        raise DeviceException(function, data[2])
    if data[1] != function:
        raise ProtocolError("Response function does not match request")
    return data[2:-2]


class Client:
    def __init__(self, transport: Transport, address: int = 1):
        if not 1 <= address <= 247:
            raise ValueError("Unicast address must be 1..247")
        self.transport, self.address = transport, address

    def read_registers(self, start: int, count: int, function: int = 4) -> tuple[int, ...]:
        if function not in (3, 4):
            raise ValueError("Only FC03/FC04 reads are implemented")
        if not 1 <= count <= 125 or not 0 <= start <= 65536 - count:
            raise ValueError("Invalid read register range")
        request = frame(self.address, function, struct.pack(">HH", start, count))
        payload = decode_frame(self.transport.exchange(request), self.address, function)
        if len(payload) != count * 2 + 1 or payload[0] != count * 2:
            raise ProtocolError("Read byte count or response length mismatch")
        return struct.unpack(f">{count}H", payload[1:])

    def write_registers(self, start: int, values: tuple[int, ...] | list[int]) -> None:
        if not 1 <= len(values) <= 123 or not 0 <= start <= 65536 - len(values):
            raise ValueError("Invalid write register range")
        if any(not isinstance(value, int) or not 0 <= value <= 65535 for value in values):
            raise ValueError("Register values must be integers 0..65535")
        header = struct.pack(">HHB", start, len(values), len(values) * 2)
        request = frame(self.address, 16, header + struct.pack(f">{len(values)}H", *values))
        payload = decode_frame(self.transport.exchange(request), self.address, 16)
        if payload != struct.pack(">HH", start, len(values)):
            raise ProtocolError("Write response does not echo the requested range")

    def write_single_register(self, address: int, value: int) -> None:
        if not 0 <= address <= 65535 or not 0 <= value <= 65535:
            raise ValueError("Single register address/value must be 0..65535")
        payload = struct.pack(">HH", address, value)
        reply = decode_frame(self.transport.exchange(frame(self.address, 6, payload)), self.address, 6)
        if reply != payload:
            raise ProtocolError("Single-write response does not echo the request")
