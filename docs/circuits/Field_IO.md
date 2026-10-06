# Field I/O circuits

I use four isolated digital inputs, four monitored high-side outputs including one bounded PWM channel, two dry-contact relays, and two independently isolated communication ports. This document fixes the circuit connections and initial test limits before schematic capture. The selections in [field_io.json](../components/field_io.json) are planned component quantities, not a released assembly BOM. I will compare every symbol pin and land pattern with the manufacturer's drawing during capture.

## Power and control boundaries

`MAIN_GND` is the protected supply return. `LOAD_RETURN` joins it at the load connector return region; I keep actuator current out of the measurement and MCU return paths. The external 12/24 V supply powers the controller; USB carries data and does not power the board. `3V3_FIELD_LOGIC` powers the local field-side control logic and the controller sides of the isolators. Field and MCU rails can still rise or fall at different times, so I retain the receiving-domain buffers and hardware-gated command nets below.

| Interface to the control sheet | Direction at this sheet | Default when field logic is absent or disarmed |
|---|---|---|
| `DI1_FIELD`, `DI2_FIELD`, `DI3_FIELD`, `DI4_FIELD` | Output through the MCU sheet's receiving-domain buffers | MCU input inactive |
| `DO1_GATED`…`DO4_GATED` | Input | Low |
| `DO_CS_SEL_L`, `DO_CS_SEL_H` | MCU selection inputs | Low |
| `DO_DIAG_EN` | Qualified hardware-health input; no MCU enable command | Low |
| `DO_FAULT_N_FIELD` | Open-drain output | Pulled up only to `3V3_FIELD_LOGIC`; receiving buffer and conditioned controller-domain fault input clear ARM |
| `DO_CS_RAW` | Analog output | Routed to the protected divider and ADC isolation on the analog sheet |
| `RELAY1_GATED`, `RELAY2_GATED` | Input | Low |
| `RS485_TX_FIELD`, `RS485_DIR_GATED` | Input | TX high; direction low |
| `RS485_RX_FIELD` | Output | Receiving-domain buffer on MCU sheet |
| `CAN_TX_FIELD`, `CAN_RX_FIELD` | Input/output | TX high, representing recessive CAN; receiving-domain buffer owns RX isolation |
| `FIELD5V_VALID` | Input | Low; separately drives each isolated converter through 22 kΩ |

The MCU, watchdog, reset, field-health and arm gates are defined on the control sheet. `FIELD5V_VALID` is the controller-domain hardware combination `FIELD_OK AND ADC5_OK`, independent of the arm state; it permits converter startup after the protected input and filtered field 5 V rail are valid. I do not connect a field-powered status signal directly to an unpowered MCU pin. The analog current-sense protection is specified in [Analog.md](Analog.md).

## Four isolated digital inputs

I select two `ISO1212DBQR` receivers. Both channels of each receiver share `DI_COM`; the four input terminals are one field group. `DI_COM` has no intentional connection to `MAIN_GND`, the bus references, or USB ground. The receiver derives its field-side operating power from the active input itself. I use these as sinking inputs for a sensor or switch that applies a positive voltage relative to `DI_COM`.

For each channel, I connect terminal `DIx` through a 100 Ω, ±1%, 0.25 W MELF threshold resistor to `DIx_SENSE`. A 562 Ω, ±1%, 0603 resistor connects `DIx_SENSE` to `DIx_IN`. The 1 nF, ±5%, 50 V C0G input capacitor connects **between `DIx_SENSE` and `DI_COM`**, following the manufacturer's input network. Each output uses a 100 Ω series resistor and a 1 nF C0G capacitor to `MAIN_GND` at the buffered control-sheet input. Each receiver has 100 nF directly across VCC1/GND1.

| ISO1212 physical pin | Connection on each receiver |
|---|---|
| 1, 8 GND1 | `MAIN_GND` |
| 2 VCC1; 3 EN | `3V3_FIELD_LOGIC`; EN permanently high while powered |
| 4 OUT1; 5 OUT2 | Receiver A: `DI1_FIELD`, `DI2_FIELD`; receiver B: `DI3_FIELD`, `DI4_FIELD`, through the output RC |
| 6, 7 NC | Explicit no-connect |
| 9 FGND2; 14 FGND1 | `DI_COM` |
| 10 IN2; 11 SENSE2 | Channel 2 sense network |
| 15 IN1; 16 SENSE1 | Channel 1 sense network |
| 12 SUB2; 13 SUB1 | Separate 2 × 2 mm floating copper patches; neither patch joins any ground or the other SUB pin |

