"""I reproduce analog-input and load-current-diagnostic selection arithmetic.

These bounded equations support capture; they are not hardware qualification.
"""
from __future__ import annotations
import json
import math


def arithmetic():
    shunt = 1000 / 5
    rcs = 1 / (1 / 1210 + 1 / 124000)
    switch_on = 2  # TMUX1511 typical, not a worst-case guarantee.
    bottom = 1 / (1 / 1500 + 1 / (47000 + switch_on))
    post = bottom / (1000 + bottom) * 47000 / (47000 + switch_on)
    cs = 68000 / 124000 * post
    # ADC input is a biased resistance, not a ground-referenced resistor.
    rin = 850000
    rs = 1000 + 100 + 8.3
    adc_at_10 = (10 * rin + 2.5 * rs) / (rin + rs)
    loop_series = 1000 + 8.3
    loop_at_20 = (.020 * shunt * rin + 2.5 * shunt + 2.5 * loop_series) / (rin + shunt + loop_series)
    out = {
        "scope": "Selection arithmetic; fixed illustrative ADC resistance/on-resistance; specified resistor tolerances cornered without statistical averaging",
        "shunt_ohm": shunt, "shunt_power_rating_w": 5 * .25,
        "shunt_power_at_40ma_w": .04 ** 2 * shunt,
        "one_shunt_resistor_power_at_40ma_w": (.04 / 5) ** 2 * 1000,
        "one_shunt_resistor_30v_55us_energy_j": 30 ** 2 / 1000 * 55e-6,
        "loop_max_20ma_burden_v": .020 * (shunt + 12.5),
        "voltage_adc_at_10v_nominal_850kohm_v": adc_at_10,
        "current_adc_at_20ma_nominal_850kohm_v": loop_at_20,
        "cs_adc_v_per_raw_v_nominal": cs,
        "cs_effective_burden_ohm": rcs,
        "cs_adc_at_0p5a_nominal_ratio300_v": .5 / 300 * rcs * cs,
        "diagnostic_switch_typical_on_ohm": switch_on,
        "diagnostic_off_leakage_2ua_times47kohm_v": 2e-6 * 47000,
        "input_protection_15v_reservation_a": .010,
        "current_diagnostic_5v_reservation_a": .012,
        "vfp11_nominal_v": 1.193 * (1 + 82000 / 10000),
        "vfp6_nominal_v": 1.193 * (1 + 40200 / 10000),
        # ±0.2% per resistor includes ±0.1% initial and 25ppm/°C over ±25°C.
        "vfp11_corner_v": [1.193 * .98 * (1 + 82000 * .998 / (10000 * 1.002)) - .1e-6 * 82000 * 1.002,
                             1.193 * 1.02 * (1 + 82000 * 1.002 / (10000 * .998)) + .1e-6 * 82000 * 1.002],
        "vfp6_corner_v": [1.193 * .98 * (1 + 40200 * .998 / (10000 * 1.002)) - .1e-6 * 40200 * 1.002,
                            1.193 * 1.02 * (1 + 40200 * 1.002 / (10000 * .998)) + .1e-6 * 40200 * 1.002],
        "adc_voltage_filter_loaded_nominal_hz": 1 / (2 * math.pi * (1 / (1 / rs + 1 / rin)) * 1e-6),
        "adc_current_filter_loaded_nominal_hz": 1 / (2 * math.pi * (1 / (1 / (shunt + loop_series) + 1 / rin)) * 1e-6),
        "diagnostic_off_s_max_at5p75v_v": 5.75 * (1500 * 1.002) / (1000 * .998 + 1500 * 1.002),
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
    assert out["diagnostic_off_s_max_at5p75v_v"] < 3.6
    return out



if __name__ == "__main__":
    print(json.dumps({"arithmetic": arithmetic()}, indent=2))
