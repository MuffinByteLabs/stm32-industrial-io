"""I check DO3 PWM timing and loss assumptions; hardware qualification is pending.

The edge model is analytical, not a TPS4H160 transistor/macromodel simulation.
I use full 0-to-100% linear ramps at the datasheet's 10-to-90% slew values as a
deliberately conservative timing approximation. Independent corners may not
occur together; I do not turn this sweep into a guaranteed output-accuracy spec.
"""

from __future__ import annotations

from itertools import product
import json
import math


TIMER_HZ = 144_000_000
PRESCALER = 143
AUTO_RELOAD = 9999
PWM_HZ = TIMER_HZ / ((PRESCALER + 1) * (AUTO_RELOAD + 1))
PERIOD_S = 1 / PWM_HZ
MIN_DUTY, MAX_DUTY = 0.10, 0.90
CURRENT_A = 0.5
HOT_RON_OHM = 0.280
SAMPLE_START_S, SAMPLE_END_S = 600e-6, 800e-6
BLEEDER_OHM = 10_000
BLEEDER_ERROR = .01 + 100e-6 * 25
BLEEDER_MIN_OHM = BLEEDER_OHM * (1 - BLEEDER_ERROR)
BLEEDER_MAX_OHM = BLEEDER_OHM * (1 + BLEEDER_ERROR)
HIGH_SIDE_SUPPLY_CORNERS_V = (8.4, 9.0, 12.0, 24.0, 30.0)


def edge_case(supply_v, duty, slew_on_v_us, slew_off_v_us,
              delay_on_s, delay_off_s):
    """I integrate a resistive-load waveform with finite delayed linear edges."""
    rise_s = supply_v / slew_on_v_us * 1e-6
    fall_s = supply_v / slew_off_v_us * 1e-6
    plateau_start_s = delay_on_s + rise_s
    plateau_end_s = duty * PERIOD_S + delay_off_s
    plateau_s = plateau_end_s - plateau_start_s
    low_s = PERIOD_S + delay_on_s - (plateau_end_s + fall_s)
    assert plateau_s > 0, "The output cannot complete its rising edge."
    assert low_s > 0, "The output cannot complete its falling edge."
    # Integrals of v(t) and v(t)^2 for ramps plus the constant high interval.
    mean_v = supply_v * (plateau_s + (rise_s + fall_s) / 2) / PERIOD_S
    mean_square_v = supply_v**2 * (plateau_s + (rise_s + fall_s) / 3) / PERIOD_S
    ideal_resistor_power_w = supply_v * CURRENT_A * duty
    resistor_power_w = mean_square_v * CURRENT_A / supply_v
    driver_current_a = CURRENT_A + supply_v / BLEEDER_MIN_OHM
    resistor_overlap_w = (supply_v * driver_current_a * (rise_s + fall_s)
                           * PWM_HZ / 6)
    constant_current_overlap_w = (supply_v * driver_current_a * (rise_s + fall_s)
                                  * PWM_HZ / 2)
    return {
        "supply_v": supply_v,
        "command_duty": duty,
        "slew_on_v_per_us": slew_on_v_us,
        "slew_off_v_per_us": slew_off_v_us,
        "delay_on_us": delay_on_s * 1e6,
        "delay_off_us": delay_off_s * 1e6,
        "rise_full_swing_us": rise_s * 1e6,
        "fall_full_swing_us": fall_s * 1e6,
        "high_plateau_us": plateau_s * 1e6,
        "low_plateau_us": low_s * 1e6,
        "sample_start_after_full_rise_us": (SAMPLE_START_S - plateau_start_s) * 1e6,
        "sample_end_before_falling_command_us": (duty * PERIOD_S - SAMPLE_END_S) * 1e6,
        "mean_output_fraction": mean_v / supply_v,
        "resistor_power_fraction_of_full_dc": mean_square_v / supply_v**2,
        "resistor_power_error_from_ideal_fraction": resistor_power_w / ideal_resistor_power_w - 1,
        "resistor_overlap_loss_w": resistor_overlap_w,
        "constant_current_overlap_estimate_w": constant_current_overlap_w,
    }


