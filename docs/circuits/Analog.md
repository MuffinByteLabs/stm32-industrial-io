# Analog circuits

I use two voltage inputs, two current inputs and protected current diagnostics for the four load outputs. This document fixes their connections, passive values, source limits and initial verification fixtures before I draw the schematic. [analog.json](../components/analog.json) contains planned component groups and quantities; it is not a released assembly BOM. I compare physical pins and land patterns with the manufacturer's drawings during capture. I use `MAIN_GND` for these nonisolated analog ports and keep their returns away from actuator current.

## Sheet boundaries

| Net | Connection and initial behavior |
|---|---|
| `5V_FIELD`, `15V_ANA` | Power-sheet rails for the ADC, current-diagnostic buffer and input protection |
| `3V3_FIELD_LOGIC` | Field digital rail, including ADS8684A DVDD and fault pullups |
| `3V3_MCU_ANA` | Receiving MCU analog rail; powers the downstream TMUX1511 |
| `VFP_ENABLE` | Independent hardware-qualified field signal; local 10 kΩ pulldown at each threshold LDO |
| `LOOP_ENABLE` | Hardware `ANALOG_VALID AND ACQ_ENABLE_CMD`, default low; drives both TPS26611 EN pins |
| `DO_CS_ENABLE` | `HEALTH_READY`, default low; enables the single current-diagnostic TMUX1511 channel |
| `ADC_CS_FIELD`, `ADC_SCLK_FIELD`, `ADC_MOSI_FIELD`, `ADC_RST_N_FIELD` | Buffered ADC commands; PC10/package pin 79 owns reset, held low until initialization |
| `ADC_MISO_FIELD` | Output through the receiving-domain interface; ALARM is unused and firmware polls range alarms |
| `AI_V_FAULT_N_FIELD`, `AI_I_FAULT_N_FIELD` | Open-drain protector flags with field-domain pullups |
| `LOOP1_SGOOD_FIELD`, `LOOP2_SGOOD_FIELD` | TPS26611 status: high invalid/fault, low good; [Loop_Status](Loop_Status.md) conditions its weak 2–3 V output |
| `DO_CS_RAW`, `DO_CS_ADC` | Field-sheet current-sense output and protected MCU ADC input; PB1/package pin 33 receives `DO_CS_ADC` |


I expose four signal/ground connector pairs: `AI_V1`, `AI_V2`, `AI_I1`, and `AI_I2`. Each uses Phoenix Contact `1844210` board header with `1840366` mating plug, pin 1 signal and pin 2 `MAIN_GND`; I verify the physical pin-1 orientation during capture. I do not connect a current terminal to a source of voltage for normal operation.

## Threshold supplies and shutdown sequencing

I generate `VFP11` and `VFP6` with two `TPS7A1601DGNR` regulators from `15V_ANA`. Their feedback bottom resistors are 10.0 kΩ; tops are 82.0 kΩ and 40.2 kΩ, all ±0.1%, 25 ppm/°C. Nominal outputs are **10.9756 V** and **5.98886 V**. Each has 10 µF/50 V X7R on IN and OUT, 100 nF on IN, and a **4.70 kΩ ±0.1% output bleeder**. Each 10 µF capacitor has a conservative upper bound of 12.65 µF including initial tolerance and temperature; its effective capacitance at bias must remain ≥2.2 µF. Including the parallel 100 nF TMUX VFP bypass, I bound each complete child output at **12.7765 µF**.

| TPS7A1601 DGN pin | Connection |
|---|---|
| 1 OUT | `VFP11` or `VFP6`, output capacitor and bleeder |
| 2 FB | Feedback resistor junction |
| 3 PG; 7 DELAY; 6 NC | Explicit no-connect; I do not use this device's PG for board health |
| 4 GND; exposed pad | `MAIN_GND` |
| 5 EN | `VFP_ENABLE`, with 10 kΩ local pulldown |
| 8 IN | `15V_ANA`, local bypass |

