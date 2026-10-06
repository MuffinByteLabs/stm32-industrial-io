"""Independent verification calculations for the STM32 Industrial I/O Rev A pre-schematic package.
All datasheet numbers below were read from the manufacturer PDFs stored in the project folder
(references/datasheets/*) during this review. Nothing here writes to the project folder.
"""
import math, json

R = {}  # results

def rng(lo, hi, nd=4):
    return [round(lo, nd), round(hi, nd)]

# ---------------------------------------------------------------- 1. Input protection (TPS26632, SLVSE94G)
VUVLOR = (1.176, 1.224); VUVLOF = (1.09, 1.15); ILEAK = 150e-9
R1, R2, tolR = 604e3, 100e3, 0.001
def div_thresh(vref, r1, r2, tol, ileak, hi):
    if hi:
        return vref * (1 + r1 * (1 + tol) / (r2 * (1 - tol))) + ileak * r1 * (1 + tol)
    return vref * (1 + r1 * (1 - tol) / (r2 * (1 + tol))) - ileak * r1 * (1 + tol)
R['efuse_uvlo_rising_V'] = rng(div_thresh(VUVLOR[0], R1, R2, tolR, ILEAK, False), div_thresh(VUVLOR[1], R1, R2, tolR, ILEAK, True), 3)
R['efuse_uvlo_falling_V'] = rng(div_thresh(VUVLOF[0], R1, R2, tolR, ILEAK, False), div_thresh(VUVLOF[1], R1, R2, tolR, ILEAK, True), 3)
# ILIM: I_OL = 18/R(kOhm); datasheet accuracy rows: 4.02k -> +/-7 %, 9k -> +/-8 %
ilim_nom = 18 / 5.11
R['efuse_ilim_A'] = {'nominal': round(ilim_nom, 3), 'pm8pct': rng(ilim_nom * 0.92, ilim_nom * 1.08, 3)}
# dVdT slew rate
Idv = (1.775e-6, 2.225e-6); G = (23.5, 26.0); Cdv = 100e-9
sr_nom = 2e-6 * 25 / Cdv
sr_min = Idv[0] * G[0] / (Cdv * 1.10 * 1.15)
sr_max = Idv[1] * G[1] / (Cdv * 0.90 * 0.85)
R['efuse_dvdt_V_per_s'] = {'nominal': sr_nom, 'range_incl_cap_tol_temp': rng(sr_min, sr_max, 0)}
# Start-up energy in the eFuse FET (24 V and 30 V input)
def startup_energy(vin, cout, sr, p_load_in_W, v_start):
    # capacitor charging: E = C * Vin^2 / 2 (independent of slew rate)
    e_cap = cout * vin ** 2 / 2
    # converter load drawn from V_start up to Vin while the FET drops (Vin - Vout)
    # I = P/Vout ; dt = dV/sr ; E = (P/sr) * integral (Vin - V)/V dV
    e_load = (p_load_in_W / sr) * (vin * math.log(vin / v_start) - (vin - v_start)) if p_load_in_W else 0
    t_ramp = (vin - 0) / sr
    return e_cap, e_load, t_ramp
for vin in (24.0, 30.0):
    ec, el, tr = startup_energy(vin, 300e-6, 500.0, 7.5, 4.2)
    R[f'efuse_startup_{int(vin)}V'] = {'cap_charge_J': round(ec, 3), 'buck_loaded_during_ramp_J': round(el, 3),
                                       'ramp_s': round(tr, 4), 'avg_power_if_loaded_W': round((ec + el) / tr, 1),
                                       'avg_power_if_buck_enabled_by_PGOOD_W': round(ec / tr, 1)}

