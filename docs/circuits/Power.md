# Power circuits

I use this sheet specification to capture the complete power tree. I have selected the networks and packages below; I have not yet captured the schematic, simulated a complete regulator model, or measured a board. My [component groups](../components/power.json) identify exact candidate order codes and the evidence behind them. They are a schematic component plan, not a released assembly BOM.

## Supply contract and partition

I qualify the prototype with a 9–30 V DC bench source limited to at most 4 A. My continuous input target is 3 A, including four 0.5 A load channels and service conversion. I use separate, initially discharged test setups for a measured 36.0 V ±0.1 V positive connection, 0.5 A source limit, 60 s at 25 °C, and a −30 V reverse connection, 0.1 A source limit, 60 s. Neither test establishes a surge-immunity rating. I keep output permission removed throughout these fault tests.

I fit one **Phoenix Contact 1759017, MSTB 2,5/2-G-5,08** right-angle board header and allocate one **1757019, MSTB 2,5/2-ST-5,08** off-board mating plug. Pin 1 is **VIN+ / VIN_RAW** and pin 2 is **VIN− / MAIN_GND**, viewed and numbered against the exact manufacturer drawing. Power owns these quantities; the shared field catalog entries stay at zero. The two-position power pair differs from the three-position relay and four-position load connectors, but this alone does not prove that every wrong plug is excluded. I verify coding, plug insertion, polarity, wire size/torque and enclosure clearance with the [harness plan](../../mechanical/README.md). [Exact header](https://www.phoenixcontact.com/en-us/products/pcb-header-mstb-25-2-g-508-1759017), [matching plug](https://www.phoenixcontact.com/en-us/products/pcb-plug-mstb-25-2-st-508-1757019)

| Net | Source and use |
| --- | --- |
| VIN_RAW | Positive connector terminal before fuse |
| VIN_RAW_FUSED | Fuse output; raw TVS, blocking-FET source and eFuse IN_SYS |
| VIN_EFUSE | Blocking-FET drain; eFuse IN pins |
| VFIELD | Controlled eFuse output; high-side outputs and main buck input |
| 5V_FIELD | Field-only 5 V: relay coils, isolated converters, field logic and analog conversion |
| 3V3_DIG | Service digital buck output |
| 3V3_MCU_ANA | Service analog LDO output |
| 3V3_FIELD_LOGIC | Field-only LDO output: DI receiver logic, bus-transceiver logic, external ADC digital supply and field buffers |
| 15V_ANA | Analog-input protection and fault-threshold regulator supply |
| MAIN_GND | Common main supply, USB, analog and load return reference |

I derive MCU, field logic, analog protection and port power from the external supply. USB VBUS is sensed only by the data-interface sheet; no board regulator or load is powered from it. I keep receiving-powered buffers and explicit output defaults because derived rails can still start and collapse at different times.

## Input protection and controlled startup

I connect VIN_RAW through a Littelfuse **0451005.MRL**, 5 A Nano² 451 fuse, to VIN_RAW_FUSED. I place **SMCJ33CA** across VIN_RAW_FUSED and MAIN_GND with a short connector-side return. I place one **2.2 µF/100 V Würth 885382209002** and one **100 nF/100 V GRM188R72A104KA35D** at VIN_RAW_FUSED, and the same pair at VIN_EFUSE. I use **CSD19537Q3** as the blocking FET, with source pins 1–3 at VIN_RAW_FUSED, gate pin 4 at BLOCK_GATE, and the drain pad/pins 5–8 at VIN_EFUSE. The installed KiCad symbol represents the electrically common drain structure as pin 5.

I connect the **BSS138P,215** fast-discharge FET with gate pin 1 at BLOCK_FAST_GATE, source pin 2 at VIN_RAW_FUSED, and drain pin 3 at BLOCK_GATE. This source floats with the raw input; it is not grounded. Its 50 pF maximum input capacitance meets the eFuse's small-discharge-FET requirement. I follow the [TPS2663 protection topology](https://www.ti.com/lit/ds/symlink/tps2663.pdf) and the [blocking-FET pinout](https://www.ti.com/lit/ds/symlink/csd19537q3.pdf).

| TPS26632RGER pin | Connection |
| --- | --- |
| 1, 2 IN | VIN_EFUSE |
| 3 B_GATE / 4 DRV | BLOCK_GATE / BLOCK_FAST_GATE |
| 5 IN_SYS | VIN_RAW_FUSED |
| 6 UVLO | 604 kΩ from VIN_RAW_FUSED; 100 kΩ to MAIN_GND |
| 7 PLIM | MAIN_GND; I disable additional power limiting |
| 8 GND / exposed pad 25 | MAIN_GND; both electrically connected |
| 9 dVdT | 100 nF to MAIN_GND |
| 10 ILIM | 5.11 kΩ to MAIN_GND |
| 11 MODE | Explicit no-connect; latch-off overload mode |
| 12 SHDN | EFUSE_SHDN test point; normally open, with the internal pullup; manual momentary connection to MAIN_GND resets a latched fault |
| 13 IMON | 10 kΩ and 100 nF to MAIN_GND; INPUT_CURRENT_MON test point only |
| 14 FLT | INPUT_FAULT_N; 100 kΩ pullup to 3V3_DIG; MCU PD10 |
| 15 PGTH | 475 kΩ from VFIELD; 100 kΩ to MAIN_GND |
| 16 PGOOD | VFIELD_PGOOD / EN_FIELD_BUCK; 100 kΩ pullup to VFIELD and 100 kΩ pulldown to MAIN_GND; main-buck EN and voltage-rated test point only |
| 17, 18 OUT | VFIELD |
| 19–24 NC | Explicit no-connect |

I use 0.1%, 25 ppm/°C thin-film resistors for these networks. The UVLO divider gives an 8.448 V nominal rising threshold for raw-input startup; FIELD_OK separately supervises the post-protection voltage under load. Using the 1.176–1.224 V reference limits, ±150 nA pin leakage and resistor tolerance gives an approximately 8.17–8.73 V rising interval before resistor temperature drift. This provides startup margin at a 9 V connector after fuse drop; UVLO is not the 9 V operating-validity decision.

I use PGOOD to hold the main buck disabled while the eFuse starts. TPS2663 requires both its internal FET gate enhanced and PGTH above its rising threshold; this is the manufacturer's downstream-converter enable use. The 475 kΩ/100 kΩ PGTH divider gives a 6.672741–7.128292 V rising and 6.179566–6.701648 V falling screen including resistor tolerance/drift and ±150 nA leakage. FIELD_OK remains the independent operating-health decision. The pullup comes from VFIELD, avoiding a startup cycle through the downstream 3.3 V rail, and tracks the buck's VIN. This PGOOD node can exceed 3.3 V and never connects to an MCU GPIO.

The 100 kΩ/100 kΩ EN network has no extra capacitor. With a conservative ±1% resistor envelope, guaranteed PGOOD leakage/sink resistance and an explicit **unverified ±1 µA EN leakage allowance**, [support arithmetic](../calcs/support_checks.py) gives EN high ≥3.245512 V at earliest PGTH release and low ≤0.045990 V at 35 V. These exceed the buck's required 1.4 V high / below-0.95 V off limits on paper. The datasheet gives typical EN leakage without a maximum, so I must verify complete-net leakage, hot/cold behavior and power-off states. I also capture rapid input collapse and retained-output behavior to enforce **EN≤VIN+0.3 V**. PGOOD sequencing reduces ramp loading; it does not approve whole-tree startup, FET SOA, capacitor-only energy or the passive boost bulk-charging path. [TPS2663 §§8.3.2/9.2.2.5.1](https://www.ti.com/lit/ds/symlink/tps2663.pdf), [LMR38020 §8.3.3](https://www.ti.com/lit/ds/symlink/lmr38020.pdf)

My 5.11 kΩ current-limit resistor gives approximately 3.52 A nominal. The datasheet specifies limit accuracy at selected test currents; I do not interpolate those points into a guaranteed 3.52 A tolerance. A ±10% IC spread with this 0.1% resistor would give approximately 3.17–3.88 A as an engineering screening envelope. I measure the assembled limit, including temperature, before assigning a rating.

I put **EEUFR1H221**, 220 µF/50 V ±20%, from VFIELD to MAIN_GND, positive terminal at VFIELD. I add a **22 kΩ/0.125 W 0805** bleeder and local 100 nF bypass. The main-buck input bank below brings the specified directly connected VFIELD capacitance to about 279 µF maximum before ceramic temperature drift; I impose a 300 µF total bound including drift and any later load-output additions. The 100 nF dVdT network produces about 500 V/s nominal, with an approximate 379–643 V/s spread from the specified charge-current/gain limits and ±10% capacitor tolerance. Applying the X7R ±15% temperature allowance expands this to approximately 330–756 V/s; I still check its low-voltage bias/aging retention. At 300 µF and 756 V/s, purely capacitive startup current is approximately 227 mA. Charging 300 µF to 30 V stores 135 mJ; converter startup load adds to the eFuse's dissipation.

I do not add a gate-to-ground resistor to the floating blocking-FET driver. I keep the controller's diagnostic pullups at 3.3 V. INPUT_CURRENT_MON is not connected directly to an MCU ADC: its field-powered analog output would need a receiving-domain isolation/clamp circuit.

I retain the [SMCJ33CA](https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_smcj_datasheet.pdf?assetguid=37388813-0d6d-4329-969b-1aa8b7614ac1) 33 V standoff, 36.7 V minimum breakdown at 25 °C and 53.3 V catalog pulse clamp as separate quantities. The defined 36.1 V maximum DC fault remains below that room-temperature breakdown minimum. I do not extend this to cold TVS conditions. The fuse's 5 A hold rating means it will not reliably open against a 4 A limited source; source limiting and the eFuse provide the primary bounded-fault behavior. I review the [451 fuse](https://www.littelfuse.com/assetdocs/fuse-451-and-453-datasheet?assetguid=533cd5cc-956c-4243-867f-6ab5a62f6ba1) interruption curve and TVS pulse energy for any future surge waveform.

I keep retained-output stress separate: the TPS2663 IN_SYS-to-OUT −85 V allowance is a 10 ms stress rating. A −53.3 V raw clamp with 35 V retained output exceeds it before layout overshoot. I therefore leave negative-surge qualification open until the actual pulse, temperature and retained voltage are coordinated. I discharge VFIELD before the standalone reverse-connection test.

## Main 5 V field buck

I use **LMR38020FDDAR**, the forced-PWM version without spread spectrum or a separate SS pin, following its [internally compensated application network](https://www.ti.com/lit/ds/symlink/lmr38020.pdf).

| Pin | Connection |
| --- | --- |
| 1 GND and exposed pad | MAIN_GND |
| 2 EN | EN_FIELD_BUCK / VFIELD_PGOOD; eFuse-qualified 100 kΩ/100 kΩ network above |
| 3 VIN | VFIELD |
| 4 RT/SYNC | 64.9 kΩ to MAIN_GND; approximately 400 kHz nominal; no external clock |
| 5 FB | 97.6 kΩ +2.00 kΩ in series from 5V_FIELD and 24.9 kΩ to MAIN_GND; Kelvin output sense |
| 6 PG | FIELD_BUCK_PG test point only, 100 kΩ pullup to 3V3_FIELD_LOGIC |
| 7 BOOT | 100 nF to SW_FIELD |
| 8 SW | SW_FIELD; inductor input |

I connect **XAL7050-153MEC**, 15 µH ±20%, between SW_FIELD and 5V_FIELD. I place **six 885382209002, 2.2 µF/100 V X7R**, plus 100 nF, at VIN-to-GND. My input-bank acceptance condition is at least 4.7 µF effective at 35 V, including initial tolerance, temperature, aging and DC bias. I place **four GRM32ER71E226KE15L, 22 µF/25 V X7R**, at the output; the output-bank acceptance condition is at least 40 µF effective at 5.1 V with ESR in the manufacturer's ceramic-capacitor application range. I have selected the parts and count but have not yet archived their DC-bias curves.

The 99.6 kΩ total top resistance sets 5.000 V nominal. Reference and initial resistor limits give approximately 4.917–5.083 V before ripple, feedback leakage and resistor temperature drift. My normal operating-envelope target is 4.90–5.10 V; my transient acceptance condition remains within the external ADC limits and the retained 5 V load operating limits. I measure the complete 5 V envelope rather than equating the nominal setting with compliance.

At 35 V input, 5.1 V output, 12 µH and an assumed 320 kHz lower frequency, inductor ripple is approximately 1.135 A peak-to-peak. A 1.2 A service load then reaches about 1.77 A peak, below the buck's 2.6 A minimum high-side current-limit test point. My 320–500 kHz screening range is an engineering allowance, not a new manufacturer frequency guarantee at the selected RT. The [inductor](https://www.coilcraft.com/getmedia/13a991b3-4273-4be3-81ba-f3cf372b4691/xal7050.pdf) has 41 mΩ maximum room-temperature DCR and a 6.4 A typical 30%-drop saturation-current point; I retain its temperature and core-loss qualification.

## Controller digital buck and two 3.3 V LDOs

I use the **TPS62160DGKR**, leaded VSSOP-8 (DGK0008A), with the [vendor-recommended 2.2 µH network](https://www.ti.com/lit/ds/symlink/tps62160.pdf). It has the same eight functional pins as the former DSG part and **no exposed pad**. I select **XFL3012-222MEC**, a 10 µF/25 V input capacitor plus 100 nF, and one 22 µF/25 V output capacitor. I require at least 4.7 µF effective input capacitance and 10 µF effective output capacitance after capacitor derating.

| TPS62160 pin | Connection |
| --- | --- |
| 1 PGND / 4 AGND | MAIN_GND, joined locally; DGK has no exposed pad 9 |
| 2 VIN / 3 EN | 5V_FIELD |
| 5 FB | 30.9 kΩ +301 Ω in series from 3V3_DIG; 10 kΩ to MAIN_GND |
| 6 VOS | Kelvin connection to 3V3_DIG at the output capacitor |
| 7 SW | SW_DIG; 2.2 µH to 3V3_DIG |
| 8 PG | DIGITAL_BUCK_PG test point; 100 kΩ to 3V3_DIG |

My 0.1% divider gives 3.296 V nominal. I use two E96 top resistors and reduce the original 312 kΩ/100 kΩ impedance tenfold: the 400 nA maximum feedback-leakage test bound would add about 125 mV with the original divider, but only 12.5 mV here. The +4% light-load reference bound, initial resistor ratio and conservative leakage screening give approximately 3.446 V maximum before resistor drift, line/load regulation and ripple. The divider consumes approximately 80 µA at nominal output. I keep supervision separate from converter PG and retain the named current budget. I verify the selected [inductor's](https://www.coilcraft.com/getmedia/f76a3c9b-4fff-4397-8028-ef8e043eb200/xfl3012.pdf) current and loss against the actual service profile.

DGK gives accessible leads for hand assembly but has less thermal spreading than DSG. TI's test-board RθJA is 184.3 °C/W for DGK versus 61.8 °C/W for DSG. An intentionally conservative screening example assigns the whole 0.75 W essential-logic reservation to this output and assumes 80% efficiency: 0.1875 W loss, about 34.6 °C calculated rise and 84.6 °C junction at 50 °C ambient if all conversion loss were in the IC. Efficiency and actual board thermal resistance are not guaranteed by that estimate. I compare the exact DGK drawing with the candidate footprint and qualify regulator/inductor temperature, ripple and startup with the intended enclosure.

I use **two TPS70933DBVR**, each with one 2.2 µF/50 V input capacitor and one 10 µF/25 V output capacitor. On each regulator, pin 1 IN joins its input supply, pin 2 GND joins MAIN_GND, pin 3 EN is left floating as the manufacturer recommends for always-enabled operation, pin 4 NC is explicitly unconnected, and pin 5 OUT is the named output. I do not tie EN to VIN. One input is 5V_FIELD and its output is 3V3_MCU_ANA; the other input is 5V_FIELD and its output is 3V3_FIELD_LOGIC. My output-bank design requirement is at least 2.2 µF effective and no more than 47 µF total including receiving-IC bypasses, with ESR no more than 0.2 Ω. This exceeds the 1.5 µF effective minimum for a 3.3 V output in the [TPS709 stability specification](https://www.ti.com/lit/ds/symlink/tps709.pdf).

I select this regulator for ordinary input-collapse behavior: its reverse-current protection operates independently of EN while OUT is above 1.8 V, and its OUT absolute maximum is 7 V independently of IN. This avoids the retained-output differential restriction of the earlier LDO. Reverse current can still flow below 1.8 V; I do not claim zero backfeed at every residual voltage. Neither output has an external power source, and hardware rail qualification removes output permission before this residual-discharge region.

I set a 100 mA field-logic capacity target and a 50 mA maximum for the MCU analog-supply branch. The IC is rated for 150 mA. Conservatively adding the ±1% DC accuracy, 10 mV maximum line regulation and 50 mV maximum load regulation gives a 3.207–3.393 V DC screening envelope under the datasheet test conditions; I still check ripple and actual loading. At 4.90 V field input, 1.507 V headroom remains above the 1.4 V maximum dropout specified at 150 mA. The MCU analog branch uses the same 4.90 V minimum input and has additional margin over the 650 mV maximum dropout specified at 50 mA. External-supply brownout removes permission and requires fresh rearming after reset.

At 5.10 V and 3.207 V output, 100 mA pass-device dissipation is approximately 189 mW. The 212.1 °C/W DBV thermal metric would imply a 40 °C rise on its test fixture; it does not replace a board thermal measurement. I accept the TPS709's higher noise for MCU diagnostic ADC measurements and check those measurements with switching rails active. My precision field conversions use the external ADC and its own reference. I do not transfer a typical noise figure characterized at another output voltage into a guaranteed 3.3 V noise specification.

## +15 V analog boost and fall sequencing

I use the active **TPS61040DBVR** SOT-23 boost for this low-current rail. Its discontinuous, peak-current PFM control is inherently stable under the [manufacturer's topology](https://www.ti.com/lit/ds/symlink/tps61040.pdf); it has no external COMP network. I use **XAL4040-153MEC**, 15 µH ±20%, and **PMEG4010CEJ,115**, 40 V/1 A SOD-323F Schottky rectifier.

| TPS61040 pin | Connection |
| --- | --- |
| 1 SW | SW_ANA; inductor from 5V_FIELD and diode anode |
| 2 GND | MAIN_GND |
| 3 FB | 110 kΩ +2.00 kΩ in series from 15V_ANA and 10 kΩ to MAIN_GND; 680 pF C0G across the full 112 kΩ series pair |
| 4 EN | FIELD5V_VALID, with 100 kΩ to MAIN_GND |
| 5 VIN | 5V_FIELD; 10 µF/25 V plus 100 nF locally |

I connect the rectifier cathode to 15V_ANA. I use **two 2.2 µF/50 V X7R** plus **EEUFR1E681, 680 µF/25 V ±20%**, at the output and a 100 kΩ bleeder. The two local 1 µF/50 V TMUX VDD bypasses add 2 µF nominal, or 2.53 µF with the conservative positive tolerance/temperature screen, to the parent startup account. I include them and the threshold-regulator input capacitors in the complete +15 V load/startup review; I take no extra hold-up credit from unverified ceramic capacitance. They do not increase the child VFP output maxima. I reserve a 25 mA load-capacity target, including analog loads, divider/bleeder current and fault-status current. The electrolytic is deliberate hold-up for the two child fault-threshold LDOs described in [Analog circuits](Analog.md). I wait for positive-rail qualification and analog settling before permitting outputs or acquisition.

The divider gives 15.043 V nominal. Reference, resistor and ±1 µA feedback-current screening gives approximately 14.60–15.50 V before ripple and resistor temperature drift. At 4.9 V input, 15.5 V output, a 350 mA minimum peak-current limit and 12 µH minimum inductance, the ideal switching-boundary frequency is approximately 798 kHz, below the 1 MHz guidance. Maximum current-ramp on-time is about 1.83 µs using 18 µH, 450 mA and a conservative 0.45 V switch drop, below the 4 µs minimum maximum-on-time setting. Assuming 60% conversion efficiency, the simple peak-current capacity estimate is 33.2 mA, leaving margin above the 25 mA target; efficiency is an assumption requiring a prototype measurement. My 680 pF feedforward choice follows the datasheet formula near a 5 mA light-load operating point, not a loop-model measurement.

I explicitly allow slow startup with the 680 µF output capacitor. At light load the converter delivers discrete energy pulses; I verify startup, ripple, load steps, enable sequencing and high/low component corners before calling this rail qualified. Disabling this boost does not isolate its output: the inductor/diode path still feeds the output from 5 V. The main buck must therefore also charge this bulk through the passive path before boost enable; my 300 µF directly connected VFIELD bound does not cover the complete converter-tree startup demand. I review the combined buck soft start, this initial charging path, boost startup and eFuse dissipation with the actual sequencing before capture approval, then measure them before qualification.

I enable the two child VFP regulators from ANALOG_VALID and pull their enables down, so +15 V undervoltage disables them above dropout. I use the monitor's 12.72283 V tolerance-bounded minimum falling threshold rather than its nominal 13.2 V decision. My sequence requires child disable within 1 ms, parent discharge load no more than 25 mA after disable, child output capacitance including the 100 nF protector bypass no more than 12.7765 µF each, and 4.7 kΩ bleeders bounded to ±0.2% including initial tolerance and temperature drift. This gives a 60.170 ms maximum child RC. I impose a 5 µA maximum total residual sourcing into each disabled child output, including the connected protector and external-input state. This is a qualification assumption: the TPS7A16's 5 µA shutdown input-supply current alone does not bound all current into the complete VFP net during unequal-rail decay.

I require the selected 680 µF parent bulk to retain **at least 500 µF throughout 0–50 °C**, not merely its 544 µF room-temperature tolerance minimum. Under this bound, the parent takes at least 254.457 ms to fall from the minimum UV decision to zero at 25 mA. Allowing 1 ms disable delay, 11.2433 V maximum initial VFP11 and 6.13227 V maximum initial VFP6, their retained voltages at parent zero are approximately 0.190 V and 0.114 V respectively, below the 0.3 V absolute-maximum differential. The exponentially falling child minus the linearly falling parent is convex, so the initial and final endpoint bounds cover the interval. I do not assume free child discharge while a child remains enabled and regulating. The bulk-capacitance and disable-delay requirements still need manufacturer temperature evidence and physical qualification; an internal hard short on 15V_ANA requires separate protection and is outside my external-terminal fault qualification.

I do not derive a guaranteed 1 ms system bound from the TPS3700's typical propagation-delay entries: those are characterized at specific supply/overdrive conditions and do not guarantee this slow falling-rail corner. I include monitor response, logic propagation, enable fall and LDO turn-off in the bound. Panasonic's initial capacitance tolerance also does not prove a 500 µF floor over temperature or service life; its endurance allowance permits additional capacitance change. I preserve the requirements and keep both evidence gates open rather than declaring the calculated fall sequence qualified.

## Budget, capture checks and qualification gates

I reserve 0.75 W for MCU/service logic, 0.50 W for field logic/ADC, 0.65 W for auxiliary conversion, 1.10 W for both relay coils and 2.75 W for both isolated converters. The sum is 5.75 W against a 6 W delivered 5V_FIELD ceiling, leaving 0.25 W. The auxiliary reservation covers 25 mA ×15 V /60% =625 mW at nominal voltage, with 25 mW additional reserve. At the screened 15.5 V upper rail, the same current and assumed efficiency need approximately 645.8 mW, leaving only 4.2 mW in that branch allocation before additional effects. I retain the positive-rail capacity and 25 mA discharge ceiling despite the lower input-only analog load, and must close the complete measured allocation and efficiency. These are engineering allocations, not a complete guaranteed maximum-power specification. I require VFIELD ≥8.4 V at a measured 9 V connector input under full load across 0–50 °C, bounding total hot input-path drop to 0.6 V. At 8.4 V and 80% assumed buck efficiency, 2 A switched loads plus 6 W electronics draw approximately 2.893 A before the four pre-diode bleeders and high-side operating-current reserve defined in the system budget. I start unloaded and measure the eFuse UVLO/startup path and hot loaded voltage drop before claiming the 9 V full-load envelope.

I retain the isolated-converter networks on the field-I/O sheet and USB data/CC/supervisor/watchdog networks on the control sheet. FIELD5V_VALID is generated from controller-powered monitors and does not depend on the boost or child VFP rails. ANALOG_VALID adds +15 V and field-logic qualification and must not depend on the VFP outputs it enables.

I still need the following evidence before releasing a layout or assigning measured ratings:

- I must archive selected-capacitor bias/temperature/aging curves and demonstrate the effective-capacitance minima listed above. Murata's production listings establish candidate lifecycle, not a bias-retention guarantee. This is a specific pre-layout component check that remains open.
- I must create the two missing local IC symbols (LMR38020 DDA and TPS709 DBV) and the XFL3012 footprint, then verify every pin/pad and exposed-pad connection against the current drawings. Existing KiCad 10 candidate footprints are identified in the component list; library existence alone is not an assembly review.
- I must review eFuse startup dissipation with the assembled capacitance and converter sequencing, and the blocking FET's temperature/SOA against source-removal and reversal waveforms. CSD19537Q3 has a 16.6 mΩ room-temperature bound at 6 V gate drive, below the driver's 8.3 V minimum gate boost; I still need its hot-board losses. TPS2663's 53 mΩ maximum internal resistance gives 477 mW at 3 A.
- I must measure buck/boost ripple and load steps, brownout/reset behavior, USB attach/power-off data leakage, child-rail discharge timing, and all disarmed fault tests using the finished schematic/layout. I have performed datasheet arithmetic and topology review here; I have not passed these physical tests.

I keep switch loops short, route feedback away from SW nodes, provide thermal copper and vias for the eFuse/buck, and preserve a continuous MAIN_GND return below the control circuits. I route the TVS return directly to the supply connector and keep its pulse current out of ADC-reference paths.
