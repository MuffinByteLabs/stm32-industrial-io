#!/usr/bin/env python3
"""
ESP32-S3 Protected Field I/O Controller (Board 2) -- design arithmetic.

Every number quoted in docs/ESP32S3_FieldIO_Final_Design_Document.md comes from
here. Run it (python3 board2_calcs.py) and compare; if a component value changes,
change it here first and re-run. No dependencies beyond the standard library.
"""
import math

def hdr(t):
    print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)

# ---------------------------------------------------------------- 1. INPUT
hdr("1. POWER ENTRY -- what the DC bus actually does")
VAC_NOM = 24.0
VAC_HI_UNLOADED = 28.0     # a class-2 HVAC transformer with nothing on it, high line
VF_BRIDGE_LIGHT = 0.70      # per diode, light load (start-up)
VF_BRIDGE_FULL  = 0.95      # per diode, ~0.7 A
R_PPTC_HOT      = 0.30      # ohm, Littelfuse 60R110 / Bourns MF-RX110 class after warm-up (R1max)
R_PPTC_COLD     = 0.10      # ohm
pk_nom = VAC_NOM * math.sqrt(2)
pk_hi  = VAC_HI_UNLOADED * math.sqrt(2)
print(f"24 VAC nominal peak            = {pk_nom:5.1f} V")
print(f"28 VAC unloaded/high-line peak = {pk_hi:5.1f} V  -> bus after bridge (light load) = {pk_hi-2*VF_BRIDGE_LIGHT:5.1f} V")
VBUS_MAX = pk_hi - 2*VF_BRIDGE_LIGHT
print(f"36 VDC in, light load          -> bus = {36-2*VF_BRIDGE_LIGHT:5.1f} V")
print(f"=> DC BUS MAXIMUM to design against: {VBUS_MAX:4.1f} V (call it 39 V)")

# 5 V rail budget (worst case, everything at once)
I_WIFI_TX = 0.360   # ESP32-S3 TX peak through the LDO (linear: same current on 5 V side)
I_RELAYS  = 2 * (5.0/ (70*0.9))  # two coils, 70 ohm -10 % tolerance
I_BASE    = 2 * 0.0038
I_LEDS    = 0.015
I_PUMP    = 0.400
I_MISC    = 0.010   # opto pull-ups, dividers, LDO ground current
I5_WORST  = I_WIFI_TX + I_RELAYS + I_BASE + I_LEDS + I_PUMP + I_MISC
P5_WORST  = 5.0 * I5_WORST
print(f"\n5 V rail worst case: TX {I_WIFI_TX*1e3:.0f} + relays {I_RELAYS*1e3:.0f} + base {I_BASE*1e3:.0f} + LEDs {I_LEDS*1e3:.0f} + pump {I_PUMP*1e3:.0f} + misc {I_MISC*1e3:.0f} = {I5_WORST*1e3:.0f} mA  ({P5_WORST:.2f} W)")
print(f"  2 A buck margin: {(2.0-I5_WORST)/I5_WORST*100:.0f} %   (1.5 A part would leave {(1.5-I5_WORST)/I5_WORST*100:.0f} %, 1 A part {(1.0-I5_WORST)/I5_WORST*100:.0f} %)")

# input current vs input voltage
ETA = 0.88
def input_current_dc(vterm, p_out=P5_WORST, eta=ETA):
    # solve I with bus = vterm - I*Rpptc - 2*Vf
    I = 0.2
    for _ in range(50):
        vbus = vterm - I*R_PPTC_HOT - 2*VF_BRIDGE_FULL
        I = p_out/eta/vbus
    return I, vbus
print("\nDC input, full 5 V load, hot PPTC (0.30 ohm), 0.95 V/diode:")
for vt in (9, 10, 12, 24, 36):
    I, vb = input_current_dc(vt)
    print(f"  {vt:2d} V terminal -> I_in = {I*1e3:4.0f} mA, bus = {vb:5.2f} V, bridge loss = {2*VF_BRIDGE_FULL*I:.2f} W")