# Input path drop at 3 A (datasheet max values; hot factors are engineering estimates)
fuse_cold = 0.0125; fuse_hot = fuse_cold * 1.35
fet_25 = 0.0166; fet_hot = fet_25 * 1.55          # NexFET Rds(on) rises ~1.5x at Tj 100-125 C
efuse_ron_max = 0.053                              # TPS2663 RON max over -40..125 C
conn = 2 * 0.002; pcb = 0.010
r_path = fuse_hot + fet_hot + efuse_ron_max + conn + pcb
R['input_path_drop_3A'] = {'R_total_mohm': round(r_path * 1e3, 1), 'drop_V': round(3 * r_path, 3), 'limit_V': 0.6,
                           'efuse_loss_W': round(9 * efuse_ron_max, 3), 'fet_loss_W': round(9 * fet_hot, 3), 'fuse_loss_W': round(9 * fuse_hot, 3)}

# ---------------------------------------------------------------- 2. Main buck LMR38020F (SNVSC40E)
VREF_B = (0.985, 1.015)
rt, rb = 99.6e3, 24.9e3
vout_lo = VREF_B[0] * (1 + rt * 0.999 / (rb * 1.001))
vout_hi = VREF_B[1] * (1 + rt * 1.001 / (rb * 0.999))
R['buck5_vout_V'] = rng(vout_lo, vout_hi, 3)
f_nom = (30970 / 64.9) ** (1 / 1.027) * 1e3
R['buck5_fsw_nom_kHz'] = round(f_nom / 1e3, 1)
def buck_ripple(vin, vout, L, f):
    return (vin - vout) * vout / (vin * L * f)
rip = {}
for vin in (8.4, 12, 24, 30, 35):
    rip[vin] = {'ripple_App_typ': round(buck_ripple(vin, 5.0, 15e-6, f_nom), 3),
                'ripple_App_worst(12uH,320k)': round(buck_ripple(vin, 5.1, 12e-6, 320e3), 3),
                'ton_ns_at_500k': round(5.0 / vin / 500e3 * 1e9, 0)}
R['buck5_ripple'] = rip
R['buck5_min_ripple_check'] = {'Vin8.4_L18uH_f490k_App': round(buck_ripple(8.4, 4.9, 18e-6, 490e3), 3),
                               'rule_of_thumb_min_App(10% of 2A)': 0.2}
I_svc = 6.0 / 5.0
R['buck5_peak_at_1.2A_35V_A'] = round(I_svc + buck_ripple(35, 5.1, 12e-6, 320e3) / 2, 3)
R['buck5_limits_A'] = {'HS_min': 2.6, 'LS_valley_min': 1.8, 'Isat_inductor_typ': 6.4}
R['buck5_Lmin_subharmonic_uH'] = round(0.25 * 5 / 400e3 * 1e6, 2)

# ---------------------------------------------------------------- 3. 3.3 V digital buck + supervisor (TPS62160, TPS3808)
VFB = 0.8; rtop = 31.201e3; rbot = 10e3
vnom = VFB * (1 + rtop / rbot)
leak = 400e-9 * rtop
v3_min_psm = vnom * 0.965 - leak
v3_min_pwm = vnom * 0.97 - leak
v3_max = vnom * 1.04 + leak
R['dig3v3_V'] = {'nominal': round(vnom, 4), 'min_PSM': round(v3_min_psm, 3), 'min_PWM': round(v3_min_pwm, 3), 'max': round(v3_max, 3)}
for name, vit in (('TPS3808G33', 3.07), ('TPS3808G30', 2.79)):
    vit_max = vit * 1.015; rel_max = vit_max * 1.025
    R[f'reset_{name}'] = {'VIT_max': round(vit_max, 3), 'release_max(VIT+2.5%hys)': round(rel_max, 3),
                          'margin_release_vs_min_PSM_V': round(v3_min_psm - rel_max, 3),
                          'margin_trip_vs_min_PSM_V': round(v3_min_psm - vit_max, 3)}
# TPS70933 output: +/-1 %, line 10 mV, load 50 mV
ldo_min = 3.3 * 0.99 - 0.010 - 0.050
R['ldo3v3_min_V'] = round(ldo_min, 3)
R['reset_TPS3808G33_vs_LDO_margin_V'] = round(ldo_min - 3.07 * 1.015 * 1.025, 3)

