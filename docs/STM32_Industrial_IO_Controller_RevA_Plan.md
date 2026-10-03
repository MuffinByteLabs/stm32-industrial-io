# STM32 Industrial I/O Controller Rev A Plan

Prepared October 2, 2026.

Build a four-layer STM32 sensor and actuator controller for nominal 12 V and 24 V DC equipment. The board should measure field sensors, switch real loads, control a 0–10 V actuator, communicate through isolated RS-485 and CAN, and report faults. Complete the project with fabricated hardware, dependable firmware, an enclosure, repeatable bench tests, and an evidence-based portfolio case study.

This is a fresh project specification. Its scope comes from the supplied conversation, the supplied Upwork listings, and the engineering choices explained below. The design targets in this document are proposed requirements. Major component capabilities were checked against manufacturer documentation; a schematic, package-specific pin allocation, simulations, layout review, and hardware qualification are still required before the board can be ordered or its performance advertised.

## Why this is the recommended project

Your existing ESP32 plant monitor already demonstrates wireless sensing. This project adds bare-MCU integration, protected field power, precision measurement, load diagnostics, wired communication, four-layer layout, and systematic validation. Those capabilities give you more examples to discuss with clients seeking equipment controllers and sensor interfaces.

The seven supplied files contain 350 listing entries, including duplicates and work outside this project's scope. They do not establish a measured hiring probability. The recommendation is a judgment about complementary portfolio evidence.

| Representative supplied listing | Source location | Relevant evidence this project can provide |
| --- | --- | --- |
| PCB & Schematic Designer for Industrial Control Unit | Pasted text (6)(1).txt, line 570 | STM32, 24 V power, relays, RS-485, analog conditioning, isolation, and manufacturing handoff |
| Hardware engineer: 10-channel current sensor PCB with CAN (STM32) – redesign + 4 prototypes | Pasted text(20261003-003934).txt, line 452 | Protected power, calibrated measurements, CAN, four-layer layout, DIN-rail integration, and tested prototypes |
| ESP32-S3 24V Bus Controller — KiCad Schematic + 4-Layer PCB | Pasted text(20261003-003934).txt, line 1249 | Input protection calculations, switching regulator layout, and a complete editable manufacturing package |
| Mixed-signal sensor PCB design (KiCad or Altium), 4-layer, low-noise analog, all-SMT | Pasted text (2)(6).txt, line 1007 | External ADC integration, analog power, stack-up decisions, and measured analog performance |
| Embedded Systems Engineer needed for PCB Redesign & Firmware Modernisation | Pasted text (6)(1).txt, line 859 | RS-485 networks, feedback inputs, protocol documentation, host stress tests, and validation |
| Complete PCB design (IoT environmental sensor reader) in KiCad, test prototypes, assemble units | Pasted text (4)(1).txt, line 1003 | STM32, industrial sensors, pulse counting, prototype assembly, and physical testing |
| PCB & Schematic Design for Zigbee-Based Commercial LED Lighting Controller | Pasted text (5)(1).txt, line 822 | A 0–10 V output, mixed-signal layout, protection, and complete manufacturing files |
| Embedded Systems Engineer - Vehicle Security Control Unit (Hardware + Firmware) | Pasted text (4)(1).txt, line 155 | Pulse sensing, actuator switching, and explicitly defined fault behavior |

The two 4–20 mA inputs are an industrial interface choice, rather than a feature whose frequency was established by these listings. The exact channel counts are chosen to create a manageable, complete demonstration. The custom lighting-controller listing supports including a 0–10 V output. The condenser listing supplies adjacent fan-interface context, but explicitly asks for an off-the-shelf controller.

The [job-fit review](Upwork_Job_Fit.md) maps each planned capability to finished evidence and coverage limits. Its [saved source excerpts](../references/upwork/README.md) preserve exact titles, short quotations, source lines, and file hashes.

The board will demonstrate general field electronics. Its on/off outputs will not by themselves prove proportional-solenoid control, and its CAN interface will not establish automotive qualification. Keep portfolio claims tied to the loads and tests actually completed.

## The board to build

Use the working project name STM32 Industrial I/O Controller. Give the first PCB revision its own hardware identity and firmware board identifier.

| Function | Rev A scope |
| --- | --- |
| Main controller | STM32G474VET6 directly on the PCB, LQFP100 |
| PCB | Four layers, approximately 140 × 100 mm starting envelope |
| Main supply | Nominal 12/24 V DC; 9–30 V continuous operating target |
| Digital inputs | Four isolated DC inputs sharing a dedicated input common; one supports pulse counting |
| Voltage inputs | Two protected, single-ended 0–10 V inputs |
| Current inputs | Two protected, single-ended 4–20 mA receivers |
| Analog output | One protected 0–10 V output for a high-impedance actuator input |
| Switched outputs | Four diagnosed high-side channels, 0.5 A each simultaneously |
| Relays | Two independent SPDT dry-contact relays, qualified initially for low-voltage DC resistive loads |
| RS-485 | Isolated, half-duplex Modbus RTU |
| CAN | Separately isolated CAN interface supporting classic CAN and CAN FD |
| Service connections | USB-C USB 2.0 full-speed device and 10-pin SWD |
| Reliability | Hardware output gating, reset supervision, external watchdog, fault latching, and command timeout |
| Calibration | Versioned coefficients and configuration stored with CRC and recoverable copies |
| Mechanical integration | Labeled pluggable terminals, mounting points, and an enclosure with an insulated DIN-rail mounting option |
| Demonstration | Real sensor, real DC actuator, analog speed command, wired telemetry, controlled faults, and measured results |

Keep Ethernet, Wi-Fi, Bluetooth, an onboard display, battery charging, GNSS, and a Linux processor for separate projects or later revisions. The first completed release should deliver the functions above. Space and package choices should serve those functions; there is no fixed 100 × 100 mm ceiling or restriction against exposed-pad packages.

## Initial performance targets

These are acceptance goals for engineering and bench qualification. If the hardware misses a target, improve the design or publish a reduced, measured rating.

| Item | Target and qualification condition |
| --- | --- |
| Supply operation | 9, 12, 24, and 30 V DC, including full rated loads |
| Board input current | 3 A continuous design budget; approximately 3.5 A nominal electronic limit subject to tolerance coordination |
| Service power | Up to 5 W total electronics power delivered from the main DC conversion system |
| Digital input OFF | Guaranteed OFF at 0–5 V relative to DI_COM |
| Digital input ON | Guaranteed ON at 9–30 V relative to DI_COM; 5–9 V is the transition region |
| Pulse channel | Count a 20 kHz, 50% duty-cycle, 12/24 V pulse train without lost counts on a specified bench cable |
| Analog acquisition | 1,000 samples/s per input channel; calibrated readings published at 100 Hz |
| Useful sensor bandwidth | Approximately 50–100 Hz after the selected analog and digital filtering |
| Voltage-input accuracy | ±0.2% of the 10 V span, or ±20 mV, after room-temperature calibration |
| Current-input accuracy | ±0.2% of the 16 mA measurement span, or ±32 µA, after room-temperature calibration |
| Temperature accuracy goal | ±0.5% of the same input spans over 0–50 °C after room-temperature calibration |
| Analog output | 0–10 V, 100 Hz command update, load at least 10 kΩ |
| Analog-output accuracy | ±0.5% of 10 V, or ±50 mV, after calibration, including zero and full-scale tests |
| High-side outputs | 0.5 A/channel continuous, all four channels together, at 0–50 °C ambient in the chosen enclosure |
| Output current measurement | Load diagnostics and calibrated reporting; publish measured error rather than a precision-current claim |
| Relay contacts | Initially qualify up to 30 V DC, 1 A resistive, using the specified wiring and terminals |
| Modbus | 9,600–115,200 bit/s; initial release at 19,200 and 115,200 bit/s |
| CAN validation | Classic CAN at 500 kbit/s; CAN FD at 500 kbit/s arbitration and 2 Mbit/s data on a documented short bus |
| Command timeout | Default 1 s; a configurable bounded interval stored in configuration |
| Initial environment | Indoor enclosed bench/equipment prototype, 0–50 °C qualification range |