The calculated output bounds, including ±2% regulator accuracy, a conservative ±0.2% envelope on each resistor for initial tolerance and 0–50 °C drift, and ±0.1 µA feedback current, are **10.710–11.243 V** and **5.846–6.132 V**. These are threshold-supply bounds; they are not guaranteed TMUX trip thresholds. [TPS7A16 sections 5, 6.1, 6.5 and 8](https://www.ti.com/lit/ds/symlink/tps7a16.pdf).

I use the control sheet's `VFP_ENABLE = ANALOG_VALID AND FIELD3V3_OK`. Its lowest cornered +15 V falling threshold is **12.72283 V**; hardware must remove enable asynchronously within a **1 ms qualification bound**, which is not guaranteed by the monitor's typical propagation-delay table. The power sheet includes **680 µF ±20%** bulk on `15V_ANA`; the shutdown contract requires at least **500 µF effective capacitance over 0–50 °C**, and a conservative discharge-current ceiling of 25 mA. With the threshold LDOs disabled, the worst VFP time constant is **60.17 ms**. Starting at 12.72283 V parent supply and the maximum child voltages, the linear parent fall takes 254.46 ms; including the 1 ms disable delay and an assumed **5 µA maximum total net sourcing** into each child output, the ending VFP levels are **0.1897 V and 0.1140 V**. The sourcing bound includes the attached TMUX and external-input conditions; the LDO's shutdown input-current specification alone does not prove it. During the initial disable delay the parent remains above either child. Subsequently the exponential child-minus-linear-parent difference is convex, so its maximum is at an endpoint: both endpoints remain below the **0.3 V** OUT-to-IN/VFP-to-VDD stress limits. This is a conditional calculation for ordinary source removal and commanded shutdown, pending capacitance, timing, total-net-current and waveform evidence. I exclude an internally shorted `15V_ANA` rail from the external-terminal qualification envelope. I measure both rail falls before release and use no generic Schottky forward-voltage assumption to claim this limit.

I keep acquisition invalid for **at least 50 ms after `VFP_ENABLE` rises**, and verify that both VFP rails have settled before accepting measurements. `VFP_ENABLE` must derive from independent power health; it must not depend on a measurement that needs these threshold supplies to start.

## TMUX protection groups

I fit two `TMUX7462FPWR` protectors with `VDD=15V_ANA`, `VSS=VFN=MAIN_GND`, `DR=15V_ANA`, **1 µF/50 V plus 100 nF locally at each VDD**, 100 nF at each VFP, and a 1 kΩ fault pullup to `3V3_FIELD_LOGIC`. The added VDD capacitors follow the manufacturer's local bypass recommendation and belong to the +15 V parent startup account, not the child VFP output-capacitance maxima. DR high selects high impedance at D during a fault. The voltage group uses `VFP11`; the current group uses `VFP6`. The negative threshold is approximately −0.7 V because VFN is ground; the positive and negative threshold offsets are typical values, so I retain independent voltage clamps and bench-test their behavior. A fault flag invalidates the reading; an open D pin does not establish that the terminal is zero. [TMUX7462F sections 5, 6, 8.3 and 9.3–9.4](https://www.ti.com/lit/ds/symlink/tmux7462f.pdf).

| TMUX7462F PW pin | Voltage group | Current group |
|---|---|---|
| 1 VFN; 4 VSS; 5 GND | `MAIN_GND` | `MAIN_GND` |
| 3 S1 → 2 D1 | `AI_V1_CLAMP` → `AI_V1_PROTECTED` | `AI_I1_SHUNT` → `AI_I1_PROTECTED` |
| 14 S2 → 15 D2 | `AI_V2_CLAMP` → `AI_V2_PROTECTED` | `AI_I2_SHUNT` → `AI_I2_PROTECTED` |
| 11 S3 → 10 D3 | Both to `MAIN_GND` | Both to `MAIN_GND` |
| 6 S4 → 7 D4 | Both to `MAIN_GND` | Both to `MAIN_GND` |
| 8 DR; 13 VDD | `15V_ANA` | `15V_ANA` |
| 9 NC | Explicit no-connect | Explicit no-connect |
| 12 FF | `AI_V_FAULT_N_FIELD` | `AI_I_FAULT_N_FIELD` |
| 16 VFP | `VFP11` | `VFP6` |

## Two 0–10 V inputs

For each channel I connect the terminal through **1.00 kΩ, CRCW25121K00FKEGHP**, to `AI_Vx_CLAMP`; an `SMCJ11CA` goes from that node to `MAIN_GND`. This is the protected S side of the voltage TMUX. Its D side passes through **100 Ω ±0.1%** to the corresponding ADC AINP. I put **1 µF/50 V X7R** between AINP and its AINGND, and connect AINGND locally to `MAIN_GND`.

I specify source resistance **≤100 Ω** and require the source to sink and source approximately 10 µA. The ADC's input resistance is biased toward about 2.5 V; it is not a simple resistor to ground. Using an illustrative 850 kΩ input resistance and 8.3 Ω TMUX resistance, 10 V produces 9.990234 V at the ADC before calibration. Changing the external source resistance by 100 Ω adds about 0.88 mV of span error. A disconnected source can drift toward the ADC bias voltage and is not a reliable zero/open-wire detector. The nominal RC pole is about 144 Hz; I publish 100 Hz values for signals whose intended useful bandwidth is ≤20 Hz, with oversampling and a defined digital filter.

I perform two-point calibration at 0 V and 10 V with the qualified source and then check 1, 2.5, 5, 7.5 and 9 V. My acceptance target is **±20 mV at room temperature and ±50 mV over 0–50 °C using the same calibration coefficients**. The illustrative resistor-loading model does not prove the ADC's worst-case thermal behavior; calibration residuals and drift must meet the target on the built board. For ±30 V DC terminal miswire, the 1 kΩ series part reduces TVS power. Using the 12.2 V minimum breakdown as a conservative estimate gives about 18 mA and 0.32 W in that resistor. The chosen 2512 high-power part has margin over that estimate. The TVS is a pulse device; this arithmetic and its 18.2 V specified clamp do not claim an EMC compliance result or unlimited continuous surge capability. [Vishay CRCW-HP ratings and pulse curves](https://www.vishay.com/docs/20043/crcwhpe3.pdf), [Littelfuse SMCJ table](https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_smcj_datasheet?assetguid=37388813-0d6d-4329-969b-1aa8b7614ac1).

## Two 4–20 mA inputs

I connect each current terminal directly to TPS26611 IN. Its OUT drives a **permanent 200 Ω shunt**: five parallel `RT1206BRD071KL` 1.00 kΩ resistors, each ±0.1%, 25 ppm/°C and 0.25 W. I route the five equal branches between two common pads and take the ADC sense and ground as a separate Kelvin pair. I do not remove this load during ADC faults or resets. Each terminal has an `SMCJ33CA` to `MAIN_GND`; the current protector remains responsible for DC current limiting.

| TPS26611 DDF pin | Connection on each channel |
|---|---|
| 1 GND; 2 MODE; 3 −Vs | `MAIN_GND`; MODE grounded selects receiver behavior |
| 4 IN | `AI_Ix` connector signal |
| 5 OUT | `AI_Ix_SHUNT`, permanent shunt to `MAIN_GND` |
| 6 +Vs | `15V_ANA`, 100 nF local bypass |
| 7 EN | `LOOP_ENABLE`, local 10 kΩ pulldown |
| 8 SGOOD | High-impedance control-sheet status interface; no external low-value pullup or pulldown |

Only the **high impedance sense branch after the shunt** goes through the current TMUX and a 1.00 kΩ ±0.1% resistor to the ADS AINP. I place 1 µF/50 V at AINP. TMUX resistance therefore does not add series loop burden. The maximum documented TPS26611 resistance of 12.5 Ω gives a **4.25 V burden at 20 mA**, before the wire and transmitter headroom. The 25–40 mA current-limit interval means I qualify overrange to **24 mA**; the 25.6 mA ADC span endpoint is a mathematical value, not a guaranteed delivered overrange.

The 40 mA limit puts 8 V and 0.32 W on the complete shunt, or 64 mW per resistor. Total nominal power rating is 1.25 W without statistical tolerance averaging. MODE grounded limits an overload for a nominal 100 ms interval, followed by nominal 800 ms auto-retry; thermal shutdown can interrupt it earlier. I verify fault/retry waveforms and do not model a sustained fault as continuous 40 mA forever. As a conservative initial-pulse fixture, 30 V across the shunt for 55 µs gives 49.5 µJ per resistor and 0.9 W instantaneous power. The 55 µs figure is characterized for a particular load transient, not a guaranteed bound for every terminal short. I compare the fixture with the selected resistor family's overload/pulse data and verify actual transient amplitude, duration and resistance shift on the protector circuit. The device's current limit does not make pulse energy zero. [TPS2661 section 8.3 and Table 8-3](https://www.ti.com/lit/ds/symlink/tps2661.pdf).

At 20 mA the illustrative 850 kΩ ADC model gives 3.997871 V after the 1 kΩ sense resistor. This fixed gain/offset shift is included in calibration. I calibrate at 4 and 20 mA, then check 0, 3.5, 8, 12, 16 and 24 mA. My 4–20 mA acceptance target is **±32 µA at room temperature and ±80 µA over 0–50 °C using the same coefficients**. A 25 ppm/°C shunt drift over 25 °C from calibration contributes 12.5 µA at 20 mA; I reserve the remaining error for ADC drift, calibration uncertainty, leakage, self-heating and reference behavior.

I test +30 V and −30 V terminal faults powered and unpowered. Receiver-mode negative-fault recovery requires an explicit reset: mark acquisition invalid, remove the fault, command both EN pins low for **≥10 ms**, then re-enable and wait for good status and settled readings. The application separately decides whether unavailable sensor data requires stopping its loads. I do not assume the protector senses terminal input voltage for its output-overvoltage threshold: that threshold is referenced to OUT and +Vs. [TPS2661 Rev C sections 6, 7 and 8](https://www.ti.com/lit/ds/symlink/tps2661.pdf).

## ADC wiring, reference and serial timing

I fit `ADS8684AIDBTR`. Both AVDD pins use filtered `5V_FIELD`: **1 Ω** in series with the ADC supply, **10 kΩ bleeder** at ADC AVDD, and 22 µF plus 1 µF at each AVDD pin. I also fit 100 nF directly at each supply pin. DVDD is `3V3_FIELD_LOGIC`, with 22 µF, 1 µF and 100 nF. Each separately placed AVDD 22 µF decoupler and the DVDD 22 µF decoupler must meet an independent **≥10 µF effective floor**; I track these three banks separately in [capacitor evidence](../calcs/capacitor_evidence.json), retaining the near-pin 1 µF bypasses required on AVDD. The recommended supply relation is **DVDD ≤ AVDD**; AVDD must be 4.75–5.25 V for specified operation, and the performance-characterized DVDD range is 2.7–5.25 V. I invalidate acquisition through startup and brownout and verify the actual AVDD/DVDD waveforms rather than treating independent supply ratings as a sequencing guarantee. The reference is internal: REFSEL low, two parallel 22 µF/25 V X7R capacitors on REFIO and two on REFCAP, plus 1 µF at REFCAP. I require effective reference capacitance **≥10 µF** after tolerance, bias and temperature; I preserve the manufacturer's capacitor curves with the capture review. I do not use either reference output to supply another circuit.

| ADS8684A DBT pin | Net |
|---|---|
| 1 SDI; 2 RST/PD; 36 SDO; 37 SCLK; 38 CS | `ADC_MOSI_FIELD`; `ADC_RST_N_FIELD` with 10 kΩ pulldown; `ADC_MISO_FIELD`; `ADC_SCLK_FIELD`; `ADC_CS_FIELD` with 10 kΩ pullup to field logic |
| 3 DAISY; 4 REFSEL | `MAIN_GND` |
| 5 REFIO; 6 REFGND; 7 REFCAP | Private reference capacitor nodes; REFGND to local `MAIN_GND` |
| 8, 28, 29, 31, 32 AGND; 33 DGND | `MAIN_GND`, short local plane connections |
| 9, 30 AVDD; 34 DVDD | ADC-filtered 5 V; field 3.3 V |
| 10 AUXIN; 11 AUXGND | `MAIN_GND` |
| 16 AIN0P; 17 AIN0GND | Voltage input 1; local `MAIN_GND` |
| 18 AIN1P; 19 AIN1GND | Voltage input 2; local `MAIN_GND` |
| 21 AIN2P; 20 AIN2GND | Current input 1; shunt Kelvin ground |
| 23 AIN3P; 22 AIN3GND | Current input 2; shunt Kelvin ground |
| 35 ALARM | Explicit no-connect; firmware polls alarm registers |
| 12–15, 24–27 NC | Explicit no-connect |

I program the voltage ranges to 0–10.24 V and current ranges to 0–5.12 V. I start at **1.125 MHz SPI**, with 32 clocks per transaction: about 28.44 µs, comfortably above the specified 850 ns conversion interval. I schedule 4 kSPS aggregate, 1 kSPS/channel, and preserve the command/data pipeline's channel identity in DMA processing. A later 4.5 MHz setting requires separate timing qualification. A 17 MHz headline serial limit is not permission to read data before conversion finishes. The two voltage and two loop RC poles are analog noise filtering; I do not describe a single-pole filter as perfect alias rejection. [ADS8684A sections 7.6, 8.3 and 10–11](https://www.ti.com/lit/ds/symlink/ads8684a.pdf).

## Protected load-current diagnostics

I attenuate `DO_CS_RAW` through **56.0 kΩ / 68.0 kΩ ±0.1%, 25 ppm/°C**. The divider midpoint feeds amplifier A of `OPA2320AIDR`, powered from **5V_FIELD**. This divider loads the field-sheet 1.21 kΩ current-sense burden by 124 kΩ, giving an effective burden of **1198.3068 Ω**. At 0.5 A of driver current and a nominal 300:1 sense ratio, `DO_CS_RAW` is approximately 1.99718 V. Driver current includes the field sheet's pre-diode 10 kΩ bleeder, up to approximately 3.038 mA per channel at 30 V in the selected resistor/temperature envelope. The actual sense-ratio uncertainty belongs in diagnostic calibration; this is not a precision overload threshold.

I create independent `CLAMP2V5` with `LM4040AIM3-2.5/NOPB`: pin 1 cathode at reference, pin 2 anode at ground, and the manufacturer's `*` pin 3 left floating. Pin 3 is permitted to float or connect to the anode; it is not a generic NC pin. I fit a **1.00 kΩ ±0.1% feed from 5V_FIELD**, a **100 kΩ bleeder** and 100 nF to ground. One `BAS70-04,215` protects the buffer input and another protects the downstream divider node. Each dual diode has pin 1 at ground, pin 3 at its protected node, and pin 2 at `CLAMP2V5`. The reference has current margin above its 65 µA minimum and below its 15 mA maximum; I use a conservative ±1% voltage allowance for reference tolerance and load change. Schottky forward-drop/leakage figures at 25 °C do not establish full-temperature guarantees. [LM4040-N sections 4 and 5.8](https://www.ti.com/lit/ds/symlink/lm4040-n.pdf), [BAS70-04 characteristics](https://assets.nexperia.com/documents/data-sheet/BAS70-04.pdf).

| OPA2320 SOIC pin | Connection |
|---|---|
| 1 OUTA; 2 −INA; 3 +INA | `DO_CS_BUFFER`; direct feedback to OUTA; protected 56 kΩ/68 kΩ midpoint |
| 4 V−; 8 V+ | `MAIN_GND`; `5V_FIELD` with 1 µF and 100 nF |
| 5 +INB; 6 −INB; 7 OUTB | `MAIN_GND`; direct feedback to OUTB; unused ground follower, output otherwise unconnected |

I add 100 kΩ from `DO_CS_BUFFER` to ground. The high-value input divider limits residual beyond-rail input current below the manufacturer's 10 mA stress limit; a negative clamped input is not normal amplifier operation. A raw 6.5 V diagnostic fault would produce about 3.565 V at the unprotected divider midpoint, so the clamp and validity checks matter. [OPA2320/OPA320 input protection and supply limits](https://www.ti.com/lit/ds/symlink/opa320.pdf).

The buffer output drives a **1.00 kΩ top / 1.50 kΩ ground divider**, then TMUX1511 S1. Both resistors are ±0.1%, 25 ppm/°C. D1 drives `DO_CS_ADC` with a **47 kΩ pulldown and 1 nF C0G**. A conservative ±0.2% resistor envelope bounds a 5.75 V buffer excursion to **≤3.456 V** at S1 when the receiving rail is absent, below the 3.6 V recommended powered-off ceiling without depending on Schottky forward drop. With the 47 kΩ load and the switch's illustrative 2 Ω typical on-resistance, the nominal 0.5 A driver-current/300 result is approximately **0.6488 V**. I calibrate the diagnostic path after channel selection and settling. I report qualified on-state driver current with its validity and sample age. An external load-current estimate subtracts `VOUT_SW / R_bleed` from calibrated driver current and includes the voltage, bleeder and calibration uncertainty; that estimate is valid only in the qualified settled on-state sampling window. It is not an off-state or average PWM-current measurement.

| TMUX1511 PW pin | Connection |
|---|---|
| 1 SEL1 | `DO_CS_ENABLE`, 10 kΩ pulldown |
| 2 S1 → 3 D1 | Buffered diagnostic divider → `DO_CS_ADC` |
| 7 GND; 14 VDD | `MAIN_GND`; `3V3_MCU_ANA` with 1 µF and 100 nF |
| 4 SEL2; 5 S2; 6 D2; 8 D3; 9 S3; 10 SEL3; 11 D4; 12 S4; 13 SEL4 | `MAIN_GND`; unused channels disabled |

I budget the specified 2 µA powered-off leakage through 47 kΩ as **94 mV uncertainty while off**, and mark that state invalid. The upstream clamp has no connection to the MCU supply. I qualify negative-transient stress limits separately and verify complete-chain settling before fixing MCU ADC sample timing. I follow the [field I/O](Field_IO.md) channel-selection and PWM sample schedule; a sample outside its qualified window is invalid. I discard the first STM32 ADC conversion after an idle interval over 1 ms where required by its silicon errata. [TMUX1511 sections 5–6 and Powered-Off Protection](https://www.ti.com/lit/ds/symlink/tmux1511.pdf).

## Reproduced checks and remaining gates

I reproduce shunt power, receiver burden, ADC biased-input loading, VFP rail tolerance/shutdown and the current-diagnostic transfer with [analog_checks.py](../calcs/analog_checks.py). I check the active voltage-input, current-input and current-diagnostic DC networks using [dc_frontends.cir](../calcs/dc_frontends.cir) and [spice_dc_check.py](../calcs/spice_dc_check.py) with the installed ngspice shared library. The SPICE testbench uses an illustrative biased ADC resistance, fixed on-resistances and an ideal finite-gain diagnostic amplifier. It checks connectivity and passive transfer equations; it does not establish active-protector fault response, amplifier stability, complete component tolerances or hardware performance.

Before I approve the analog sheet for manufacture, I close these gates:

- Preserve capacitor bias curves and confirm reference minimum capacitance, VFP maximum capacitance and bleeder/bulk shutdown bounds.
- Compare symbols and footprint pins with manufacturer drawings, then inspect the captured netlist against these tables.
- Measure threshold-rail startup/shutdown, ADC AVDD during power loss, loop reset/recovery and fault currents using current-limited fixtures.
- Measure calibration residuals, drift and diagnostic clamp/settling behavior over the selected 0–50 °C envelope.

I reserve **10 mA from 15V_ANA** for both current protectors, both TMUX protectors and threshold regulators/bleeders. The permanent shunts receive loop current from external transmitters, not the board supply. I retain a conservative **12 mA from 5V_FIELD for the diagnostic buffer/reference branch**, separate from the ADC reservation. The power sheet adds boost feedback/bleed and conversion loss. These are design allocations; simultaneous fault and shutdown waveforms remain measurement gates.