# ---------------------------------------------------------------- 4. TPS3702CX50 (SET high: UV 4.80 V / OV 5.20 V, +/-0.9 % accuracy)
uv_max = 4.80 * 1.009; ov_min = 5.20 * 0.991
adc_avdd_min = vout_lo - 0.0115 * 1.0     # 11.5 mA max dynamic through the 1 ohm filter
adc_avdd_max = vout_hi
R['adc5_ok_window'] = {'UV_trip_max_V': round(uv_max, 3), 'OV_trip_min_V': round(ov_min, 3),
                       'AVDD_DC_min_V': round(adc_avdd_min, 3), 'AVDD_DC_max_V': round(adc_avdd_max, 3),
                       'DC_margin_low_V': round(adc_avdd_min - uv_max, 3), 'DC_margin_high_V': round(ov_min - adc_avdd_max, 3)}

# ---------------------------------------------------------------- 5. +15 V boost TPS61040 and 680 uF precharge through the passive path
ip_min, ip_max = 0.35, 0.45
fs_max = 4.9 * (15.5 - 4.9) / (ip_min * 12e-6 * 15.5)
iload_max = 0.6 * ip_min * 4.9 / (2 * 15.5)
R['boost15'] = {'fs_max_kHz': round(fs_max / 1e3, 1), 'Iout_max_mA_eta0.6': round(iload_max * 1e3, 1),
                'Iout_max_mA_eta0.75': round(0.75 * ip_min * 4.9 / (2 * 15.5) * 1e3, 1),
                'ton_max_us(18uH,450mA)': round(18e-6 * 0.45 / (4.9 - 0.45 * 1.12) * 1e6, 2)}
t_ss = 4e-3  # LMR38020 internal soft-start
i_pre = 680e-6 * 1.2 * 5.0 / t_ss
R['boost_bulk_precharge_during_5V_softstart_A'] = round(i_pre, 2)
R['boost_bulk_LC_Z0_ohm'] = round(math.sqrt(15e-6 / 680e-6), 4)
R['boost_bulk_energy_to_15V_mJ'] = round(0.5 * 680e-6 * (15 ** 2 - 4.6 ** 2) * 1e3, 1)

# ---------------------------------------------------------------- 6. Bottom-up 5V_FIELD load (datasheet maxima where available)
loads_3v3dig = {  # mA
    'STM32G474 @144MHz + peripherals (est.)': 50, 'SiT8008 (max)': 4.5, '24LC64 write (max)': 3,
    'LEDs 2x1.3mA': 2.6, 'pull-ups/logic/supervisors (est.)': 8, 'loop-status + misc (doc)': 0.5}
loads_3v3field = {'ISO1212 x2 (1.9 max)': 3.8, 'ISO1410 VCC1 (3.1 max)': 3.1, 'ISO1042 VCC1 (3.5 max)': 3.5,
                  'ADS8684A DVDD': 0.5, 'buffers/gates/pull-ups (est.)': 6}
i3d = sum(loads_3v3dig.values()) / 1e3
i3f = sum(loads_3v3field.values()) / 1e3
p_buck3 = 3.3 * i3d / 0.85
loads_5v = {  # W at 5V_FIELD
    'TPS62160 input (3V3_DIG)': p_buck3,
    'TPS709 field logic (I_in = I_out)': 5.1 * i3f,
    'TPS709 MCU analog (5 mA)': 5.1 * 0.005,
    'ADS8684A AVDD (11.5 mA max)': 5.1 * 0.0115,
    'OPA2320 (2x1.75 mA) + LM4040 feed 2.5 mA': 5.1 * 0.006,
    'Relay coils 2x (5.1V/51.6ohm at 0C)': 2 * 5.1 ** 2 / 51.6,
    'RS-485 port: UCC33421 180 mA out @ ~55 %': 5.0 * 0.180 / 0.55,
    'CAN port: ISO1042 77.5 mA dominant @ ~45 %': 5.0 * 0.0775 / 0.45,
    '+15 V boost (real load ~9 mA @ 60 %)': 15.5 * 0.009 / 0.6,
}
p5_total = sum(loads_5v.values())
R['service_5V_bottom_up_W'] = {k: round(v, 3) for k, v in loads_5v.items()}
R['service_5V_total_W'] = round(p5_total, 3)
R['service_5V_total_A'] = round(p5_total / 5.0, 3)
R['service_reservation_W'] = 6.0

