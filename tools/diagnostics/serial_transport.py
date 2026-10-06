"""Optional pySerial adapter; other diagnostics and tests need only Python."""
from __future__ import annotations

import math
import time

from rtu import ProtocolError


class SerialTransport:
    def __init__(self, port: str, baud: int = 19200, timeout: float = 0.5):
        if baud not in (9600, 19200, 38400, 57600, 115200):
            raise ValueError("Unsupported configured baud rate")
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Timeout must be finite and positive")
        try:
            import serial
        except ImportError as error:
            raise RuntimeError("Serial access needs pySerial: python -m pip install -r tools/diagnostics/requirements.txt") from error
        self.serial = serial.Serial(port=port, baudrate=baud, bytesize=8,
                                    parity=serial.PARITY_EVEN, stopbits=1,
                                    timeout=timeout, write_timeout=timeout)
        self.timeout = timeout
        self.silent_interval = 3.5 * 11 / baud if baud <= 19200 else 0.00175
        self.last_end = 0.0

    def _read_exact(self, size: int, deadline: float) -> bytes:
        result = bytearray()
        while len(result) < size:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ProtocolError("Serial response timed out or was truncated")
            self.serial.timeout = remaining
            chunk = self.serial.read(size - len(result))
            if not chunk:
                raise ProtocolError("Serial response timed out or was truncated")
            result.extend(chunk)
        return bytes(result)

    def exchange(self, request: bytes) -> bytes:
        # One request at a time. Do not retry mutations whose outcome is unknown.
        delay = self.silent_interval - (time.monotonic() - self.last_end)
        if delay > 0:
            time.sleep(delay)
        self.serial.reset_input_buffer()
        try:
            written = self.serial.write(request)
            if written != len(request):
                raise ProtocolError("Incomplete serial request write")
            self.serial.flush()
            deadline = time.monotonic() + self.timeout
            header = self._read_exact(3, deadline)
            if header[1] & 0x80:
                remaining = 2
            elif header[1] in (3, 4):
                if header[2] > 250 or header[2] % 2:
                    raise ProtocolError("Invalid serial read byte count")
                remaining = header[2] + 2
            elif header[1] in (6, 16):
                remaining = 5
            else:
                raise ProtocolError("Unexpected serial response function")
            response = header + self._read_exact(remaining, deadline)
            time.sleep(self.silent_interval)
            if self.serial.in_waiting:
                raise ProtocolError("Extra bytes after response; check echo/adapter framing")
            return response
        finally:
            self.last_end = time.monotonic()

    def close(self) -> None:
        self.serial.close()