print("  => a 0.5 A-hold PPTC (plan v7.3) trips at 9-12 V DC full load. Use 1.1 A hold, 60 V (Littelfuse 60R110 / Bourns MF-RX110).")

# 24 VAC: capacitor-input rectifier
I_AVG_AC = P5_WORST/ETA/ (pk_nom - 2*VF_BRIDGE_FULL - 2.5)   # bus mid-ripple
print(f"\n24 VAC, full load: bus avg ~{pk_nom-2*VF_BRIDGE_FULL-2.5:.0f} V -> I_dc = {I_AVG_AC*1e3:.0f} mA; RMS through PPTC/bridge ~ {2.2*I_AVG_AC*1e3:.0f} mA (capacitor-input factor ~2.2)")

# bulk cap ripple
for C in (330e-6, 470e-6):
    for I in (0.2, I_AVG_AC):
        dv = I * (1/120) / C
        print(f"  C = {C*1e6:.0f} uF, I = {I*1e3:.0f} mA: dV(120 Hz, full-period worst case) = {dv:.2f} V")
print("  plan v7.3 '330 uF sags ~5 V at 0.2 A' -> confirmed (conservative; real recharge window makes it ~4 V)")
print(f"  bulk-cap ripple current to spec: >= {2.2*I_AVG_AC*1e3:.0f} mA rms at 120 Hz -> pick a 105 C low-ESR part rated >= 0.6 A (120 Hz derating ~0.6x of the 100 kHz figure)")

# TVS
hdr("2. TVS vs buck absolute maximum")
V_RWM, V_BR_MIN, V_C_MAX, I_PP = 43.0, 47.8, 69.4, 8.6   # SMBJ43A
r_dyn = (V_C_MAX - V_BR_MIN)/I_PP
print(f"SMBJ43A: standoff {V_RWM} V (bus max {VBUS_MAX:.1f} V -> {V_RWM-VBUS_MAX:.1f} V margin), VBR min {V_BR_MIN} V, VC {V_C_MAX} V @ {I_PP} A, Rdyn ~ {r_dyn:.1f} ohm")
for abs_max, name in ((66, "LMR36015 (60 V class)"), (65, "LMR16020 (60 V class)"), (85, "LMR38020 (80 V class)")):
    i_at = (abs_max - V_BR_MIN)/r_dyn
    ok = "PASS at full 600 W surge" if V_C_MAX <= abs_max else f"clamp exceeds abs-max above ~{i_at:.1f} A of TVS current"
    print(f"  {name:26s} abs max {abs_max} V: {ok}")
# what the bulk cap does with a surge
for C in (330e-6,):
    for I, t in ((8.6, 50e-6), (30, 20e-6)):
        print(f"  {C*1e6:.0f} uF bulk cap absorbing {I} A for {t*1e6:.0f} us rises only {I*t/C:.1f} V -> the TVS only ever sees ns-scale edges")

# UVLO
hdr("3. Buck EN/UVLO divider (LMR38020: VEN-H 1.25 V typ (1.10-1.40), VEN-L 1.10 V typ (0.95-1.22))")
RENB = 20e3
for VON in (7.0, 7.5):
    RENT = RENB*(VON/1.25 - 1)
    # nearest E24
    e24 = [1.0,1.1,1.2,1.3,1.5,1.6,1.8,2.0,2.2,2.4,2.7,3.0,3.3,3.6,3.9,4.3,4.7,5.1,5.6,6.2,6.8,7.5,8.2,9.1]
    cand = sorted([m*10**e for e in range(3,6) for m in e24], key=lambda x: abs(x-RENT))[0]
    ratio = 1 + cand/RENB
    print(f"VON target {VON} V: RENT = {RENT/1e3:.1f} k -> use {cand/1e3:.0f} k with RENB 20 k (ratio {ratio:.2f})")
    print(f"   turn-on  typ {1.25*ratio:.2f} V  (min {1.10*ratio:.2f}, max {1.40*ratio:.2f})")
    print(f"   turn-off typ {1.10*ratio:.2f} V  (min {0.95*ratio:.2f}, max {1.22*ratio:.2f})")
    print(f"   divider current at 39 V bus: {39/(cand+RENB)*1e3:.2f} mA, {39**2/(cand+RENB)*1e3:.0f} mW -> 0603 fine; RENT sees {39*cand/(cand+RENB):.0f} V -> 0805 for the 150 V rating habit")
