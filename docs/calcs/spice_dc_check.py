"""I reproduce limited static frontend checks with the ngspice shared library."""

from __future__ import annotations

import argparse
import ctypes as c
import json
import math
import os
from pathlib import Path


class Vector(c.Structure):
    _fields_ = [("name", c.c_char_p), ("type", c.c_int), ("flags", c.c_short),
                ("real", c.POINTER(c.c_double)), ("complex", c.c_void_p),
                ("length", c.c_int)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, required=True,
                        help="Path to an installed ngspice shared library")
    args = parser.parse_args()
    library = args.library.resolve(strict=True)
    dll_directory = os.add_dll_directory(str(library.parent)) if os.name == "nt" else None
    ng = c.CDLL(str(library))
    messages = []
    send_type = c.CFUNCTYPE(c.c_int, c.c_char_p, c.c_int, c.c_void_p)
    exit_type = c.CFUNCTYPE(c.c_int, c.c_int, c.c_bool, c.c_bool, c.c_int, c.c_void_p)

    @send_type
    def send(message, _identifier, _user):
        messages.append(message.decode("utf-8", errors="replace"))
        return 0

    @exit_type
    def controlled_exit(status, _immediate, _quit, _identifier, _user):
        messages.append(f"ngspice requested exit {status}")
        return 0

    ng.ngSpice_Init.argtypes = [send_type, send_type, exit_type,
                               c.c_void_p, c.c_void_p, c.c_void_p, c.c_void_p]
    ng.ngSpice_Circ.argtypes = [c.POINTER(c.c_char_p)]
    ng.ngSpice_Command.argtypes = [c.c_char_p]
    ng.ngGet_Vec_Info.argtypes = [c.c_char_p]
    ng.ngGet_Vec_Info.restype = c.POINTER(Vector)
    ng.ngSpice_Init(send, send, controlled_exit, None, None, None, None)
    source = Path(__file__).with_name("dc_frontends.cir")
    lines = [line.encode("ascii") for line in source.read_text().splitlines()]
    circuit = (c.c_char_p * (len(lines) + 1))(*lines, None)
    if ng.ngSpice_Circ(circuit) != 0:
        raise RuntimeError("ngspice rejected circuit: " + "\n".join(messages))
    ng.ngSpice_Command(b"op")

    def value(name):
        info = ng.ngGet_Vec_Info(name.encode("ascii"))
        if not info or info.contents.length != 1 or not info.contents.real:
            raise RuntimeError(f"Missing operating-point vector {name}: " + "\n".join(messages))
        result = info.contents.real[0]
        if not math.isfinite(result):
            raise RuntimeError(f"Nonfinite result: {name}")
        return result

    result = {
        "scope": "Ideal-amplifier DC topology check; no IC transient, stability, surge, or hardware validation",
        "assumed_main_switch_ohm": 12.5,
        "assumed_series_protection_ohm": 100,
        "assumed_feedback_path_total_ohm": 8600,
        "load_ohm": 10000,
        "terminal_pulldown_ohm": 100000,
        "gain_stage_v": value("gain"),
        "terminal_feedback_v": value("ao"),
        "without_terminal_feedback_v": value("uncomp"),
        "current_shunt_v_at_20ma": value("shunt"),
        "adc_sense_v_at_20ma": value("sense"),
    }
    # Independent equations check model connectivity and solver output.
    expected_shunt = (200 * .020 + 200 * 2.5 / (850000 + 8.3)) / (1 + 200 / (850000 + 8.3))
    if abs(result["current_shunt_v_at_20ma"] - expected_shunt) > 1e-8:
        raise RuntimeError("Shunt model disagrees with independent loading equation")
    if abs(result["terminal_feedback_v"] - 10) > .001:
        raise RuntimeError("Ideal DC terminal-feedback topology failed")
    if not result["without_terminal_feedback_v"] < 9.95:
        raise RuntimeError("Expected resistive load drop is absent")
    print(json.dumps(result, indent=2))
    ng.ngSpice_Command(b"destroy all")
    if dll_directory:
        dll_directory.close()


if __name__ == "__main__":
    main()
