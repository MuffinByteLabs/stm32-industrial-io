"""Read-only by default diagnostics for the draft FieldIO Modbus contract."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys
import time

from fieldio import FieldIO
from rtu import Client, ProtocolError
from simulation import SimulatedTransport


def integer(value: str) -> int:
    try: return int(value, 0)
    except ValueError as error: raise argparse.ArgumentTypeError("Use a decimal or 0x/0b-prefixed integer") from error


def two_point_fit(raw_low: int, reference_low: float, raw_high: int,
                  reference_high: float, unit: str) -> dict:
    if not 0 <= raw_low <= 65535 or not 0 <= raw_high <= 65535 or raw_low == raw_high:
        raise ValueError("Raw ADC points must be distinct integers in 0..65535")
    if not all(math.isfinite(v) for v in (reference_low, reference_high)):
        raise ValueError("Reference values must be finite")
    gain = (reference_high-reference_low)/(raw_high-raw_low)
    offset = reference_low-gain*raw_low
    if not math.isfinite(gain) or not math.isfinite(offset):
        raise ValueError("Calibration gain/offset overflowed; use bounded engineering references")
    if gain <= 0: raise ValueError("Unipolar ADC calibration requires a positive slope")
    return {"evidence_kind": "OFFLINE_COEFFICIENT_CALCULATION", "unit": unit,
            "gain_per_raw_code": gain, "offset": offset,
            "equation": "engineering_value = gain_per_raw_code * raw_adc_code + offset",
            "raw_low": raw_low, "reference_low": reference_low,
            "raw_high": raw_high, "reference_high": reference_high,
            "device_write_performed": False,
            "limitation": "Two-point fit only; independent verification points, reference uncertainty and temperature evidence are required. Not a device coefficient record or qualification result."}


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--simulate", action="store_true", help="Use synthetic registers, never hardware evidence")
    mode.add_argument("--port", help="RS-485 adapter serial port, for example COM5")
    p.add_argument("--simulation-state", help="Optional persistent SIMULATED device JSON; usable only with --simulate")
    p.add_argument("--baud", type=int, default=19200, choices=(9600, 19200, 38400, 57600, 115200))
    p.add_argument("--address", type=int, default=1, help="Unicast server 1..247, default 1")
    p.add_argument("--timeout", type=float, default=0.5, help="Serial response deadline in seconds")
    sub = p.add_subparsers(dest="command")
    sub.add_parser("identity", help="Read protocol, revision, UID and capability masks")
    sub.add_parser("snapshot", help="Read one coherent acquisition/status snapshot (default)")
    sub.add_parser("raw", help="Read a snapshot and its sequence-matched raw ADC capture")
    log = sub.add_parser("log", help="Read-only CSV recording; never renews an output lease")
    log.add_argument("--csv", required=True, help="New CSV file; existing files are not overwritten")
    log.add_argument("--samples", type=int, default=25)
    log.add_argument("--interval", type=float, default=0.2, help="Seconds per polling cycle; default 5 Hz")
    for action in ("arm", "disarm", "keepalive", "set"):
        command = sub.add_parser(action, help=f"Explicit {action} command, one shot; no automatic retry")
        command.add_argument("--lease-ms", type=int, default=1000, help="500..5000 ms; reads never maintain this lease")
        if action == "disarm":
            command.add_argument("--unconditional", action="store_true", help="Explicit unicast FC06 stop without boot/epoch/sequence guards")
        if action == "set":
            command.add_argument("--outputs", type=integer, default=0, help="Complete DO1..DO4 mask, default all off")
            command.add_argument("--relays", type=integer, default=0, help="Complete relay1..2 coil mask, default all off")
            command.add_argument("--pwm-permille", type=int, help="DO3 duty 100..900 at 100 Hz, only if implemented AND qualified")
    fit = sub.add_parser("calibration-fit", help="Offline two-point math only; no device connection or write")
    fit.add_argument("--raw-low", type=integer, required=True)
    fit.add_argument("--reference-low", type=float, required=True)
    fit.add_argument("--raw-high", type=integer, required=True)
    fit.add_argument("--reference-high", type=float, required=True)
    fit.add_argument("--unit", choices=("mV", "uA"), required=True)
    return p


def emit(value): print(json.dumps(value, indent=2, allow_nan=False))


def stamp(value: dict, identity: dict, simulated: bool) -> dict:
    return {"evidence_kind": "SIMULATED" if simulated else "SERIAL_DEVICE_OBSERVATION_UNQUALIFIED",
            "host_received_utc": datetime.now(timezone.utc).isoformat(),
            "uid96_hex": identity["uid96_hex"], "boot_id": identity["boot_id"],
            "firmware_version": identity["firmware_version"], "build_id": identity["build_id"],
            "hardware_revision": identity["hardware_revision"], "assembly_variant": identity["assembly_variant"],
            "protocol_version": identity["protocol_version"], "map_revision": identity["map_revision"],
            "implemented_mask": identity["implemented_mask"], "qualified_mask": identity["qualified_mask"],
            **value}


def log_csv(device: FieldIO, path: str, samples: int, interval: float, simulated: bool) -> dict:
    if samples <= 0 or not math.isfinite(interval) or interval < 0.2:
        raise ValueError("CSV logging needs positive samples and interval >=0.2 s (maximum requested 5 Hz)")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with target.open("x", newline="", encoding="utf-8") as handle:
        writer = None
        for _ in range(samples):
            cycle_start = time.monotonic()
            snapshot = device.capture_snapshot()
            record = stamp(snapshot.as_dict(), snapshot.identity.as_dict(), simulated)
            for name in ("ai_sample_age_ms", "current_sample_age_ms"):
                ages = record.pop(name)
                for number, age in enumerate(ages, 1): record[f"{name}_{number}"] = age
            if writer is None:
                writer = csv.DictWriter(handle, fieldnames=list(record))
                writer.writeheader()
            writer.writerow(record)
            handle.flush()
            count += 1
            if count < samples:
                time.sleep(max(0, interval-(time.monotonic()-cycle_start)))
    return {"evidence_kind": "SIMULATED" if simulated else "SERIAL_DEVICE_OBSERVATION_UNQUALIFIED",
            "csv": str(target.resolve()), "samples": count, "read_only": True,
            "note": "No command/lease writes; invalid samples are empty CSV fields. Host UTC is receipt time, not acquisition time."}


def main(argv=None) -> int:
    p = parser()
    args = p.parse_args(argv)
    command = args.command or "snapshot"
    transport = None
    try:
        if command == "calibration-fit":
            if args.port or args.simulate or args.simulation_state:
                raise ValueError("calibration-fit is offline; omit transport arguments")
            emit(two_point_fit(args.raw_low, args.reference_low, args.raw_high, args.reference_high, args.unit))
            return 0
        if not 1 <= args.address <= 247: raise ValueError("Address must be unicast 1..247")
        if args.simulation_state and not args.simulate:
            raise ValueError("--simulation-state requires --simulate")
        if args.simulate:
            transport = SimulatedTransport(args.address, args.simulation_state)
        elif args.port:
            from serial_transport import SerialTransport
            transport = SerialTransport(args.port, args.baud, args.timeout)
        else:
            p.error("Choose --simulate or --port; default operation is read-only snapshot")
        device = FieldIO(Client(transport, args.address))
        if command == "identity":
            identity = device.identity().as_dict()
            emit(stamp(identity, identity, args.simulate))
        elif command == "snapshot":
            snapshot = device.capture_snapshot()
            emit(stamp(snapshot.as_dict(), snapshot.identity.as_dict(), args.simulate))
        elif command == "raw":
            identity, capture = device.capture_raw()
            emit(stamp(capture, identity.as_dict(), args.simulate))
        elif command == "log": emit(log_csv(device, args.csv, args.samples, args.interval, args.simulate))
        else:
            unconditional = command == "disarm" and args.unconditional
            snapshot = device.unconditional_disarm() if unconditional else device.command(
                command, outputs=getattr(args, "outputs", 0), relays=getattr(args, "relays", 0),
                pwm_permille=getattr(args, "pwm_permille", None), lease_ms=args.lease_ms)
            emit(stamp({"explicit_command": "unconditional_disarm" if unconditional else command, "snapshot": snapshot.as_dict(),
                        "note": "One command only. No automatic retry, rearm or background lease renewal."}, snapshot.identity.as_dict(), args.simulate))
        return 0
    except (ValueError, RuntimeError, OSError, ProtocolError) as error:
        print(f"Diagnostic stopped: {error}", file=sys.stderr)
        return 1
    finally:
        if transport is not None: transport.close()


if __name__ == "__main__": sys.exit(main())