print("=> plan v7.3's 7.5 V UVLO kills 9 V DC operation (bus at 9 V in is 6.6-7.6 V). Use VON 7.0 V typ -> guaranteed start >= 10 V DC (worst-case 7.8 V + 1.5 V light-load drops = 9.3 V), typical start ~8.5 V.")

# buck design
hdr("4. Buck design values (LMR38020SDDAR, 400 kHz, 5.0 V)")
VREF = 1.0; RFBT = 100e3; RFBB = 24.9e3
VOUT = VREF*(1+RFBT/RFBB)
print(f"VOUT = 1.0 x (1 + 100k/24.9k) = {VOUT:.3f} V (spec 5.00 +-3 % = 4.85-5.15 V; ref +-1.5 %, 1 % resistors -> +-2.7 % worst)")
fsw = 400e3
RT = 30970 * (fsw/1e3)**(-1.027)
print(f"RT for 400 kHz = 30970 x 400^-1.027 = {RT:.1f} k -> datasheet Table 8-1: 64.9 k (E96)")
for L in (10e-6, 15e-6, 22e-6):
    for vin in (12.0, VBUS_MAX):
        dIL = (vin-VOUT)*(VOUT/vin)/(fsw*L)
        print(f"  L = {L*1e6:2.0f} uH, Vin {vin:4.1f} V: dIL = {dIL*1e3:4.0f} mA p-p -> peak at 0.95 A load {0.95+dIL/2:.2f} A, at 2 A {2+dIL/2:.2f} A")
print("  Isat rule (datasheet): >= high-side current limit 3.8 A max -> 15 uH shielded, Isat >= 3.8 A, DCR <= 60 mohm (10x10 mm class)")
# efficiency / dissipation
for vin, eta in ((12, 0.90), (24, 0.89), (36, 0.87)):
    ploss = P5_WORST*(1/eta-1)
    print(f"  Vin {vin} V, eta ~{eta:.2f}: total loss {ploss:.2f} W; ~70 % in the IC = {0.7*ploss:.2f} W -> dT = {0.7*ploss*50:.0f} C at 50 C/W (2-layer pour)")
print("  plan v7.3 '~0.6 W at 36 V' -> confirmed")

# LDO
hdr("5. AP2112K on the OR'd logic rail")
for v5, label in ((5.0, "hard 5.0 V rail (plan v7.3 topology)"), (4.6, "behind SS14 OR diode (this document)")):
    print(f"  {label}: TX peak (5-3.3)... P = ({v5}-3.3) x 0.355 = {(v5-3.3)*0.355:.2f} W;  sustained 150 mA: {(v5-3.3)*0.15:.2f} W -> dT ~ {(v5-3.3)*0.15*150:.0f} C at 150 C/W (SOT-23-5 on a pour)")
print("  AP2112K dropout ~0.25 V @ 600 mA -> needs >= 3.6 V in; 4.6 V rail leaves 1.0 V")

# Schottky OR
hdr("6. Diode-OR on the logic 5 V rail")
print("  Buck 5.02 V -> SS14 (Vf ~0.40 V @ 0.4 A) -> 5V_SYS ~4.6 V;  USB 4.75-5.25 V -> SS14 -> 4.35-4.85 V")
print("  Buck can never back-feed USB, USB can never feed relays/VLOAD (they hang on 5V_BUCK before the diode).")
print(f"  OR diode dissipation at 0.4 A: {0.4*0.40:.2f} W (SMA, fine)")