def calculate():
    cases = [edge_case(v, d, sr_on, sr_off, td_on, td_off)
             for v, d, sr_on, sr_off, td_on, td_off in product(
                 HIGH_SIDE_SUPPLY_CORNERS_V,
                 tuple(n / 10 for n in range(1, 10)),
                 (0.1, 0.3, 0.55), (0.1, 0.3, 0.55),
                 (20e-6, 90e-6), (20e-6, 90e-6))]
    worst_rise_us = 30.0 / 0.1 + 90.0
    shortest_command_us = min(MIN_DUTY, 1 - MAX_DUTY) * PERIOD_S * 1e6
    # The 1 nF ADC node is driven by 1k/1.5k in parallel with 47k when enabled.
    readback_thevenin_ohm = 1 / (1 / 1000 + 1 / 1500 + 1 / 47000)
    readback_five_tau_us = 5 * readback_thevenin_ohm * 1e-9 * 1e6
    selected = edge_case(30.0, .9, .1, .1, 90e-6, 90e-6)
    driver_peak_a = CURRENT_A + 30 / BLEEDER_MIN_OHM
    conduction_w = driver_peak_a**2 * HOT_RON_OHM * (3 + MAX_DUTY)
    # IN-low output release planning model. Actual diag-enabled leakage and
    # output capacitance must meet these explicit qualification constraints.
    output_node_max_cap_f = 10e-9
    off_net_source_leakage_a = 100e-6
    off_release_allowance_s = 90e-6
    off_fault_difference_max_v = 2.6
    off_equilibrium_v = off_net_source_leakage_a * BLEEDER_MAX_OHM
    clear_cases = []
    for supply_v in HIGH_SIDE_SUPPLY_CORNERS_V:
        target_v = supply_v - off_fault_difference_max_v
        discharge_s = BLEEDER_MAX_OHM * output_node_max_cap_f * math.log(
            (supply_v - off_equilibrium_v) / (target_v - off_equilibrium_v))
        clear_cases.append({"supply_v": supply_v,
                            "release_plus_discharge_us": (off_release_allowance_s + discharge_s) * 1e6})
    # A cleared ARM state persists after a DO fault clears while the timer runs.
    arm = True
    armed_fault_sequence = []
    for do_fault_n, fresh_arm, command in (
        (True, False, True), (False, False, True),
        (True, False, True), (True, True, False)):
        if not do_fault_n:
            arm = False
        elif fresh_arm:
            arm = True
        permitted = arm and do_fault_n and command
        armed_fault_sequence.append(permitted)
    result = {
        "scope": "Pre-capture arithmetic and analytical resistive edge model; schematic, firmware, PCB, temperature and fault qualification pending",
        "sources": {
            "switch": "https://www.ti.com/lit/ds/symlink/tps4h160-q1.pdf (Rev E, sections 6.5, 6.6, 8.2)",
            "pwm_method": "https://www.ti.com/lit/pdf/slvaf10 (sections 2-4)",
            "timer_pin": "https://www.st.com/resource/en/datasheet/stm32g474ve.pdf (Rev 6, tables 12-13)",
        },
        "qualification_target": {
            "channel": "DO3 / PE9 / LQFP100 pin40 / TIM1_CH1 AF2",
            "input_connector_v": [9, 30],
            "high_side_supply_planning_v": [8.4, 30],
            "whole_input_path_drop_max_at9v_v": .6,
            "ambient_c": [0, 50],
            "instantaneous_current_max_a": CURRENT_A,
            "loads": "Resistive first; specifically qualified resistor-limited LED assembly later; no motor/proportional-solenoid claim",
            "command_duty_window": [MIN_DUTY, MAX_DUTY],
            "endpoints": "Steady 0/100% use timer disabled, GPIO low/high behind hardware PERMISSION",
        },
        "timer": {
            "apb2_prescaler": 1, "tim1_kernel_hz": TIMER_HZ,
            "prescaler": PRESCALER, "auto_reload": AUTO_RELOAD,
            "tick_s": (PRESCALER + 1) / TIMER_HZ, "pwm_hz": PWM_HZ,
            "ccr1_min_max": [1000, 9000],
            "pwm_mode": "Mode1 active high; compare preload on period boundary",
        },
        "datasheet_conditions": {
            "supply_v": 13.5, "load_a": .5, "logic_v": 5,
            "current_limit_for_cs_timing_a": 2,
            "delay_max_us": 90, "slew_min_v_per_us": .1,
            "delay_match_us": [-50, 50],
            "cs_on_settling_max_us": 150, "sense_mux_settling_max_us": 50,
            "supply_operating_min_v": 4,
            "current_sense_full_linear_range_min_supply_v": 6.5,
            "note": "The actual 8.4-30 V post-protection supply, 3.3 V logic and ~0.7 A limit need bench confirmation; applying slew/delay across that range is a planning assumption. Connector fixtures remain 9-30 V and require ≤0.6 V whole-path drop at 9 V/full load.",
        },
        "timing": {
            "shortest_command_phase_us": shortest_command_us,
            "full_swing_plus_delay_estimate_us": worst_rise_us,
            "command_phase_remaining_us": shortest_command_us - worst_rise_us,
            "sample_window_after_rising_command_us": [600, 800],
            "mux_preselect_before_edge_us": 200,
            "cs_guard_before_sample_us": 600 - 150,
            "readback_five_tau_estimate_us": readback_five_tau_us,
            "note": "ADC acquisition and amplifier recovery need measured closure; the RC estimate alone is not full-chain settling.",
        },
        "model_sweep": {
            "cases": len(cases),
            "minimum_high_plateau_us": min(c["high_plateau_us"] for c in cases),
            "minimum_low_plateau_us": min(c["low_plateau_us"] for c in cases),
            "minimum_sample_start_after_full_rise_us": min(c["sample_start_after_full_rise_us"] for c in cases),
            "minimum_sample_end_before_falling_command_us": min(c["sample_end_before_falling_command_us"] for c in cases),
            "resistor_power_error_extremes_fraction": [
                min(c["resistor_power_error_from_ideal_fraction"] for c in cases),
                max(c["resistor_power_error_from_ideal_fraction"] for c in cases)],
            "note": "Independent delay/slew corners deliberately ignore their correlations. Diode drop, RON, capacitor inrush, current limiting, parasitics, LED behavior and IC bias are outside this waveform model. No precision duty-to-power claim.",
        },
        "loss_screen": {
            "supply_v": 30, "pwm_hz": PWM_HZ,
            "pwm_instantaneous_external_load_a": CURRENT_A,
            "pwm_peak_driver_current_including_bleeder_a": driver_peak_a,
            "full_rise_fall_us": [300, 300],
            "resistor_overlap_estimate_w": selected["resistor_overlap_loss_w"],
            "constant_current_overlap_estimate_w": selected["constant_current_overlap_estimate_w"],
            "three_continuous_and_one_90percent_conduction_estimate_w": conduction_w,
            "four_continuous_conduction_estimate_w": 4 * driver_peak_a**2 * HOT_RON_OHM,
            "four_blocking_diodes_125c_loss_model_w": 4 * (.56 * CURRENT_A + .045 * CURRENT_A**2),
            "note": "Overlap is a screening estimate, not a guaranteed maximum; operating current, COSS/other parasitics, PCB thermal resistance and measured temperature remain separate.",
        },
        "current_telemetry": {
            "reported_quantity": "Settled on-state driver current including bleeder; sample age, duty and validity",
            "average_current": "Duty x estimated external on-load current, after accounting for bleeder uncertainty, is only an estimate for the qualified resistor fixture; exclude transition/fault samples",
            "note": "No off-current, proportional-current-control or precision average-current guarantee; low-current CS error remains datasheet dependent.",
        },
        "output_bleeders": {
            "component": "4x YAGEO RC1206FR-0710KL, 10k, 1%, 0.25W at70C, 1206",
            "connection": "Each DOx_SW before blocking diode to MAIN_GND; no off-load pullup",
            "resistance_error_fraction_including_temperature": BLEEDER_ERROR,
            "resistance_min_max_ohm": [BLEEDER_MIN_OHM, BLEEDER_MAX_OHM],
            "nominal_current_each_at30v_a": 30 / BLEEDER_OHM,
            "maximum_current_each_at30v_a": 30 / BLEEDER_MIN_OHM,
            "maximum_power_each_at30v_w": 30**2 / BLEEDER_MIN_OHM,
            "nominal_four_full_dc_power_at30v_w": 4 * 30**2 / BLEEDER_OHM,
            "off_node_capacitance_max_f": output_node_max_cap_f,
            "off_net_source_leakage_assumption_a": off_net_source_leakage_a,
            "release_allowance_us": off_release_allowance_s * 1e6,
            "off_fault_difference_max_v": off_fault_difference_max_v,
            "clear_cases": clear_cases,
            "acceptance_clear_time_us": 150,
            "datasheet_off_fault_deglitch_min_us": 300,
            "source": "https://yageogroup.com/component-documentation/download/specsheet/RC1206FR-0710KL",
            "scope": "Capacitance, diag-enabled net source leakage and release allowance are design/qualification constraints; the datasheet does not guarantee them for this assembled node. Verify previously energized/unloaded channels before enabling PWM.",
        },
        "fault_inhibition": {
            "arm_clear_source": "Conditioned receiving-domain DO_FAULT_N participates in asynchronous ARM clear",
            "ic_thermal_latch": "THER-high latch resets when INx toggles; PWM edges must not be relied on to hold that IC latch",
            "sequence_permitted_command": armed_fault_sequence,
            "sequence": "Armed high command; fault assertion; fault clears with stale high command; fresh rearm with command cleared",
            "scope": "State/truth model only; captured logic, propagation and measured shutdown remain pending",
        },
    }
    assert PWM_HZ == 100
    assert min(HIGH_SIDE_SUPPLY_CORNERS_V) > result["datasheet_conditions"]["supply_operating_min_v"]
    assert min(HIGH_SIDE_SUPPLY_CORNERS_V) > result["datasheet_conditions"]["current_sense_full_linear_range_min_supply_v"]
    assert shortest_command_us >= 999.999
    assert result["timing"]["command_phase_remaining_us"] > 600
    assert result["model_sweep"]["minimum_high_plateau_us"] > 600
    assert result["model_sweep"]["minimum_low_plateau_us"] > 600
    assert result["model_sweep"]["minimum_sample_start_after_full_rise_us"] >= 200
    assert result["model_sweep"]["minimum_sample_end_before_falling_command_us"] >= 199.999
    assert .45 < selected["constant_current_overlap_estimate_w"] < .46
    assert .273 < conduction_w < .28
    assert all(c["release_plus_discharge_us"] < 150 for c in clear_cases)
    assert result["output_bleeders"]["maximum_power_each_at30v_w"] < .25 / 2
    assert armed_fault_sequence == [True, False, False, False]
    return result


if __name__ == "__main__":
    print(json.dumps(calculate(), indent=2))