# ---------------------------------------------------------------- 7. Input current
def iin(vfield, eta, p_service=6.0, loads_A=2.0, bleed_A=4 * 0.003, hs_A=0.020):
    return loads_A + bleed_A + hs_A + p_service / eta / vfield
R['input_current_A'] = {f'{v}V_eta{e}': round(iin(v, e), 3) for v in (8.4, 9.0, 12.0, 24.0, 30.0) for e in (0.80, 0.85)}

# ---------------------------------------------------------------- 8. High-side outputs (TPS4H160-Q1 SLVSCV8E)
icl_nom = 0.8 * 2500 / 2870
R['hs_current_limit_A'] = {'nominal': round(icl_nom, 3), 'pm15pct_pm1pctR': rng(icl_nom * 0.85 / 1.01, icl_nom * 1.15 / 0.99, 3)}
rsns_eff = 1 / (1 / 1210 + 1 / 124e3)
R['hs_CS_volts'] = {'at_0.5A': round(0.5 / 300 * rsns_eff, 3), 'at_limit_max': round(icl_nom * 1.15 / 0.99 / 300 * rsns_eff, 3),
                    'linear_range_max_V': 4.0, 'fault_VCS_H_V': [4.5, 6.5]}
p_cond_hot = 4 * 0.5 ** 2 * 0.28
p_iop = 0.008 * 30
R['hs_IC_dissipation_W_4x0.5A_hot'] = round(p_cond_hot + p_iop, 3)
R['hs_IC_Tj_rise_C_(RthJA 32.7 C/W, JEDEC)'] = round((p_cond_hot + p_iop) * 32.7, 1)
R['hs_short_circuit_W_30V'] = round(30 * icl_nom * 1.15 / 0.99, 1)
R['blocking_diode_loss_W_each(ST model)'] = 0.291
R['blocking_diodes_total_W'] = round(4 * 0.291, 3)
R['bleeders_total_W_30V'] = round(4 * 30 ** 2 / 9875, 3)
R['inductive_energy_mJ_100mH_0.5A'] = round(0.5 * 0.1 * 0.5 ** 2 * 1e3, 1)
R['DO_terminal_voltage_at_VFIELD8.4V_V'] = round(8.4 - 0.5 * 0.28 - 0.6, 2)

# ---------------------------------------------------------------- 9. Digital inputs (ISO1212 SLLSEY7G)
vih_max = 8.55 + 0.1 * (10.95 - 8.55); vil_min = 6.5 + 0.1 * (8.7 - 6.5)
R['DI_thresholds_RTHR100'] = {'VIH_max_interp_V': round(vih_max, 3), 'VIL_min_interp_V': round(vil_min, 3),
                              'ON_spec_V': 9.0, 'margin_V': round(9.0 - vih_max - 0.1 * 2.75e-3 * 100 * 0.01, 3),
                              'IEC61131-2_Type3': 'ON>=11V&>=2mA, OFF<=5V: met (ON current 2.05-2.75 mA)'}
R['DI_power_30V_mW'] = round(30 * 2.75, 1)

# ---------------------------------------------------------------- 10. Analog front end
Rin_min, Rin_typ = 0.85e6, 1.0e6
Rs_v = 1000 + 8.3 + 100
R['AI_V_loading'] = {'gain_error_pct_typ': round(Rs_v / (Rs_v + Rin_typ) * 100, 4),
                     'TVS_SMCJ11CA_IR_max_uA_at_11V': 5, 'error_from_5uA_x_1.1k_mV': round(5e-6 * 1100 * 1e3, 2),
                     'pole_Hz': round(1 / (2 * math.pi * Rs_v * 1e-6), 1)}