# ---------------------------------------------------------------- OPTO
hdr("7. Opto inputs (PC817 rank C: CTR 200-400 % @ IF = 5 mA; use CTR_min 50 % x 0.7 low-IF derating in the maths)")
R_SERIES = 4800.0
VF_LED_OPTO = 1.15
VF_LED_IND  = 1.9   # red indicator in series, field side
R_PU = 10e3; V33 = 3.3
I_PU = V33/R_PU
CTR_MIN = 0.50*0.7
for vin in (12, 24, 30, 36, 40):
    i_f = (vin - VF_LED_OPTO - VF_LED_IND)/R_SERIES
    p_r = i_f**2*R_SERIES
    i_c = i_f*CTR_MIN
    print(f"  {vin:2d} V DC: IF = {i_f*1e3:4.2f} mA, P(R total) = {p_r*1e3:5.0f} mW ({p_r/2*1e3:3.0f} mW each of two), IC avail (CTR 35 %) = {i_c*1e3:4.2f} mA vs {I_PU*1e3:.2f} mA needed -> margin {i_c/I_PU:.1f}x")
print("  => 0805 (125 mW each) is over its rating at 36 V DC; 1206 (250 mW each) keeps 2x margin. Two 2.4 k 1206 in series.")
i_f_min = (I_PU/CTR_MIN)
v_thresh = VF_LED_OPTO + VF_LED_IND + i_f_min*R_SERIES
print(f"  Input threshold: needs IF >= {i_f_min*1e3:.2f} mA -> V_in >= {v_thresh:.1f} V to register (below that reads OFF = good noise immunity)")
# AC gap
Vpk = 24*math.sqrt(2)
ang = math.degrees(math.asin(v_thresh/Vpk))
on_frac = (180-2*ang)/360
T = 1/60
print(f"  24 VAC: conducts from {ang:.1f} deg to {180-ang:.1f} deg -> ON {on_frac*T*1e3:.1f} ms, OFF (gap) {(1-on_frac)*T*1e3:.1f} ms per 16.7 ms cycle")
gap = (1-on_frac)*T
for C in (1e-6, 2.2e-6, 4.7e-6, 10e-6):
    tau = R_PU*C
    v_end = V33*(1-math.exp(-gap/tau))
    tau_d = R_PU*C*0.8  # X7R derated at 3.3 V bias
    v_end_d = V33*(1-math.exp(-gap/tau_d))
    print(f"  C = {C*1e6:4.1f} uF: tau = {tau*1e3:3.0f} ms -> node rises to {v_end:.2f} V by the end of the gap ({v_end_d:.2f} V with 20 % cap derating); release time ~{3*tau*1e3:.0f} ms")
print("  ESP32-S3 VIL = 0.25 x 3.3 = 0.825 V, VIH = 0.75 x 3.3 = 2.475 V")
print("  => plan v7.3's 1 uF (tau 10 ms) reaches ~2 V during the gap: NOT a steady LOW. 4.7 uF (tau 47 ms) holds < 0.7 V. Chosen: 10 k + 4.7 uF X7R 16 V 0805.")
# discharge time on first cycle
print(f"  First-detect delay: opto must pull 4.7 uF from 3.3 V to 0.8 V with ~{(0.8e-3-I_PU)*1e3:.2f} mA net at 12 V -> {4.7e-6*2.5/((0.8e-3-I_PU))*1e3:.0f} ms (~1 cycle) - fine")