My nominal threshold estimate is about 8.48 V rising and 7.33 V falling using TI's design equations. The datasheet's RTHR=0/1 kΩ threshold table permits linear interpolation: the calculated upper rising threshold at 100 Ω is 8.79 V. With the resistor tolerance and a conservative 2.75 mA current bound, I reserve about 40 mV more and treat **8.83 V** as the design estimate. The interpolated lower falling threshold is about 6.72 V. I therefore specify ON at 9–30 V and OFF at 0–5 V; 5–9 V is the transition region. These calculated limits require a threshold sweep before release; they do not establish IEC compliance. I do not substitute the typical 2.2–2.47 mA current range for the **2.75 mA maximum** applicable up to 30 V.

The DI voltage is the external signal relative to `DI_COM`, independently of controller power. At the 9 V power-input endpoint my protected `VFIELD` may be only 8.4 V, so I do not use that rail or its load output as a guaranteed 9 V DI stimulus. I perform output-to-input loopback at 12/24 V with the actual terminal high level verified.

At 30 V the conservative input power is 82.5 mW per channel; the 100 Ω resistor dissipates less than 0.8 mW in steady state. The MELF body provides pulse tolerance; its selection alone does not establish surge immunity.

I reserve **four DNP bidirectional TVS sites, one from each DIx_SENSE to DI_COM after the 100 Ω threshold resistor**, following ISO1212 Figure8-10 for a fast small-RTHR network. SMBJ33CA-E3/52 is a candidate, not an approved population: its catalog clamp is waveform/temperature dependent and its capacitance is only typically characterized. Before fitting it I define pulse source/energy/repetition, check clamp/overshoot and resistor survival, and rerun DI thresholds and the 20 kHz timing with the actual capacitance, source and cable. No shunt or return crosses into MAIN_GND or either bus reference. The IC's ±60 V field-pin stress limit does not establish assembled-board DC/transient withstand, and a fitted bidirectional TVS changes negative-voltage behavior. [ISO1212 §8.2.1.2.5, Figures8-9/8-10](https://www.ti.com/lit/ds/symlink/iso1212.pdf), [candidate SMBJ family](https://www.vishay.com/docs/88392/smbj.pdf)