lsb_v = 10.24 / 65536; lsb_i = 5.12 / 65536 / 200
R['ADC_LSB'] = {'V_range_uV': round(lsb_v * 1e6, 3), 'I_range_nA': round(lsb_i * 1e9, 2)}
# Error budget over 0-50 C relative to 25 C calibration
dT = 25
v_fs = 10.0
ev = {'ADC gain drift 4ppm/C': v_fs * 4e-6 * dT, 'internal ref drift 10ppm/C': v_fs * 10e-6 * dT,
      'offset drift 3ppm/C of 10.24V FSR': 10.24 * 3e-6 * dT, 'INL 2LSB': 2 * lsb_v,
      'TVS leakage change (est.)': 5e-6 * 1100, 'calibration source (assume 0.01%+1mV)': 10 * 1e-4 + 1e-3}
R['AI_V_error_budget_mV'] = {k: round(v * 1e3, 3) for k, v in ev.items()}
R['AI_V_error_RSS_mV'] = round(math.sqrt(sum(v ** 2 for v in ev.values())) * 1e3, 2)
R['AI_V_error_linear_sum_mV'] = round(sum(ev.values()) * 1e3, 2)
i_fs = 0.020
ei = {'shunt TCR 25ppm/C': i_fs * 25e-6 * dT, 'ADC gain drift 4ppm/C': i_fs * 4e-6 * dT, 'ref drift 10ppm/C': i_fs * 10e-6 * dT,
      'offset drift (3ppm x 5.12V)/200ohm': 5.12 * 3e-6 * dT / 200, 'INL 2LSB': 2 * lsb_i,
      'shunt self-heating (~3C x 25ppm)': i_fs * 25e-6 * 3, 'calibration source (assume 0.01%+1uA)': i_fs * 1e-4 + 1e-6}
R['AI_I_error_budget_uA'] = {k: round(v * 1e6, 3) for k, v in ei.items()}
R['AI_I_error_RSS_uA'] = round(math.sqrt(sum(v ** 2 for v in ei.values())) * 1e6, 2)
R['AI_I_error_linear_sum_uA'] = round(sum(ei.values()) * 1e6, 2)
# loop compliance with a 24 V -10 % supply, 2 x 100 m of 0.5 mm2 cable, 2-wire transmitter needing 10.5 V
r_cable = 2 * 100 * 0.0365
for i in (0.020, 0.024):
    R[f'loop_headroom_{int(i*1e3)}mA_V'] = round(21.6 - 10.5 - i * (200 + 12.5) - i * r_cable, 2)
R['loop_burden_20mA_V'] = round(0.020 * (200 + 12.5), 3)
# TPS26611 OUT OVLO if +Vs were 5V_FIELD (simplification option)
R['tps2661_ovlo_if_Vs_5V'] = {'OVLO_min_V': round(4.917 + 0.05, 3), 'shunt_V_at_24mA_max': round(0.024 * 200 * 1.001, 3),
                             'margin_V': round(4.917 + 0.05 - 0.024 * 200 * 1.001, 3), 'ADC_range_V': 5.12}

# ---------------------------------------------------------------- 11. ADC serial budget
t_tr = 32 / 1.125e6
R['ADC_SPI'] = {'transaction_us': round(t_tr * 1e6, 2), 'scan4_us': round(4 * t_tr * 1e6, 1),
                'max_aggregate_kSPS': round(1 / t_tr / 1e3, 2), 'planned_kSPS': 4, 'bus_utilisation_pct': round(4e3 * t_tr * 100, 1)}

# ---------------------------------------------------------------- 12. Bus ports
R['RS485_idle_bias_V'] = {'nominal': round(5 * 60 / (249 + 249 + 60), 3),
                          'worst(4.75V,+1%bias,-1%term)': round(4.75 * (60 * 0.99) / (2 * 249 * 1.01 + 60 * 0.99), 3),
                          'TIA-485 failsafe threshold': 0.2}
