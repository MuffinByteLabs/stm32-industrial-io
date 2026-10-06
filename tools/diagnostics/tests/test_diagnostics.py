"""Host software checks using synthetic frames; not PCB or firmware validation."""
import contextlib
import csv
import io
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fieldio import (ARM_LATCH, CAP_PWM, CAP_STATIC_DO, COMMAND_START, FieldIO,
                     SNAPSHOT_START, words32)
from fieldio_cli import log_csv, main, two_point_fit
from rtu import Client, DeviceException, ProtocolError, crc16, decode_frame, frame
from serial_transport import SerialTransport
from simulation import SimulatedTransport


class ReplyTransport:
    def __init__(self, reply): self.reply, self.requests = reply, []
    def exchange(self, request):
        self.requests.append(request)
        return self.reply
    def close(self): pass


class AlteredTransport:
    def __init__(self, inner, alter): self.inner, self.alter = inner, alter
    def exchange(self, request): return self.alter(request, self.inner.exchange(request))
    def close(self): self.inner.close()


class CodecTests(unittest.TestCase):
    def test_known_modbus_crc_vector(self):
        request = bytes.fromhex("01 03 00 00 00 0a c5 cd")
        self.assertEqual(crc16(request[:-2]), 0xcdc5)
        self.assertEqual(frame(1, 3, bytes.fromhex("00 00 00 0a")), request)

    def test_corrupt_and_truncated_frames_rejected(self):
        with self.assertRaisesRegex(ProtocolError, "CRC"):
            decode_frame(bytes.fromhex("01 03 00 00 00 0a c5 cc"), 1, 3)
        with self.assertRaisesRegex(ProtocolError, "length"):
            decode_frame(b"\x01\x04", 1, 4)

    def test_address_function_and_exception_shape(self):
        with self.assertRaisesRegex(ProtocolError, "address"):
            decode_frame(frame(2, 4, b"\x02\x00\x01"), 1, 4)
        with self.assertRaisesRegex(ProtocolError, "function"):
            decode_frame(frame(1, 3, b"\x02\x00\x01"), 1, 4)
        with self.assertRaisesRegex(ProtocolError, "Malformed"):
            decode_frame(frame(1, 0x84, b"\x02\x00"), 1, 4)
        with self.assertRaises(DeviceException) as raised:
            decode_frame(frame(1, 0x84, b"\x02"), 1, 4)
        self.assertEqual(raised.exception.code, 2)

    def test_bad_read_byte_count_and_trailing_bytes(self):
        for payload in (b"\x04\x00\x01", b"\x02\x00\x01\x00\x02"):
            with self.assertRaisesRegex(ProtocolError, "byte count"):
                Client(ReplyTransport(frame(1, 4, payload))).read_registers(0, 1)

    def test_write_echo_mismatch_no_retry(self):
        transport = ReplyTransport(frame(1, 16, struct.pack(">HH", 0x101, 1)))
        with self.assertRaisesRegex(ProtocolError, "echo"):
            Client(transport).write_registers(0x100, [1])
        self.assertEqual(len(transport.requests), 1)

    def test_request_limits_and_broadcast_disabled(self):
        with self.assertRaises(ValueError): frame(0, 16, b"\x00")
        with self.assertRaises(ValueError): Client(ReplyTransport(b""), 248)
        client = Client(ReplyTransport(b""))
        for start, count in ((0, 0), (0, 126), (65535, 2)):
            with self.assertRaises(ValueError): client.read_registers(start, count)
        with self.assertRaises(ValueError): client.write_registers(0, [65536])

    def test_serial_deadline_must_be_finite_without_opening_a_port(self):
        for timeout in (0, -1, float("nan"), float("inf")):
            with self.subTest(timeout=timeout), self.assertRaisesRegex(ValueError, "finite and positive"):
                SerialTransport("UNOPENED_TEST_PORT", timeout=timeout)


