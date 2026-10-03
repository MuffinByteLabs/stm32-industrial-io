# Analog circuits

I use two voltage inputs, two current inputs and one protected voltage output. This document fixes their connections, passive values, source limits and initial verification fixtures before I draw the schematic. [analog.json](../components/analog.json) contains planned component groups and quantities; it is not a released assembly BOM. I compare physical pins and land patterns with the manufacturer's drawings during capture. I use `MAIN_GND` for these nonisolated analog ports and keep their returns away from actuator current.

## Sheet boundaries

| Net | Connection and initial behavior |
|---|---|
| `5V_FIELD`, `15V_ANA`, `VNEG` | Power-sheet rails; VNEG comes from LM7705 and is required for AO zero headroom |
| `3V3_FIELD_LOGIC` | Field digital rail, including ADS8684A DVDD and fault pullups |
| `3V3_MCU_ANA` | Receiving MCU analog rail; powers only the downstream TMUX1511 on this sheet |
| `VFP_ENABLE` | Hardware-qualified field-domain signal from the control sheet; local 10 kΩ pulldown at each threshold LDO |
| `LOOP_ENABLE` | Hardware `ANALOG_VALID AND ACQ_ENABLE_CMD`, default low; drives both TPS26611 EN pins |
| `AO_ENABLE_GATED` | Control-sheet arm and rail-health gate, default low; drives ADG5401F IN |
| `READBACK_ENABLE` | Receiving-domain reset, field-health and analog-health qualification; default low; drives two TMUX1511 SEL pins |
| `ADC_CS_FIELD`, `ADC_SCLK_FIELD`, `ADC_MOSI_FIELD`, `ADC_RST_N_FIELD` | Field-buffered command inputs; PC10/package pin 79 owns ADC reset and the tenth outgoing buffer carries it; reset is pulled low until initialization |
| `ADC_MISO_FIELD` | Output through the control sheet's receiving-domain interface; ALARM is unused and firmware polls range alarms |
| `DAC_CS_FIELD`, `DAC_SCLK_FIELD`, `DAC_MOSI_FIELD` | Field-buffered DAC command inputs; CS pulled high |
| `AI_V_FAULT_N_FIELD`, `AI_I_FAULT_N_FIELD`, `AO_FAULT_N_FIELD` | Open-drain fault outputs, field-domain pullups; receiving-domain interface on control sheet |
| `LOOP1_SGOOD_FIELD`, `LOOP2_SGOOD_FIELD` | TPS26611 status; high means invalid/fault, low means signal good; the [Loop_Status](Loop_Status.md) sheet conditions its weak 2–3 V output before the receiving interface |
| `DO_CS_RAW` | Field-sheet TPS4H160B current-sense output |
| `AO_READBACK`, `DO_CS_ADC` | Protected receiving-domain analog ADC inputs |

I expose five signal/ground connector pairs: `AI_V1`, `AI_V2`, `AI_I1`, `AI_I2`, and `AO1`. Each uses Phoenix Contact `1844210` board header with `1840366` mating plug, pin 1 signal and pin 2 `MAIN_GND`; I verify the physical pin-1 orientation during capture. I do not connect a current terminal to a source of voltage for normal operation.

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

I use the control sheet's `VFP_ENABLE = ANALOG_VALID AND FIELD3V3_OK`. Its lowest cornered +15 V falling threshold is **12.72283 V**; hardware removes enable asynchronously within a **1 ms qualification bound**. The power sheet includes **680 µF ±20%** bulk on `15V_ANA`; the shutdown contract requires at least **500 µF effective capacitance over 0–50 °C**, and a conservative discharge-current ceiling of 25 mA. With the threshold LDOs disabled, the worst VFP time constant is **60.17 ms**. Starting at 12.72283 V parent supply and the maximum child voltages, the linear parent fall takes 254.46 ms; including the 1 ms disable delay and 5 µA shutdown current into each child output, the ending VFP levels are **0.1897 V and 0.1140 V**. During the initial disable delay the parent remains above either child. Subsequently the exponential child-minus-linear-parent difference is convex, so its maximum is at an endpoint: both endpoints remain below the **0.3 V** OUT-to-IN/VFP-to-VDD stress limits. This calculation covers ordinary source removal and commanded shutdown. I exclude an internally shorted `15V_ANA` rail from the external-terminal qualification envelope. I measure both rail falls before release and use no generic Schottky forward-voltage assumption to claim this limit.