A 16-bit converter does not establish 16-bit system accuracy. Calibration-source uncertainty, front-end errors, loading, temperature drift, and noise must appear in the measured results.

## System architecture

The sensor return, MCU ground, and main DC return share one main domain. Digital-input common, RS-485 reference, CAN reference, and relay contact circuits are separate domains.

~~~mermaid
flowchart LR
    P["9–30 V DC"] --> IP["Fuse, TVS, blocking FET, eFuse"]
    IP --> VF["Protected field rail"]
    VF --> HS["Four diagnosed high-side outputs"]
    VF --> B["5 V buck"]
    B --> F5["5 V field service"]
    F5 --> R["Two relay coils"]
    F5 --> AP["15 V boost and small negative bias"]
    USB["USB-C"] --> MUX["Logic power selection"]
    F5 --> MUX
    MUX --> MCU["STM32G474VE and logic rails"]
    VI["Two 0–10 V and two 4–20 mA inputs"] --> FP["Analog fault protection and filters"]
    AP --> FP
    FP --> ADC["External 16-bit ADC"]
    ADC --> MCU
    MCU --> DAC["DAC and amplifier"]
    AP --> DAC
    DAC --> AO["Protected 0–10 V output"]
    DI["Four DC digital inputs"] --> ISO["Isolated input receivers"]
    ISO --> MCU
    MCU --> RS["Isolated RS-485"]
    MCU --> CAN["Isolated CAN FD"]
    F5 --> RP["Independent isolated RS-485 supply"]
    RP --> RS
    F5 --> CP["Independent isolated CAN supply"]
    CP --> CAN
    MCU --> G["Hardware output permission"]
    G --> HS
    G --> R
    G --> AO
~~~

The diagram shows functional dependencies. It is not a wiring diagram or a substitute for checking component pin connections.

## Grounds and isolation boundaries

| Domain | Connections | Boundary |
| --- | --- | --- |
| Main ground | DC negative, MCU, ADC returns, analog terminals, load returns, USB ground | One continuous reference system |
| DI_COM | All four digital-input field returns | Group isolation from main ground |
| RS485_REF | RS-485 bus-side transceiver, protection, and dedicated isolated supply | Isolated from main ground and CAN |
| CAN_REF | CAN bus-side transceiver, protection, and dedicated isolated supply | Isolated from main ground and RS-485 |
| Relay 1 contacts | Relay 1 COM, NO, NC | Independent of coil/main domain |
| Relay 2 contacts | Relay 2 COM, NO, NC | Independent of coil/main domain and relay 1 |
| Chassis/shield provision | Cable shields or enclosure bond where the installation requires them | Connection strategy documented separately |

The digital inputs are isolated as a group; the four channels are not isolated from one another. The analog inputs and output are not galvanically isolated. A sensor whose signal return is at another ground potential may require an external isolated transmitter.

USB connects the host computer to main board ground. This must be accounted for when bench instruments and externally powered sensors are connected. A wire joining an isolated reference to main ground removes that isolation in that installation.

Choose isolation components and footprint spacing together. Maintain copper keepouts on every layer across the barriers, and record actual creepage/clearance. Prefer wide-body parts and approximately 8 mm layout separation for the communication barriers where the chosen packages support it. Set the digital-input barrier geometry from its receiver package and the intended low-voltage installation. The finished system rating depends on its weakest component and layout; an IC's dielectric-test rating is not the board's certification.

## Power system

### Main input protection

Use the following order:

1. Pluggable DC terminal rated for at least 5 A under the relevant conditions.
2. Replaceable fuse, selected after startup and fault coordination.
3. Bidirectional raw-input TVS and a deliberately small amount of raw-input capacitance.
4. External reverse-blocking MOSFET and eFuse arrangement.
5. Controlled bulk capacitance on the protected side.
6. Branches to the high-side load switch and the 5 V buck.