For DI1 I allocate a 20 kHz, 50% duty-cycle input: 25 µs high and 25 µs low, with a source that settles to at least 9 V and at most 5 V at the connector. The input RC has a nominal 100 Ω × 1 nF = **0.100 µs** time constant; the output RC also has **0.100 µs**. With source impedance ≤100 Ω and ≤300 pF cable capacitance, I allow 2 µs for both filters to settle, including component tolerances. The initial DI cable is ≤3 m. TI specifies 140 ns maximum rising propagation and 15 ns maximum falling propagation under its stated edge conditions. I keep the timer's digital filter at no more than 1 µs and leave EN continuously asserted. This comfortably fits a 25 µs phase on paper. I will confirm pulse width, missed-edge count, and noise response with the selected cable and input source. Firmware debounce for DI2–DI4 is separate from DI1's pulse capture. [ISO1212 datasheet, sections 4, 5.9–5.10 and 8.2.1](https://www.ti.com/lit/ds/symlink/iso1212.pdf).

## Four monitored load outputs

I select version B, `TPS4H160BQPWPRQ1`, so that one analog CS pin multiplexes the four channel currents. The device takes `VFIELD` and `MAIN_GND`; all paired power and output pins are connected. I put 100 nF/50 V and 10 µF/50 V bypass capacitors beside VS. The exposed pad connects to `MAIN_GND` with thermal vias.

My external input fixtures remain **9–30 V at the power connector**. The post-protection high-side supply planning range is **8.4–30 V at VFIELD**: at a 9 V connector/full-load fixture I require at least 8.4 V after the fuse, reverse-protection and eFuse path, a total drop no greater than 0.6 V. I measure that drop before accepting the low-voltage endpoint. An 8.4 V supply remains above this switch's 4 V operating minimum and the 6.5 V supply boundary for its full current-sense linear range. Output-terminal voltage is lower again because of switch and blocking-diode drops. [TPS4H160-Q1 sections 6.3 and 6.5](https://www.ti.com/lit/ds/symlink/tps4h160-q1.pdf).

| TPS4H160 version B pin | Net or support circuit |
|---|---|
| 1, 12 GND; exposed pad | `MAIN_GND` |
| 2, 19, 24 NC | Explicit no-connect |
| 3, 4, 5, 6 IN1…IN4 | `DO1_GATED`…`DO4_GATED`, each with 100 kΩ local pulldown |
| 7 SEH; 8 SEL | `DO_CS_SEL_H`, `DO_CS_SEL_L`, each with 100 kΩ local pulldown |
| 9 FAULT | `DO_FAULT_N_FIELD`, 10 kΩ pullup to `3V3_FIELD_LOGIC` |
| 10 CS | `DO_CS_RAW`; 1.21 kΩ, ±1%, to `MAIN_GND`; protected analog-sheet readback branch |
| 11 CL | 2.87 kΩ, ±1%, to device ground |
| 13 THER | 10 kΩ to `3V3_FIELD_LOGIC`; latched thermal-shutdown selection when operational |
| 14 DIAG_EN | `DO_DIAG_EN`, 100 kΩ pulldown |
| 15/16 OUT4; 17/18 OUT3; 25/26 OUT2; 27/28 OUT1 | `DO4_SW`…`DO1_SW` |
| 20–23 VS | `VFIELD` |

For each channel I connect `DOx_SW` to the **anode** of an `STPS2H100A` blocking diode; its **cathode** connects to terminal `DOx`. A second `STPS2H100A` has **anode at `LOAD_RETURN` and cathode at terminal `DOx`**, so a disconnected high-side switch still leaves a local inductive recirculation path. The freewheel diode is on the terminal side of the blocking diode. I put this loop at the connector and route its return directly to the load return region. The blocking diode limits positive terminal backfeed into the high-side switch and supply; its reverse leakage remains finite. This arrangement does not promise survival of an arbitrary negative DC terminal miswire. [STPS2H100 ratings and package](https://www.st.com/resource/en/datasheet/stps2h100.pdf).

I fit a **10 kΩ, ±1%, 0.25 W 1206 `RC1206FR-0710KL` bleeder from each `DOx_SW` to MAIN_GND**, before the blocking diode. It drains the internal output node even when the terminal load is unplugged or isolated by that diode. Each bleeder dissipates 90 mW nominal at 30 V; the four add 12 mA and 360 mW nominal at full DC output. Including ±100 ppm/°C drift over 0–50 °C, the resistor minimum is 9.875 kΩ, giving **3.038 mA and 91.14 mW per bleeder**. I reserve their current separately in the input budget. I fit no output-to-supply pullup for off-state open-load detection. I do not use a capacitor on `DOx_SW`; I constrain its total internal/PCB capacitance to **≤10 nF** as a planning and qualification limit. The blocking diode prevents terminal capacitance from simply becoming the same discharge node. I leave accessible scope pads at each `DOx_SW`. [Exact YAGEO resistor reference](https://yageogroup.com/component-documentation/download/specsheet/RC1206FR-0710KL).

The off-state fault comparator reports an output that remains near VS, with a **300 µs minimum deglitch time** and a 1.6–2.6 V difference threshold. I use the 2.6 V end to conservatively calculate when an unloaded node leaves that condition. With the largest 10.125 kΩ bleeder, 10 nF total capacitance, an assumed **≤100 µA net source leakage while IN is low**, and a 90 µs release allowance, the 8.4 V VFIELD corner takes approximately **134 µs**; higher voltages are faster. The capacitance, release allowance and diagnostic-enabled leakage are explicit implementation/measurement constraints, not extra datasheet guarantees. I require **IN falling edge to `VS−DOx_SW ≥2.6 V` within 150 µs** at 8.4/9/12/24/30 V at the switch supply, all initial loads and 0–50 °C, leaving margin to the fault deglitch minimum. Connector fixtures remain 9/12/24/30 V and include the measured protection-path drop. If this fails I change the discharge/timing circuit before enabling PWM; I do not hide it by masking FAULT. Unconnected, never-energized and previously energized channels are all tested. The bleeder makes a defined off node; it does not establish precision open-load detection. [TPS4H160-Q1 sections 6.5 and 7.3.5–7.3.6](https://www.ti.com/lit/ds/symlink/tps4h160-q1.pdf).

The nominal external limit is `0.8 V × 2500 / 2870 Ω = 0.697 A` per channel. Combining the stated ±15% IC accuracy with ±1% resistor tolerance gives approximately **0.586–0.809 A**, under the datasheet's overload conditions at 13.5 V; the accuracy specification only applies when overload exceeds 1.5 times the set limit. I use 0.5 A as the initial continuous load limit, not the trip point. A short can still dissipate roughly supply voltage × limited current until thermal protection responds. I will test that with a current-limited supply and one channel at a time before testing four loaded channels.

The analog sheet's 56 kΩ/68 kΩ divider feeds a field-powered OPA2320 buffer, so it loads CS by about 124 kΩ. In parallel with 1.21 kΩ, that gives a nominal **1.1983068 kΩ effective burden**. Using the nominal 300:1 sense ratio, 0.5 A produces about **1.99718 V raw CS** and **0.6488 V at the MCU ADC**, including the buffered 1 kΩ/1.5 kΩ divider, 47 kΩ receiving pulldown and illustrative 2 Ω TMUX1511 on-resistance. The CS fault voltage can reach 6.5 V: the unprotected divider would produce 3.565 V before tolerance, so the analog sheet clamps that input and the buffered output independently. The 1 kΩ/1.5 kΩ divider also keeps the switch-side input below 3.6 V when the MCU is off: at a conservative 5.75 V buffer excursion and ±0.2% divider envelope covering initial tolerance and 0–50 °C drift, it remains at or below 3.456 V. At a 5.25 V buffer level with the MCU powered, the nominal ADC level is about 3.110 V. The analog sheet defines the clamped fault behavior and calibration. I retain the downstream independent clamp and receiving-domain analog isolation; the raw CS pin never goes directly to the MCU. At 0.5 A the datasheet's ±3% sense accuracy is specified at 13.5 V, while accuracy becomes much poorer at small currents. This is load diagnostics, with calibration and separate fault coding, rather than a precision current meter.

| SEH | SEL | Selected channel |
|---|---|---|
| 0 | 0 | DO1 |
| 0 | 1 | DO2 |
| 1 | 0 | DO3 |
| 1 | 1 | DO4 |

I drive `DO_DIAG_EN = FIELD5V_VALID AND FIELD3V3_OK` through a field-powered hardware gate, independently of MCU, reset and ARM. Firmware cannot disable fault reporting while the field supplies are valid. Firmware waits at least 200 µs after a sense-channel change and 400 µs after enabling an on/off output before collecting an averaged sample; I will measure settling against these starting allowances. FAULT is global across all four channels, regardless of the CS selection. Its conditioned receiving-domain signal participates in the asynchronous ARM-clear path, while firmware records the arm state, CS selection and commands around a fault. With the series output diode I do not promise reliable off-state open-load detection without a separate terminal test circuit. THER selects the IC's thermal-latch mode, but that latch clears when INx toggles, including a normal PWM edge. The external ARM latch therefore holds every actuator command off after a DO fault, even if the IC's own fault subsequently clears; I require a fresh authorized recovery. The device's thermal-swing behavior can still retry before fault inhibition takes effect. [TPS4H160 version B diagnostics and thermal recovery, sections 7.3.5–7.3.6](https://www.ti.com/lit/ds/symlink/tps4h160-q1.pdf).

My first fixture uses 24 V and a 48 Ω, at least 25 W resistive load per channel; the blocking diode makes actual current slightly below 0.5 A. I then test a 12 V or 24 V coil with **measured current ≤0.5 A, inductance ≤100 mH, and stored energy ≤12.5 mJ** (`L I²/2`). I start at one turn-off per second, with cable length ≤1 m. I measure the diode and switch temperatures, negative terminal excursion, supply disturbance and current decay before expanding the duty cycle or load energy. I do not infer allowable inductive energy from the diode's 2 A average-current rating. The bench supply's 4 A fault-test setting is separate from the board's **3 A continuous input target**. Simultaneous operating loads must meet the 3 A target, including controller consumption; 0.5 A remains the maximum instantaneous load current on every channel.

### DO3 PWM power control

I use the existing DO3 high-side path for low-frequency PWM: the controller rapidly switches it on and off to vary average load power. DO1, DO2 and DO4 remain on/off outputs. The initial PWM envelope is **100 Hz, 10–90% command duty**, with separate steady OFF and steady ON modes. I start with resistive loads; a suitably rated resistor-limited LED assembly is a second fixture only after I verify that assembly's inrush, dimming behavior and temperature. Bare LEDs, electronic loads with unknown input capacitance, motors and proportional solenoids are outside this initial PWM fixture. A 100 Hz result does not establish flicker-free lighting or compatibility with an arbitrary fan or LED driver.

`DO3_CMD` uses **PE9, LQFP100 pin 40, TIM1_CH1 AF2**. TIM2 still owns DI1 pulse acquisition. I explicitly select a 144 MHz TIM1 kernel clock with APB2 prescaler 1, PSC=143 and ARR=9999: a 1 µs tick and 10 ms period. PWM mode 1 is active high; CCR1=1000…9000 covers the initial duty window. I preload duty changes for a period boundary. The existing field-powered `PERMISSION` AND gate, with Ioff protection and defined pulldowns, remains between the timer output and TPS IN3, so loss of health, reset, watchdog permission, conditioned DO fault, or ARM overrides PWM independently of software. On disarm or recovery I stop TIM1, disable its channel and main output, clear the compare/queued command and drive PE9 low. Recovery requires READY, a fresh ARM with zero commands, then a separate fresh SET. An accepted guarded SET may change static/PWM mode while ARMED: I first validate the entire request, stage PE9 low with timer/channel/main output disabled, initialize the new GPIO/timer state, and enable only the accepted new state through the existing permission gate. The finite low interval and first pulse must be bounded and measured; this transition does not generate a new ARM edge or resume stale timer state. Transactional validation does not imply physically simultaneous output edges. Steady OFF/ON use a stopped timer and a low/high GPIO behind the same permission gates. Clearing a fault never resumes an old PWM setting. [STM32G474 pin and alternate-function tables 12–13](https://www.st.com/resource/en/datasheet/stm32g474ve.pdf).

The TPS4H160 timing table specifies 90 µs maximum on/off delay, 0.1 V/µs minimum 10–90% slew, ±50 µs delay matching, 150 µs maximum CS rise settling, and 50 µs maximum sense-selection settling under its stated test conditions. I use a deliberately conservative **full-swing** 30 V / 0.1 V/µs estimate of 300 µs plus 90 µs delay: 390 µs per edge. The shortest commanded on or off interval is 1000 µs, leaving 610 µs after this planning estimate. These timing specifications were taken at 13.5 V, 0.5 A and 5 V logic; CS settling was tested with a 2 A limit. My 8.4–30 V post-protection supply, 3.3 V logic and approximately 0.7 A limit therefore still need measured timing and telemetry qualification. [TPS4H160-Q1 section 6.6 and PWM example in section 8.2](https://www.ti.com/lit/ds/symlink/tps4h160-q1.pdf).

I select DO3's current-sense channel at least 200 µs before its rising command edge, keep diagnostics enabled, and initially collect samples only **600–800 µs after that edge**. A sample arriving late, spanning the falling edge, taken during a fault, or collected before analog/readback health is valid is discarded. The other three channels use their existing settling allowances in the remaining frame time. I report DO3's settled **on-state driver current**, sample age, duty and validity separately. Driver current includes the bleeder, up to about 3.038 mA in this envelope; an estimated external load current must account for that path and its uncertainty. I do not label the sample average load current, off-state leakage, or a closed-loop current regulator. For the qualified resistor fixture only, duty times estimated on-state load current is an approximate average; finite edges and delay mismatch change the actual result, especially at low duty. I average valid samples across frames rather than promising a faster current-report rate than the qualified acquisition allows.

I check pulse shape and heat using [pwm_checks.py](../calcs/pwm_checks.py), an analytical piecewise-linear model of delayed rising/falling ramps. The model uses documented timing assumptions, rather than a manufacturer transistor model or measured PCB behavior. At 30 V, 0.5 A external load plus the worst-envelope bleeder current, 100 Hz, 300 µs rise and fall, the constant-current overlap estimate is approximately **0.453 W** on the PWM channel. With three 0.5 A continuous channels and DO3 at 90%, including bleeder current, the 0.28 Ω hot-resistance conduction estimate is approximately **0.276 W total**, before IC operating power and parasitic losses. These are screening estimates; the layout, thermal vias, ambient temperature and actual waveforms determine the measured result. I retain the four-channel full-current power budget plus bleeder current because DO3 also has a steady ON mode. [TI SLVAF10, timing, thermal and diagnostics methods](https://www.ti.com/lit/pdf/slvaf10).

The existing series blocking diode and terminal-side freewheel diode stay in place. They add voltage drop and diode heat; the freewheel path produces slow inductive decay and does not establish PWM solenoid performance. I do not increase channel current based on reduced duty. For a 30 V resistor fixture I use **at least 60 Ω**, suitable pulse/continuous dissipation and a measured peak current no greater than 0.5 A; I do not reuse the 24 V / 48 Ω fixture at 30 V. I qualify duty/frequency, on-state telemetry, temperature and shutdown at 9/12/24/30 V connector input and 0–50 °C, including the 8.4 V post-protection corner, other outputs loaded and PWM frozen high. Watchdog/health removal and DO fault assertion must inhibit the command. I also check for nuisance FAULT pulses during normal PWM; I do not mask a global fault to hide them. Resistive-terminal decay and any retained energy are measured separately.

## Two SPDT dry-contact relays

I select two `G5Q-1 DC5` relays, standard SPDT, with 5 V coils. A `PMV30UN2R` SOT23 MOSFET drives each coil: gate pin 1 receives `RELAYx_GATED` through 100 Ω with a 100 kΩ gate-source pulldown, source pin 2 joins `MAIN_GND`, drain pin 3 joins coil pin 5. Coil pin 1 joins `5V_FIELD`. A suppression `STPS2H100A` connects anode to coil pin 5 and cathode to coil pin 1. I apply steady coil voltage; this selection is not the -PW relay variant.

| G5Q-1 physical pin | Connection |
|---|---|
| 1, 5 | Coil positive and MOSFET drain, respectively; the relay coil itself has no polarity |
| 2 | `RELAYx_COM`, connector pin 1 |
| 3 | `RELAYx_NO`, connector pin 2 |
| 4 | `RELAYx_NC`, connector pin 3 |

I checked this arrangement against the **bottom-view** manufacturer drawing: pin 2 is the moving common and rests against pin 4 when de-energized. I will make the footprint's top-view transformation explicit in the library review.

The SPDT coil is **80 mA nominal**, 63 Ω ±10% at 23°C, approximately 400 mW. It is not the 40 mA SPST coil. At 5.25 V, minimum room-temperature resistance implies 92.6 mA per coil; I reserve 210 mA for both to cover the initial 0–50°C fixture and driver tolerances. Wider cold-temperature use requires a revised coil-current budget. The MOSFET has a 20 V rating and an on-resistance maximum of 43 mΩ at VGS=2.5 V, 25°C, giving ample coil-drive margin. Suppression extends relay release time, which I will measure. I specify the board's contacts at **30 VDC, 1 A maximum resistive** for both NO and NC. The contact nets remain independent of board power and ground. [Current G5Q production information](https://components.omron.com/sg-en/products/relays/G5Q), [manufacturer coil and terminal drawing](https://components.omron.com/eu-en/datasheet_pdf/J155-E1.pdf), [PMV30UN2 datasheet](https://assets.nexperia.com/documents/data-sheet/PMV30UN2.pdf).

The G5Q contact specification also lists a **10 mA at 5 VDC P-level reference**, measured under its stated 120 operations/min condition. That is not a universal guaranteed minimum switching load. I do not promise reliable tiny dry-circuit/2–3 mA sensing contacts with this power relay; such use needs its own contact-reliability qualification or a suitable signal-relay variant. [G5Q characteristics, p3](../../references/datasheets/G5Q.pdf).

## Isolated RS-485 / Modbus RTU

I select `ISO1410DWR`, a half-duplex 500 kbps transceiver, and use 9600–115200 baud for the first fixture. I join DE and active-low RE on `RS485_DIR_GATED`: low receives; high transmits. A 100 kΩ pulldown at that node makes reset receive-only. `RS485_TX_FIELD` has a 10 kΩ pullup to `3V3_FIELD_LOGIC`.

| ISO1410DWR pin | Net |
|---|---|
| 1 VCC1; 2/8 GND1 | `3V3_FIELD_LOGIC`; `MAIN_GND` |
| 3 R | `RS485_RX_FIELD` |
| 4 /RE; 5 DE | `RS485_DIR_GATED` |
| 6 D | `RS485_TX_FIELD` |
| 7, 10, 11, 14 NC | Explicit no-connect |
| 9/15 GND2; 16 VCC2 | `RS485_REF`; `5V_RS485_ISO` |
| 12 A; 13 B | Non-inverting A and inverting B through the optional choke/bypass region to connector pins 1/2 |

I provide 100 nF on each supply and 1 µF beside the bus-side 100 nF. A 120 Ω, ±1%, 0.25 W resistor across A/B is enabled through a two-pin termination jumper. The termination is on the connector side of the choke; only the two physical ends of a cable are terminated.

The receiver has true failsafe behavior for idle, open and shorted bus states. **External bias is DNP by default.** I reserve two 249 Ω, ±1%, 0.25 W resistors for optional A-to-isolated-5-V pullup and B-to-RS485_REF pulldown at one chosen bus location. With two 120 Ω end terminations, nominal idle differential is `5 × 60 / (249+249+60) = 0.538 V`. At 4.75 V, with unfavorable ±1% tolerances, it remains about **0.502 V** before extra receiver loading. If I populate bias, I confirm that no adapter or other node also supplies it and check driver loading with that exact network. My initial two-node fixture does not need these resistors. [ISO1410 failsafe behavior and physical pins](https://www.ti.com/lit/ds/symlink/iso1410.pdf).

For each line I select a **Vishay `SMBJ8.5CA-E3/52` bidirectional TVS** to `RS485_REF`, at the connector. It has 8.5 V standoff and a 14.4 V maximum clamp under its 25°C rated-pulse condition. ISO1410's bus absolute limit is ±18 V, so I constrain my port common-mode operating target to **−7 to +7 V** relative to RS485_REF. This TVS does not preserve the full +12 V RS-485 common-mode window. Temperature, trace-inductance overshoot and applied transient energy still need measurement; I do not claim an IEC surge result or continuous 24/30 V miswire survival. I use a reference conductor between the two isolated bus references. [Vishay SMBJ table and pulse conditions](https://www.vishay.com/docs/88392/smbj.pdf).

The optional common-mode choke is `ACT45B-510-2P-TL003`, DNP initially, with two populated 0 Ω bypass links. If I fit it, I remove both bypasses. I will verify the manufacturer's paired winding map when creating its custom symbol and footprint; I do not assign a generic four-pad winding order. I keep A/B together with matched short routes and compare waveform quality with and without the choke before adopting it. [TDK choke specifications and terminal drawing](https://product.tdk.com/info/en/catalog/datasheets/cmf_automotive_signal_act45b_en.pdf).

The first cable is a 120 Ω twisted pair, ≤5 m, with a separate reference conductor and no star branches. I use two nodes and two end terminations, then test 9600, 19200, 38400, 57600 and 115200 baud. Stub length starts at ≤0.1 m. Cable length, node count and data rate expand only after error-count and waveform results.

## Isolated CAN / CAN FD

I select the **8-pin DWV** part `ISO1042DWVR`; this pin map must not be used for a 16-pin DW package. It has no enable or standby pin. Its transmit input is pulled high with 10 kΩ so reset is recessive. `FIELD5V_VALID` removes its isolated bus supply when the protected input or field 5 V health is invalid; I verify the resulting shutdown waveform and externally connected bus behavior.

| ISO1042DWVR physical pin | Net |
|---|---|
| 1 VCC1; 4 GND1 | `3V3_FIELD_LOGIC`; `MAIN_GND` |
| 2 TXD; 3 RXD | `CAN_TX_FIELD`; `CAN_RX_FIELD` |
| 5 GND2; 8 VCC2 | `CAN_REF`; `5V_CAN_ISO` |
| 6 CANL; 7 CANH | Through choke/bypass region to CAN connector pins 2/1 |

I provide 100 nF at each supply and 1 µF on the bus side. Split termination uses two **60.4 Ω, ±1%, 0.25 W** resistors from CANH and CANL to `CAN_TERM_MID`, with 4.7 nF/50 V C0G from that midpoint to `CAN_REF`. Two matching two-pin jumpers disconnect **both bus ends** of the split network; both jumpers are either installed or removed. The resulting DC termination is 120.8 Ω. The capacitor adds no DC reference connection to the pair.

A `PESD2CANFD24V-T` TVS array sits beside the connector: pins 1/2 to CANH/CANL, common pin 3 to `CAN_REF`. Its 24 V standoff and 42 V maximum clamp at 1 A, 8/20 µs, 25°C sit within the transceiver's ±70 V bus absolute limit under that stated condition. The array is a transient protector; it does not make a 24/30 V wiring fault functional, and trace overshoot and energy remain test conditions. I reserve the same optional DNP choke with two populated 0 Ω bypasses as on RS-485. [ISO1042 DWV pins and bus limits](https://www.ti.com/lit/ds/symlink/iso1042.pdf), [PESD2CANFD24V-T connections and limits](https://assets.nexperia.com/documents/data-sheet/PESD2CANFD24V-T.pdf).

I start with two nodes on ≤5 m of 120 Ω CAN cable, two end terminations, stubs ≤0.1 m and a reference conductor between the isolated bus references. I test classical CAN at 125/250/500 kbps, then CAN FD at **500 kbps arbitration and 2 Mbps data**. These rates require the MCU timing configuration and measured edge margins; the transceiver's maximum data-rate headline alone is not a cable-length guarantee.

## Independent isolated port supplies

I use **two `UCC33421QDHARQ1` modules**, one per port. Their primary return is `MAIN_GND`; the secondary returns are `RS485_REF` and `CAN_REF`. Neither secondary return joins MAIN_GND or the other port. The nominal 5V_FIELD design envelope is 4.90–5.10 V before qualification; the converter's allowable input is 4.5–5.5 V. I allocate a bus-side current budget of **≤180 mA per port** initially and verify supply startup, ripple, rail range and temperature with the actual transceiver load.

| UCC33421QDHARQ1 physical pin | Connection on each port |
|---|---|
| 1 EN/FLT | `FIELD5V_VALID` through its own 22 kΩ; 100 kΩ to MAIN_GND at the pin |
| 2/3 VINP | Local `5V_PORT_INPUT` after the input ferrite |
| 4–8 GNDP | `MAIN_GND` |
| 9 SEL | Directly to that module's raw secondary VCC; selects **5.0 V**, not 5.5 V |
| 10/11 VCC | Raw isolated output |
| 12–16 GNDS | Respective isolated reference |

For each module I put 15 nF/50 V X7R and 10 µF/25 V X7R directly across VINP/GNDP, then 15 nF/50 V X7R and 22 µF/25 V X7R directly across VCC/GNDS. The 15 nF capacitors are 0402 and closest to the pin pairs. The larger capacitors have higher voltage ratings to reduce DC-bias loss; I will check their effective capacitance against TI's load/capacitance calculator rather than equating nominal and effective values.

I select an input and an output `BLM21PG221SN1D` ferrite bead per module (220 Ω at 100 MHz, 2 A, 45 mΩ maximum DC resistance). The output bead is after the module's 22 µF capacitor; 1 µF and the transceiver's 100 nF sit after the bead. The input bead is before both local input capacitors. Grounds remain continuous within each power domain. I do not add a capacitor across an isolation barrier in the initial population. Ferrite behavior, bypass geometry and module emissions require measurement; these are EMI provisions, not a pre-compliance pass.

The 22 kΩ enable resistor meets TI's minimum 18 kΩ condition for the shared EN/FLT pin. With a 3.3 V valid signal, the 22 kΩ/100 kΩ network produces about 2.705 V before pin leakage; even a conservative 10 µA loss leaves about 2.525 V, above the 2.1 V enable threshold. A fault pulls the pin down for 200 µs. I expose each raw fault node as a test point; a direct MCU fault connection is not fitted. Firmware can detect a failed port through communication health and separately qualified rail monitoring. [UCC33421-Q1 connections and application network](https://www.ti.com/lit/ds/symlink/ucc33421-q1.pdf), [Murata bead reference sheet](https://www.murata.com/en-eu/api/pdfdownloadapi?cate=cgsubChipFerriBead&partno=BLM21PG221SN1D).

## Connector schedule

I use manufacturer-matched pluggable headers and screw-terminal plugs. The article numbers below are exact order identifiers. The 3.5 mm MC family is rated 8 A and the 5.08 mm MSTB family 12 A under their manufacturer conditions; my board interface limits above remain lower. I mark pin 1 on copper/silkscreen and label the mating plug from the same view as the board connector. A continuity check on the first fitted pair verifies the drawing-to-harness orientation.

| Interface | Board header / matching plug | Connector pins |
|---|---|---|
| DI1/DI2 and DI3/DI4; two 3-position, 3.5 mm pairs | MC 1,5/3-G-3,5 **1844223** / MC 1,5/3-ST-3,5 **1840379** | 1 DI odd; 2 DI even; 3 DI_COM |
| RS-485; one 3-position, 3.5 mm pair | Same 1844223 / 1840379 | 1 A(+); 2 B(−); 3 RS485_REF |
| CAN; one 3-position, 3.5 mm pair | Same 1844223 / 1840379 | 1 CANH; 2 CANL; 3 CAN_REF |
| DO1/DO2 and DO3/DO4; two 4-position, 5.08 mm pairs | MSTB 2,5/4-G-5,08 **1759033** / MSTB 2,5/4-ST-5,08 **1757035** | 1 DO odd; 2 LOAD_RETURN; 3 DO even; 4 LOAD_RETURN |
| Relay 1 and relay 2; two 3-position, 5.08 mm pairs | MSTB 2,5/3-G-5,08 **1759020** / MSTB 2,5/3-ST-5,08 **1757022** | 1 COM; 2 NO; 3 NC |

The shared selection also provides 2-position MC parts **1844210 / 1840366**, 4-position MC parts **1844236 / 1840382**, and 2-position MSTB parts **1759017 / 1757019** for the analog and power sheets. Those sheets own their fitted quantities. The analog and power pair counts must be reconciled once, rather than duplicated in this sheet's quantities. [Phoenix MC mating table](https://www.phoenixcontact.com/en-us/products/pcb-plug-mc-15-4-st-35-1840382), [MC 3-position header](https://www.phoenixcontact.com/en-de/products/pcb-header-mc-15-3-g-35-1844223), [MSTB 4-position pair](https://www.phoenixcontact.com/en-ca/products/pcb-header-mstb-25-4-g-508-1759033), [MSTB 3-position pair](https://www.phoenixcontact.com/en-us/products/pcb-header-mstb-25-3-g-508-1759020), [MSTB 2-position pair](https://www.phoenixcontact.com/en-fr/products/pcb-header-mstb-25-2-g-508-1759017).

## Capture and bench checks

I will check the bottom-view relay transformation, the exact UCC DHA isolated lead geometry, ISO1042 **DWV** pin numbering, and each choke winding before attaching the footprints. The JSON's project-specific symbol and footprint names are intended library targets where a stock item has not been verified; they do not assert that those assets already exist.

I will first measure all local and isolated rails with output commands disarmed, then confirm hardware shutdown and reset behavior before loading the outputs. DI thresholds and 20 kHz edge counting come next, followed by resistive load/current-readback tests, the bounded on/off inductive fixture, DO3's PWM duty/timing/current/thermal sweep, relay continuity/release measurements, and the two bus fixtures. I test watchdog and health shutdown during PWM and require a fresh command after rearm. I record stimulus, current limit, cable, temperature and waveform alongside each result. No schematic, assembled board or bench result is claimed by this circuit-selection document.
