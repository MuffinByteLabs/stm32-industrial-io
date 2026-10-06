"""Host view of firmware/Protocol.md v1.0/map1. Device firmware is pending."""
from __future__ import annotations

from dataclasses import dataclass

from rtu import Client, DeviceException, ProtocolError

PROTOCOL_VERSION = 0x0100
MAP_REVISION = 1
IDENTITY_START, IDENTITY_COUNT = 0x0000, 24
SNAPSHOT_START, SNAPSHOT_COUNT = 0x0040, 48
COMMAND_START, COMMAND_COUNT = 0x0100, 16
RAW_START, RAW_COUNT = 0x0080, 16
CAP_STATIC_DO, CAP_RELAYS, CAP_MODBUS, CAP_PWM = 1 << 3, 1 << 4, 1 << 6, 1 << 9
CAP_NAMES = ("digital_inputs", "voltage_inputs", "current_inputs", "static_outputs",
             "relays", "current_diagnostics", "modbus", "usb", "classic_can", "pwm",
             "can_fd", "configuration_write", "calibration_write")
STATE_NAMES = ("BOOT", "READY", "ARMED", "DRIVER_FAULT", "GLOBAL_FAULT", "RECOVERY")
OWNER_NAMES = ("none", "modbus", "can", "local")
ACTIONS = {"disarm": 1, "arm": 2, "set": 3, "keepalive": 4}
UNAVAILABLE = 0xffff
REQUIRED_HEALTH = 0x03bf
ARM_LATCH, UPDATE_MODE, COMMIT_BUSY = 1 << 6, 1 << 10, 1 << 14


def u32(registers: tuple[int, ...], index: int) -> int:
    return (registers[index] << 16) | registers[index + 1]


def words32(value: int) -> list[int]:
    return [(value >> 16) & 0xffff, value & 0xffff]


def capabilities(mask: int) -> list[str]:
    return [name for bit, name in enumerate(CAP_NAMES) if mask & (1 << bit)]


@dataclass(frozen=True)
class Identity:
    registers: tuple[int, ...]

    @property
    def boot_id(self) -> int: return u32(self.registers, 20)
    @property
    def implemented(self) -> int: return u32(self.registers, 2)
    @property
    def qualified(self) -> int: return u32(self.registers, 4)

    def supports(self, mask: int) -> bool:
        return (self.implemented & self.qualified & mask) == mask

    def as_dict(self) -> dict:
        r = self.registers
        return {"protocol_version": f"{r[0] >> 8}.{r[0] & 0xff}", "map_revision": r[1],
                "implemented_mask": self.implemented, "qualified_mask": self.qualified,
                "implemented": capabilities(self.implemented), "qualified": capabilities(self.qualified),
                "firmware_version": ".".join(map(str, r[6:9])),
                "hardware_revision": f"{r[9]}.{r[10]}", "assembly_variant": r[11],
                "build_id": u32(r, 12), "uid96_hex": "".join(f"{v:04x}" for v in r[14:20]),
                "boot_id": self.boot_id}


@dataclass(frozen=True)
class Snapshot:
    registers: tuple[int, ...]
    identity: Identity | None = None

    @property
    def sequence(self) -> int: return u32(self.registers, 0)
    @property
    def state(self) -> int: return self.registers[4]
    @property
    def owner(self) -> int: return self.registers[5]
    @property
    def status(self) -> int: return u32(self.registers, 6)
    @property
    def faults(self) -> int: return u32(self.registers, 8)
    @property
    def validity(self) -> int: return u32(self.registers, 10)
    @property
    def command_sequence(self) -> int: return u32(self.registers, 27)
    @property
    def control_epoch(self) -> int: return u32(self.registers, 44)

    def as_dict(self) -> dict:
        r = self.registers
        # Validity meanings are authoritative; never turn unavailable samples into zeros.
        def sample(index: int, bit: int, age_index: int):
            age_valid = r[age_index] <= 20 if index < 22 else r[age_index] != UNAVAILABLE
            return r[index] if self.validity & (1 << bit) and r[index] != UNAVAILABLE and age_valid else None
        return {"sequence": self.sequence, "uptime_ms": u32(r, 2),
                "state": STATE_NAMES[self.state], "owner": OWNER_NAMES[self.owner],
                "status_mask": self.status, "fault_mask": self.faults, "validity_mask": self.validity,
                "digital_input_mask": r[12] if self.validity & 1 else None,
                "output_applied_mask": r[13], "relay_coil_mask": r[14],
                "pwm_applied_permille": r[15], "di1_pulse_count": u32(r, 16) if self.validity & 2 else None,
                "voltage_1_mV": sample(18, 2, 34), "voltage_2_mV": sample(19, 3, 35),
                "current_1_uA": sample(20, 4, 36), "current_2_uA": sample(21, 5, 37),
                **{f"output_{n+1}_on_current_mA": sample(22+n, 6+n, 38+n) for n in range(4)},
                "lease_remaining_ms": r[26], "last_command_sequence": self.command_sequence,
                "last_command_result": r[29], "configuration_revision": u32(r, 30),
                "calibration_revision": u32(r, 32), "ai_sample_age_ms": list(r[34:38]),
                "current_sample_age_ms": list(r[38:42]), "pwm_frequency_Hz": r[42],
                "configured_owner": OWNER_NAMES[r[43]],
                "control_epoch": self.control_epoch}


