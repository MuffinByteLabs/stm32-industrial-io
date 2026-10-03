# STM32 Industrial I/O Controller Rev A — Interface and Wiring Guide

Status: planned functional connections. Connector part numbers, physical pin order, reference designators, mating plugs and board silk are not frozen. Use the final assembly drawing before connecting hardware. This guide does not establish measured ratings or a verified schematic.

The authoritative requirements are [the board plan](STM32_Industrial_IO_Controller_RevA_Plan.md). [Resource reservations](PinMap_CheatSheet.md) and [bring-up](BringUp_Guide.md) cover capture and tests.

## Ground and isolation map

| Domain | Connections | Meaning |
| --- | --- | --- |
| MAIN_GND | DC negative, MCU, USB ground, analog returns, load returns | One shared electrical reference |
| DI_COM | All four digital-input field returns | Input group isolated from MAIN_GND; channels not isolated from one another |
| RS485_REF | Dedicated RS-485 bus-side supply/transceiver/protection | Separate from MAIN_GND, CAN and DI |
| CAN_REF | Separate CAN bus-side supply/transceiver/protection | Separate from MAIN_GND, RS-485 and DI |
| Relay 1 contacts | COM1, NO1, NC1 | Dry contacts separate from coil/main domain |
| Relay 2 contacts | COM2, NO2, NC2 | Separate from coil/main domain and relay 1 |
| Chassis/shield | Planned cable/enclosure bond provision | Exact bonding strategy must be documented for the installation |

AI_RETURN, AO_RETURN and LOAD_RETURN belong to MAIN_GND. Their connector/routing paths keep load current away from ADC returns, but this does not create galvanic analog isolation.

Connecting DI_COM or a bus reference to MAIN_GND removes that separation in the installation. USB, oscilloscope grounds and external sensor supplies can create the same bond. Record the actual connection map during tests. Component isolation ratings alone do not establish board certification.

## Planned terminals

| Connection | Functional labels | Planned use |
| --- | --- | --- |
| Main power | VIN+, VIN− | Nominal 12/24 V DC; 9–30 V continuous operating goal |
| Digital inputs | DI1, DI2, DI3, DI4, DI_COM | Four positive DC signals relative to a shared input return |
| Voltage inputs | AI_V1/AI_RETURN; AI_V2/AI_RETURN | Two single-ended 0–10 V signals |
| Current inputs | AI_I1/AI_RETURN; AI_I2/AI_RETURN | Two externally powered 4–20 mA receivers |
| Analog output | AO1, AO_RETURN | 0–10 V into ≥10 kΩ |
| Load outputs | DO1–DO4, adequately rated LOAD_RETURN terminals | Four positive high-side DC outputs |
| Relay 1 | COM1, NO1, NC1 | SPDT dry-contact circuit |
| Relay 2 | COM2, NO2, NC2 | Separate SPDT dry-contact circuit |
| RS-485 | D+, D−, RS485_REF | Half-duplex bus; explicit transceiver polarity mapping |
| CAN | CAN_H, CAN_L, CAN_REF | Classic CAN/CAN FD physical interface |
| Service | USB-C, keyed SWD | Service logic, programming and debug |

Terminal wire size/current rating, pin order and screw access must be selected together with the enclosure. No channel on this board is a mains interface.

## Main DC supply and USB

Connect supply positive to VIN+ and negative to VIN−. A DC fuse, TVS, reverse-blocking FET/eFuse and controlled capacitance precede VFIELD. Reverse input protection is a fault-survival target; it does not make reverse polarity an ordinary wiring option. Use the specified DC polarity.

VFIELD supplies loads. 5V_FIELD supplies relay coils, external ADC/DAC, isolated converters and analog auxiliary conversion. 5V_SYS selects field/USB service power for the MCU. 3V3_FIELD_LOGIC is distinct from MCU 3.3 V rails.

USB-only mode operates essential service logic and inhibits field outputs. External ADC/DAC and bus-side supplies are field-only. Buffering/monitor protection must prevent USB signals or readback paths from backpowering absent field rails. Field data must be marked unavailable when its supplies are invalid.

Both USB and field power are an intended source-selection test case. They may be used together only after source/signal isolation and ground connections have been reviewed and qualified. USB connects the host to MAIN_GND. A disconnected main supply must not rise through USB, SPI or a field signal source.

## Digital inputs

The base wiring accepts positive 9–30 V DC ON signals relative to DI_COM. Guaranteed OFF target is 0–5 V; the region between 5 and 9 V is a transition region.

For a separately powered PNP/sourcing sensor, connect its reference negative to DI_COM and its positive-going output to the selected DI terminal. Verify sensor leakage/current compatibility and the final threshold network. A dry contact requires an external DC source: source positive → contact → DI; source negative → DI_COM.

DI1 is the pulse-counting channel, with a 20 kHz, 50% duty-cycle target on the specified 12/24 V bench cable. DI2–DI4 support slower sensors/switches with configurable debounce. Do not impose the same long filter on DI1.

The four returns form one isolated group. For example, an external supply tied to DI_COM can preserve group separation; tying DI_COM to the board DC negative intentionally removes it. NPN/sinking, bipolar or AC inputs require a separately reviewed circuit/wiring option; they are not established by the base interface.

## Voltage inputs

Connect signal positive to AI_V1 or AI_V2 and signal return to AI_RETURN. The normal range is 0–10 V; terminal input-impedance goal is at least 500 kΩ.

These are single-ended main-domain inputs. ADS8684A input-ground pins are near the local ADC reference, not arbitrary floating negative terminals. Use an external isolated transmitter when sensor return potential is incompatible.