R['RS485_TVS'] = {'SMBJ8.5CA_VC_max_V': 14.4, 'ISO1410_bus_absmax_V': 18, 'standoff_V': 8.5, 'RS485_common_mode_spec_V': [-7, 12]}
R['CAN_split_term_ohm'] = 2 * 60.4
R['CAN_TVS'] = {'PESD2CANFD24V_VC_V': 42, 'ISO1042_absmax_V': 70}
R['isolated_port_out_W'] = {'RS485_worst(160mA x 5.15V)': round(0.160 * 5.15, 3), 'CAN_worst(77.5mA x 5.15V)': round(0.0775 * 5.15, 3), 'UCC33421_rating_W': 1.5}

# ---------------------------------------------------------------- 13. MCU clock / timers / bus timing
f_in = 8e6 / 2; f_vco = f_in * 72
R['MCU_clock'] = {'PLL_in_MHz': f_in / 1e6, 'VCO_MHz': f_vco / 1e6, 'SYSCLK_MHz': f_vco / 2 / 1e6, 'PLLQ_MHz': f_vco / 6 / 1e6,
                  'USB_accuracy_needed_ppm': 2500, 'clock_ppm': 25,
                  'FDCAN_tq_per_bit_500k_at_48MHz': 48e6 / 500e3, 'FDCAN_tq_per_bit_2M_at_48MHz': 48e6 / 2e6,
                  'CiA601-3_recommended_clock_MHz': [20, 40, 80]}
R['TIM1_PWM'] = {'tick_us': 144e6 / 144 / 1e6, 'period_ms': (9999 + 1) / (144e6 / 144) * 1e3}
R['I2C_rise_ns'] = round(0.8473 * 4.7e3 * 200e-12 * 1e9, 0)
R['WDT_margin'] = {'WDI_period_ms': 50, 'tWD_min_ms': 170, 'ratio': round(170 / 50, 2)}
R['LED_current_mA'] = round((3.3 - 2.0) / 1000 * 1e3, 2)

# ---------------------------------------------------------------- 14. Relays (G5Q-1 DC5: 63 ohm +/-10 % at 23 C, 80 mA)
r_cold = 63 * 0.9 * (1 + 0.00393 * (0 - 23))
R['relay_coil_mA_each_0C_5.1V'] = round(5.1 / r_cold * 1e3, 1)
R['relay_two_coils_W'] = round(2 * 5.1 ** 2 / r_cold, 3)

# ---------------------------------------------------------------- 15. Board heat at 24 V full load (estimate)
heat = {
    'eFuse RON at 2.3 A (24 V full load)': (2.0 + 6.0 / 0.85 / 24) ** 2 * 0.045,
    'blocking FET + fuse (2.3 A)': (2.0 + 6.0 / 0.85 / 24) ** 2 * (fet_hot + fuse_hot),
    'TPS4H160 4x0.5 A + I_op': p_cond_hot + 0.008 * 24,
    'series blocking diodes 4x': 4 * 0.291,
    'output bleeders 4x @24V': 4 * 24 ** 2 / 10e3,
    'LMR38020 + inductor loss (6 W out, 88 %)': 6.0 / 0.88 - 6.0,
    'UCC33421 x2 losses (RS-485 worst + CAN)': (0.9 / 0.55 - 0.9) + (0.39 / 0.45 - 0.39),
    'relay coils (2x)': 2 * 5.0 ** 2 / 63,
    'TPS709 x2 + TPS62160 + boost losses (est.)': 0.19 + 0.05 + 0.10,
    'ISO1212 x2 field-side (2.75 mA x 24 V x 4)': 4 * 24 * 0.00275,
}
R['board_heat_24V_full_load_W'] = {k: round(v, 3) for k, v in heat.items()}
R['board_heat_total_W'] = round(sum(heat.values()), 2)

# ---------------------------------------------------------------- 16. IPC-2221 conductor width (k=0.048 ext, 0.024 int)
def ipc2221_width_mm(I, dT, oz, internal=False):
    k = 0.024 if internal else 0.048
    area_mil2 = (I / (k * dT ** 0.44)) ** (1 / 0.725)
    t_mil = 1.378 * oz
    return area_mil2 / t_mil * 0.0254
