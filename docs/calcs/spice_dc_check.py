"""I reproduce active-input DC and passive-pole checks with ngspice."""

from __future__ import annotations

import argparse
import ctypes as c
import hashlib
import json
import math
import os
from pathlib import Path

from analog_checks import arithmetic


class Complex(c.Structure):
    _fields_ = [("real", c.c_double), ("imag", c.c_double)]


class Vector(c.Structure):
    _fields_ = [("name", c.c_char_p), ("type", c.c_int), ("flags", c.c_short),
                ("real", c.POINTER(c.c_double)), ("complex", c.POINTER(Complex)),
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
    if ng.ngSpice_Init(send, send, controlled_exit, None, None, None, None) != 0:
        raise RuntimeError("ngspice initialization failed: " + "\n".join(messages))
    version_start = len(messages)
    if ng.ngSpice_Command(b"version") != 0:
        raise RuntimeError("ngspice version query failed: " + "\n".join(messages))
    version_messages = messages[version_start:]
    source = Path(__file__).with_name("dc_frontends.cir")
    lines = [line.encode("ascii") for line in source.read_text().splitlines()]
    circuit = (c.c_char_p * (len(lines) + 1))(*lines, None)
    if ng.ngSpice_Circ(circuit) != 0:
        raise RuntimeError("ngspice rejected circuit: " + "\n".join(messages))
    def command(text):
        if ng.ngSpice_Command(text.encode("ascii")) != 0:
            raise RuntimeError("ngspice command failed: " + text + "\n" + "\n".join(messages))

    command("op")

    def value(name):
        info = ng.ngGet_Vec_Info(name.encode("ascii"))
        if not info or info.contents.length != 1 or not info.contents.real:
            raise RuntimeError(f"Missing operating-point vector {name}: " + "\n".join(messages))
        result = info.contents.real[0]
        if not math.isfinite(result):
            raise RuntimeError(f"Nonfinite result: {name}")
        return result

    dc = {
        "voltage_adc_v_at_10v": value("vadc"),
        "current_shunt_v_at_20ma": value("shunt"),
        "current_adc_v_at_20ma": value("iadc"),
        "current_diagnostic_raw_v_at0p5a_ratio300": value("csraw"),
        "current_diagnostic_adc_v_at0p5a_ratio300": value("csadc"),
    }
    equations = arithmetic()
    expected_shunt = (200 * .020 + 200 * 2.5 / (850000 + 1008.3)) / (1 + 200 / (850000 + 1008.3))
    expectations = {
        "voltage_adc_v_at_10v": equations["voltage_adc_at_10v_nominal_850kohm_v"],
        "current_shunt_v_at_20ma": expected_shunt,
        "current_adc_v_at_20ma": equations["current_adc_at_20ma_nominal_850kohm_v"],
        "current_diagnostic_raw_v_at0p5a_ratio300": .5 / 300 * equations["cs_effective_burden_ohm"],
        "current_diagnostic_adc_v_at0p5a_ratio300": equations["cs_adc_at_0p5a_nominal_ratio300_v"],
    }
    for name, expected in expectations.items():
        if abs(dc[name] - expected) > 2e-6:
            raise RuntimeError(f"DC model disagrees with equation for {name}: {dc[name]} versus {expected}")

    command("ac dec 120 1 100000")

    def info(name):
        vector = ng.ngGet_Vec_Info(name.encode("ascii"))
        if not vector or vector.contents.length < 1:
            raise RuntimeError(f"Missing vector {name}")
        return vector.contents

    frequency = info("frequency")
    frequencies = [frequency.real[i] if frequency.real else frequency.complex[i].real
                   for i in range(frequency.length)]

    def pole(name):
        vector = info(name)
        if not vector.complex or vector.length != len(frequencies):
            raise RuntimeError(f"Missing complex AC vector {name}")
        magnitudes = [math.hypot(vector.complex[i].real, vector.complex[i].imag)
                      for i in range(vector.length)]
        target = magnitudes[0] / math.sqrt(2)
        for i in range(1, len(magnitudes)):
            if magnitudes[i] <= target < magnitudes[i - 1]:
                fraction = math.log(target / magnitudes[i - 1]) / math.log(magnitudes[i] / magnitudes[i - 1])
                return frequencies[i - 1] * (frequencies[i] / frequencies[i - 1]) ** fraction
        raise RuntimeError(f"No -3 dB crossing found for {name}")

    poles = {"voltage_input_hz": pole("vadc"), "current_input_hz": pole("iadc")}
    for name, key in [("voltage_input_hz", "adc_voltage_filter_loaded_nominal_hz"),
                      ("current_input_hz", "adc_current_filter_loaded_nominal_hz")]:
        if abs(poles[name] / equations[key] - 1) > .002:
            raise RuntimeError(f"Passive pole disagrees with equation for {name}")
    print(json.dumps({
        "scope": "Active-input DC and passive-pole connectivity checks; ideal finite-gain diagnostic amplifier, fixed ADC resistance/on-resistances; no IC fault, stability, surge or hardware validation",
        "simulator": {"library_file": library.name,
                      "library_sha256": hashlib.sha256(library.read_bytes()).hexdigest(),
                      "version_output": version_messages},
        "circuit": {"file": source.name,
                    "sha256": hashlib.sha256(source.read_bytes()).hexdigest()},
        "assumptions": {"adc_biased_input_ohm": 850000, "adc_bias_v": 2.5,
                        "input_protector_on_ohm": 8.3, "diagnostic_switch_on_ohm": 2,
                        "diagnostic_amplifier_open_loop_gain": 1e6},
        "dc": dc, "passive_poles": poles,
    }, indent=2))
    command("destroy all")
    if dll_directory:
        dll_directory.close()


if __name__ == "__main__":
    main()