A 0 V reading may be valid. Do not treat it universally as a broken wire. Signal-terminal ±30 V miswire survival is a future qualification target requiring the complete active protector, clamp and pulse-limiting design; do not use it as an ordinary input range.

## Current-loop inputs

The board receives current; it does not provide loop power in Rev A.

For a two-wire transmitter:

1. External nominal 24 V loop positive connects to transmitter positive.
2. Transmitter negative connects to AI_I1 or AI_I2.
3. AI_RETURN connects to loop-supply negative.
4. Verify transmitter voltage requirement, cable drop and total receiver burden before operation.

For an independently powered current-output transmitter, connect its current output to AI_Ix and its reference/return to AI_RETURN as its manufacturer specifies. Confirm the output topology and required common reference before connecting it.

The planned 200 Ω Kelvin shunt gives 0.8–4 V at 4–20 mA and 4 V shunt burden at 20 mA. Protection-switch/series resistance adds burden. The ADC 0–5.12 V range covers up to 25.6 mA before other circuit limits. A 12 V system may not provide enough loop compliance for the selected sensor; the demonstration uses an externally powered 24 V loop.

Low/high alarm thresholds are sensor-specific. Approximately 3.6 mA and 21 mA are starting values only for compatible transmitters. The two receivers share MAIN_GND and are not isolated from each other or the MCU. A voltage accidentally placed across an unprotected shunt can dissipate destructive power; active disconnection and pulse-energy qualification are part of the planned circuit.

## Analog output

Connect AO1 to the actuator's voltage-command input and AO_RETURN to its command reference. Use a compatible voltage-input actuator with ≥10 kΩ load. Confirm its own power wiring and manufacturer interface requirements; AO1 is a command signal, not actuator power.

Planned path: DAC → amplifier → separately controlled default-off disconnect → TMUX drain D → protected source S → AO1. A terminal pulldown defines the disabled voltage in the supported high-impedance/unloaded case. Rail monitoring, external watchdog/reset status and explicit arming qualify the disconnect.

The planned DAC supplies 0–2.5 V to an amplifier of gain near four, with +15 V and small negative bias. Target terminal accuracy is ±50 mV after calibration, including zero and full scale. Qualify minimum load, cable capacitance, short/recovery and external fault cases.

AO_READBACK is protected amplifier-side telemetry before the disconnect. It cannot prove actual terminal voltage, contact/disconnect continuity, or every external wiring fault. Measure the terminal independently during qualification. Do not connect a divider around the protector without its own fault/unpowered-MCU protection.

This output is not a 4–20 mA transmitter or a guaranteed current-sinking dimming interface. Verify the selected actuator expects the specified sourced voltage command.

## Four high-side load outputs

Wire DOx → load positive; load negative → LOAD_RETURN. Each output switches protected positive field power, with a target of 0.5 A continuously per channel, all four simultaneously over the tested 0–50 °C enclosure conditions.

Rev A includes a series positive-backfeed blocking diode per channel and a load-side freewheel diode, with its anode at LOAD_RETURN and cathode at DOx. Terminal voltage is approximately VFIELD minus switch/diode drops. External load wiring must remain within the reviewed diode and fault-energy envelope.

Freewheeling gives relatively slow inductive-current decay; it is not a fast-release solenoid stage. The initial release is qualified for on/off loads. High-frequency PWM/proportional operation needs further design and measurements.

Current sensing is multiplexed; channel readings are sequential. Open-load behavior must be qualified on the assembled path because series diodes alter diagnostics. Positive backfeed protection does not establish arbitrary negative-terminal fault survival. A stalled/shorted load latches its channel off and requires explicit recovery.

## Relay dry contacts

Each relay has COM, NO and NC. With its coil deenergized, COM–NO is open and COM–NC is closed. Use COM–NO for the demonstration so deenergizing the coil opens its load circuit.

The contacts are dry: apply the external load supply through COM/NO or COM/NC. Do not assume the board supplies voltage there or join the contact circuit to MAIN_GND unless the installation intentionally requires it.

Initial board qualification target is up to 30 V DC, 1 A resistive, with specified terminals/wiring. Inductive contact loads need external suppression and separate qualification. Coil-command telemetry is not measured contact-state feedback.

## Independently isolated wired ports

RS-485 uses D+/D− and RS485_REF, with one dedicated regulated isolated supply. Connect the reference as required by the bus installation. Final drawings must map differential polarity to the actual transceiver pins; vendor A/B labels alone are insufficient. Enable 120 Ω termination only at bus ends. Use reviewed bias at one designated network location. Initial software qualification is Modbus RTU at 19,200/115,200 bit/s.

CAN uses CAN_H/CAN_L and CAN_REF with another isolated supply. Use two end terminations, a documented cable/reference/shield arrangement and an appropriate second node. Qualify classic CAN at 500 kbit/s before FD at 500 kbit/s arbitration/2 Mbit/s data on the documented short bus.

Do not join RS485_REF and CAN_REF; doing so removes port-to-port isolation. Protection returns stay in their corresponding islands. Shield/chassis bonding is an installation decision, not an automatic main-ground connection.

## Enabling operation

Start disarmed. General hardware permission is equivalent to FIELD_VALID AND RESET_OK AND WATCHDOG_OK AND ARM. AO additionally requires FIELD_ANALOG_VALID. Explicitly select Modbus, CAN or local demonstration as the command owner.

Commands from other interfaces must not silently take control. Default owner timeout is 1 s. Owner change, reset, watchdog failure, invalid power, update mode or global fault inhibits energy outputs and clears arming. Recovery requires fresh valid commands and explicit rearming.

Use the hardware output-inhibit control during bench service. After wiring changes, repeat domain, polarity, load and permission checks from the bring-up guide. Publish only the ratings and wiring cases that the completed board actually passes.
