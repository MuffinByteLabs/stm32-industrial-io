"""Synthetic register-level device for host development, never hardware evidence."""
from __future__ import annotations

import json
from pathlib import Path
import struct
import time

from fieldio import (ARM_LATCH, CAP_MODBUS, CAP_PWM, CAP_RELAYS, CAP_STATIC_DO,
                     COMMAND_COUNT, COMMAND_START, IDENTITY_COUNT, IDENTITY_START,
                     MAP_REVISION, PROTOCOL_VERSION, RAW_COUNT, RAW_START,
                     REQUIRED_HEALTH, SNAPSHOT_COUNT, SNAPSHOT_START, words32)
from rtu import DeviceException, ProtocolError, decode_frame, frame


class SimulatedTransport:
    """One simulated unicast server, optionally persisting state between CLI calls."""
    def __init__(self, address: int = 1, state_path: str | None = None,
                 *, pwm_qualified: bool = False, clock=time.time):
        self.address, self.clock = address, clock
        self.state_path = Path(state_path) if state_path else None
        self.requests: list[bytes] = []
        self.raw_latch = None
        self.raw_latch_deadline = 0.0
        self.state = {"schema": "SIMULATED-fieldio-map1", "boot_id": 1, "epoch": 1,
                      "last_command": 0, "last_result": 0, "state": 1, "owner": 0, "configured_owner": 1,
                      "status": REQUIRED_HEALTH, "faults": 0, "outputs": 0, "relays": 0,
                      "pwm": 0, "lease_expires": 0.0, "sequence": 0,
                      "started": clock(), "implemented": 0x7f, "qualified": 0x5f}
        if self.state_path and self.state_path.exists():
            saved = json.loads(self.state_path.read_text(encoding="utf-8"))
            if saved.get("schema") != self.state["schema"]:
                raise ValueError("Simulation state file has an unsupported schema")
            if set(saved) != set(self.state):
                raise ValueError("Simulation state file has unexpected fields")
            self.state = saved
        if pwm_qualified:
            self.state["implemented"] |= CAP_PWM
            self.state["qualified"] |= CAP_PWM

    def _save(self):
        if self.state_path:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            self.state_path.write_text(json.dumps(self.state, indent=2) + "\n", encoding="utf-8")

    def _disarm(self, acknowledge=False):
        s = self.state
        if acknowledge:
            s["faults"] &= ~(1 << 4)  # Model only a recoverable expired-lease latch.
        s.update(state=1 if not s["faults"] else 4, owner=0, outputs=0, relays=0,
                 pwm=0, lease_expires=0.0, status=s["status"] & ~ARM_LATCH,
                 epoch=min(0xffffffff, s["epoch"]+1), last_command=0, last_result=0)
        self.raw_latch = None

    def _expire(self):
        if self.state["state"] == 2 and self.clock() >= self.state["lease_expires"]:
            self.state["faults"] |= 1 << 4
            self._disarm()

    def _identity(self):
        s = self.state
        return ([PROTOCOL_VERSION, MAP_REVISION] + words32(s["implemented"])
                + words32(s["qualified"]) + [0, 0, 0, 1, 0, 0] + words32(0)
                + [0x5349, 0x4d55, 0x4c41, 0x5445, 0x4400, 0x0001]
                + words32(s["boot_id"]) + [0, 0])

    def _snapshot(self):
        self._expire()
        s = self.state
        s["sequence"] = (s["sequence"]+1) & 0xffffffff
        seq = words32(s["sequence"])
        # Fixed examples exercise engineering-unit parsing, not accuracy targets.
        validity = 0x3f  # Synthetic DI, pulse and AI; no measured-calibration claim.
        r = (seq + words32(int((self.clock()-s["started"])*1000) & 0xffffffff)
             + [s["state"], s["owner"]] + words32(s["status"]) + words32(s["faults"])
             + words32(validity) + [5, s["outputs"], s["relays"], s["pwm"]]
             + words32(s["sequence"]) + [2500, 7500, 8000, 16000]
             + [0xffff]*4 + [max(0, min(5000, int((s["lease_expires"]-self.clock())*1000)))]
             + words32(s["last_command"]) + [s["last_result"]] + words32(1) + words32(1)
             + [10]*4 + [0xffff]*4 + [100 if s["pwm"] else 0, s["configured_owner"]]
             + words32(s["epoch"]) + seq)
        self.raw_latch = seq + [16000, 48000, 20480, 40960, 1, 1, 2, 2] + [0xffff]*4 + seq
        self.raw_latch_deadline = self.clock() + 1.0
        return r

    def _command(self, values):
        s = self.state
        def number(index): return (values[index] << 16) | values[index+1]
        boot, epoch, command = number(0), number(2), number(4)
        action, owner, lease, outputs, relays, mode, frequency, duty = values[6:14]
        def reject(result):
            s["last_result"] = result
            raise DeviceException(16, 3)
        if not s["boot_id"] or boot != s["boot_id"]: reject(3)
        if not s["epoch"] or s["epoch"] == 0xffffffff or epoch != s["epoch"]: reject(4)
        if s["last_command"] == 0xffffffff or command != s["last_command"]+1: reject(5)
        if (action not in (1, 2, 3, 4) or owner != 1 or not 500 <= lease <= 5000
                or outputs > 15 or relays > 3 or mode not in (0, 1) or any(values[14:])):
            reject(2)
        if action != 3 and any(values[9:14]):
            reject(2)
        if mode == 0 and (frequency or duty): reject(2)
        if mode == 1 and (frequency != 100 or not 100 <= duty <= 900 or outputs & 4):
            reject(11)
        supported = s["implemented"] & s["qualified"]
        if action != 1 and (not supported & CAP_MODBUS or s["faults"]
                            or s["status"] & REQUIRED_HEALTH != REQUIRED_HEALTH
                            or s["status"] & ((1 << 10) | (1 << 14))):
            reject(8)
        if action == 2 and (s["state"] != 1 or s["owner"] != 0
                            or s["configured_owner"] != 1 or s["status"] & ARM_LATCH
                            or not supported & (CAP_STATIC_DO | CAP_RELAYS)):
            reject(7)
        if action in (3, 4) and (s["state"] != 2 or s["owner"] != 1
                                or s["configured_owner"] != 1 or not s["status"] & ARM_LATCH
                                or s["lease_expires"] <= self.clock()):
            reject(6)
        if (outputs or mode) and not supported & CAP_STATIC_DO: reject(9)
        if relays and not supported & CAP_RELAYS: reject(9)
        if mode and not supported & CAP_PWM: reject(9)
        if action == 1:
            self._disarm(acknowledge=True)
        elif action == 2:
            s.update(state=2, owner=1, outputs=0, relays=0, pwm=0,
                     status=s["status"] | ARM_LATCH, lease_expires=self.clock()+lease/1000)
        elif action == 3:
            s.update(outputs=outputs, relays=relays, pwm=duty, lease_expires=self.clock()+lease/1000)
        else:
            s["lease_expires"] = self.clock()+lease/1000
        if action != 1:
            s["last_command"] = command
        s["last_result"] = 1
        self.raw_latch = None

    def exchange(self, request: bytes) -> bytes:
        self.requests.append(request)
        if len(request) < 2: raise ProtocolError("Incomplete simulated request")
        function = request[1]
        payload = decode_frame(request, self.address, function)
        self._expire()
        if function in (6, 16):
            self.raw_latch = None  # A valid-address/CRC write invalidates capture even when rejected.
        try:
            if function == 4:
                if len(payload) != 4: raise DeviceException(function, 3)
                start, count = struct.unpack(">HH", payload)
                if (start, count) == (IDENTITY_START, IDENTITY_COUNT): values = self._identity()
                elif (start, count) == (SNAPSHOT_START, SNAPSHOT_COUNT): values = self._snapshot()
                elif (start, count) == (RAW_START, RAW_COUNT):
                    if self.raw_latch is None or self.clock() >= self.raw_latch_deadline:
                        raise DeviceException(function, 4)
                    values = self.raw_latch
                else: raise DeviceException(function, 2)
                reply = bytes((len(values)*2,)) + struct.pack(f">{len(values)}H", *values)
            elif function == 6:
                if payload != struct.pack(">HH", 0, 0xd15a): raise DeviceException(function, 2)
                self._disarm(acknowledge=True)
                self.state["last_result"] = 1
                reply = payload
            elif function == 3:
                if payload != struct.pack(">HH", 0, 1): raise DeviceException(function, 2)
                reply = b"\x02\x00\x00"
            elif function == 16:
                if len(payload) < 5: raise DeviceException(function, 3)
                start, count, size = struct.unpack(">HHB", payload[:5])
                if start != COMMAND_START or count != COMMAND_COUNT: raise DeviceException(function, 2)
                if size != count*2 or len(payload) != size+5: raise DeviceException(function, 3)
                self._command(struct.unpack(f">{count}H", payload[5:]))
                reply = struct.pack(">HH", start, count)
            else:
                raise DeviceException(function, 1)
            return frame(self.address, function, reply)
        except DeviceException as error:
            return frame(self.address, function | 0x80, bytes((error.code,)))
        finally:
            self._save()

    def close(self): self._save()
