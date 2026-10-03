# Field I/O circuits

I use four isolated digital inputs, four monitored high-side outputs, two dry-contact relays, and two independently isolated communication ports. This document fixes the circuit connections and initial test limits before schematic capture. The selections in [field_io.json](../components/field_io.json) are planned component quantities, not a released assembly BOM. I will compare every symbol pin and land pattern with the manufacturer's drawing during capture.

## Power and control boundaries

`MAIN_GND` is the protected supply return. `LOAD_RETURN` joins it at the load connector return region; I keep actuator current out of the measurement and MCU return paths. `3V3_FIELD_LOGIC` powers the local field-side control logic and the controller sides of the isolators. It is absent in USB-only service mode. The MCU sheet supplies receiving-domain buffers and the hardware-gated command nets below.

| Interface to the control sheet | Direction at this sheet | Default when field logic is absent or disarmed |
|---|---|---|
| `DI1_FIELD`, `DI2_FIELD`, `DI3_FIELD`, `DI4_FIELD` | Output through the MCU sheet's receiving-domain buffers | MCU input inactive |
| `DO1_GATED`…`DO4_GATED` | Input | Low |
| `DO_CS_SEL_L`, `DO_CS_SEL_H`, `DO_DIAG_EN` | Input | Low |
| `DO_FAULT_N_FIELD` | Open-drain output | Pulled up only to `3V3_FIELD_LOGIC`; receiving buffer owns MCU-domain isolation |
| `DO_CS_RAW` | Analog output | Routed to the protected divider and ADC isolation on the analog sheet |
| `RELAY1_GATED`, `RELAY2_GATED` | Input | Low |
| `RS485_TX_FIELD`, `RS485_DIR_GATED` | Input | TX high; direction low |
| `RS485_RX_FIELD` | Output | Receiving-domain buffer on MCU sheet |
| `CAN_TX_FIELD`, `CAN_RX_FIELD` | Input/output | TX high, representing recessive CAN; receiving-domain buffer owns RX isolation |
| `FIELD5V_VALID` | Input | Low; separately drives each isolated converter through 22 kΩ |

The MCU, watchdog, reset, field-health and arm gates are defined on the control sheet. `FIELD5V_VALID` is the service-domain hardware combination `FIELD_OK AND ADC5_OK`, independent of the arm state; it permits converter startup after the protected input and filtered field 5 V rail are valid. I do not connect a field-powered status signal directly to an unpowered MCU pin. The analog current-sense protection is specified in [Analog.md](Analog.md).

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

At 30 V the conservative input power is 82.5 mW per channel; the 100 Ω resistor dissipates less than 0.8 mW in steady state. The MELF body provides pulse tolerance; its selection alone does not establish surge immunity.

