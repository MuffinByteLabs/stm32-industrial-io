"""I reproduce selected Rev A design calculations independently of bench tests."""

from __future__ import annotations

import argparse
import json


def calculate(service_w: float, efficiency: float) -> dict:
    n, current, shunt = 4, 0.5, 200.0
    service_reservations = {
        "mcu_and_essential_logic_w": 0.75,
        "external_adc_and_field_logic_w": 0.50,
        "analog_auxiliaries_w": 0.65,
        "two_relay_coils_w": 1.10,
        "two_isolated_bus_supplies_w": 2.75,
    }
    reserved_w = sum(service_reservations.values())
    relay_upper_v = 5.25
    relay_min_cold_ohm = 62.5 * 0.90 * (1 + 0.00393 * (0.0 - 23.0))
    adc_input_ohm, adc_bias_v, example_series_ohm = 1_000_000.0, 2.5, 1000.0
    limit_resistor_ohm = 5110.0
    sense_burden_ohm = 1 / (1 / 1210.0 + 1 / 124000.0)
    return {
        "scope": "Design arithmetic; prototype measurements remain pending",
        "assumptions": {
            "service_power_delivered_w": service_w,
            "main_buck_conversion_efficiency_assumed": efficiency,
            "output_channels": n,
            "current_per_output_a": current,
            "input_continuous_budget_a": 3.0,
            "excluded": "Extra input-protection losses, high-side operating current/VFIELD overhead, inrush, limit tolerances, transient peaks",
            "note": "Service power is referred to the delivered 5V_FIELD rail and includes downstream conversion losses. Efficiency is an assumption, not a guaranteed datasheet minimum.",
        },
        "service_reservations": {
            "branches_w": service_reservations,
            "total_reserved_w": reserved_w,
            "margin_to_selected_ceiling_w": service_w - reserved_w,
            "nominal_design_ceiling_w": 6.0,
            "note": "Branch engineering allocations combine component limits and reserves; they are not a completed worst-case BOM maximum. Inrush and fault loading are separate.",
        },
        "isolation_budget": {
            "converter_candidate": "UCC33421QDHARQ1, two independent 5 V outputs",
            "each_converter_output_class_w": 1.5,
            "isolated_output_upper_v": 5.15,
            "iso1410_bus_dynamic_max_a": 0.160,
            "iso1042_bus_dc_dominant_max_a": 0.0734,
            "can_switching_cable_reserve_a": 0.020,
            "combined_bus_bias_local_reserve_a": 0.010,
            "isolated_efficiency_assumed": 0.50,
            "total_output_with_reserves_w": 5.15 * (0.160 + 0.0734 + 0.020 + 0.010),
            "estimated_primary_with_reserves_w": 5.15 * (0.160 + 0.0734 + 0.020 + 0.010) / 0.50,
            "primary_reservation_w": service_reservations["two_isolated_bus_supplies_w"],
            "note": "160 mA is specified at 500 kbps, 54 ohm/50 pF; 73.4 mA is DC dominant at 60 ohm, not a guaranteed dynamic FD maximum. Reserves and 50% efficiency require circuit and measured closure; the module's output class derates with temperature.",
        },
        "relay_coils": {
            "coil_candidate": "G5Q-1 DC5, SPDT",
            "nominal_current_per_coil_a": 0.080,
            "resistance_at_23c_nominal_ohm": 62.5,
            "resistance_tolerance_fraction": 0.10,
            "copper_temperature_coefficient_per_c_assumed": 0.00393,
            "upper_rail_v": relay_upper_v,
            "minimum_resistance_at_0c_model_ohm": relay_min_cold_ohm,
            "cold_upper_rail_total_current_a": 2 * relay_upper_v / relay_min_cold_ohm,
            "cold_upper_rail_total_power_w": 2 * relay_upper_v**2 / relay_min_cold_ohm,
            "reservation_w": service_reservations["two_relay_coils_w"],
            "note": "Copper-temperature modeling is an engineering assumption; 80 mA is nominal, not a worst-case supply bound. Qualify the actual coils and rail envelope.",
        },
        "analog_auxiliary_budget": {
            "positive_rail_v": 15.0,
            "positive_rail_screening_upper_v": 15.5,
            "positive_rail_design_current_a": 0.025,
            "positive_output_power_w": 15.0 * 0.025,
            "boost_efficiency_assumed": 0.60,
            "boost_primary_power_estimate_w": 15.0 * 0.025 / 0.60,
            "boost_primary_power_at_upper_rail_estimate_w": 15.5 * 0.025 / 0.60,
            "branch_reservation_w": service_reservations["analog_auxiliaries_w"],
            "upper_rail_margin_to_reservation_w": service_reservations["analog_auxiliaries_w"] - 15.5 * 0.025 / 0.60,
            "note": "25 mA positive-rail capacity conservatively covers two TPS26611 supplies, two TMUX groups, VFP supplies/bleeders and reserve. The 60% boost efficiency is an engineering assumption. Nominal conversion is 0.625 W; the 15.5 V scenario is about 0.646 W, leaving only 0.0042 W in the retained 0.65 W allocation before unmodeled effects. Efficiency and the complete allocation remain to be closed; boost disable does not isolate its passive output path.",
        },
        "input_current": [
            {"supply_v": v,
             "total_before_extra_losses_a": n * current + service_w / (v * efficiency),
             "output_bleeders_nominal_a": n * v / 10000,
             "high_side_operating_current_engineering_reserve_a": 0.020,
             "total_with_bleeders_and_operating_reserve_a": n * current + service_w / (v * efficiency) + n * v / 10000 + 0.020,
             "remaining_3a_after_bleeders_and_operating_reserve_a": 3.0 - n * current - service_w / (v * efficiency) - n * v / 10000 - 0.020}
            for v in (9.0, 12.0, 24.0, 30.0)
        ],
        "vfield_overhead": {
            "pre_diode_bleeders": "Four 10 kohm / 0.25 W resistors; nominal 12 mA and 0.36 W total at 30 V",
            "high_side_operating_current_reserve_a": 0.020,
            "note": "20 mA is an engineering allocation, not a guaranteed TPS4H160 maximum. Bleeder tolerance, measured chip consumption and input-protection losses require margin closure at actual post-protection voltage.",
        },
        "post_protection_low_line_contract": {
            "connector_minimum_v": 9.0,
            "vfield_minimum_target_v": 8.4,
            "maximum_protection_path_drop_target_v": 0.6,
            "main_buck_efficiency_assumed": 0.80,
            "total_with_nominal_bleeders_and_operating_reserve_a": n * current + service_w / (8.4 * 0.80) + n * 8.4 / 10000 + 0.020,
            "margin_to_3a_before_remaining_effects_a": 3.0 - n * current - service_w / (8.4 * 0.80) - n * 8.4 / 10000 - 0.020,
            "note": "Captured hot/tolerance fuse, FET, eFuse, terminals and traces must prove VFIELD >=8.4 V at 9 V connector with combined load. The 20 mA allocation and 80% efficiency are assumptions, not guaranteed maxima/minima. If this contract fails, revise the power path and recheck the retained operating envelope before release.",
        },
        "efuse_current_limit_reference": {
            "continuous_input_target_a": 3.0,
            "candidate": "TPS26632RGER",
            "initial_limit_resistor_ohm": limit_resistor_ohm,
            "resistor_tolerance_fraction": 0.001,
            "nominal_limit_a": 18000.0 / limit_resistor_ohm,
            "illustrative_limit_tolerance_fraction": 0.10,
            "illustrative_lower_limit_a": 18000.0 / (limit_resistor_ohm * 1.001) * 0.90,
            "illustrative_upper_limit_a": 18000.0 / (limit_resistor_ohm * 0.999) * 1.10,
            "note": "The +/-10% IC spread is an engineering screening assumption, aligned with Power.md; specified endpoint tests do not guarantee that spread at the selected 3.52 A setpoint. This reference does not freeze a guaranteed assembled limit or a fuse rating.",
        },
        "input_voltage_coordination": {
            "continuous_window_v": [9.0, 30.0],
            "initial_positive_dc_fault_v": 36.0,
            "initial_positive_dc_fault_temperature_c": 25.0,
            "tvs_candidate": "SMCJ33CA",
            "catalog_tvs_breakdown_min_at_25c_v": 36.7,
            "catalog_tvs_clamp_at_28_2a_10_1000us_v": 53.3,
            "efuse_input_output_negative_10ms_stress_limit_v": -85.0,
            "negative_clamp_plus_retained_30v_differential_v": -(53.3 + 30.0),
            "negative_clamp_plus_retained_35v_differential_v": -(53.3 + 35.0),
            "note": "36 V requires a bounded source, tolerance, duration, and TVS temperature; it is not a cold-corner or sustained +40 V guarantee. Catalog clamping is waveform-specific. Negative pulse coordination including initial retained output, temperature, parasitics and overshoot remains pending.",
        },
        "current_receiver": {
            "shunt_ohm": shunt,
            "at_4ma_v": 0.004 * shunt,
            "at_20ma_v": 0.020 * shunt,
            "at_20ma_shunt_w": 0.020**2 * shunt,
            "supported_overrange_goal_ma": 24.0,
            "at_24ma_v": 0.024 * shunt,
            "at_24ma_shunt_w": 0.024**2 * shunt,
            "at_25_6ma_shunt_w": 0.0256**2 * shunt,
            "5_12v_range_overrange_ma": 5.12 / shunt * 1000,
            "current_lsb_ua": 5.12 / 2**16 / shunt * 1e6,
            "200ohm_direct_30v_fault_w_without_protection": 30.0**2 / shunt,
            "loop_protector_candidate": "TPS26611DDFR, supply 15 V and default-off enable",
            "protector_maximum_ron_ohm": 12.5,
            "20ma_shunt_plus_protector_burden_v": 0.020 * (shunt + 12.5),
            "24ma_shunt_plus_protector_burden_v": 0.024 * (shunt + 12.5),
            "fault_current_limit_range_ma": [25.0, 40.0],
            "at_maximum_40ma_limit_shunt_v": 0.040 * shunt,
            "at_maximum_40ma_limit_shunt_w": 0.040**2 * shunt,
            "minimum_nominal_shunt_power_class_w": 1.0,
            "note": "The ADC range alone gives 25.6 mA; the complete supported-overrange goal is 24 mA. 4.25 V burden at 20 mA includes only the shunt and maximum protector resistance, before terminals/wiring. Fault energy comes from the external loop, separate from service supply power. Verify resistor derating/pulse limits and protector tolerance; direct-fault power is not a permitted operating point.",
        },
        "adc_loading_example": {
            "adc_input_impedance_reference_ohm": adc_input_ohm,
            "adc_input_impedance_min_max_ohm": [850_000.0, 1_150_000.0],
            "adc_equivalent_bias_v": adc_bias_v,
            "illustrative_series_resistance_ohm": example_series_ohm,
            "formula": "V_ADC = (V_source * R_ADC + V_bias * R_series) / (R_ADC + R_series)",
            "points": [
                {"source_v": v,
                 "adc_v": (v * adc_input_ohm + adc_bias_v * example_series_ohm) / (adc_input_ohm + example_series_ohm),
                 "loading_error_mv": (adc_bias_v - v) * example_series_ohm / (adc_input_ohm + example_series_ohm) * 1000,
                 "loading_error_mv_with_minimum_850kohm": (adc_bias_v - v) * example_series_ohm / (850_000.0 + example_series_ohm) * 1000}
                for v in (0.0, 2.5, 10.0)
            ],
            "current_shunt_model_formula": "V_shunt = (I_terminal + V_bias / R_ADC) / (1 / R_shunt + 1 / R_ADC)",
            "current_shunt_points_without_additional_sense_series_r": [
                {"terminal_current_ma": i * 1000,
                 "shunt_voltage_v": (i + adc_bias_v / adc_input_ohm) / (1 / shunt + 1 / adc_input_ohm),
                 "indicated_current_error_ua": ((i + adc_bias_v / adc_input_ohm) / (1 / shunt + 1 / adc_input_ohm) / shunt - i) * 1e6}
                for i in (0.004, 0.020, 0.024)
            ],
            "note": "This nominal 1 Mohm/2.5 V equivalent model illustrates offset and loading, not a divider to ground. The 1 kohm example is not a frozen circuit value; verify impedance/bias tolerance, protector resistance, external source impedance, filtering and calibration.",
        },
        "accuracy_targets": {
            "voltage_room_temperature_mv": 10.0 * 0.002 * 1000,
            "current_room_temperature_ua": (20.0 - 4.0) * 0.002 * 1000,
            "voltage_temperature_goal_mv": 10.0 * 0.005 * 1000,
            "current_temperature_goal_ua": (20.0 - 4.0) * 0.005 * 1000,
            "voltage_lsb_uv_on_10_24v_range": 10.24 / 2**16 * 1e6,
            "note": "Quantization is only one error term; calibration and component/temperature errors remain.",
        },
        "output_path": {
            "high_side_candidate": "TPS4H160BQPWPRQ1",
            "blocking_and_freewheel_diode_candidate": "STPS2H100A",
            "diode_reverse_voltage_class_v": 100.0,
            "diode_current_class_a": 2.0,
            "diode_loss_model_125c_w_per_channel": 0.56 * current + 0.045 * current**2,
            "four_blocking_diodes_loss_model_125c_w": n * (0.56 * current + 0.045 * current**2),
            "hs_switch_four_channel_conduction_w_with_25c_max_ron": n * current**2 * 0.165,
            "hs_switch_four_channel_conduction_w_with_150c_max_ron": n * current**2 * 0.280,
            "hs_switch_four_channel_conduction_w_at30v_with_nominal_bleeders": n * (current + 30 / 10000)**2 * 0.280,
            "reference_short_circuit_switch_w_at_24v_0_7a": 24.0 * 0.7,
            "initial_current_limit_resistor_ohm": 2870.0,
            "nominal_current_limit_a": 0.8 * 2500.0 / 2870.0,
            "selected_sense_burden_ohm": sense_burden_ohm,
            "nominal_sense_ratio": 300.0,
            "nominal_sense_v_at_0_5a": current / 300.0 * sense_burden_ohm,
            "sense_fault_voltage_v": [4.5, 6.5],
            "note": "The diode equation is the manufacturer's 125 C loss model, not a guaranteed maximum across production. Ron limits bound conduction only; operating current, diode leakage, fault energy, thermal coupling and layout remain. Sense/current-limit tolerance and an unpowered MCU require protection; thermal swing can precede latched thermal shutdown.",
        },
        "blocking_fet_reference": {
            "candidate": "CSD19537Q3",
            "fast_gate_discharge_candidate": "BSS138P,215",
            "vds_rating_v": 100.0,
            "gate_absolute_voltage_v": 20.0,
            "rds_on_max_at_25c_vgs10v_ohm": 0.0145,
            "conduction_w_at_3a_25c_vgs10v_reference": 3.0**2 * 0.0145,
            "efuse_gate_drive_min_typ_max_v": [8.3, 10.23, 14.0],
            "note": "The 10 V Rds maximum does not establish a maximum loss at the eFuse's 8.3 V minimum gate drive. Verify lower-drive/hot resistance and transient SOA. A 100 V FET alone does not resolve the IC's -85 V input/output pulse limit.",
        },
        "pwm_budget_policy": {
            "channel": "DO3 / PE9 / TIM1_CH1 / AF2",
            "initial_frequency_hz": 100.0,
            "commanded_duty_percent": [10.0, 90.0],
            "static_endpoints_percent": [0.0, 100.0],
            "instantaneous_load_ceiling_a": current,
            "continuous_full_on_channels_budgeted": n,
            "note": "No input-current credit for reduced duty. PWM overlap redistributes delivered power into switch heat and is screened separately in pwm_checks.py; do not add it twice to the fixed-current supply model. High-side operating current, parasitics, conversion/protection losses and measured margins remain to be closed.",
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
    parser.add_argument("--service-w", type=float, default=6.0)
    parser.add_argument("--efficiency", type=float, default=0.85)
    args = parser.parse_args()
    if args.service_w < 0 or not 0 < args.efficiency <= 1:
        parser.error("service power must be nonnegative and efficiency must be in (0, 1]")
    print(json.dumps(calculate(args.service_w, args.efficiency), indent=2))


if __name__ == "__main__":
    main()