# ---------------------------------------------------------------- RELAY
hdr("8. Relay driver (SRD-05VDC-SL-C: 70 ohm +-10 %, S8050 hFE min 85 @ 50 mA)")
for v5 in (5.02, 4.85):
    for r in (63, 70, 77):
        i = (v5-0.15)/r
        print(f"  rail {v5:.2f} V, coil {r} ohm: I_coil = {i*1e3:.0f} mA, coil V = {v5-0.15:.2f} V ({(v5-0.15)/5*100:.0f} % of nominal; must-operate 75 % = 3.75 V)")
IB = (3.3-0.7-0.0)/680 - 0.7/10e3
print(f"  Base drive: (3.3-0.7)/680 - 0.7/10k(pulldown) = {IB*1e3:.2f} mA; forced beta at 79 mA = {0.079/IB:.0f}; hFE_min/forced = {85/(0.079/IB):.1f}x -> saturated")
print(f"  Reset-state check: if the pin had a 45 k internal pull-up, base node = 3.3 x (0.68k+10k)/(0.68k+10k+45k) = {3.3*(10.68)/(55.68):.2f} V -> relay stays off; pins chosen (IO9-IO12) have NO default pull anyway")
print(f"  GPIO source: {IB*1e3:.1f} mA base + 1.3 mA LED = {IB*1e3+1.3:.1f} mA (ESP32-S3 default drive 20 mA)")
print("  1N4148W flyback: coil energy 0.5 x L x I^2 with L ~ 50 mH: %.1f mJ per turn-off, decay ~ L/R = %.1f ms" % (0.5*0.05*0.079**2*1e3, 0.05/70*1e3))

# ---------------------------------------------------------------- MOSFET
hdr("9. MOSFET outputs (AO3400A: 30 V, Rds(on) 33 mohm @ 2.5 V, Vgs(th) 0.65-1.45 V)")
for i in (0.4, 1.0):
    print(f"  {i} A load: I^2R = {i**2*0.033*1e3:.0f} mW")
print(f"  Gate pulldown 10 k vs hypothetical 45 k internal pull-up: gate = 3.3 x 10/55 = {3.3*10/55:.2f} V (< 0.65 V Vgs(th) min); with plan's 100 k it would sit at {3.3*100/145:.2f} V = ON. Use 10 k.")
print(f"  100 ohm gate resistor, Ciss ~ 900 pF: tau = {100*900e-12*1e9:.0f} ns")

# ---------------------------------------------------------------- VIN sense
hdr("10. VIN_SENSE divider")
RT_, RB_ = 100e3, 6.8e3
for v in (9, 24, 39, 45):
    print(f"  bus {v:2d} V -> {v*RB_/(RT_+RB_):.2f} V at the ADC (0-2.9 V usable, ATTEN 3)")
print(f"  divider current at 39 V: {39/(RT_+RB_)*1e6:.0f} uA, {39**2/(RT_+RB_)*1e3:.0f} mW; 100 k sees {39*RT_/(RT_+RB_):.0f} V -> 0805 (150 V) ")

# ---------------------------------------------------------------- traces
hdr("11. Trace widths (IPC-2221 external, 1 oz = 1.37 mil)")
def ipc_current(w_mm, dT=10, oz=1.0):
    A = (w_mm/0.0254)*(1.37*oz)
    return 0.048*dT**0.44*A**0.725
for w in (0.3, 0.5, 0.8, 1.0, 1.5, 2.0):
    print(f"  {w:3.1f} mm: {ipc_current(w):.2f} A @ 10 C rise, {ipc_current(w,20):.2f} A @ 20 C rise")
print("  => relay contact paths (2 A rating) >= 1.5 mm; 5V_BUCK / VLOAD (1 A) >= 0.8 mm; bus input >= 0.8 mm")

hdr("12. Creepage / clearance sanity (IPC-2221 B2 uncoated external, <= 100 V: 0.6 mm; B4 coated: 0.13 mm)")
print("  Moat 2.5 mm >= 4x the uncoated requirement for 39 V DC / 40 V peak. Fine; it is discipline + optics, as the plan says.")
