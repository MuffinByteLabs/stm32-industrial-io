"""I reproduce capture-support bounds; this does not validate the built circuit."""
from itertools import product
import json


def divider_bounds(top, bottom, thresholds, bias):
    # Independent tolerance plus worst 25 C excursion at 25 ppm/C.
    rerr = 0.001 + 25e-6 * 25
    values = [(v * (1 + rt / rb) + ib * rt)
              for v, rt, rb, ib in product(thresholds,
                  (top * (1-rerr), top * (1+rerr)),
                  (bottom * (1-rerr), bottom * (1+rerr)), (-bias, bias))]
    return [min(values), max(values)]


def fixed_reset_screen(nominal_trip):
    # TPS3808 SBVS050N, pp. 3 and 6: full -40..125 C trip accuracy
    # +/-1.5%, fixed-version hysteresis 1% typical / 2.5% maximum.
    # There is no guaranteed minimum hysteresis. Applying the maximum to
    # the largest possible trip is conservative; 1% is not a worst-case bound.
    trip_min = nominal_trip * .985
    trip_max = nominal_trip * 1.015
    return {
        'nominal_falling_trip_v': nominal_trip,
        'falling_trip_v': [trip_min, trip_max],
        'rising_release_screen_v': [trip_min, trip_max * 1.025],
        'release_lower_bound_assumes_zero_hysteresis': True,
        'maximum_hysteresis_fraction': .025,
        'source': 'TPS3808 SBVS050N, pp. 3, 6; fixed thresholds, full -40..125 C accuracy. Reset delay and propagation are separate timing requirements.',
    }


def window_monitor_screen(uv_nominal, ov_nominal):
    # TPS3702 SBVS251A p. 5 and pp. 11, 14, 21: +/-0.9% threshold
    # accuracy; X hysteresis 0.3..0.8% of the NOMINAL trip threshold.
    # UV recovery rises above trip; OV recovery falls below trip.
    return {
        'uv_falling_trip_v': [uv_nominal * .991, uv_nominal * 1.009],
        'uv_rising_reentry_v': [uv_nominal * (.991 + .003),
                                uv_nominal * (1.009 + .008)],
        'ov_rising_trip_v': [ov_nominal * .991, ov_nominal * 1.009],
        'ov_falling_reentry_v': [ov_nominal * (.991 - .008),
                                ov_nominal * (1.009 - .003)],
        'source': 'TPS3702 SBVS251A, p. 5 electrical limits, pp. 11/14 trip/reentry grammar, p. 21 CX50 SET thresholds. Static limits do not establish response to a transient.',
    }