class FieldIOTests(unittest.TestCase):
    def setUp(self):
        self.now = 1000.0
        self.transport = SimulatedTransport(clock=lambda: self.now)
        self.device = FieldIO(Client(self.transport))

    def writes(self): return [r for r in self.transport.requests if r[1] in (6, 16)]

    def test_read_only_identity_snapshot_and_raw_do_not_write(self):
        identity = self.device.identity()
        snapshot = self.device.snapshot().as_dict()
        raw = self.device.raw_capture()
        self.assertEqual(identity.as_dict()["protocol_version"], "1.0")
        self.assertEqual(snapshot["state"], "READY")
        self.assertEqual(snapshot["voltage_1_mV"], 2500)
        self.assertIsNone(snapshot["output_1_on_current_mA"])
        self.assertEqual(raw["raw_adc_codes"], [16000, 48000, 20480, 40960])
        self.assertEqual(self.writes(), [])

    def test_incoherent_snapshot_retried_bounded_then_rejected(self):
        def alter(request, response):
            if request[1] == 4 and struct.unpack(">H", request[2:4])[0] == SNAPSHOT_START:
                payload = bytearray(decode_frame(response, 1, 4))
                payload[-1] ^= 1
                return frame(1, 4, payload)
            return response
        broken = FieldIO(Client(AlteredTransport(self.transport, alter)))
        with self.assertRaisesRegex(ProtocolError, "coherent"):
            broken.snapshot()
        self.assertEqual(len(self.transport.requests), 3)
        self.assertEqual(self.writes(), [])

    def test_raw_full_scale_is_not_missing_sentinel(self):
        def alter(request, response):
            if request[1] == 4 and struct.unpack(">H", request[2:4])[0] == 0x80:
                payload = bytearray(decode_frame(response, 1, 4))
                payload[5:7] = b"\xff\xff"  # raw V1 register2, after byte count.
                return frame(1, 4, payload)
            return response
        self.assertEqual(FieldIO(Client(AlteredTransport(self.transport, alter))).raw_capture()["raw_adc_codes"][0], 65535)

    def test_raw_generation_mismatch_retries_entire_pair(self):
        def alter(request, response):
            if request[1] == 4 and struct.unpack(">H", request[2:4])[0] == 0x80:
                payload = bytearray(decode_frame(response, 1, 4))
                payload[-1] ^= 1
                return frame(1, 4, payload)
            return response
        with self.assertRaisesRegex(ProtocolError, "latched"):
            FieldIO(Client(AlteredTransport(self.transport, alter))).raw_capture()
        addresses = [struct.unpack(">H", r[2:4])[0] for r in self.transport.requests]
        self.assertEqual(addresses, [0x40, 0x80]*3)

    def test_set_does_not_automatically_arm(self):
        with self.assertRaisesRegex(ProtocolError, "never automatically arms"):
            self.device.command("set", outputs=1)
        self.assertEqual(self.writes(), [])

    def test_arm_clear_set_atomic_and_disarm_clear(self):
        armed = self.device.command("arm")
        self.assertEqual(armed.state, 2)
        self.assertEqual(armed.registers[29], 1)  # Contract: accepted=1, none=0.
        self.assertEqual(armed.registers[13:16], (0, 0, 0))
        applied = self.device.command("set", outputs=9, relays=2)
        self.assertEqual(applied.registers[13:16], (9, 2, 0))
        stopped = self.device.command("disarm")
        self.assertEqual(stopped.state, 1)
        self.assertEqual(stopped.registers[13:16], (0, 0, 0))
        self.assertEqual(stopped.command_sequence, 0)
        self.assertEqual(stopped.control_epoch, 2)
        self.assertEqual(self.device.command("arm").command_sequence, 1)
        self.assertEqual(len(self.writes()), 4)

    def test_lease_expires_and_reads_never_renew(self):
        self.device.command("arm")
        self.device.command("set", outputs=1)
        self.now += 0.8
        self.assertEqual(self.device.snapshot().state, 2)
        self.now += 0.3
        expired = self.device.snapshot()
        self.assertEqual(expired.state, 4)
        self.assertTrue(expired.faults & (1 << 4))
        self.assertEqual(expired.registers[13:16], (0, 0, 0))
        self.assertEqual(len(self.writes()), 2)
        with self.assertRaises(ProtocolError): self.device.command("keepalive")

    def test_sequence_exhaustion_requires_unconditional_stop_and_reset(self):
        self.device.command("arm")
        self.transport.state["last_command"] = 0xffffffff
        with self.assertRaisesRegex(ProtocolError, "sequence exhausted"):
            self.device.command("set", outputs=1)
        stopped = self.device.unconditional_disarm()
        self.assertEqual(stopped.command_sequence, 0)
        self.assertEqual(stopped.control_epoch, 2)
        self.assertEqual(stopped.registers[13:16], (0, 0, 0))
        self.assertEqual(self.device.command("arm").command_sequence, 1)

    def test_commit_busy_and_zero_boot_inhibit_guarded_commands(self):
        self.transport.state["status"] |= 1 << 14
        with self.assertRaisesRegex(ProtocolError, "health"):
            self.device.command("arm")
        self.transport.state["status"] &= ~(1 << 14)
        self.transport.state["boot_id"] = 0
        with self.assertRaisesRegex(ProtocolError, "zero"):
            self.device.command("arm")
        self.assertEqual(self.device.unconditional_disarm().state, 1)

    def test_stale_analog_age_is_excluded_even_if_validity_bit_is_set(self):
        def alter(request, response):
            if request[1] == 4 and struct.unpack(">H", request[2:4])[0] == SNAPSHOT_START:
                payload = bytearray(decode_frame(response, 1, 4))
                payload[69:71] = struct.pack(">H", 21)  # register34 ageV1.
                return frame(1, 4, payload)
            return response
        stale = FieldIO(Client(AlteredTransport(self.transport, alter)))
        self.assertIsNone(stale.snapshot().as_dict()["voltage_1_mV"])
        self.assertIsNone(stale.raw_capture()["raw_adc_codes"][0])

    def test_pwm_refused_without_both_capability_masks(self):
        self.device.command("arm")
        self.transport.state["implemented"] |= CAP_PWM
        with self.assertRaisesRegex(ProtocolError, "physically qualified"):
            self.device.command("set", pwm_permille=500)
        self.assertEqual(len(self.writes()), 1)
        self.transport.state["qualified"] |= CAP_PWM
        self.transport.state["qualified"] &= ~CAP_STATIC_DO
        with self.assertRaisesRegex(ProtocolError, "static outputs"):
            self.device.command("set", pwm_permille=500)
        self.assertEqual(len(self.writes()), 1)
        self.transport.state["qualified"] |= CAP_STATIC_DO
        pwm = self.device.command("set", pwm_permille=500)
        self.assertEqual((pwm.registers[15], pwm.registers[42]), (500, 100))
        with self.assertRaises(ValueError): self.device.command("set", outputs=4, pwm_permille=500)

    def test_rejected_write_invalidates_raw_capture_latch(self):
        self.device.snapshot()
        with self.assertRaises(DeviceException):
            self.device.client.write_registers(COMMAND_START+1, [1])
        with self.assertRaises(DeviceException) as raised:
            self.device.client.read_registers(0x80, 16)
        self.assertEqual(raised.exception.code, 4)

    def test_health_config_owner_and_missing_static_qualification(self):
        self.transport.state["status"] &= ~(1 << 8)
        with self.assertRaisesRegex(ProtocolError, "health"):
            self.device.command("arm")
        self.transport.state["status"] |= 1 << 8
        self.transport.state["configured_owner"] = 2
        with self.assertRaises(ProtocolError): self.device.command("arm")
        self.transport.state["configured_owner"] = 1
        self.device.command("arm")
        self.transport.state["qualified"] &= ~CAP_STATIC_DO
        with self.assertRaisesRegex(ProtocolError, "static outputs"):
            self.device.command("set", outputs=1)
        self.device.command("disarm")

    def test_boot_epoch_stale_sequence_guards_enforced_by_device(self):
        valid = words32(1)+words32(1)+words32(1)+[2, 1, 1000, 0, 0, 0, 0, 0, 0, 0]
        for index in (0, 2, 4):
            wrong = valid.copy()
            wrong[index+1] += 1
            with self.assertRaises(DeviceException):
                self.device.client.write_registers(COMMAND_START, wrong)
        self.assertEqual(self.transport.state["last_command"], 0)
        self.assertEqual(self.transport.state["state"], 1)

    def test_corrupt_mutation_reply_has_uncertain_outcome_and_no_retry(self):
        def alter(request, response):
            return response[:-1]+bytes((response[-1]^1,)) if request[1] == 16 else response
        broken = FieldIO(Client(AlteredTransport(self.transport, alter)))
        with self.assertRaisesRegex(ProtocolError, "outcome uncertain"):
            broken.command("arm")
        self.assertEqual(len(self.writes()), 1)
        self.assertEqual(self.transport.state["state"], 2)

    def test_accepted_result_cannot_confirm_wrong_epoch_state_or_applied_outputs(self):
        # A valid echoed write and accepted sequence are insufficient when a target
        # publishes a different control epoch/state or an incomplete applied update.
        for register, replacement, action, options in ((45, 2, "arm", {}),
                                                       (4, 1, "arm", {}),
                                                       (13, 0, "set", {"outputs": 1}),
                                                       (42, 100, "set", {"outputs": 1})):
            with self.subTest(register=register):
                inner = SimulatedTransport(clock=lambda: self.now)
                original = FieldIO(Client(inner))
                if action == "set": original.command("arm")
                mutated = False
                def alter(request, response):
                    nonlocal mutated
                    if request[1] == 16:
                        mutated = True
                    elif mutated and request[1] == 4 and struct.unpack(">H", request[2:4])[0] == SNAPSHOT_START:
                        payload = bytearray(decode_frame(response, 1, 4))
                        payload[1+register*2:3+register*2] = struct.pack(">H", replacement)
                        return frame(1, 4, payload)
                    return response
                device = FieldIO(Client(AlteredTransport(inner, alter)))
                before_writes = len([r for r in inner.requests if r[1] == 16])
                with self.assertRaisesRegex(ProtocolError, "applied control state.*outcome uncertain"):
                    device.command(action, **options)
                self.assertEqual(len([r for r in inner.requests if r[1] == 16]), before_writes+1)

    def test_csv_marks_simulation_and_reads_only(self):
        with tempfile.TemporaryDirectory() as folder:
            target = str(Path(folder)/"synthetic.csv")
            log_csv(self.device, target, 1, 0.2, True)
            with open(target, newline="", encoding="utf-8") as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(row["evidence_kind"], "SIMULATED")
            self.assertEqual(row["build_id"], "0")
            self.assertEqual(row["protocol_version"], "1.0")
            self.assertEqual(row["voltage_1_mV"], "2500")
            self.assertEqual(row["output_1_on_current_mA"], "")
            with self.assertRaises(FileExistsError):
                log_csv(self.device, target, 1, 0.2, True)
        self.assertEqual(self.writes(), [])

    def test_sentinel_current_age_excludes_scaled_and_raw_diagnostics(self):
        def alter(request, response):
            address = struct.unpack(">H", request[2:4])[0]
            payload = bytearray(decode_frame(response, 1, 4))
            if address == SNAPSHOT_START:
                validity = struct.unpack(">I", payload[21:25])[0] | (1 << 6)
                payload[21:25] = struct.pack(">I", validity)
                payload[45:47] = struct.pack(">H", 100)  # DO1 scaled current.
            elif address == 0x80:
                payload[21:23] = struct.pack(">H", 1234)  # DO1 raw MCU code.
            return frame(1, 4, payload)
        device = FieldIO(Client(AlteredTransport(self.transport, alter)))
        self.assertIsNone(device.snapshot().as_dict()["output_1_on_current_mA"])
        self.assertIsNone(device.raw_capture()["raw_current_diagnostic_codes"][0])

    def test_reset_mid_log_discards_ambiguous_sample_and_updates_identity(self):
        snapshot_reads = 0
        def alter(request, response):
            nonlocal snapshot_reads
            if request[1] == 4 and struct.unpack(">H", request[2:4])[0] == SNAPSHOT_START:
                snapshot_reads += 1
                if snapshot_reads == 2:
                    self.transport.state["boot_id"] += 1
                    self.transport.state["sequence"] = 0
            return response
        device = FieldIO(Client(AlteredTransport(self.transport, alter)))
        with tempfile.TemporaryDirectory() as folder:
            target = str(Path(folder)/"reset.csv")
            log_csv(device, target, 2, 0.2, True)
            with open(target, newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
        self.assertEqual([row["boot_id"] for row in rows], ["1", "2"])
        self.assertEqual(snapshot_reads, 3)  # Ambiguous generation discarded and retried.
        self.assertEqual(self.writes(), [])

    def test_repeated_reset_refuses_to_publish_mismatched_identity(self):
        def alter(request, response):
            if request[1] == 4 and struct.unpack(">H", request[2:4])[0] == SNAPSHOT_START:
                self.transport.state["boot_id"] += 1
            return response
        device = FieldIO(Client(AlteredTransport(self.transport, alter)))
        with self.assertRaisesRegex(ProtocolError, "traceable"):
            device.capture_snapshot()
        with self.assertRaisesRegex(ProtocolError, "traceable"):
            device.capture_raw()
        self.assertEqual(self.writes(), [])

    def test_default_cli_is_read_only_snapshot(self):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream): self.assertEqual(main(["--simulate"]), 0)
        self.assertIn('"evidence_kind": "SIMULATED"', stream.getvalue())
        self.assertIn('"state": "READY"', stream.getvalue())


class CalibrationMathTests(unittest.TestCase):
    def test_two_point_fit_units_and_no_write(self):
        result = two_point_fit(100, 0, 64100, 10000, "mV")
        self.assertAlmostEqual(result["gain_per_raw_code"]*32100+result["offset"], 5000)
        self.assertFalse(result["device_write_performed"])

    def test_degenerate_nonfinite_and_negative_slope_rejected(self):
        for points in ((1, 0, 1, 10), (0, float("nan"), 1, 10), (0, 10, 1, 0), (0, -1e308, 1, 1e308)):
            with self.assertRaises(ValueError): two_point_fit(*points, "mV")


if __name__ == "__main__": unittest.main()
