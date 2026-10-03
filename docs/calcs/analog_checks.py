"""I reproduce analog selection arithmetic and optional TI-model AO checks.

The vendor model remains external. These checks are not hardware qualification.
"""
from __future__ import annotations
import argparse
import ctypes as c
import hashlib
import json
import math
import os
import shutil
import tempfile
from pathlib import Path


class Vector(c.Structure):
    _fields_ = [("name", c.c_char_p), ("type", c.c_int), ("flags", c.c_short),
                ("real", c.POINTER(c.c_double)), ("complex", c.c_void_p),
                ("length", c.c_int)]


def arithmetic():
    shunt = 1000 / 5
    rcs = 1 / (1 / 1210 + 1 / 124000)
    bottom = 1 / (1 / 1500 + 1 / 47000)
    post = bottom / (1000 + bottom)
    ao = 68000 / 268000 * post
    cs = 68000 / 124000 * post
    # ADC input is a biased resistance, not a ground-referenced resistor.
    rin = 850000
    rs = 1000 + 100 + 8.3
    adc_at_10 = (10 * rin + 2.5 * rs) / (rin + rs)
    loop_series = 1000 + 8.3
    loop_at_20 = (.020 * shunt * rin + 2.5 * shunt + 2.5 * loop_series) / (rin + shunt + loop_series)
    out = {
        "scope": "Selection arithmetic; specified resistor tolerances are cornered without statistical averaging",
        "shunt_ohm": shunt, "shunt_power_rating_w": 5 * .25,
        "shunt_power_at_40ma_w": .04 ** 2 * shunt,
        "one_shunt_resistor_power_at_40ma_w": (.04 / 5) ** 2 * 1000,
        "one_shunt_resistor_30v_55us_energy_j": 30 ** 2 / 1000 * 55e-6,
        "loop_max_20ma_burden_v": .020 * (shunt + 12.5),
        "voltage_adc_at_10v_nominal_850kohm_v": adc_at_10,
        "current_adc_at_20ma_nominal_850kohm_v": loop_at_20,
        "ao_readback_v_per_terminal_v": ao,
        "cs_readback_v_per_raw_v": cs,
        "cs_effective_burden_ohm": rcs,
        "cs_adc_at_0p5a_nominal_ratio300_v": .5 / 300 * rcs * cs,
        "vfp11_nominal_v": 1.193 * (1 + 82000 / 10000),
        "vfp6_nominal_v": 1.193 * (1 + 40200 / 10000),
        # ±0.2% per resistor includes ±0.1% initial and 25ppm/°C over ±25°C.
        "vfp11_corner_v": [1.193 * .98 * (1 + 82000 * .998 / (10000 * 1.002)) - .1e-6 * 82000 * 1.002,
                             1.193 * 1.02 * (1 + 82000 * 1.002 / (10000 * .998)) + .1e-6 * 82000 * 1.002],
        "vfp6_corner_v": [1.193 * .98 * (1 + 40200 * .998 / (10000 * 1.002)) - .1e-6 * 40200 * 1.002,
                            1.193 * 1.02 * (1 + 40200 * 1.002 / (10000 * .998)) + .1e-6 * 40200 * 1.002],
        "ao_gain_resistor_drift_25c_opposing_25ppm_v_at10v": 10 * .75 * 50e-6 * 25,
        "adc_volt_filter_nominal_hz": 1 / (2 * math.pi * rs * 1e-6),
        "adc_loop_filter_nominal_hz": 1 / (2 * math.pi * (shunt + loop_series) * 1e-6),
        "ao_fault_peak_a_at45v_resistor_minus1percent": 45 / 99,
        "ao_series_resistor_45v_1p8us_screening_energy_j": 45 ** 2 / 99 * 1.8e-6,
        "ao_feedback_fault_a_at45v_min_switch_and_resistor": 45 / (4700 * .998 + 600),
        "readback_off_s_max_at5p75v_v": 5.75 * (1500 * 1.002) / (1000 * .998 + 1500 * 1.002),
    }
    supply_min = 12.72283
    bulk_min = 500e-6
    parent_load = .025
    # The 100nF TMUX VFP bypass is parallel with the 10uF LDO output cap.
    child_cap_max = (10e-6 + .1e-6) * 1.10 * 1.15
    tau = child_cap_max * 4700 * 1.002
    fall_time = supply_min * bulk_min / parent_load
    disable_delay = .001
    # Disabled LDO supply current is pessimistically assigned entirely to OUT.
    asymptote = 5e-6 * 4700 * 1.002
    child_ends = [asymptote + (v - asymptote) * math.exp(-(fall_time - disable_delay) / tau)
                  for v in (out["vfp11_corner_v"][1], out["vfp6_corner_v"][1])]
    out["vfp_shutdown"] = {"parent_disable_min_v": supply_min,
                           "parent_bulk_min_f": bulk_min,
                           "parent_discharge_max_a": parent_load,
                           "child_disable_delay_max_s": disable_delay,
                           "child_cap_max_f": child_cap_max,
                           "child_tau_max_s": tau,
                           "parent_zero_time_s": fall_time,
                           "child_end_max_v": child_ends,
                           "scope": "Parent >=500uF effective over 0-50C; child disable <=1ms; ordinary rail removal, no internal hard short; convex exponential-minus-linear bound"}
    assert out["shunt_power_at_40ma_w"] < out["shunt_power_rating_w"]
    assert out["loop_max_20ma_burden_v"] == 4.25
    assert .6 < out["cs_adc_at_0p5a_nominal_ratio300_v"] < .7
    assert max(child_ends) < .3
    assert out["ao_fault_peak_a_at45v_resistor_minus1percent"] < .515
    assert out["ao_feedback_fault_a_at45v_min_switch_and_resistor"] < .010
    assert out["readback_off_s_max_at5p75v_v"] < 3.6
    return out


