"""I reproduce selected Rev A design calculations independently of bench tests."""

from __future__ import annotations

import argparse
import json


def calculate(service_w: float, efficiency: float) -> dict:
    n, current, shunt = 4, 0.5, 200.0
    return {
        "scope": "Design arithmetic; prototype measurements remain pending",
        "assumptions": {
            "service_power_delivered_w": service_w,
            "aggregate_conversion_efficiency": efficiency,
            "output_channels": n,
            "current_per_output_a": current,
            "input_continuous_budget_a": 3.0,
            "excluded": "Extra protection losses, inrush, limit tolerances, transient peaks",
        },
        "input_current": [
            {"supply_v": v,
             "total_before_extra_losses_a": n * current + service_w / (v * efficiency),
             "remaining_3a_budget_a": 3.0 - n * current - service_w / (v * efficiency)}
            for v in (9.0, 12.0, 24.0, 30.0)
        ],
        "current_receiver": {
            "shunt_ohm": shunt,
            "at_4ma_v": 0.004 * shunt,
            "at_20ma_v": 0.020 * shunt,
            "at_20ma_shunt_w": 0.020**2 * shunt,
            "at_25_6ma_shunt_w": 0.0256**2 * shunt,
            "5_12v_range_overrange_ma": 5.12 / shunt * 1000,
            "current_lsb_ua": 5.12 / 2**16 / shunt * 1e6,
            "200ohm_direct_30v_fault_w_without_protection": 30.0**2 / shunt,
            "note": "Direct-fault power motivates active protection; this is not a permitted shunt operating point.",
        },
        "accuracy_targets": {
            "voltage_room_temperature_mv": 10.0 * 0.002 * 1000,
            "current_room_temperature_ua": (20.0 - 4.0) * 0.002 * 1000,
            "voltage_temperature_goal_mv": 10.0 * 0.005 * 1000,
            "current_temperature_goal_ua": (20.0 - 4.0) * 0.005 * 1000,
            "ao_mv": 10.0 * 0.005 * 1000,
            "voltage_lsb_uv_on_10_24v_range": 10.24 / 2**16 * 1e6,
            "note": "Quantization is only one error term; calibration and component/temperature errors remain.",
        },
        "output_path": {
            "blocking_diode_w_per_channel_range": [current * 0.3, current * 0.5],
            "four_blocking_diodes_total_w_range": [n * current * 0.3, n * current * 0.5],
            "hs_switch_total_w_at_160mohm_typical": n * current**2 * 0.160,
            "note": "160 milliohm is illustrative typical resistance; worst-case hot resistance and other losses remain.",
        },
        "ao_loading": {
            "load_ohm": 10000.0,
            "at_10v_load_ma": 10.0 / 10000.0 * 1000,
            "50ohm_series_drop_mv_at_1ma": 0.001 * 50.0 * 1000,
            "note": "This series drop consumes the entire AO error allowance before other errors.",
        },
        "resistive_load_fixture": [
            {"supply_v": v,
             "ideal_terminal_resistance_ohm_per_channel": v / current,
             "minimum_dissipation_w_per_channel": v * current,
             "total_fixture_dissipation_w": n * v * current}
            for v in (9.0, 12.0, 24.0, 30.0)
        ],
        "fixed_48ohm_fixture_at_30v": {
            "current_a_per_channel": 30.0 / 48.0,
            "dissipation_w_per_channel": 30.0**2 / 48.0,
            "note": "A 24 V fixture exceeds 0.5 A/channel at 30 V; choose appropriate loading.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--service-w", type=float, default=5.0)
    parser.add_argument("--efficiency", type=float, default=0.85)
    args = parser.parse_args()
    if args.service_w < 0 or not 0 < args.efficiency <= 1:
        parser.error("service power must be nonnegative and efficiency must be in (0, 1]")
    print(json.dumps(calculate(args.service_w, args.efficiency), indent=2))


if __name__ == "__main__":
    main()