For DI1 I allocate a 20 kHz, 50% duty-cycle input: 25 µs high and 25 µs low, with a source that settles to at least 9 V and at most 5 V at the connector. The input RC has a nominal 100 Ω × 1 nF = **0.100 µs** time constant; the output RC also has **0.100 µs**. With source impedance ≤100 Ω and ≤300 pF cable capacitance, I allow 2 µs for both filters to settle, including component tolerances. The initial DI cable is ≤3 m. TI specifies 140 ns maximum rising propagation and 15 ns maximum falling propagation under its stated edge conditions. I keep the timer's digital filter at no more than 1 µs and leave EN continuously asserted. This comfortably fits a 25 µs phase on paper. I will confirm pulse width, missed-edge count, and noise response with the selected cable and input source. Firmware debounce for DI2–DI4 is separate from DI1's pulse capture. [ISO1212 datasheet, sections 4, 5.9–5.10 and 8.2.1](https://www.ti.com/lit/ds/symlink/iso1212.pdf).

## Four monitored load outputs

I select version B, `TPS4H160BQPWPRQ1`, so that one analog CS pin multiplexes the four channel currents. The device takes `VIN_PROTECTED` and `MAIN_GND`; all paired power and output pins are connected. I put 100 nF/50 V and 10 µF/50 V bypass capacitors beside VS. The exposed pad connects to `MAIN_GND` with thermal vias.

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
| 20–23 VS | `VIN_PROTECTED` |

For each channel I connect `DOx_SW` to the **anode** of an `STPS2H100A` blocking diode; its **cathode** connects to terminal `DOx`. A second `STPS2H100A` has **anode at `LOAD_RETURN` and cathode at terminal `DOx`**, so a disconnected high-side switch still leaves a local inductive recirculation path. The freewheel diode is on the terminal side of the blocking diode. I put this loop at the connector and route its return directly to the load return region. The blocking diode limits positive terminal backfeed into the high-side switch and supply; its reverse leakage remains finite. This arrangement does not promise survival of an arbitrary negative DC terminal miswire. [STPS2H100 ratings and package](https://www.st.com/resource/en/datasheet/stps2h100.pdf).

The nominal external limit is `0.8 V × 2500 / 2870 Ω = 0.697 A` per channel. Combining the stated ±15% IC accuracy with ±1% resistor tolerance gives approximately **0.586–0.809 A**, under the datasheet's overload conditions at 13.5 V; the accuracy specification only applies when overload exceeds 1.5 times the set limit. I use 0.5 A as the initial continuous load limit, not the trip point. A short can still dissipate roughly supply voltage × limited current until thermal protection responds. I will test that with a current-limited supply and one channel at a time before testing four loaded channels.

The analog sheet's 56 kΩ/68 kΩ divider feeds a field-powered OPA2320 buffer, so it loads CS by about 124 kΩ. In parallel with 1.21 kΩ, that gives a nominal **1.1983065 kΩ effective burden**. Using the nominal 300:1 sense ratio, 0.5 A produces about **1.99718 V raw CS** and **0.648853 V at the MCU ADC**, including the buffered 1 kΩ/1.5 kΩ divider and 47 kΩ receiving pulldown. The CS fault voltage can reach 6.5 V: the unprotected divider would produce 3.565 V before tolerance, so the analog sheet clamps that input and the buffered output independently. The 1 kΩ/1.5 kΩ divider also keeps the switch-side input below 3.6 V when the MCU is off: at a conservative 5.75 V buffer excursion and ±0.1% divider corners, it remains at or below 3.453 V. At a 5.25 V buffer level with the MCU powered, the nominal ADC level is 3.1103 V. The analog sheet defines the clamped fault behavior and calibration. I retain the downstream independent clamp and receiving-domain analog isolation; the raw CS pin never goes directly to the MCU. At 0.5 A the datasheet's ±3% sense accuracy is specified at 13.5 V, while accuracy becomes much poorer at small currents. This is load diagnostics, with calibration and separate fault coding, rather than a precision current meter.

| SEH | SEL | Selected channel |
|---|---|---|
| 0 | 0 | DO1 |
| 0 | 1 | DO2 |
| 1 | 0 | DO3 |
| 1 | 1 | DO4 |

I enable diagnostics after field power is valid. Firmware waits at least 200 µs after a sense-channel change and 400 µs after enabling an output before collecting an averaged sample; I will measure settling against these starting allowances. FAULT is global; firmware records the CS selection and output states when a fault occurs. With the series output diode I do not promise reliable off-state open-load detection without a separate terminal test circuit. THER selects latch-off for absolute overtemperature; the device's thermal-swing behavior can still retry. A latched fault clears only after the firmware and hardware arm sequence authorize a retry. [TPS4H160 version B connections, current limits and diagnostics](https://www.ti.com/lit/ds/symlink/tps4h160-q1.pdf).

My first fixture uses 24 V and a 48 Ω, at least 25 W resistive load per channel; the blocking diode makes actual current slightly below 0.5 A. I then test a 12 V or 24 V coil with **measured current ≤0.5 A, inductance ≤100 mH, and stored energy ≤12.5 mJ** (`L I²/2`). I start at one turn-off per second, with cable length ≤1 m. I measure the diode and switch temperatures, negative terminal excursion, supply disturbance and current decay before expanding the duty cycle or load energy. I do not infer allowable inductive energy from the diode's 2 A average-current rating. The protected bench supply is limited to 4 A; simultaneous loads must stay inside that input budget.

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

I select the **8-pin DWV** part `ISO1042DWVR`; this pin map must not be used for a 16-pin DW package. It has no enable or standby pin. Its transmit input is pulled high with 10 kΩ so reset is recessive. Removing its isolated bus supply is the hardware path that disables bus operation in USB-only service mode.

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

I will first measure all local and isolated rails with output commands disarmed, then confirm hardware shutdown and reset behavior before loading the outputs. DI thresholds and 20 kHz edge counting come next, followed by resistive load/current-readback tests, the bounded inductive fixture, relay continuity/release measurements, and the two bus fixtures. I record stimulus, current limit, cable, temperature and waveform alongside each result. No schematic, assembled board or bench result is claimed by this circuit-selection document.