def vendor_checks(library: Path, model: Path, code_models: Path):
    dll_dir = os.add_dll_directory(str(library.parent)) if os.name == "nt" else None
    ng = c.CDLL(str(library))
    messages = []
    callback = c.CFUNCTYPE(c.c_int, c.c_char_p, c.c_int, c.c_void_p)
    exiting = c.CFUNCTYPE(c.c_int, c.c_int, c.c_bool, c.c_bool, c.c_int, c.c_void_p)

    @callback
    def send(message, _identifier, _user):
        messages.append(message.decode("utf-8", errors="replace"))
        return 0

    @exiting
    def controlled_exit(status, _immediate, _quit, _identifier, _user):
        messages.append(f"ngspice exit {status}")
        return 0

    ng.ngSpice_Init.argtypes = [callback, callback, exiting, c.c_void_p, c.c_void_p, c.c_void_p, c.c_void_p]
    ng.ngSpice_Command.argtypes = [c.c_char_p]
    ng.ngSpice_Circ.argtypes = [c.POINTER(c.c_char_p)]
    ng.ngGet_Vec_Info.argtypes = [c.c_char_p]
    ng.ngGet_Vec_Info.restype = c.POINTER(Vector)
    ng.ngSpice_Init(send, send, controlled_exit, None, None, None, None)
    def command(value):
        if ng.ngSpice_Command(value.encode()) != 0:
            raise RuntimeError(value + "\n" + "\n".join(messages[-30:]))
    command("set ngbehavior=ps")
    # The ngspice command parser treats quote characters as filename content.
    # Its codemodel command cannot handle the Windows installation's spaces.
    cm_temp = tempfile.TemporaryDirectory(prefix="analog_cm_", ignore_cleanup_errors=True)
    for filename in ("analog.cm", "spice2poly.cm", "xtradev.cm"):
        copy = Path(cm_temp.name) / filename
        shutil.copyfile(code_models / filename, copy)
        command(f"codemodel {copy.as_posix()}")
    def vector(name):
        v = ng.ngGet_Vec_Info(name.encode())
        if not v or not v.contents.real or v.contents.length < 1:
            raise RuntimeError("Missing " + name + "\n" + "\n".join(messages[-40:]))
        return [v.contents.real[i] for i in range(v.contents.length)]
    results = []
    for cap in (100e-12, 1e-9, 10e-9):
        for feedback in (600, 3900):
            lines = ["TI OPAx197 AO two-stage typical macromodel check",
                     f'.include "{model.as_posix()}"',
                     ".global GND", "RGND GND 0 1m", "VCC vp 0 15", "VEE vn 0 -.232",
                     "VIN vin 0 PULSE(.25 2.25 100u 10u 10u 900u 2m)",
                     "XGAIN vin fba vp vn gain OPAx197", "RGA gain fba 30k", "RGB fba 0 10k",
                     "XBUF gain fbb vp vn driver OPAx197",
                     "RON driver switched 12.5", "RPRO switched terminal 100",
                     f"RFB terminal fbb {feedback + 4700}", "CCOMP driver fbb 1n",
                     "RLOAD terminal 0 10k", "RPULL terminal 0 100k", "RREAD terminal 0 268k",
                     f"CCABLE terminal 0 {cap}", ".options reltol=1e-3 abstol=1e-9 gmin=1e-10 method=gear", ".end"]
            source = (c.c_char_p * (len(lines) + 1))(*[x.encode() for x in lines], None)
            if ng.ngSpice_Circ(source) != 0:
                raise RuntimeError("Circuit rejected\n" + "\n".join(messages[-40:]))
            command("tran 1u 900u")
            ts, ys = vector("time"), vector("terminal")
            band = [y for t, y in zip(ts, ys) if t >= 500e-6]
            peak = max(y for t, y in zip(ts, ys) if 120e-6 <= t <= 500e-6)
            final = sum(band[-100:]) / len(band[-100:])
            error = max(abs(y - final) for y in band)
            result = {"cable_capacitance_f": cap, "feedback_switch_ohm": feedback,
                      "main_switch_ohm": 12.5, "terminal_series_ohm": 100,
                      "external_feedback_series_ohm": 4700, "compensation_f": 1e-9,
                      "final_terminal_v": final, "peak_terminal_v": peak,
                      "peak_overshoot_percent": max(0, (peak - final) / 8 * 100),
                      "residual_after_500us_v": error}
            if abs(final - 9) > .01 or error > .01 or result["peak_overshoot_percent"] > 5:
                raise RuntimeError("AO transient acceptance failed: " + json.dumps(result))
            results.append(result)
            command("destroy all")
    if dll_dir:
        dll_dir.close()
    # Loaded native code-model files remain open until the process exits.
    # Leave cleanup to TemporaryDirectory; Windows may defer locked-file removal.
    cm_temp._finalizer.detach()
    return {"scope": "TI OPAx197 typical macromodel; switches modeled as fixed resistors; excludes switch transitions, layout, tolerances, fault pulses, and hardware qualification",
            "model_source": "https://www.ti.com/lit/zip/sboma34",
            "model_sha256": hashlib.sha256(model.read_bytes()).hexdigest(), "corners": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--code-models", type=Path)
    args = parser.parse_args()
    result = {"arithmetic": arithmetic()}
    if any((args.library, args.model, args.code_models)):
        if not all((args.library, args.model, args.code_models)):
            parser.error("All three SPICE paths are required together")
        result["vendor_ao"] = vendor_checks(args.library.resolve(strict=True), args.model.resolve(strict=True), args.code_models.resolve(strict=True))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
