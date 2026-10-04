# Rev A schematic capture package

I have specified the revised Rev A circuits and exact component candidates. I use this document as the entry point and the four circuit specifications below as drawing instructions. I can begin schematic hierarchy and library preparation; effective-capacitance evidence and package comparison still need closure before the affected circuits are frozen.

## Preparation status

| Item | Status |
| --- | --- |
| Scope, circuit connections, MCU resources, connectors and support values | Specified in the circuit documents and selection files |
| Power, input protection and PWM timing arithmetic | Reproducible with stated device test conditions and engineering assumptions |
| Effective capacitor values at operating voltage/temperature | Open bank-by-bank evidence in [capacitor_evidence.json](calcs/capacitor_evidence.json) |
| Project-local symbols and footprints | Missing assets identified; create and compare each package before wiring |
| Schematic connectivity/ERC, layout/DRC and measured ratings | Pending native implementation |

I do not treat nominal capacitor values or catalog listings as effective-capacitance evidence. A failed minimum requires a controlled part/quantity change with inrush, discharge and stability recalculated together.

## Capture references

| Specification | Implementation detail |
| --- | --- |
| [Power](circuits/Power.md) | Input protection, field-powered regulators, positive auxiliary/threshold rails, inrush and budgets |
| [Control and service](circuits/Control_Service.md) | Physical MCU pins, clock, self-powered USB, SWD, EEPROM, health/watchdog/ARM and powered-off crossings; [loop status](circuits/Loop_Status.md) |
| [Analog](circuits/Analog.md) | External ADC, voltage/current protection, permanent shunts, thresholds, filtering and output-current diagnostics |
| [Field I/O](circuits/Field_IO.md) | DI timing, high-side channels/DO3 PWM, current sensing, relays, isolated supplies, bus protection and connectors |
| [Component selections](components/README.md) | Ordering codes, values, packages, quantity allocations and CAD targets |
| [Interfaces](Interfaces.md) | External wiring and command behavior |
| [Validation](Validation.md) | Qualification conditions and evidence |

The native schematic will own reference designators, connectivity and the released assembly BOM. My pre-capture quantity allocations are not ordering quantities.

## Fixed scope and targets

I am building a four-layer STM32G474VET6 controller for enclosed 0–50 °C operation from external nominal 12/24 V DC, with a 9–30 V qualification range. I include four group-isolated digital inputs, two 0–10 V inputs, two externally powered 4–20 mA receivers, four 0.5 A high-side outputs, two low-voltage SPDT relays, independently isolated Modbus and CAN/CAN FD, USB data service, SWD/SWO and EEPROM settings.

DI1 targets 20 kHz counting. The four analog channels target 1 kSPS/channel and 100 Hz publication. Calibrated room-temperature input targets are ±20 mV and ±32 µA; the same coefficients target ±50 mV and ±80 µA at 0/25/50 °C.

DO3 adds TIM1_CH1 PWM on PE9, physical pin 40, AF2. Its initial target is 100 Hz, 10–90% commanded duty plus static off/on endpoints, with a resistive or compatible LED load ≤0.5 A. DO1/DO2/DO4 remain on/off. I retain all four channels in the continuous full-load budget. Actual edge timing, load compatibility and current-sense scheduling require qualification at the selected 9–30 V supply, 3.3 V control and approximately 0.7 A limit.

I reserve 6 W delivered service power with 5.75 W in conservative named branches and a 3 A continuous main-input target. The first source is limited to ≤4 A. USB VBUS does not power the board; external power is required for USB communication. My low-line power-path contract requires VFIELD ≥8.4 V at the 9 V connector/full-load fixture; I use the cornered 190 kΩ/10 kΩ FIELD_OK UV network and verify the remaining 3 A budget at this post-protection voltage.

## Sheets and rails

| Sheet | Scope |
| --- | --- |
| 00_System | Hierarchy, connector overview, domains and shutdown truth table |
| 01_Input_Power | VIN_RAW, protection, VFIELD, MAIN_GND |
| 02_Rails | 5V_FIELD, ADC_AVDD, 3V3_FIELD_LOGIC, 15V_ANA, VFP11/VFP6, 3V3_DIG, 3V3_MCU_ANA |
| 03_Control_Service | MCU, clock, USB, SWD, EEPROM and health/permission logic |
| 04_Analog | Voltage/current acquisition and protected output-current diagnostic path |
| 05_Digital_Actuation | ISO1212 inputs, TPS4H160 channels/DO3 PWM, blocking/freewheel diodes and relay drivers |
| 06_RS485 | Dedicated isolated supply, RS485_REF, transceiver, protection and termination |
| 07_CAN | Independent isolated supply, CAN_REF, transceiver, protection and split termination |

AI_RETURN and LOAD_RETURN join MAIN_GND with controlled routing. DI_COM, RS485_REF, CAN_REF and each relay-contact group remain separate. FIELD5V_VALID qualifies the isolated converters and positive boost; ADC_AVDD starts independently, avoiding a startup cycle. ANALOG_VALID combines FIELD5V_VALID, ANA15_OK and FIELD3V3_OK. I preserve analog-health shutdown because it qualifies input protection and diagnostic paths.

## Capture order

1. I place complete input protection and rails, including support passives, hold-up/bleeder paths, enables and test points.
2. I place MCU power, clocks, reset, USB, debug and EEPROM from the physical-pin table, then generate/check the peripheral clock allocation.
3. I draw the actual supervisor/watchdog/ARM gate network and receiving-domain isolation from [Control and service](circuits/Control_Service.md). I check rail ramps, external-power loss with USB connected, watchdog failure and recovery without a fresh ARM edge.
4. I draw all analog inputs and the protected current-diagnostic path, including permanent shunts, threshold supplies, ADC reference/filter support and qualified enables.
5. I draw DI, load outputs, relays and both isolated buses. I route DO3 timer command through its hardware gate, include conditioned driver FAULT in asynchronous ARM clearing, fit pre-diode output bleeders and define PWM current-sense timing.
6. I compare the captured netlist to these contracts, check every default and crossing, run ERC, and replace allocations with reference-counted BOM data.

## Libraries and release gates

I populate MPN, Manufacturer, Datasheet, Package, Tolerance, Rating and selection evidence in each symbol. I compare physical pins before wiring and land patterns before layout, especially UCC33421 DHA0016A, TPS4H160 PWP0028V, isolated transceiver package variants and relay bottom-view numbering.

My [calculations](calcs/README.md) cover power, input loading, rail health, timing and bounded ideal DC simulation. They verify only their stated models. Native schematic/ERC approval precedes layout; native PCB/DRC, effective capacitance, thermal paths, fuse/inrush/FET SOA, rail sequencing, USB attach/backpower behavior and measured PWM/fault tests precede release.

The first positive-input fault fixture is +36 V at 25 °C, measured tolerance ±0.1 V, 0.5 A source limit, outputs disarmed and exposure up to 60 s only after protection timing/TVS-temperature review. Initial reverse connection is −30 V, ≤0.1 A, 60 s, with discharged rails. I keep these finite fixtures distinct from certified surge/EMC ratings and update the package when implementation evidence changes a target.