def calculate():
    rerr = .001 + 25e-6*25
    # TPS62160 SLVSAM2E p. 6: initial device accuracy PWM +/-3%, PSM
    # -3.5/+4% (COUT=22uF); footnote 5 EXCLUDES line/load regulation.
    # The 400nA FB leakage maximum is tested at VFB=1.2V, whereas this
    # circuit regulates FB at 0.8V. Treating it as +/-400nA here is an
    # explicit conservative screen, not a manufacturer bidirectional bound
    # or a guarantee at this application's FB voltage. Ripple is also absent.
    digital_top_ohm = 30900.0 + 301.0
    digital_bottom_ohm = 10000.0
    digital_nominal_v = .8 * (1 + digital_top_ohm / digital_bottom_ohm)
    digital_psm_screen_v = divider_bounds(digital_top_ohm,
        digital_bottom_ohm, (.8 * .965, .8 * 1.04), 400e-9)
    digital_pwm_screen_v = divider_bounds(digital_top_ohm,
        digital_bottom_ohm, (.8 * .97, .8 * 1.03), 400e-9)
    old_g33 = fixed_reset_screen(3.07)
    selected_g30 = fixed_reset_screen(2.79)
    # TPS709 SBVS186H p. 5, section 6.5: additive accuracy/line/load
    # screen, keeping the project's conservative existing 3.207V floor.
    ldo_min_v = 3.3 * .99 - .010 - .050
    ldo_max_v = 3.3 * 1.01 + .010 + .050
    digital_g30_release_margin_v = digital_psm_screen_v[0] - selected_g30['rising_release_screen_v'][1]
    ldo_g30_release_margin_v = ldo_min_v - selected_g30['rising_release_screen_v'][1]

    adc5 = window_monitor_screen(4.80, 5.20)
    wider_field5 = window_monitor_screen(4.55, 5.45)
    # LMR38020 SNVSC40E p. 6: FPWM reference 0.985..1.015V.
    # This DC screen adds divider initial tolerance and 0..50 C resistor
    # drift. Unspecified FB leakage, ripple, dynamic steps and layout effects
    # are still excluded; it is not the measured 4.90..5.10V rail target.
    field5_dc_screen_v = divider_bounds(99600.0, 24900.0,
                                      (.985, 1.015), 0)
    # ADS8684A SBAS680 p. 10: 11.5mA max dynamic AVDD at AVDD=5V,
    # fS maximum/internal reference. Include the actual 10k bleeder and
    # TPS3702 1.5uA SENSE bound rather than only the IC's dynamic current.
    # Include the selected 1-ohm series resistor's +1% initial tolerance;
    # its temperature drift is excluded from this initial DC margin screen.
    # This DC current test condition does not bound every startup waveform.
    adc_bleeder_upper_supply_screen_v = max(field5_dc_screen_v[1], 5.10)
    adc_avdd_current_screen_a = .0115 + adc_bleeder_upper_supply_screen_v / (
        10000.0 * (1-rerr)) + 1.5e-6
    adc_filter_resistance_screen_ohm = 1.0 * 1.01
    adc_avdd_dc_screen_v = [field5_dc_screen_v[0] -
        adc_avdd_current_screen_a * adc_filter_resistance_screen_ohm,
        field5_dc_screen_v[1]]
    adc_target_dc_screen_v = [4.90 -
        adc_avdd_current_screen_a * adc_filter_resistance_screen_ohm, 5.10]
    # A contemplated, NOT adopted SET-low field monitor would sense before
    # each input bead. At its latest permitted UV assertion, the post-bead
    # converter input can already be outside the 4.5V recommended minimum.
    # 50% efficiency is an engineering scenario, not a guaranteed minimum.
    wider_uv_min_v = wider_field5['uv_falling_trip_v'][0]
    port_output_current_a = .180
    port_output_upper_v = 5.15
    assumed_port_efficiency = .50
    bead_room_temperature_dcr_max_ohm = .045
    port_input_current_scenario_a = port_output_current_a * port_output_upper_v / (
        assumed_port_efficiency * wider_uv_min_v)
    bead_drop_scenario_v = port_input_current_scenario_a * bead_room_temperature_dcr_max_ohm
    # TPS2663 SLVSE94G pp. 8/19/32: PGOOD requires enhanced internal FET
    # AND PGTH above its rising threshold, supports downstream converter EN,
    # and may be pulled to OUT. The present 3V3_FIELD_LOGIC pullup cannot be
    # reused for buck EN: that rail is produced downstream of the buck.
    # LMR38020 SNVSC40E pp. 6/11: EN rising max1.4V, falling min0.95V,
    # EN<=VIN+0.3V; EN leakage is only 5nA TYP at VEN=3.3V, no MAX.
    # Consequently the +/-1uA EN allowance below is a qualification
    # assumption, not a datasheet guarantee at the whole VFIELD/EN range.
    pgth_new_rise_v = divider_bounds(475000, 100000,
                                    (1.176, 1.224), 150e-9)
    pgth_new_fall_v = divider_bounds(475000, 100000,
                                    (1.09, 1.15), 150e-9)
    pg_pullup_ohm = 100000.0
    en_pulldown_ohm = 100000.0
    pg_en_resistor_tolerance = .01
    pg_output_leak_max_a = 150e-9
    en_signed_leakage_allowance_a = 1e-6
    pg_en_total_signed_leakage_allowance_a = (
        pg_output_leak_max_a + en_signed_leakage_allowance_a)
    pullup_max = pg_pullup_ohm * (1+pg_en_resistor_tolerance)
    pulldown_min = en_pulldown_ohm * (1-pg_en_resistor_tolerance)
    def en_high_min(vfield):
        return (vfield / pullup_max - pg_en_total_signed_leakage_allowance_a) / (
            1 / pullup_max + 1 / pulldown_min)
    pullup_min = pg_pullup_ohm * (1-pg_en_resistor_tolerance)
    pulldown_max = en_pulldown_ohm * (1+pg_en_resistor_tolerance)
    pg_output_sink_max_ohm = 130.0
    pg_en_low_max_v = (35.0 / pullup_min + pg_en_total_signed_leakage_allowance_a) / (
        1 / pullup_min + 1 / pulldown_max + 1 / pg_output_sink_max_ohm)
    # PA15/JTDI has an enabled reset pullup. The external 1k pulldown must
    # overcome its 25k minimum plus a separately reviewed total-net allowance.
    pa15_pullup_min_ohm = 25000.0
    pa15_pulldown_max_ohm = 1000.0 * 1.01
    pa15_source_allowance_a = 10e-6
    pa15_reset_node_max_v = (3.6 / pa15_pullup_min_ohm + pa15_source_allowance_a) / (
        1 / pa15_pullup_min_ohm + 1 / pa15_pulldown_max_ohm)
    result={
        'scope':'Arithmetic and documented assumptions; pin/net/layout/firmware/bench checks pending',
        'resistor_error_fraction':rerr,
        'field_uv_rising_release_v':divider_bounds(190000,10000,(.396,.404),25e-9),
        'field_uv_falling_assert_v':divider_bounds(190000,10000,(.387,.400),25e-9),
        'minimum_full_load_vfield_v':8.4,
        'field_ov_rising_assert_v':divider_bounds(770000,10000,(.396,.404),15e-9),
        'field_ov_falling_release_v':divider_bounds(770000,10000,(.387,.400),15e-9),
        'analog15_uv_rising_release_v':divider_bounds(320000,10000,(.396,.404),25e-9),
        'analog15_uv_falling_assert_v':divider_bounds(320000,10000,(.387,.400),25e-9),
        'analog15_ov_rising_assert_v':divider_bounds(400000,10000,(.396,.404),15e-9),
        'analog15_ov_falling_release_v':divider_bounds(400000,10000,(.387,.400),15e-9),
        'eeprom_rise_time_200pf_s':.8473*4700*200e-12,
        'hse_pll':{'input_hz':8000000,'m':2,'n':72,'r':2,'q':6,
                   'core_hz':144000000,'usb_fdcan_hz':48000000},
        'watchdog_timeout_ms':[170,230],
        'watchdog_service_interval_ms':50,
        'digital3v3_screen': {
            'divider_top_ohm': digital_top_ohm,
            'divider_bottom_ohm': digital_bottom_ohm,
            'nominal_v': digital_nominal_v,
            'power_save_initial_accuracy_screen_v': digital_psm_screen_v,
            'power_save_initial_accuracy_without_fb_leakage_v': divider_bounds(
                digital_top_ohm, digital_bottom_ohm,
                (.8 * .965, .8 * 1.04), 0),
            'pwm_initial_accuracy_screen_v': digital_pwm_screen_v,
            'signed_fb_leakage_allowance_a': [-400e-9, 400e-9],
            'source': 'TPS62160 SLVSAM2E p. 6 section 7.5/footnotes 5-6; 0.1% resistors plus 25ppm/C over +/-25C. FB leakage is MAX at VFB=1.2V; this signed allowance at regulated 0.8V is conservative screening.',
            'limitations': 'Initial accuracy excludes line/load regulation; capacitor retention, ripple, startup, transient excursions and physical loading remain qualification gates. This arithmetic does not guarantee the complete 3.0..3.6V USB operating envelope.',
        },
        'reset_compatibility_screen': {
            'superseded_g33': old_g33,
            'selected_g30_all_three_rails': selected_g30,
            'tps709_additive_dc_screen_v': [ldo_min_v, ldo_max_v],
            'superseded_g33_release_margin_digital_psm_v': digital_psm_screen_v[0] - old_g33['rising_release_screen_v'][1],
            'superseded_g33_release_margin_ldo_v': ldo_min_v - old_g33['rising_release_screen_v'][1],
            'selected_g30_release_margin_digital_psm_v': digital_g30_release_margin_v,
            'selected_g30_release_margin_ldo_v': ldo_g30_release_margin_v,
            'ldo_source': 'TPS709 SBVS186H p. 5: +/-1% accuracy, 10mV max line, 50mV max load at specified input/load conditions. Screen requires dropout headroom; ripple/transients excluded.',
            'usb_policy_boundary': 'STM32G474 DS12288 Table 92 p. 179 requires VDD=3.0..3.6V for full USB characteristics. G30 minimum trip 2.74815V is below 3.0V. Brownout is outside normal USB qualification: detach on existing health/clock loss, discard interrupted service writes, and reattach only after stable qualified rails; software is not a guaranteed 3.0V undervoltage detector. Prove collapse/recovery behavior physically, including independent digital-rail collapse.',
        },
        'adc5_window_screen': {
            'selected_set_high': adc5,
            'field5_divider_dc_screen_v': field5_dc_screen_v,
            'adc_bleeder_upper_supply_screen_v': adc_bleeder_upper_supply_screen_v,
            'adc_avdd_dynamic_bleeder_sense_current_screen_a': adc_avdd_current_screen_a,
            'adc_filter_resistance_screen_ohm': adc_filter_resistance_screen_ohm,
            'adc_avdd_dc_screen_v': adc_avdd_dc_screen_v,
            'uv_assert_margin_v': adc_avdd_dc_screen_v[0] - adc5['uv_falling_trip_v'][1],
            'uv_reentry_margin_v': adc_avdd_dc_screen_v[0] - adc5['uv_rising_reentry_v'][1],
            'ov_assert_margin_v': adc5['ov_rising_trip_v'][0] - adc_avdd_dc_screen_v[1],
            'ov_reentry_margin_v': adc5['ov_falling_reentry_v'][0] - adc_avdd_dc_screen_v[1],
            'nominal_field_target_v': [4.90, 5.10],
            'adc_avdd_from_nominal_field_target_dc_screen_v': adc_target_dc_screen_v,
            'target_uv_reentry_margin_v': adc_target_dc_screen_v[0] - adc5['uv_rising_reentry_v'][1],
            'target_ov_reentry_margin_v': adc5['ov_falling_reentry_v'][0] - adc_target_dc_screen_v[1],
            'limitations': 'Strict ADC5_OK remains in analog validity and global output permission. Reentry margins include maximum hysteresis and are much smaller than trip-only margins; they do not prove nuisance-free startup or load steps. ADC current and monitor specifications have stated test conditions. The selected 1-ohm initial +/-1% tolerance is included; its temperature drift and supply-filter transients are excluded.',
        },
        'not_adopted_wider_field_monitor_scenario': {
            'status': 'Not selected: comparison only; no extra monitor or gating change is authorized by this arithmetic',
            'set_low_monitor': wider_field5,
            'converter_recommended_input_v': [4.5, 5.5],
            'upstream_uv_static_margin_to_converter_min_v': wider_uv_min_v - 4.5,
            'upstream_ov_static_margin_to_converter_max_v': 5.5 - wider_field5['ov_rising_trip_v'][1],
            'assumed_efficiency_fraction': assumed_port_efficiency,
            'port_output_current_a': port_output_current_a,
            'port_output_voltage_v': port_output_upper_v,
            'bead_room_temperature_dcr_max_ohm': bead_room_temperature_dcr_max_ohm,
            'input_current_scenario_a': port_input_current_scenario_a,
            'input_bead_drop_scenario_v': bead_drop_scenario_v,
            'post_bead_input_at_uv_trip_scenario_v': wider_uv_min_v - bead_drop_scenario_v,
            'source': 'TPS3702 SBVS251A p. 21 SET-low CX50; UCC33421-Q1 recommended VINP 4.5..5.5V; BLM21PG221SN1D manufacturer 45mohm max room-temperature DCR; project 180mA bus-side allowance.',
            'limitations': 'Threshold accuracy, post-bead voltage drop and dynamic response leave no established complete converter-input protection envelope. Broad field-power gating would not cure global disarm caused by strict ADC5_OK if that safety condition remains. Exact converter efficiency/current, hot bead DCR and transient/startup behavior require evidence.',
        },
        'efuse_pgood_buck_enable_screen': {
            'status': 'Selected sequencing direction with conditional EN-network screen; capture and complete startup/collapse qualification remain open',
            'pgood_release_condition': 'Internal pass-FET gate enhanced AND PGTH above rising threshold, then PGOOD rising deglitch; PGOOD falls when PGTH falls below its falling threshold',
            'superseded_pgth_604k_100k_rising_v': divider_bounds(604000, 100000, (1.176, 1.224), 150e-9),
            'superseded_pgth_604k_100k_falling_v': divider_bounds(604000, 100000, (1.09, 1.15), 150e-9),
            'selected_pgth_475k_100k_rising_v': pgth_new_rise_v,
            'selected_pgth_475k_100k_falling_v': pgth_new_fall_v,
            'pgood_pullup_to_vfield_ohm': pg_pullup_ohm,
            'en_pulldown_to_main_ground_ohm': en_pulldown_ohm,
            'pullup_pulldown_initial_tolerance_fraction': pg_en_resistor_tolerance,
            'pgood_guaranteed_signed_output_leakage_a': [-pg_output_leak_max_a, pg_output_leak_max_a],
            'en_unverified_signed_leakage_allowance_a': [-en_signed_leakage_allowance_a, en_signed_leakage_allowance_a],
            'en_high_min_at_8p4v_field_v': en_high_min(8.4),
            'en_high_min_at_minimum_pgth_rising_v': en_high_min(pgth_new_rise_v[0]),
            'en_required_start_max_v': 1.4,
            'en_low_max_at_35v_field_v': pg_en_low_max_v,
            'en_guaranteed_off_ceiling_v': .95,
            'pgood_sink_current_screen_max_a': 35.0 / pullup_min + pg_en_total_signed_leakage_allowance_a,
            'pgood_output_sink_resistance_max_ohm': pg_output_sink_max_ohm,
            'pgood_rising_deglitch_s': [.00107, .00160],
            'source': 'TPS2663 SLVSE94G pp. 8-9 output/PGTH/timing limits, p. 19 section 8.3.2 gate-enhanced condition, p. 32 section 9.2.2.5.1 direct downstream EN and 10..100k pullup recommendation. LMR38020 SNVSC40E p. 6 EN limits and p. 11 section 8.3.3 tracking/never-floating requirements.',
            'limitations': 'Static calculation assumes EN leakage <=1uA in either direction and initial +/-1% resistors; EN leakage over actual voltage/temperature/power states and resistor drift still need evidence. Pullup is to VFIELD=LMR VIN, no added EN capacitor; this prevents DC excess VIN in the passive network but does not bound rapid collapse/parasitic charge/retained-output backfeed. Verify EN<=VIN+0.3V throughout collapse and the disabled state at unpowered eFuse conditions. PGTH changes eFuse retained-output fast-recovery selection too. This sequencing does not validate whole-tree inrush, SOA, thermal behavior, converter soft starts or 680uF boost precharge.',
        },
        'pa15_acquisition_default': {
            'mcu_supply_upper_v': 3.6,
            'reset_internal_pullup_min_ohm': pa15_pullup_min_ohm,
            'external_pulldown_ohm': 1000.0,
            'external_pulldown_tolerance_fraction': .01,
            'total_net_positive_source_allowance_a': pa15_source_allowance_a,
            'reset_node_max_v': pa15_reset_node_max_v,
            'lvc_guaranteed_low_ceiling_v': .8,
            'driven_high_pulldown_current_max_a': 3.6 / (1000.0 * .99),
            'note': 'DS12288 reset JTDI pullup and 25k minimum require the approved 1k pulldown. The 10uA complete-net positive sourcing allowance remains to be verified; this arithmetic is not a captured-netlist or physical reset test.',
        },
    }
    # These checks concern useful design margins, not implementation equivalence.
    assert result['field_uv_rising_release_v'][1] < result['minimum_full_load_vfield_v']
    assert result['field_uv_falling_assert_v'][1] < result['minimum_full_load_vfield_v']
    assert result['field_ov_falling_release_v'][0] > 30
    assert result['eeprom_rise_time_200pf_s'] < 1e-6
    # The retained divider has useful DC release margin with G30. This checks
    # static compatibility, never a complete rail/USB/transient guarantee.
    assert digital_g30_release_margin_v > 0
    assert ldo_g30_release_margin_v > 0
    assert en_high_min(pgth_new_rise_v[0]) > 1.4
    assert pg_en_low_max_v < .95
    assert pa15_reset_node_max_v < result['pa15_acquisition_default']['lvc_guaranteed_low_ceiling_v']
    assert result['pa15_acquisition_default']['driven_high_pulldown_current_max_a'] + pa15_source_allowance_a < .008
    return result


if __name__ == '__main__':
    print(json.dumps(calculate(),indent=2))