I keep acquisition invalid for **at least 50 ms after `VFP_ENABLE` rises**, and verify that both VFP rails have settled before permitting output arm. `VFP_ENABLE` must derive from independent power health; it must not depend on a measurement that needs these threshold supplies to start.

## TMUX protection groups

I fit two `TMUX7462FPWR` protectors with `VDD=15V_ANA`, `VSS=VFN=MAIN_GND`, `DR=15V_ANA`, 100 nF at VDD and VFP, and a 1 kΩ fault pullup to `3V3_FIELD_LOGIC`. DR high selects high impedance at D during a fault. The voltage group uses `VFP11`; the current group uses `VFP6`. The negative threshold is approximately −0.7 V because VFN is ground; the positive and negative threshold offsets are typical values, so I retain independent voltage clamps and bench-test their behavior. A fault flag invalidates the reading; an open D pin does not establish that the terminal is zero. [TMUX7462F sections 5, 6 and 8.3](https://www.ti.com/lit/ds/symlink/tmux7462f.pdf).

| TMUX7462F PW pin | Voltage group | Current group |
|---|---|---|
| 1 VFN; 4 VSS; 5 GND | `MAIN_GND` | `MAIN_GND` |
| 3 S1 → 2 D1 | `AI_V1_CLAMP` → `AI_V1_PROTECTED` | `AI_I1_SHUNT` → `AI_I1_PROTECTED` |
| 14 S2 → 15 D2 | `AI_V2_CLAMP` → `AI_V2_PROTECTED` | `AI_I2_SHUNT` → `AI_I2_PROTECTED` |
| 11 S3 → 10 D3 | `AO1` → `AO_READBACK_PROTECTED` | Both to `MAIN_GND` |
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

The 40 mA limit puts 8 V and 0.32 W on the complete shunt, or 64 mW per resistor. Total nominal power rating is 1.25 W without statistical tolerance averaging. As a conservative initial-pulse fixture, 30 V across the shunt for 55 µs gives 49.5 µJ per resistor and 0.9 W instantaneous power. I compare that with the selected resistor family's overload/pulse data and verify transient amplitude, duration and resistance shift on the actual protector circuit. The device's current limit does not make pulse energy zero.

At 20 mA the illustrative 850 kΩ ADC model gives 3.997871 V after the 1 kΩ sense resistor. This fixed gain/offset shift is included in calibration. I calibrate at 4 and 20 mA, then check 0, 3.5, 8, 12, 16 and 24 mA. My 4–20 mA acceptance target is **±32 µA at room temperature and ±80 µA over 0–50 °C using the same coefficients**. A 25 ppm/°C shunt drift over 25 °C from calibration contributes 12.5 µA at 20 mA; I reserve the remaining error for ADC drift, calibration uncertainty, leakage, self-heating and reference behavior.

I test +30 V and −30 V terminal faults powered and unpowered. Receiver-mode negative-fault recovery requires an explicit reset: disarm outputs, remove the fault, command both EN pins low for **≥10 ms**, then re-enable and wait for good status and settled readings. I do not assume the protector senses terminal input voltage for its output-overvoltage threshold: that threshold is referenced to OUT and +Vs. [TPS2661 Rev C sections 6, 7 and 8](https://www.ti.com/lit/ds/symlink/tps2661.pdf).

## ADC wiring, reference and serial timing

I fit `ADS8684AIDBTR`. Both AVDD pins use filtered `5V_FIELD`: **1 Ω** in series with the ADC supply, **10 kΩ bleeder** at ADC AVDD, and 22 µF plus 1 µF at each AVDD pin. I also fit 100 nF directly at each supply pin. DVDD is `3V3_FIELD_LOGIC`, with 22 µF, 1 µF and 100 nF. The reference is internal: REFSEL low, two parallel 22 µF/25 V X7R capacitors on REFIO and two on REFCAP, plus 1 µF at REFCAP. I require effective reference capacitance **≥10 µF** after tolerance, bias and temperature; I preserve the manufacturer's capacitor curves with the capture review. I do not use either reference output to supply another circuit.

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

I program the voltage ranges to 0–10.24 V and current ranges to 0–5.12 V. I start at **1.125 MHz SPI**, shared with the DAC, with 32 clocks per transaction: about 28.44 µs, comfortably above the specified 850 ns conversion interval. I schedule 4 kSPS aggregate, 1 kSPS/channel, and preserve the command/data pipeline's channel identity in DMA processing. A later 4.5 MHz setting requires separate timing qualification. A 17 MHz headline serial limit is not permission to read data before conversion finishes. The two voltage and two loop RC poles are analog noise filtering; I do not describe a single-pole filter as perfect alias rejection. [ADS8684A sections 7.6, 8.3 and 10–11](https://www.ti.com/lit/ds/symlink/ads8684a.pdf).

## Protected 0–10 V output

I fit `DAC80501ZDGSR`, the zero-scale-at-reset version, and `OPA2197IDR`. Amplifier A provides gain four through 30.0 kΩ feedback and 10.0 kΩ ground resistors, both ±0.1%, 25 ppm/°C. Amplifier B is a separate unity buffer with terminal feedback through `ADG5401FBCPZ-RL7`. Both amplifiers use `15V_ANA` and `VNEG`, with 100 nF at each rail and 1 µF on VNEG. A 100 kΩ VNEG bleeder discharges the negative rail. The power sheet separately owns the LM7705 circuit.

| DAC80501 DGSR pin | Connection |
|---|---|
| 1 VDD; 4 AGND; 5 SPI2C | `5V_FIELD` with 100 nF; `MAIN_GND`; `MAIN_GND` selects SPI |
| 2 VOUT | Amplifier A positive input |
| 6 SCLK; 7 SYNC; 8 SDIN | DAC field command nets; SYNC has 10 kΩ pullup |
| 10 VREFIO | Private internal-reference node with 1 µF/50 V to `MAIN_GND` |
| 3, 9 NC | Explicit no-connect |

I explicitly configure **REF-DIV=1 and BUFF-GAIN=1**, keeping the default internal reference enabled, to obtain a 2.5 V DAC span before gain four. The register names encode bits: DIV=2 and GAIN=2 multiply to unity. I wait at least 250 µs after DAC power-up, write/read back configuration, load zero, and keep the AO hardware disconnect open until initialization and calibration checks are complete. [DAC80501 sections 8.3 and 8.5](https://www.ti.com/lit/ds/symlink/dac80501.pdf).

| OPA2197 SOIC pin | Connection |
|---|---|
| 1 OUTA; 2 −INA; 3 +INA | Gain node; 30 kΩ/10 kΩ feedback junction; DAC output |
| 4 V−; 8 V+ | `VNEG`; `15V_ANA` |
| 5 +INB; 6 −INB; 7 OUTB | Gain node; ADG DFB; `AO_DRIVER` |

| ADG5401F CP pin | Connection |
|---|---|
| 1 S | Through **100 Ω CRCW1206100RFKEAHP** to terminal `AO1` |
| 2 SFB | Terminal `AO1` through **4.7 kΩ ±0.1%** |
| 3 FF | `AO_FAULT_N_FIELD`, 10 kΩ pullup to field logic |
| 4 GND; 6 VSS; 7 POC | `MAIN_GND`; POC low selects the disabled pull-to-ground behavior |
| 5 VDD | `15V_ANA`, 100 nF local bypass |
| 8 IN | `AO_ENABLE_GATED`, local 10 kΩ pulldown |
| 9 DFB | Amplifier B negative input, with **1 nF C0G** from `AO_DRIVER` |
| 10 D | `AO_DRIVER` |

The feedback switch is not part of the gain-four divider. Its 0.6 kΩ nominal feedback path, conservatively modeled to 3.9 kΩ, carries amplifier input current only. At high frequency the 1 nF local compensation capacitor restores fast local feedback; at DC the amplifier compensates switch/100 Ω drops at the actual terminal. When disabled or faulted, the ADG's internal D-to-DFB path maintains a closed amplifier loop. I fit a **100 kΩ terminal pulldown** and **SMCJ33CA** at `AO1`. I also fit two `PMEG3010CEH,115` driver clamps: one has anode at ground/cathode at `AO_DRIVER`, and the other anode at `AO_DRIVER`/cathode at `15V_ANA`. I put them directly beside the driver and provide a short return to the power-sheet bulk capacitor. [ADG5401F sections Pin Functions and Applications](https://www.analog.com/media/en/technical-documentation/data-sheets/adg5401f.pdf), [OPA197/OPA2197 electrical data](https://www.ti.com/lit/ds/symlink/opa197.pdf), [driver clamp ratings](https://assets.nexperia.com/documents/data-sheet/PMEG3010CEH.pdf).

I qualify loads ≥10 kΩ and total terminal capacitance **≤10 nF**, including cable, receiver and TVS. The initial cable fixture is ≤5 m with measured capacitance. At 10 V, the external load, 100 kΩ pulldown and 268 kΩ readback branch take approximately 1.138 mA; gain-stage feedback adds 0.25 mA. The 100 Ω resistor limits a conservative 45 V initial difference to 0.455 A at its −1% corner, below the ADG's 515 mA pulse stress limit. A conservative 1.8 µs negative-fault screening pulse at that difference represents about 36.8 µJ; this uses the longer single-supply timing table and still requires measured qualification at the actual +15 V supply; I compare the selected resistor's pulse curves and measure the actual response. The 4.7 kΩ feedback resistor plus a 600 Ω switch path limits the same initial difference to about 8.5 mA, below the amplifier's 10 mA input-clamp current limit. These are stress calculations, not normal operation. The selected driver diodes have a 0.44 V maximum forward drop at 0.5 A/25 °C; I measure their clamp voltage, parasitic overshoot and leakage across 0–50 °C before accepting the AO fault fixture. I do not claim full-temperature clamp limits from a 25 °C specification. The +15 V bulk absorbs the brief upper-clamp injection; persistent faults must open the ADG and clear arm.

My output target remains **±50 mV after calibration**, with 100 Hz command updates. Opposing 25 ppm/°C feedback-resistor drift over 25 °C contributes approximately 9.375 mV at 10 V; I reserve the balance for DAC/reference drift, amplifier errors, leakage, calibration uncertainty and noise. The external meter is the primary AO acceptance instrument; the MCU readback provides independent diagnostics.

## Independent readback protection

I protect AO readback through the spare voltage-group TMUX channel, then **200 kΩ/68 kΩ ±0.1%** to `MAIN_GND`. CS uses **56 kΩ/68 kΩ ±0.1%**. The two divider midpoints feed unity channels of `OPA2320AIDR` powered from **5V_FIELD**, not MCU service power. The CS divider loads `DO_CS_RAW` by 124 kΩ; with the field-sheet 1.21 kΩ burden, the effective burden is 1198.3068 Ω. A raw 6.5 V CS fault would produce 3.565 V without its clamp, so it is not a normal measurement.

I create an independent `CLAMP2V5` with `LM4040AIM3-2.5/NOPB`: pin 1 cathode at reference, pin 2 anode at ground, pin 3 NC; a **1.00 kΩ ±0.1% feed from 5V_FIELD**, **100 kΩ bleeder** and 100 nF to ground. For each buffer input and each post-buffer divider node, one `BAS70-04,215` provides lower/upper diodes: pin 1 at ground, pin 3 at protected node, pin 2 at `CLAMP2V5`. I fit four such dual diodes total. The reference has substantial current margin above its 65 µA minimum and below its 15 mA maximum; a conservative ±1% voltage allowance covers reference tolerance and load change. Schottky forward-drop/leakage values quoted at 25 °C are not promoted into full-temperature guarantees. [LM4040-N section 5.8](https://www.ti.com/lit/ds/symlink/lm4040-n.pdf), [BAS70-04 characteristics](https://assets.nexperia.com/documents/data-sheet/BAS70-04.pdf).

OPA2320 pins are 1 OUTA, 2 −INA, 3 +INA, 4 ground, 5 +INB, 6 −INB, 7 OUTB, 8 5V_FIELD. Each negative input connects directly to its output. I add 100 kΩ from each output to ground. The high-value input dividers limit any residual beyond-rail current to much less than the manufacturer's 10 mA limit; I do not claim normal amplifier operation for a negative clamped input. The amplifier has no connection to the receiving MCU rail. [OPA2320/OPA320 input protection and supply limits](https://www.ti.com/lit/ds/symlink/opa320.pdf).

Each buffer output drives a **1 kΩ top / 1.5 kΩ ground divider**, then TMUX1511 S. Both resistors are ±0.1%, 25 ppm/°C. Each TMUX D drives its MCU ADC net with **47 kΩ pulldown and 1 nF C0G**. Including a conservative ±0.2% resistor envelope for initial tolerance and temperature drift, this hard divider bounds a 5.75 V buffer excursion to **≤3.456 V** at S when the receiving rail is absent, below the 3.6 V recommended powered-off input ceiling without depending on Schottky forward drop. With the switch on and 47 kΩ connected, the nominal post-buffer factor is 0.592437; AO gives **1.503198 V at 10 V**, and the nominal 0.5 A/300 CS case gives **0.648853 V**. Negative transients remain invalid samples and require oscilloscope verification of stress limits; the circuit does not reinterpret them as a valid below-zero output.

| TMUX1511 PW pin | Connection |
|---|---|
| 1 SEL1; 4 SEL2 | `READBACK_ENABLE`, separate 10 kΩ pulldowns |
| 2 S1 → 3 D1 | Buffered AO divider → `AO_READBACK` |
| 5 S2 → 6 D2 | Buffered CS divider → `DO_CS_ADC` |
| 7 GND; 14 VDD | `MAIN_GND`; `3V3_MCU_ANA` with 1 µF and 100 nF |
| 8 D3; 9 S3; 10 SEL3; 11 D4; 12 S4; 13 SEL4 | `MAIN_GND`, unused channels disabled |

I treat the specified 2 µA off leakage through 47 kΩ as a **94 mV uncertainty budget** while off, not a valid measurement. The independent output divider/clamp is upstream of the isolator; there is no clamp into the MCU rail before it. I calibrate both readback paths separately and use status plus a tolerance window to diagnose disagreement. The 47 kΩ/1 nF node needs a long ADC sample time and a discarded first conversion; I measure full-chain settling before selecting firmware timing. [TMUX1511 sections 5–6 and Powered-Off Protection](https://www.ti.com/lit/ds/symlink/tmux1511.pdf).

## Reproduced checks and remaining gates

I ran [analog_checks.py](../calcs/analog_checks.py) with ngspice 46 and TI's unmodified OPAx197 macromodel, downloaded from [TI sboma34](https://www.ti.com/lit/zip/sboma34). The model is external rather than redistributed. [ao_model_results.json](../calcs/ao_model_results.json) records its SHA-256, source, assumptions and numerical results. Six typical transient cases use 100 pF, 1 nF and 10 nF cable loads, 600 Ω and 3.9 kΩ feedback paths plus 4.7 kΩ externally, 12.5 Ω main switch resistance, 100 Ω terminal resistance, and 1 nF local compensation. The worst simulated 1-to-9 V step overshoot is **2.889%**, and all six are within 10 mV of their final value by 500 µs. These runs verify typical amplifier dynamics with fixed switch resistances; they do not simulate switch transitions, fault pulses, full component tolerances, PCB parasitics or hardware.

I reproduce arithmetic with `python docs/calcs/analog_checks.py`. To repeat the typical vendor runs, I pass `--library`, `--model` and `--code-models` paths for the installed ngspice shared library, downloaded `OPAx197.LIB`, and ngspice code-model directory. I retain the selected 1 nF compensation because this limited model supports it; the finished board must still pass the measured load/cable sweep.

Before I call the analog sheet ready for manufacture, I close these explicit gates:

- Qualify the selected AO pulse resistors and driver clamps over the full fixture temperature range; the fixed circuit's measured ±30 V AO fault envelope is not yet established.
- Preserve exact capacitor bias curves and confirm reference minimum capacitance, VFP output maximum capacitance and the selected bleeder/bulk shutdown bounds.
- Check library symbols and footprint pins, then inspect the captured netlist against these tables. Capture comparison is separate from component-selection arithmetic.
- Measure threshold-rail start/fall, ADC AVDD during power loss, loop reset/recovery and fault currents with current-limited fixtures.
- Measure factory calibration residuals and drift, AO cable/load settling, and readback clamp/settling behavior over the selected 0–50 °C envelope.

I reserve **15 mA from 15V_ANA**, **3 mA from VNEG**, and **12 mA from 5V_FIELD for the readback buffer/reference branch**, in addition to the ADC/DAC and LM7705 budgets on the power sheet. A shorted AO amplifier can exceed the boost's 25 mA service capacity until protection and the hardware disconnect respond; I make no continuous-short power claim from the steady-state budget.