class FieldIO:
    def __init__(self, client: Client): self.client = client

    def identity(self) -> Identity:
        r = self.client.read_registers(IDENTITY_START, IDENTITY_COUNT)
        if r[0] != PROTOCOL_VERSION or r[1] != MAP_REVISION:
            raise ProtocolError(f"Unsupported protocol/map: 0x{r[0]:04x}/{r[1]}; expected 0x0100/1")
        if any(r[22:24]):
            raise ProtocolError("Nonzero reserved identity fields")
        if u32(r, 4) & ~u32(r, 2):
            raise ProtocolError("Qualified capabilities are not a subset of implemented capabilities")
        if u32(r, 2) & ~0x1fff:
            raise ProtocolError("Unknown capability bits require a map update")
        return Identity(r)

    def snapshot(self, attempts: int = 3) -> Snapshot:
        if not 1 <= attempts <= 10: raise ValueError("Snapshot attempts must be 1..10")
        for _ in range(attempts):
            r = self.client.read_registers(SNAPSHOT_START, SNAPSHOT_COUNT)
            if u32(r, 0) != u32(r, 46):
                continue
            if r[4] >= len(STATE_NAMES) or r[5] >= len(OWNER_NAMES) or r[43] not in (1, 2, 3):
                raise ProtocolError("Unknown state/current owner/configured owner")
            if r[12] & ~0xf or r[13] & ~0xf or r[14] & ~0x3:
                raise ProtocolError("Out-of-range applied/input mask")
            if r[15] > 1000:
                raise ProtocolError("Out-of-range PWM telemetry")
            if r[29] > 12:
                raise ProtocolError("Unknown command result")
            if u32(r, 6) & ~0x7fff or u32(r, 8) & ~0x3ff or u32(r, 10) & ~0x7fff:
                raise ProtocolError("Unknown status/fault/validity bits require a map update")
            return Snapshot(r)
        raise ProtocolError("Snapshot sequence changed inside every response; no coherent data returned")

    def raw_capture(self, attempts: int = 3) -> dict:
        """Read the full snapshot then its matching, port-latched raw generation."""
        if not 1 <= attempts <= 10: raise ValueError("Raw capture attempts must be 1..10")
        for _ in range(attempts):
            snapshot = self.snapshot()
            try:
                raw = self.client.read_registers(RAW_START, RAW_COUNT)
            except DeviceException as error:
                if error.code == 4:
                    continue  # Re-read the entire pair; never retry an expired raw latch alone.
                raise
            if u32(raw, 0) != snapshot.sequence or u32(raw, 14) != snapshot.sequence:
                continue
            if any(code not in (0, 1, 2) for code in raw[6:10]):
                raise ProtocolError("Unknown ADC range code in raw capture")
            samples = [raw[2+n] if snapshot.validity & (1 << (2+n)) and raw[6+n] and snapshot.registers[34+n] <= 20 else None for n in range(4)]
            return {"snapshot": snapshot.as_dict(), "raw_adc_codes": samples,
                    "adc_range_codes": list(raw[6:10]),
                    "raw_current_diagnostic_codes": [raw[10+n] if snapshot.validity & (1 << (6+n)) and snapshot.registers[38+n] != UNAVAILABLE else None for n in range(4)]}
        raise ProtocolError("Raw block did not match its latched snapshot generation")

    def capture_snapshot(self, attempts: int = 3) -> Snapshot:
        """Tie a snapshot to identity metadata across reset/build/capability changes."""
        if not 1 <= attempts <= 10: raise ValueError("Session attempts must be 1..10")
        for _ in range(attempts):
            before = self.identity()
            snapshot = self.snapshot()
            after = self.identity()
            if before.registers == after.registers:
                return Snapshot(snapshot.registers, after)
        raise ProtocolError("Identity changed around every snapshot; no traceable sample returned")

    def capture_raw(self, attempts: int = 3) -> tuple[Identity, dict]:
        if not 1 <= attempts <= 10: raise ValueError("Session attempts must be 1..10")
        for _ in range(attempts):
            before = self.identity()
            capture = self.raw_capture()
            after = self.identity()
            if before.registers == after.registers:
                return after, capture
        raise ProtocolError("Identity changed around every raw capture; no traceable sample returned")

    def command(self, action: str, *, outputs: int = 0, relays: int = 0,
                pwm_permille: int | None = None, lease_ms: int = 1000) -> Snapshot:
        if action not in ACTIONS: raise ValueError("Unknown output command")
        if not 500 <= lease_ms <= 5000: raise ValueError("Lease must be 500..5000 ms")
        if not 0 <= outputs <= 15 or not 0 <= relays <= 3:
            raise ValueError("DO mask must be 0..15; relay mask 0..3")
        if action != "set" and (outputs or relays or pwm_permille is not None):
            raise ValueError("Output fields are allowed only on explicit set commands")
        if pwm_permille is not None and not 100 <= pwm_permille <= 900:
            raise ValueError("Qualified PWM duty is 100..900 permille; use static DO3 for 0/100%")
        if pwm_permille is not None and outputs & 4:
            raise ValueError("DO3 static bit must be clear when DO3 PWM mode is selected")
        before = self.capture_snapshot()
        identity = before.identity
        if not identity.boot_id or not before.control_epoch:
            raise ProtocolError("Boot ID/control epoch is zero; guarded commands are inhibited")
        if before.control_epoch == 0xffffffff:
            raise ProtocolError("Control epoch exhausted; outputs must remain disarmed pending service")
        if before.command_sequence == 0xffffffff:
            raise ProtocolError("Command sequence exhausted; use explicit unconditional disarm")
        if action != "disarm" and not identity.supports(CAP_MODBUS):
            raise ProtocolError("Modbus command capability must be implemented and qualified")
        if action != "disarm" and (before.status & REQUIRED_HEALTH != REQUIRED_HEALTH or before.status & (UPDATE_MODE | COMMIT_BUSY)):
            raise ProtocolError("Command requires qualified health/configuration and no update mode")
        if action == "arm" and (before.state != 1 or before.owner != 0 or before.registers[43] != 1 or before.faults or before.status & ARM_LATCH or any(before.registers[13:16])):
            raise ProtocolError("ARM requires READY, no other owner and no reported faults")
        if action == "arm" and not (identity.implemented & identity.qualified & (CAP_STATIC_DO | CAP_RELAYS)):
            raise ProtocolError("ARM requires at least static-output or relay implementation and qualification")
        if action in ("set", "keepalive") and (before.state != 2 or before.owner != 1 or before.registers[43] != 1 or before.faults or not before.status & ARM_LATCH or before.registers[26] == 0):
            raise ProtocolError("Command requires ARMED, Modbus ownership and no reported faults; never automatically arms")
        for mask, enabled, label in ((CAP_STATIC_DO, outputs != 0 or pwm_permille is not None, "static outputs"),
                                     (CAP_RELAYS, relays != 0, "relays"),
                                     (CAP_PWM, pwm_permille is not None, "PWM")):
            if enabled and not identity.supports(mask):
                raise ProtocolError(f"{label} must be both implemented and physically qualified")
        sequence = before.command_sequence + 1
        values = (words32(identity.boot_id) + words32(before.control_epoch) + words32(sequence)
                  + [ACTIONS[action], 1, lease_ms, outputs, relays, int(pwm_permille is not None),
                     100 if pwm_permille is not None else 0, pwm_permille or 0, 0, 0])
        try:
            self.client.write_registers(COMMAND_START, values)
            after = self.capture_snapshot()
        except DeviceException:
            raise
        except (ProtocolError, OSError) as error:
            raise ProtocolError(f"Command outcome uncertain: {error}; no retry. Re-read state or explicitly disarm") from error
        expected_sequence = 0 if action == "disarm" else sequence
        if after.identity.registers != identity.registers:
            raise ProtocolError("Identity changed during command; outcome uncertain, no retry")
        if after.command_sequence != expected_sequence or after.registers[29] != 1:
            raise ProtocolError("Write echoed, but snapshot does not confirm accepted command; outcome uncertain, no retry")
        if action == "disarm":
            if (after.control_epoch <= before.control_epoch or after.owner
                    or any(after.registers[13:16]) or after.registers[26]
                    or after.registers[42] or after.status & ARM_LATCH):
                raise ProtocolError("DISARM response did not confirm cleared output permissions; outcome uncertain, no retry")
        else:
            expected_outputs = ((outputs, relays, pwm_permille or 0) if action == "set"
                                else (0, 0, 0) if action == "arm" else before.registers[13:16])
            expected_frequency = (100 if pwm_permille is not None else 0) if action == "set" else (0 if action == "arm" else before.registers[42])
            if (after.control_epoch != before.control_epoch or after.state != 2
                    or after.owner != 1 or after.registers[43] != 1
                    or after.faults or not after.status & ARM_LATCH
                    or after.status & REQUIRED_HEALTH != REQUIRED_HEALTH
                    or after.status & (UPDATE_MODE | COMMIT_BUSY) or not after.registers[26]
                    or after.registers[13:16] != tuple(expected_outputs)
                    or after.registers[42] != expected_frequency):
                raise ProtocolError("Write echoed, but applied control state does not confirm the command; outcome uncertain, no retry")
        return after

    def unconditional_disarm(self) -> Snapshot:
        """Explicit unicast stop without session/owner guards; never broadcasts."""
        try:
            self.client.write_single_register(0, 0xd15a)
            after = self.capture_snapshot()
        except DeviceException:
            raise
        except (ProtocolError, OSError) as error:
            raise ProtocolError(f"Disarm outcome uncertain: {error}; no retry") from error
        if after.owner or any(after.registers[13:16]) or after.registers[26] or after.registers[42] or after.status & ARM_LATCH:
            raise ProtocolError("Unconditional disarm did not confirm cleared output permissions")
        return after