A suitable starting point is TPS26632 with its required external blocking FET and support circuitry. This device combines current limiting and startup control with a fixed 35 V maximum output clamp. It does not provide an adjustable overvoltage-cutoff pin in this variant. Its clamp operation has a timeout, so surge energy and safe operating area must be checked. Use a 100 V MOSFET as a starting voltage class, then verify positive and negative stress and gate ratings. [TPS2663 manufacturer datasheet](https://www.ti.com/lit/ds/symlink/tps2663.pdf)

Start TVS evaluation with SMCJ33CA. Its 33 V number is the stand-off rating; its specified clamp can be 53.3 V at the stated pulse current. Final selection requires a defined waveform, source impedance, repetition, and temperature. Raw-input capacitors should initially be 63 V rated, with actual worst-case voltage checked. [Littelfuse SMCJ datasheet](https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_smcj_datasheet?assetguid=37388813-0d6d-4329-969b-1aa8b7614ac1)

Set the final eFuse limit around 3.5 A nominal while allowing 3 A continuous board input. The limit tolerance, fuse curve, connector rating, MOSFET heating, and PCB copper must be evaluated together. Put the large input capacitor after startup control, rather than allowing it to bypass inrush limiting.

The 9–30 V operating specification is separate from fault-survival tests. The initial steady fault targets are reverse connection to −30 V and positive source overvoltage to +40 V, under a documented bench current limit. The output-permission circuit must disarm loads outside the valid operating window. At +40 V the protection may clamp and then disconnect; normal operation is not required.

Transient immunity levels must be frozen before choosing a final surge suppressor. An IEC-style surge level cannot be inferred from the TVS's wattage. The first release should publish the steady-fault and hot-plug results; laboratory surge/EFT/ESD work is a separate qualification milestone.

### Rails and power partition

| Rail | Recommended implementation | Role |
| --- | --- | --- |
| VFIELD | Protected main input | Actuator energy |
| 5V_FIELD | LMR38020 buck, nominal 5.0 V | Field service power, relay coils, isolated supplies, analog auxiliary conversion |
| 5V_SYS | Power-mux output from field 5 V or limited USB VBUS | MCU and essential service electronics |
| 3V3_DIG | TPS62160 buck from 5V_SYS | MCU digital power and digital interfaces |
| 3V3_MCU_ANA | TPS7A20 3.3 V variant from 5V_SYS | MCU analog supply/reference-related support, including USB service |
| 3V3_FIELD_LOGIC | Separate suitable 3.3 V regulator from 5V_FIELD | External ADC digital supply and field-side interface buffers |
| ADC_AVDD | Filtered, qualified 5V_FIELD with defined discharge impedance | Field-only external ADC analog supply |
| DAC supply | Filtered, qualified 5V_FIELD | Field-only external DAC |
| 15V_ANA | TPS55340 boost from 5V_FIELD | Analog protectors and output amplifier |
| Negative analog bias | LM7705 from a suitable field 5 V source | Small negative amplifier rail for the zero-volt output endpoint |
| 5V_RS485_ISO | Independent regulated isolated converter | RS-485 bus side |
| 5V_CAN_ISO | Another independent regulated isolated converter | CAN bus side |

LMR38020 has an 80 V input rating and 2 A output capability. Initially qualify the service system for 5 V at 1 A combined, rather than promising the full regulator rating. Use its data-sheet design procedure to select switching frequency, inductor, compensation-related components, capacitance, and thermal layout. [LMR38020 documentation](https://www.ti.com/product/LMR38020)

The filtered ADC supply must meet its operating range under ripple and transient conditions. A 5 V LDO fed from nominal 5 V cannot be assumed to produce a regulated 5 V output; check headroom before adding one. Separate filtering and return paths should be designed with damping and measured at the ADC pins.

TPS2121 is a power-selection candidate with reverse-current blocking. Its output should supply service logic, rather than the load energy path. USB-only mode must leave relay coils, isolated field supplies, the analog auxiliary rail, and all field outputs inactive. The ADC may lack a valid analog supply or fault-protection supply in this mode, so mark field measurements unavailable rather than reporting plausible numbers. [TPS2121 documentation](https://www.ti.com/product/TPS2121)

Freeze the external ADC/DAC as field-powered devices. Require FIELD_ANALOG_VALID, derived from the relevant rail monitors, before driving their interfaces, accepting acquisition data, or enabling AO. Use powered-off isolation buffers or another verified circuit to prevent USB-powered SPI/control signals from injecting into absent field supplies. Check buffer direction, pull-up domains, reset states, and supply sequencing; firmware flags alone do not prevent electrical backpower.

Keep MCU analog power available in USB service mode. Distinguish it from the external ADC's field-side analog/digital supplies. Check every rail monitor, diagnostic signal, and analog readback against an unpowered MCU as well as normal operation.

Use a regulated isolated supply for each communication port. UCC12050 is one candidate; its regulated output and approximately 500 mW capability must cover the transceiver's worst-case bus drive, termination, temperature, and startup demand. If that budget is insufficient, choose a suitably rated regulated 1 W converter. Avoid relying on the nominal voltage of an unloaded unregulated module. [UCC12050 documentation](https://www.ti.com/product/UCC12050)

TPS55340 can generate the auxiliary positive rail from field 5 V. LM7705 produces a small negative bias near −0.232 V; keep its 5 V source inside the specified range. Both introduce switching activity that must be kept out of the sensitive input paths. [TPS55340 documentation](https://www.ti.com/product/TPS55340), [LM7705 datasheet](https://www.ti.com/lit/ds/symlink/lm7705.pdf)

### Initial power budget

Reserve 2 A for the four load channels and 5 W for service electronics. At 9 V and an assumed 85% conversion efficiency, service input current is 5 W / (9 V × 0.85) = 0.654 A. The combined estimate is approximately 2.65 A before small field overhead, leaving limited headroom below the 3 A board budget.

Use the following service allocation as a planning ceiling, then replace it with worst-case component calculations:

| Service branch | Initial 5 V equivalent allocation |
| --- | --- |
| MCU, digital conversion, LEDs, and service logic | 200 mA |
| ADC, DAC, and quiet analog support | 100 mA |
| Two SPDT relay coils | 160 mA |
| Two isolated communication supplies | 250 mA |
| Analog auxiliary conversion | 200 mA |
| Margin | 90 mA |
| Total | 1,000 mA |

The budget permits approximately 50 mA at 15 V if boost efficiency is about 80%; this is an allocation, not an output rating established by the selected inductor or layout.

Rev A uses externally powered 4–20 mA loops. An onboard sensor-power output is a later addition requiring its own current limit and input-budget allocation.

## MCU integration and resource plan

Use STM32G474VET6 in LQFP100. The family provides USB full-speed device support, FDCAN, timers, ADCs, and the serial interfaces needed here. The larger package makes room for diagnostics and expansion without forcing an early I/O expander into the output-permission path. Its maximum 170 MHz CPU capability is not a requirement to run every subsystem at that speed. [STM32G474VE documentation](https://www.st.com/en/microcontrollers-microprocessors/stm32g474ve.html)

Provide:

- All required power pins, local decoupling, bulk capacitors, and analog-supply treatment.
- An external high-speed crystal; begin clock-tree evaluation with a 24 MHz candidate.
- A reset supervisor and accessible reset button.
- Boot recovery access and an explicitly documented option-byte configuration.
- A keyed 10-pin Cortex debug connector carrying SWD, reset, reference voltage, ground, and SWO where available.
- USB-C device wiring, individual CC pull-downs, data-line ESD protection, VBUS detection, and a protected service-power path.
- Debug UART test points.
- User/service button and status indicators.
- Test points on every supply and critical permission/reset signal.

The STM32 boot ROM supports recovery methods including USB DFU for the relevant family, but the exact package, boot activation, clock, and option-byte details must be checked against ST's bootloader documentation. SWD remains the primary bring-up and recovery route. [ST AN2606](https://www.st.com/resource/en/application_note/an2606-stm32microcontroller-system-memory-boot-mode-stmicroelectronics.pdf)

| Resource | Allocation to reserve before schematic capture |
| --- | --- |
| SPI acquisition | ADC clock, data in/out, chip select, reset, and any required alarm/control |
| DAC serial interface | Separate SPI instance preferred; shared SPI only after mode/timing verification |
| RS-485 | USART TX/RX and driver-enable control |
| CAN | One FDCAN TX/RX pair |
| Pulse input | Hardware timer counter/input capture |
| Other digital inputs | Three GPIO/interrupt inputs |
| High-side commands | Four GPIO, each passing through hardware permission gating |
| Output diagnostics | Sense selection, enable/control, and protected internal-ADC measurement |
| Relay commands | Two gated GPIO |
| Analog output | DAC control and independent hardware disconnect |
| Monitoring | Raw/protected field voltage, service rails, output readback, and temperature |
| Configuration storage | I2C EEPROM, with room for a temperature sensor |
| Debug/recovery | SWD/SWO, reset, boot access, UART, and USB |
| Expansion | Aim to retain at least 10 usable GPIO after a complete allocation |

Keep a preliminary signal budget of roughly 45–60 MCU pins. Complete a CubeMX allocation and a manual package-pin review before drawing the full schematic. Verify timer availability, alternate functions, ADC channels, DMA access, debug reservations, and boot-pin implications together. This document deliberately does not present an unverified final pin map.

## Digital inputs

Use two ISO1212 dual-channel industrial input receivers, or an equivalent verified receiver architecture. They provide four inputs with group isolation and controlled input current. Design the threshold network for the proposed 12/24 V specification; a conventional 24 V input threshold is not enough to prove operation at 9 V. [ISO1212 datasheet](https://www.ti.com/lit/ds/symlink/iso1212.pdf)

Route DI1 to a hardware timer. Keep its input filtering light enough for a 20 kHz pulse train, whose high and low intervals are each 25 µs at 50% duty cycle. Verify delay, threshold crossings, cable capacitance, and pulse distortion at minimum and maximum input voltage.

DI2–DI4 can use stronger software debounce for switches and slow sensors. Provide selectable debounce times in firmware rather than forcing the pulse channel through the same filter.

Each field input requires defined surge/ESD protection, correctly rated series components, reverse-polarity behavior, and terminal labeling. Test thresholds with slow ramps, reversed wiring, a long bench cable, and inputs applied while the MCU is unpowered. A field-status LED must not materially alter the selected receiver current or thresholds.

## Analog inputs

### ADC choice and acquisition

Use ADS8684A as the initial four-channel converter candidate. Its single-ended programmable input ranges are useful here. Configure voltage channels for 0–10.24 V and current channels for 0–5.12 V. The board only needs a small fraction of its available conversion rate. Its input-ground pins must stay close to the ADC ground; they are not floating differential measurement terminals. [ADS8684A datasheet](https://www.ti.com/lit/ds/symlink/ads8684a.pdf)

Acquire 1 kSPS/channel with deterministic scan timing, then publish filtered values at 100 Hz. Measure settling after channel changes and faults. Keep the raw samples available to host tools so noise and load-switching disturbances can be examined.

### Two voltage channels

Each voltage input should contain connector transient protection, pulse-rated series impedance, an active fault-protection path, and an appropriately designed filter. Its normal range is 0–10 V relative to AI_RETURN.

Aim for at least 500 kΩ terminal input impedance over the normal measurement range. Verify the total effect of the ADC input impedance, protection resistance, leakage, and any indicator or bias network. Calibrate the assembled path, rather than only the converter.

Do not universally report wire break from a 0 V voltage measurement: zero may be a valid sensor output. Report the measurement and any protection fault; add wire-break detection only for a specifically supported sensor arrangement.

### Two current channels

Use 200 Ω shunts, at least 0.5 W initially, 0.05% tolerance or better, with low temperature coefficient and Kelvin sensing. Normal 4–20 mA gives 0.8–4 V. The 5.12 V ADC range extends to 25.6 mA, preserving useful overrange information.

At 20 mA, the shunt dissipates 0.02² × 200 = 0.08 W and imposes 4 V burden. Protection-switch and series-resistor drops add to that burden. Record the total burden in the wiring guide.

Support two wiring cases:

1. A separately powered two-wire transmitter: external loop positive → transmitter → AI_I input → board current receiver → loop negative tied to AI_RETURN.
2. An active current-output transmitter: current output → AI_I input, with its reference return connected to AI_RETURN as required by the transmitter.

The demonstration should use a nominal 24 V externally powered loop. Confirm the transmitter's minimum operating voltage plus receiver/cable burden. These receivers are not loop power sources, and a 12 V board supply does not produce a regulated 24 V sensor supply.

Make low-current and high-current alarm thresholds configurable. Approximately 3.6 mA and 21 mA are useful starting values for compatible transmitters; their interpretation depends on the selected sensor.

### Sustained miswire protection

The terminal-fault target is ±30 V applied to a signal terminal relative to its assigned board return, both powered and unpowered, for 60 s using a defined bench setup. Common-mode ground faults are a different case and are not solved by these single-ended channels.

Evaluate two TMUX7462F protector groups, supplied from 15V_ANA. Use one group for the voltage channels and analog output, with a starting positive threshold near 11 V. Use another group for the current channels, with a starting positive threshold near 6 V. Thresholds are shared within each quad protector, so combining both input types under one threshold would compromise the design. Put protected source pins toward field terminals and drain pins toward the ADC or shunts. Select high-impedance drain behavior during a fault. [TMUX7462F datasheet](https://www.ti.com/lit/ds/symlink/tmux7462f.pdf)

Add pulse-limiting impedance and secondary transient protection. A current shunt exposed directly to 24 V can dissipate destructive power; an ADC clamp alone cannot solve that fault. Even with active disconnection, verify response delay, transient switch current, resistor pulse energy, and ADC peak voltage.

The provisional 6 V threshold plus switching threshold must also pass the intended diagnostic current without false trips. All normal-signal drops and worst-case tolerances enter that calculation. If this fails, revise the threshold or shunt value and the error budget before schematic freeze.

The protectors operate autonomously; their drain-response control is not a normal output-enable input. Their source-pin fault rating does not eliminate the need to qualify the assembled protection network.

Also qualify the case where a protector remains powered while ADC_AVDD has collapsed. The ADC's permitted input stress depends on its supply impedance; a floating AVDD has a lower input-voltage limit. Provide a permanent AVDD discharge/bleeder path that satisfies the manufacturer's low-impedance condition, with 10 kΩ as a starting candidate for a requirement below 30 kΩ. Include any load-switch disconnection in that impedance analysis. Verify secondary clamps and transient peaks during every startup/shutdown order, including field removal while USB keeps the MCU alive. [ADS8684A absolute maximum conditions](https://www.ti.com/lit/ds/symlink/ads8684a.pdf)

### Error budget and calibration

| Error contribution | Engineering work |
| --- | --- |
| ADC gain, offset, and nonlinearity | Use guaranteed limits; separate removable calibration errors from residual nonlinearity |
| Reference | Include initial error, drift, supply sensitivity, and warm-up |
| Current shunt | Include tolerance, temperature coefficient, self-heating, and Kelvin routing |
| Protection path | Include leakage, input loading, resistance, and powered-off recovery |
| Filtering | Calculate settling, source loading, bandwidth, and alias rejection |
| Ground and load currents | Include return-path voltage under simultaneous switched loads |
| Calibration equipment | Include source and meter uncertainty in every claimed accuracy result |

Use a two-point calibration per channel and at least five independent verification points. Suggested voltage points are 0, 2.5, 5, 7.5, and 10 V. Suggested current points are 4, 8, 12, 16, and 20 mA, plus diagnostic points below and above the valid range.

Repeat verification with outputs off, outputs switching, all channels loaded, both communication ports active, and the enclosure warm. An independent meter should be materially better than the claimed board accuracy; choose equipment whose uncertainty is preferably no more than one quarter of the acceptance limit.

## Analog output

Include one 0–10 V output in Rev A.

This is a voltage-source command for a compatible high-impedance actuator input. It does not automatically support current-sinking lighting dimming interfaces. Verify the chosen driver or actuator's electrical contract before using it in a demonstration.

Use DAC80501Z, the zero-scale power-on-reset variant, at a qualified 5 V supply. Configure 0–2.5 V output and an amplifier gain near four. Prefer its leaded package where practical for first-article inspection. [DAC80501 datasheet](https://www.ti.com/lit/ds/symlink/dac80501.pdf)

OPA197 is a suitable amplifier candidate. Power it from the positive auxiliary rail and the small negative bias so the zero-volt endpoint has real headroom. Design the gain network, output current handling, cable-capacitance isolation, and stability together. [OPA197 datasheet](https://www.ti.com/lit/ds/symlink/opa197.pdf)

The functional path should be DAC → amplifier → separately controlled default-off disconnect → TMUX drain D → protected source S → terminal. A terminal pull-down establishes an off-state voltage for the specified unloaded/high-impedance wiring case.

Use protected amplifier-side readback into the MCU ADC, taken before the commanded disconnect. Verify its divider, current limiting, clamps, and unpowered-MCU behavior. This confirms the amplifier-side value; it cannot prove actual terminal voltage or detect every external terminal fault. Use an independent meter at the terminal for output qualification. Any future terminal-side readback must have its own ±30 V fault protection because it would bypass the main AO protector.

The TMUX fault protector does not supply the commanded disconnect. Select a separate switch whose signal range, leakage, on-resistance, startup behavior, and disabled state fit the amplifier path. The disconnect must stay off during missing/invalid rails and unexpected supply sequences; select high-impedance fault-drain behavior on the protector.

The output must deliver 0–10 V into at least 10 kΩ. Include the protection and disconnect resistance in the ±50 mV error budget. At 10 V the load draws 1 mA; a 50 Ω total series path would already drop 50 mV and consume the full error allowance. Use a smaller impedance, suitable feedback/compensation, or a revised verified specification.

Test zero, full scale, minimum load, open load, a short to return, cable capacitance, a sensor connected during startup, and ±30 V external terminal faults. Keep negative-bias startup, disabled leakage, and rail-loss behavior in the test plan. The amplifier's supply-voltage rating alone says nothing about external terminal fault survival.

## Four high-side outputs

Use the current-sensing TPS4H160B-Q1 variant as the starting four-channel switch. Each channel switches positive field power to a load whose other terminal returns to LOAD_RETURN. The first release targets 0.5 A continuously per channel, all together. [TPS4H160 datasheet](https://www.ti.com/lit/ds/symlink/tps4h160-q1.pdf)

Start the common current-limit design near 0.7 A/channel, accounting for tolerance. A stalled or shorted load should produce a latched channel fault requiring explicit recovery. Let hardware perform immediate current limiting; firmware handles fault state and recovery. Thermal shutdown is a backup, not a normal operating cycle.

Current sensing is multiplexed through one shared output. Firmware must select a channel, wait the required settling time, sample, and tag the reading. Protect the MCU measurement input against the sense output's fault voltage and unpowered MCU cases. Do not describe the four current readings as simultaneous.

Fit a series blocking diode per channel for Rev A and a load-side freewheel diode, anode at LOAD_RETURN and cathode at the output terminal. Select their reverse-voltage, surge, repetitive-current, and thermal ratings from the final fault envelope. The blocking diode addresses ordinary positive external output backfeed; it does not establish arbitrary negative-output fault survival.

This diode approach introduces voltage drop and slow inductive-current decay. At 0.5 A and 0.3–0.5 V forward drop, each blocking diode dissipates approximately 0.15–0.25 W. Document that the output is approximately VFIELD minus its semiconductor drops.

Initially qualify resistive loads, a small 24 V solenoid, and a modest fan/pump load within the current limit. Keep high-frequency PWM and fast-release solenoid operation for a qualified extension. A faster inductive clamp needs its own diode/TVS energy design.

Nominal switch conduction for all four channels is 4 × 0.5² × 0.16 = 0.16 W. Actual hot resistance, quiescent power, diodes, traces, and connectors add heat. A current-limited 24 V short near 0.7 A can create roughly 17 W instantaneous switch dissipation, so fault tests need separate analysis.

The series diode can alter off-state diagnostic behavior. Qualify open-load detection using on-state current and the selected load; do not advertise the IC's unmodified diagnostic behavior without testing the assembled output.

## Two relay outputs

Use two G5Q-1 DC5 SPDT relays, or an equivalent qualified part with documented coil/contact limits. Drive their 5 V coils from field service power through gated transistor stages and coil suppression. SPDT versions have approximately 400 mW coils, so reserve about 80 mA per relay. [Omron G5Q datasheet](https://components.omron.com/system/files/2025-07/datasheet_pdf/J155-E1.pdf)

Expose COM, NO, and NC separately. The initial board-level contact target is 30 V DC at 1 A resistive. Contact-current ratings depend on DC versus AC service, load type, connector capability, PCB routing, and enclosure temperature.

Use COM–NO for the demonstration so a deenergized coil leaves the controlled circuit open. COM–NC remains closed when the board is off; document that behavior in the wiring guide. For an inductive contact load, specify suppression at the load and qualify that particular load separately.

Keep each contact circuit separated from the coil/main circuit and the other relay's contact circuit. Include test-access provisions without accidentally bonding the dry contacts to logic ground.

## Wired communication

### RS-485 and Modbus RTU

Use ISO1410 with its own isolated 5 V supply and reference island. Its maximum data rate is sufficient for the planned Modbus speeds. [ISO1410 datasheet](https://www.ti.com/lit/ds/symlink/iso1410.pdf)

Provide selectable 120 Ω termination, selectable network bias, field-side transient protection, a reference terminal, and clear differential-polarity labeling. Bias normally belongs at one designated location on the network. Calculate its worst-case differential voltage with the termination network and all receiver loads.

Prefer differential names D+ and D− in the wiring guide, with the selected transceiver pin mapping shown explicitly. Vendor A/B naming is not sufficiently consistent to stand alone.

Implement server addressing, CRC handling, silent intervals, correct driver-enable timing, exception responses, broadcast behavior, and atomic output updates against the official protocol specifications. Demonstrate multidrop communication using a second device and a documented cable/termination arrangement. [Modbus specifications](https://www.modbus.org/modbus-specifications)

Support functions 01/02/03/04/05/06/15/16 as appropriate to the chosen register model. Keep one internal data model shared with USB and CAN so values and faults agree.

### CAN and CAN FD

Use ISO1042 with another isolated supply and reference island. Provide selectable termination, protection on the bus side, and documented shield/reference wiring. The transceiver's maximum supported rate is not an installed-network guarantee. [ISO1042 datasheet](https://www.ti.com/lit/ds/symlink/iso1042.pdf)

Demonstrate classic CAN at 500 kbit/s first. Then qualify FD at 500 kbit/s arbitration and 2 Mbit/s data with an FD-capable second node or adapter, two end terminations, and a documented short bus.

Define a small application protocol containing node identity, heartbeat, analog readings, digital inputs, pulse count, output commands, current diagnostics, and faults. Document CAN identifiers, byte order, units, scaling, sequence counters, and timeout behavior. This is a custom application protocol; do not label it CANopen unless CANopen is actually implemented.

Report bus-off and communication-error counters. Recovery must require fresh valid commands and explicit rearming rather than restoring old output commands automatically.

### USB service interface

Provide CDC configuration, readout, calibration, firmware/version information, and CSV/structured logging through a small host application. Respect USB VBUS current rules, source sequencing, and suspend behavior. Use a service mode that powers only the essential logic before enumeration.

USB should not silently compete with a field controller. Make the command owner explicit: Modbus, CAN, or local demonstration mode. Other interfaces can still read diagnostics. Changes of command owner disarm outputs.

## Connector and indicator plan

Choose pluggable terminals early enough to constrain the enclosure and PCB outline. Terminal pitch, wire range, current rating, screw access, and mating plugs all belong in the mechanical/BOM review.

| Connection | Proposed signals |
| --- | --- |
| Power | VIN+, VIN− |
| Digital inputs | DI1, DI2, DI3, DI4, DI_COM |
| Voltage input 1 | AI_V1, AI_RETURN |
| Voltage input 2 | AI_V2, AI_RETURN |
| Current input 1 | AI_I1, AI_RETURN |
| Current input 2 | AI_I2, AI_RETURN |
| Analog output | AO1, AO_RETURN |
| Load outputs | DO1–DO4 and adequately rated LOAD_RETURN terminals |
| Relay 1 | COM1, NO1, NC1 |
| Relay 2 | COM2, NO2, NC2 |
| RS-485 | D+, D−, RS485_REF; shield provision if used |
| CAN | CAN_H, CAN_L, CAN_REF; shield provision if used |
| Service | USB-C and keyed SWD |

Although analog return and load return belong to main ground, their physical paths must keep actuator currents out of ADC return connections. Use local connector labels and a wiring diagram; do not rely on connector designator numbers alone.

Provide field-power, logic-power, running, armed, and fault indication. Add port activity indication and meaningful channel status in software. Hardware LEDs on sensitive input terminals are optional and must be included in loading calculations.

Use an easily accessible output-inhibit jumper or switch for bench service. Its hardware effect must be clear and tested.

## Firmware plan

Implement the firmware in C/C++ with STM32Cube-generated startup/HAL support where useful and version-controlled application code. Use a deterministic timer-driven scheduler first. An RTOS may be introduced if concurrency benefits are demonstrated; it is not a portfolio requirement by itself.

Separate drivers, calibrated acquisition, output management, fault state, communication adapters, and application/demo logic. Keep protocol parsing away from direct output-register writes.

### States and permissions

| State | Behavior |
| --- | --- |
| USB service | Logic available; field measurements flagged unavailable where supplies are invalid; all field outputs inhibited |
| Boot/self-test | Outputs inhibited while rails, configuration, ADC/DAC, and watchdog are checked |
| Ready | Valid power and no blocking faults; output permission still off |
| Armed | Selected command owner has explicitly armed the board; valid fresh commands may control outputs |
| Channel fault | Faulted channel off and latched; unaffected channels follow the documented policy |
| Global fault | High-side channels, relay coils, and analog output inhibited |
| Recovery | Fault condition removed, self-check passed, fresh arm command required |

Use a hardware permission expression equivalent to FIELD_VALID AND RESET_OK AND WATCHDOG_OK AND ARM. Apply it to each high-side command input, each relay driver, and the analog-output disconnect. The switch's diagnostic-enable pin must not be mistaken for a global power-output disable.

External pull-downs keep command pins off during reset or unpowered MCU conditions. Hardware rail monitoring and watchdog faults must remove permission independently of firmware. ARM must be cleared by reset and global faults.

TPS3431 is an external watchdog candidate. Its active-low output and enable behavior need a reviewed connection to reset/permission logic. Service it only after software health checks have passed; a free-running hardware PWM must not continue feeding it while the application hangs. [TPS3431 documentation](https://www.ti.com/product/TPS3431)

### Release behavior

- Default high-side outputs off, relay coils off, analog output disabled/at the documented zero state.
- Default 1 s command watchdog for the active command owner.
- Invalid or corrupt configuration prevents arming.
- Output commands include bounds checks and are applied atomically.
- Global brownout, reset, watchdog, invalid power, or command-owner change clears arming.
- Channel overloads latch off; no unlimited automatic short-circuit retries.
- Calibration and configuration have version, CRC, and two recoverable storage copies.
- Bootloader/update mode inhibits all field outputs.
- Debugger halt is tested against the physical watchdog; any service override is visibly documented and disables outputs.
- Stale ADC data, protection faults, and communication faults appear in telemetry.
- Data includes board identity, firmware version, units, calibration validity, and uptime.

Store calibration/configuration in a small I2C EEPROM such as a suitably selected 24LC64 variant. Do not write high-rate telemetry or every heartbeat to EEPROM. Keep a RAM event buffer and stream logs to the host; commit only bounded configuration changes and selected persistent counters.

### Data model

Define named values for four analog inputs, four digital inputs, pulse count/frequency, four output commands, four multiplexed current readings, two relay commands, analog-output command/amplifier-side readback, rails, temperature, arm state, and fault flags.

Use fixed documented units for field protocols, such as millivolts, microamps, milliamps, and integer pulse counts. Document scaling, signedness, multi-register ordering, and rollover. Reserve register/identifier ranges for configuration and future features without committing to a large unused address space.

### Demonstration control loop

Provide a local demonstration mode that reads a pressure/level/temperature transmitter, applies a bounded control rule, switches a small DC actuator, and commands a 0–10 V fan or actuator input. Include a maximum runtime and a manual inhibit. Report current and faults over both buses.

The initial demonstration can use threshold control. A calibrated PI loop can be added after the sensor path and actuator response are characterized. Avoid describing an untuned control loop as proven process-control performance.

## Host tools and test fixture

Build a small Python host package with command-line tools and a simple dashboard. It should read the board through USB, Modbus, and CAN adapters; run tests; plot measurements; and save timestamped CSV results with hardware/firmware identifiers.

Provide commands for discovery, live readings, configuration, calibration, output arming, fault readout, and automated qualification. Pin dependencies and store a reproducible setup guide. No cloud account should be necessary to operate the demonstration.

The bench fixture should contain:

- A current-limited 0–40 V supply and suitable DC wiring.
- Precision voltage and current stimulus, with an independent calibrated meter.
- Load resistors or electronic loads for 0.5 A/channel tests.
- One qualified 24 V solenoid or similar inductive actuator.
- A 0–10 V controlled fan/actuator, or a representative electrical load for initial AO tests.
- A 12/24 V pulse source for DI1, plus switches for the other inputs.
- An isolated RS-485 adapter and an FD-capable CAN adapter or second node.
- A scope, SWD probe, and a temperature-measurement method.
- Clearly labeled, current-limited fault-injection leads and a hardware inhibit.

Four 0.5 A resistive loads at 24 V dissipate 48 W outside the PCB, and at 30 V would dissipate 60 W if current is held at 0.5 A. Choose fixture loads, heatsinks, wiring, and supplies for the actual test condition.

Ordinary resistor fixtures sized for 24 V do not automatically draw exactly 0.5 A at every supply voltage. Use an electronic load or explicitly calculate each test's resistance and dissipation.

## PCB and mechanical plan

### Four-layer stack-up

Start with this arrangement, then obtain the fabricator's actual dielectric/copper stack-up:

| Layer | Main purpose |
| --- | --- |
| L1 | Components and critical signal routing, including USB referenced to L2 |
| L2 | Continuous main ground plane, with required isolated-domain boundaries |
| L3 | Power distribution and selected slow routing; isolated power islands where needed |
| L4 | Secondary components/slow signals and ground copper with stitching |

Route USB over its continuous reference and use the manufacturer's impedance calculation for a 90 Ω differential target. Keep fast clock/SPI traces over a defined return path. Avoid placing a fast bottom-layer trace over a fragmented power layer simply because routing space is available.

Analog/digital placement should control current paths without cutting the main ground plane into arbitrary analog and digital halves. True isolation domains require deliberate boundaries; functional analog/digital separation usually benefits from one continuous reference.

### Placement priorities

1. Fix enclosure geometry, terminal access, mounting holes, and USB/SWD access.
2. Place input protection at the power terminal.
3. Place high-side switch and blocking/freewheel diodes near load terminals.
4. Keep buck, boost, and isolated-converter switching loops compact.
5. Place ADC, shunts, fault protection, and filters near analog terminals, away from hot/load-switching paths.
6. Keep relay contact routing distinct from coil and low-level analog circuitry.
7. Place communication protection at its terminal and isolation barrier beside its transceiver/power supply.
8. Place MCU decoupling and crystal components directly according to the verified MCU guidance.
9. Add accessible test points before filling remaining space.

Start with 0.20 mm minimum ordinary track/space and a conservative via process such as 0.30 mm drill/0.60 mm pad where feasible. These are planning defaults; check the selected fabricator and fine-pitch footprint needs. Size power copper from current, temperature rise, copper thickness, and available plane area. Do not set a universal width for every 3 A route.

Use thermal pads and vias according to each power IC's package guidance. Check assembly consequences of vias in exposed pads, solder wicking, tenting/filling, and paste apertures. Prefer 0603/0805 passives where they help inspection, but choose resistor size from voltage, pulse, and power requirements.

Use a 3D model to verify terminal plugs, screwdriver clearance, cable bends, relay height, LED visibility, mounting hardware, and enclosure airflow. The approximately 140 × 100 mm outline is provisional until that check; enlarging it is preferable to compromised isolation or thermal placement.

### Review before fabrication

Run ERC, DRC, schematic/PCB connectivity comparison, and a package-pad-to-datasheet check. Manually verify every MCU power pin, external transistor, protection IC, regulator, relay, diode orientation, and connector pin mapping.

Simulate the input/output analog conditioning, filters, amplifier stability, and applicable power-transient cases using available models. Follow with EMC and thermal reviews when schematic and PCB information exists. Simulations complement physical verification and cannot replace it.

Review Gerbers, drill files, solder mask, paste, board outline, component placement, and assembly rotations. Record intentional exceptions and evidence before release.

## Schematic organization

| Sheet | Content |
| --- | --- |
| System | Top-level hierarchy, power/ground domains, permission signals, and connector summary |
| Input power | Fuse, TVS, blocking FET/eFuse, bulk capacitance, input sensing |
| Service power | 5 V buck, logic power mux, 3.3 V digital/analog supplies |
| Auxiliary power | Analog positive/negative rails and two separate isolated communication supplies |
| MCU and debug | MCU power, clock, reset, boot, watchdog interface, USB, SWD |
| Digital inputs | Four field receivers, threshold/filter/protection networks |
| Analog inputs | ADC, shunts, voltage paths, protectors, filters, and reference treatment |
| Analog output | DAC, amplifier, hardware disconnect, protector, readback |
| Switched outputs | Four high-side channels, diagnostics, blocking/freewheel diodes |
| Relays | Two coil drivers, suppression, dry-contact routing |
| Communications | RS-485 and CAN transceivers, bus protection, termination/bias |
| Permission and service | Hardware gating, indicators, inhibit switch, storage, and test access |

Cross-sheet labels should show direction and domain. Add design notes containing actual limits, selected fault envelope, and calculation references, rather than relying on remembered conversations.

## Major component selection plan

These are preferred starting candidates. Verify exact orderable suffix, package, lifecycle, availability, ratings, and footprint before freezing the BOM.

| Function | Candidate | Main selection check |
| --- | --- | --- |
| MCU | STM32G474VET6 | Complete pin/clock/DMA allocation; LQFP100 symbol and footprint |
| External ADC | ADS8684A | Supply/reference, SPI timing, single-ended returns, acquisition settling |
| Input eFuse | TPS26632 | Fixed-clamp variant, reverse-blocking arrangement, limit and surge SOA |
| Blocking MOSFET | 100 V class, exact MPN to select | RDS(on), gate compatibility, reverse-fault differential stress, thermal area |
| Raw TVS | SMCJ33CA starting candidate | Defined surge waveform/source impedance and worst-case clamp |
| 5 V buck | LMR38020 | Inductor/capacitor calculations, frequency, startup, EMI and heat |
| Digital 3.3 V | TPS62160 | Load budget and local switching layout |
| Quiet 3.3 V | TPS7A20 suitable 3.3 V variant | Dropout, output capacitance, noise, analog-load budget |
| Logic source selection | TPS2121 | USB current limits and every source insertion/removal sequence |
| Analog positive supply | TPS55340 | 5 V to 15 V boost, current margin, ripple and startup |
| Negative bias | LM7705 | Input limit, startup, bias-current margin, noise |
| Input receivers | 2 × ISO1212 | 12/24 V thresholds, current and pulse timing |
| Analog fault protectors | 2 × TMUX7462F | Shared thresholds, source orientation, switch-current limits and pulse stress |
| Current shunts | 2 × 200 Ω precision parts | Low TCR, Kelvin connection, sustained/pulse ratings |
| Output DAC | DAC80501Z variant | Zero-scale POR and selected package/interface |
| Output amplifier | OPA197 | Load/stability, gain, negative bias, fault/recovery conditions |
| Analog disconnect | Exact MPN to select | 0–10 V path, default-off control, leakage, resistance, rail-loss behavior |
| High-side switch | TPS4H160B-Q1 | Version B current sensing, limit tolerance, inductive loads and backfeed |
| Output diodes | Exact MPNs to select | Fault voltage, repetitive current, heat, and decay time |
| Relay | 2 × G5Q-1 DC5 or equivalent | SPDT variant, coil power, board-qualified DC contact load |
| RS-485 | ISO1410 | Half-duplex timing and bus-side supply |
| CAN | ISO1042 wide-body variant | FD timing, reference/shield strategy, termination |
| Isolated power | 2 × UCC12050 candidates or qualified regulated modules | Separate islands, worst-case load, thermal derating and startup |
| External watchdog | TPS3431 | Reset/permission response and development-mode behavior |
| Configuration memory | 24LC64 family candidate | Supply, write protection, endurance and recovery protocol |
| Terminals and enclosure | Select together | Wire/current ratings, pitch, mating plugs, access, and mechanical fit |

For every schematic symbol, store manufacturer, exact MPN, datasheet, footprint, relevant distributor numbers, and assembly/substitution notes. Once a new schematic exists, its symbol properties should be the BOM source of truth.

Create procurement data from that new design. Check exact parts through authorized distributors and obtain assembly quotes before choosing substitutions. Pin compatibility, diagnostic behavior, and protection limits all matter; a similar description is not enough.

Use the [procurement plan](Procurement_Plan.md) to organize candidates, the [reference manifest](../references/datasheets/manifest.json) to identify supporting PDFs, and the [open engineering items](Open_Engineering_Items.md) to track unresolved decisions. PDF identity checks do not establish exact-package pin correctness.

## Build and manufacturing sequence

1. Finalize requirements, block-level budgets, and enclosure geometry.
2. Evaluate the highest-risk circuits on small fixtures or manufacturer evaluation boards: analog faults, AO zero/stability, high-side short/inductive behavior, and USB/field source selection.
3. Complete MCU resource allocation.
4. Calculate and capture the fresh schematic.
5. Review every critical part and simulate applicable circuits.
6. Route the four-layer board and perform electrical, thermal, EMC, mechanical, and assembly reviews.
7. Freeze exact BOM, check stock, and obtain current fabrication/assembly quotes.
8. Order five PCBs and a suitable stencil, or a staged assembly service.
9. Populate/qualify the first article before completing the remaining boards.
10. Assemble at least three fully working units for repeatability evidence; use the remaining units for spare/debug or a complete five-board set after first-article success.
11. Run calibration and qualification against recorded hardware/firmware revisions.
12. Make a revision if critical fixes would otherwise depend on fragile rework.

Favor machine assembly for exposed-pad/high-density parts if available. Hand installation of terminals, relay parts, or selected connectors may be appropriate, but the process must be documented.

Manufacturing outputs include native KiCad files and libraries, schematic PDF, Gerbers, drill files, fabrication drawing/stack-up, exact BOM, placement data, assembly drawings, polarity notes, stencil files, DNP/substitution notes, and a programming/test procedure.

Order mating terminal plugs, debug cable/probe, screws/standoffs, enclosure parts, external suppression for the demonstration load, and spare critical ICs alongside PCB components. These system items belong in the procurement plan even when absent from the schematic.

## Bring-up sequence

| Stage | Work and evidence required before continuing |
| --- | --- |
| Unpowered | Visual inspection, polarity/footprint checks, resistance checks, isolation-domain continuity |
| Input protection | Current-limited supply; check eFuse startup, protected rail, reverse-blocking configuration |
| Rails | Verify 5 V, digital/analog 3.3 V, ripple and power sequencing |
| MCU | Connect SWD, read identity, run a minimal program, verify reset, clocks, watchdog and USB |
| Auxiliary rails | Verify positive/negative analog supply and separate isolated supplies, including loading |
| Digital inputs | Measure thresholds and pulse behavior before connecting machinery |
| Analog acquisition | Read known voltage/current stimuli; identify reference, settling and ground errors |
| Analog output | Start disabled, then test zero, range, minimum load and capacitive-load stability |
| Load outputs | Test one resistive load per channel, current sensing, permission gating and fault latching |
| Relays | Verify coil suppression and COM/NO/NC behavior using low-voltage loads |
| Communications | Qualify RS-485 first, classic CAN next, then CAN FD |
| Integrated operation | Sensor/control demo, switching-noise measurement, full-load enclosure temperature |

Record supply limits, test setup, scope captures, unexpected behavior, and rework. Firmware convenience must not bypass physical permission gating during bring-up.

## Qualification matrix

| Test | Procedure | Pass condition or required report |
| --- | --- | --- |
| Normal supply | Operate at 9, 12, 24, 30 V | All required functions and service rails inside their limits |
| Startup/hot plug | Repeated insertion with representative cable and loads | No unintended output pulse; peaks remain within the reviewed envelope |
| Reverse input | −30 V, documented current-limited setup | No destructive fault or backpower; recovery after proper reconnection |
| Positive input fault | +40 V with defined source limit | Loads disarm; clamp/disconnect follows design; recovery requires rearm |
| Brownout | Slow ramps and rapid drop/reconnect | Outputs reach the specified off state; no automatic old-command restoration |
| USB sequencing | USB only, field only, both, either removed; measure inactive field rails | No source/signal backfeed or field-output activation from USB |
| Input thresholds | Voltage sweep over each DI | Guaranteed OFF ≤5 V and ON ≥9 V |
| Pulse count | 20 kHz reference train at low/high input voltage | Count matches source over the specified interval/cable |
| Voltage accuracy | Calibration and independent five-point sweep | Within ±20 mV at room temperature |
| Current accuracy | Calibration and independent five-point sweep | Within ±32 µA over 4–20 mA at room temperature |
| Input temperature accuracy | Repeat input sweeps at 0/25/50 °C using the same room-temperature coefficients | Within ±50 mV for voltage and ±80 µA for current; include measurement uncertainty |
| Analog overrange | Inputs below/above nominal ranges | Correct values/flags; no false calibrated-valid result after protector trip |
| Analog terminal miswire | ±30 V on each signal terminal, powered/unpowered, 60 s | No damage/backpower; accurate recovery after fault removal |
| Analog supply sequencing | Protector on with ADC supply off; all startup/decay orders; remove field power with USB present | ADC pin stress within reviewed limits, field rails not backpowered, data invalid until qualified rails recover |
| Switching disturbance | Repeat AI measurements while rated loads switch | Measure transient/settled error and meet published accuracy condition |
| AO accuracy | Zero/full-scale and intermediate points into ≥10 kΩ | Within ±50 mV; stable operation |
| AO faults | Open, short, cable capacitance and external ±30 V | No damage; default-off/recovery behavior as documented |
| AO readback | Compare amplifier-side telemetry with independent terminal measurements | Readback location/limitations clear; no MCU injection during faults or rail loss |
| Output load | Four channels at 0.5 A simultaneously | Voltage drop/temperature within qualified specification |
| Output open load | Remove each known load | Diagnostic reports appropriate to the supported load, without false precision claims |
| Output overload/short | Controlled overload and hard-short fixture | Hardware limits current; firmware latches fault; no uncontrolled repeated restart |
| Inductive switch-off | Selected real load, individual/simultaneous switching | Peak voltage, energy and diode temperatures within reviewed limits |
| Positive output backfeed | Apply rated positive terminal voltage with source absent | No unintended rise of VFIELD/logic supply through the output |
| Relay operation | Exercise specified resistive DC load | Correct contact behavior and acceptable contact drop/temperature |
| Reset/watchdog | Reset, software hang, debugger halt, update mode | Hardware permission removed; fresh rearm required |
| Communication loss | Stop selected owner's valid commands | All commanded energy outputs off within configured timeout |
| Modbus robustness | Bad CRC, invalid function/address, bus loading, repeated traffic | Defined exceptions, no unintended output changes, no persistent lockup |
| CAN robustness | Bus error/bus-off, classic and FD tests | Correct diagnostics and controlled recovery |
| Corrupt configuration | Corrupt or interrupt a stored update | Recover valid copy or remain disarmed with a clear fault |
| Enclosure thermal | Full load at 0/25/50 °C | Meets rated operation; publish actual temperatures and derating |
| Soak | At least 24 h on multiple units with recorded traffic/load schedule | No unexplained reset, calibration loss, missed commands or output fault |
| Reproducibility | Repeat programming/calibration on ≥3 boards | Traceable results and consistent behavior |

For hardware short-circuit tests, record the immediate analog waveform separately from the slower firmware diagnostic response. A passed communication test does not establish immunity to every cable installation.

If equipment cannot cover the proposed temperature range, publish only the tested temperature rating and leave the wider target unqualified. Component temperature ratings do not establish assembled-board accuracy or enclosure performance.

The optional lab stage can evaluate IEC 61000-4-2 ESD, IEC 61000-4-4 EFT, and IEC 61000-4-5 surge against explicitly selected installation levels, coupling networks, and performance criteria. Agree that plan and revise protection calculations before applying those waveforms. Publish the achieved test conditions, not a general compliance claim.

## Schedule and effort

Use milestones rather than a promised completion date. A planning allowance of 180–280 focused hours is reasonable for this first complete build; it is an estimate, not a guarantee. At 15 hours/week it corresponds to approximately 12–19 weeks, excluding unusual sourcing delays or another PCB cycle.

| Phase | Estimated effort | Exit condition |
| --- | --- | --- |
| Requirements, wiring cases, enclosure, resource plan | 15–25 h | Scope and interface/power budgets coherent |
| Risk-circuit experiments and calculations | 20–35 h | Analog faults, output faults, AO endpoint and power selection have evidence |
| Schematic and review | 30–45 h | Critical pin/package review and simulations complete |
| Layout and manufacturing release | 30–45 h | DRC, thermal/EMC/mechanical/assembly reviews complete |
| Firmware and host tools | 35–50 h | Drivers, states, protocols, logging and test automation usable |
| Assembly, bring-up and calibration | 20–35 h | First article and multiple boards functional |
| Qualification, enclosure and portfolio | 30–45 h | Evidence package meets release criteria |
| Total | 180–280 h | Completed and measured project |

Firmware and host tools can start on development hardware while the PCB is being designed or manufactured. Do not count this overlap as reducing the engineering work itself.

## Budget allowance

The following amounts are planning reserves in USD, not current distributor or assembly quotes. Exact costs will depend on the final BOM, quantities, assembly route, shipping, and equipment already owned.

| Category | Planning reserve |
| --- | --- |
| Five PCB component sets and selected spares | 500–900 USD |
| Four-layer boards, stencil, and fabrication shipping | 80–180 USD |
| Assembly/rework support | 100–300 USD |
| Enclosure, mating connectors, wiring and demonstration hardware | 150–300 USD |
| Second PCB cycle/contingency | 250–500 USD |
| Total excluding major bench instruments | 1,080–2,180 USD |

Budget adapters, debug probe, precision stimulus/meter, suitable precision loads, and any manufacturer evaluation boards separately if you do not own them. The demonstration-hardware reserve covers ordinary enclosure/wiring/load items, rather than a complete laboratory or a guaranteed set of risk-circuit evaluation boards. Borrowing appropriate calibration equipment may be more useful than buying a meter that cannot support the accuracy claim.

Obtain live quotes after the schematic/BOM freeze. Cost reductions should preserve testability and demonstrated functions; package/connector and assembly decisions often matter more than saving small amounts on individual resistors.

## Portfolio deliverables

Finish with a public-facing case study and a separate engineering package.

The case study should contain:

1. A clear problem statement and specification.
2. A readable block diagram and photographs of the assembled board/enclosure.
3. A short video showing a sensor reading, actuator control, a 0–10 V command, Modbus/CAN telemetry, and a controlled fault.
4. Input/output accuracy plots with calibration method and uncertainty.
5. Power startup/brownout captures and full-load thermal results.
6. A specific design issue found during testing and the evidence used to fix it.
7. A feature/limitations table that matches the tested release.

The engineering package should contain:

- Native schematic/layout and project libraries.
- Exact BOM and manufacturing outputs.
- Firmware source, reproducible build steps, versioned release binaries.
- Host tools, test procedure, raw measurement data and reports.
- Connector/wiring guide and protocol/register documentation.
- Calibration/configuration procedure and recovery instructions.
- Enclosure CAD/drawing and assembly photographs.
- Revision log and known limitations.

Present yourself as having designed, assembled, programmed, and tested a protected sensor/actuator controller. Use measured values in the portfolio description. Save terms such as certified, automotive-qualified, safety-rated, and production-ready for evidence that actually establishes them.

## Criteria for a completed first release

Rev A is complete when at least three physical boards can be programmed and calibrated reproducibly; all base interfaces work; the documented real loads operate; reset, fault, and command-loss behavior passes; the enclosure meets the thermal specification; and another person can reproduce basic operation from the supplied files and instructions.

If a target must change after testing, update the specification, wiring guide, firmware bounds, and portfolio claims together. A smaller verified capability is a stronger deliverable than an unsupported large rating.

## First implementation tasks

Start with these concrete tasks:

1. Confirm the base scope and select the demonstration sensor, solenoid, and 0–10 V actuator.
2. Choose terminals and an enclosure that fit the starting board envelope.
3. Finish the STM32G474VET6 resource allocation and clock tree.
4. Draw the ground/isolation map and external wiring cases.
5. Calculate input protection, service power, output fault energy, analog error budgets, and total current-loop burden.
6. Bench-test the analog miswire protector, AO zero/disconnect behavior, and one diagnosed load output.
7. Capture the hierarchical schematic using verified package-specific pinouts.

The parts still needing exact selection are the input blocking FET, terminal/relay connector system, output diodes, analog disconnect, reset/window-supervision implementation, calibration memory suffix, and final isolated-converter implementation. Threshold/filter values, crystal capacitors, converter passives, and copper widths must be calculated from the chosen parts. Resolve those in the schematic phase; they are not reasons to broaden the project's features.

After the base release, the most useful extensions are a protected sensor-power feed, a qualified proportional/PWM output, faster inductive release, or separately isolated analog channels. Choose one based on real client requests and measurements from Rev A.