R['IPC2221_width_mm'] = {
    '3A_ext_1oz_dT10': round(ipc2221_width_mm(3, 10, 1), 2), '3A_int_0.5oz_dT10': round(ipc2221_width_mm(3, 10, 0.5, True), 2),
    '3A_int_1oz_dT10': round(ipc2221_width_mm(3, 10, 1, True), 2), '0.5A_ext_1oz_dT10': round(ipc2221_width_mm(0.5, 10, 1), 2),
    '2A_LOAD_RETURN_ext_1oz_dT10': round(ipc2221_width_mm(2, 10, 1), 2)}


# ---------------------------------------------------------------- 7. Checks of the fixes proposed in the report
# (a) Second TPS3702CX50 with SET = GND -> +/-9 % nominal window (TPS3702 datasheet SBVS251A section 6.3.3), +/-0.9 % accuracy
uv9 = 5.0 * 0.91; ov9 = 5.0 * 1.09
f5_min, f5_max = vout_lo, vout_hi          # 5V_FIELD DC range, no 1-ohm filter drop
R['fix_TPS3702_SET_low_on_5V_FIELD'] = {
    'UV_trip_V': rng(uv9 * 0.991, uv9 * 1.009, 3), 'OV_trip_V': rng(ov9 * 0.991, ov9 * 1.009, 3),
    'margin_low_V': round(f5_min - uv9 * 1.009, 3), 'margin_high_V': round(ov9 * 0.991 - f5_max, 3),
    'inside_UCC33421_4.5-5.5V': (uv9 * 0.991 >= 4.5) and (ov9 * 1.009 <= 5.5)}
# (b) TPS3808G30 on all three 3.3 V rails
R['fix_TPS3808G30'] = {'trip_min_V': round(2.79 * 0.985, 3), 'release_max_V': round(2.79 * 1.015 * 1.025, 3),
                       'margin_vs_3V3_DIG_min_V': round(v3_min_psm - 2.79 * 1.015 * 1.025, 3),
                       'margin_vs_TPS70933_min_V': round(ldo_min - 2.79 * 1.015 * 1.025, 3)}
# (c) Alternative: raise 3V3_DIG with a 32.4 k top resistor
vn2 = 0.8 * (1 + 32.4 / 10)
R['alt_3V3_DIG_32k4_top'] = {'nominal_V': round(vn2, 3), 'min_PSM_V': round(vn2 * 0.965 - 400e-9 * 32.4e3, 3),
                             'max_V': round(vn2 * 1.04 + 400e-9 * 32.4e3, 3)}
# (d) eFuse PGTH rescaled for buck-enable use: 475 k / 100 k (VPGTHR 1.176-1.224, VPGTHF 1.09-1.15)
k = 1 + 475 / 100
R['fix_PGTH_475k_100k'] = {'rising_V': rng(1.176 * k, 1.224 * k, 2), 'falling_V': rng(1.09 * k, 1.15 * k, 2)}
# (e) Present PGTH (604 k / 100 k) for comparison
k0 = 1 + 604 / 100
R['present_PGTH_604k_100k'] = {'rising_V': rng(1.176 * k0, 1.224 * k0, 2), 'falling_V': rng(1.09 * k0, 1.15 * k0, 2)}
# (f) R3 indicative divider: 22 k / 47 k after RCS 1.21 k
ratio = 47 / (22 + 47); r_eff = 1 / (1 / 1.21e3 + 1 / 69e3)
R['R3_CS_divider_22k_47k'] = {'ratio': round(ratio, 3), 'CS_gain_change_pct': round((r_eff / 1.21e3 - 1) * 100, 2),
                              'ADC_V_at_0.809A_limit': round(0.809 / 300 * r_eff * ratio, 3),
                              'ADC_V_at_min_fault_4.5V': round(4.5 * ratio, 3),
                              'clamp_current_mA_at_6.5V_fault': round((6.5 - 3.6) / 22e3 * 1e3, 3)}


if __name__ == '__main__':
    print(json.dumps(R, indent=1))
