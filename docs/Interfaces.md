# Interface contract

I define the Rev A connections and operating targets here. I have selected exact connector pairs and pin order in the [power](circuits/Power.md), [analog](circuits/Analog.md) and [field I/O](circuits/Field_IO.md) specifications. Reference designators and as-built assembly drawings follow capture. Schematic implementation and measured ratings remain pending; this document is not an as-built wiring drawing.

My [architecture](Architecture.md) describes the circuit blocks, [design decisions](Design_Decisions.md) records the rationale, and [validation plan](Validation.md) defines the acceptance evidence.

## References and isolation

| Domain | Connections and intended separation |
| --- | --- |
| MAIN_GND | DC negative, MCU, USB ground, analog returns, and load returns share one electrical reference |
| DI_COM | All four DI field returns form one isolated group; the channels are not isolated from each other |
| RS485_REF | Dedicated RS-485 bus-side supply, transceiver, and protection return |
| CAN_REF | Independent CAN bus-side supply, transceiver, and protection return |
| Relay contacts | Each relay's COM/NO/NC circuit is separate from its coil/main domain and the other relay |
| Chassis/shield | Installation-specific cable/enclosure bonding provision |

I keep analog and load return paths separated in routing so load current avoids the measurement return, but AI_RETURN, AO_RETURN, and LOAD_RETURN remain part of MAIN_GND. The analog interfaces are single-ended and not galvanically isolated.

Bonding a field reference to MAIN_GND intentionally removes its separation. USB hosts, grounded oscilloscope probes, and external supplies can create the same bond. I will record the actual connection map during qualification.

## Connection summary

| Functional connection | Planned labels | Rev A target |
| --- | --- | --- |
| DC power | VIN+, VIN− | Nominal 12/24 V DC; 9–30 V continuous operation |
| Digital inputs | DI1–DI4, DI_COM | Four positive DC inputs; DI1 supports pulse counting |
| Voltage inputs | AI_V1, AI_V2, AI_RETURN | Two 0–10 V inputs |
| Current inputs | AI_I1, AI_I2, AI_RETURN | Two externally powered 4–20 mA receivers |
| Analog output | AO1, AO_RETURN | One sourced 0–10 V command into at least 10 kΩ |
| Load outputs | DO1–DO4, LOAD_RETURN | Four high-side outputs, 0.5 A/channel simultaneously |
| Relays | COM1/NO1/NC1, COM2/NO2/NC2 | Two SPDT dry contacts; up to 30 V DC, 1 A resistive qualification target |
| RS-485 | D+, D−, RS485_REF | Half-duplex Modbus RTU |
| CAN | CAN_H, CAN_L, CAN_REF | Classic CAN followed by CAN FD qualification |
| Service | USB-C, keyed SWD | Service logic, programming, and debug |

I use the selected terminal ratings/pin order from my circuit specifications and check screw access with the enclosure. All external circuits in this design are low-voltage DC; relay contact ratings do not make the board a mains interface.

## DC supply and USB service

VIN+ accepts supply positive and VIN− accepts supply negative. The fuse, TVS, blocking FET/eFuse, and controlled capacitance precede VFIELD. Reverse-polarity protection is a fault-survival target rather than an alternative operating connection.

VFIELD powers the load outputs. Field-derived rails power relay coils, the external ADC/DAC, isolated port supplies, and analog auxiliary conversion. The power mux supplies MCU service logic from field or USB power.

I intend USB-only mode to support essential service functions while field outputs remain inhibited and field measurements are unavailable. The external ADC/DAC and bus-side supplies remain off. Digital interfaces and readback protection must prevent USB-powered logic from energizing absent field rails.

I will qualify field-only, USB-only, both-present, hot-plug, and source-removal cases. USB ground joins the host to MAIN_GND; the main field supply must not be backpowered through USB, SPI, telemetry, or a field signal.

## Digital inputs

I use positive DC signals referenced to DI_COM. The OFF target is 0–5 V and the ON target is 9–30 V. The 5–9 V interval is a transition region.

A separately powered PNP/sourcing sensor connects its negative reference to DI_COM and its positive-going output to DIx. A dry contact uses an external DC source: source positive through the contact to DIx, and source negative to DI_COM. I will verify input current, sensor leakage, and the final threshold network.

DI1 has a 20 kHz, 50% duty-cycle pulse-counting target on the specified 12/24 V test cable. DI2–DI4 support slower signals with configurable debounce. I will preserve DI1 timing rather than applying the slower channels' long filters to it.

NPN/sinking, bipolar, and AC signals require another reviewed circuit or wiring option; they are outside this base interface.

## Voltage and current inputs

For voltage acquisition, signal positive connects to AI_Vx and signal return to AI_RETURN. The normal range is 0–10 V with a terminal input-impedance goal of at least 500 kΩ. These single-ended inputs require a compatible return potential; a floating or incompatible sensor requires an external isolated interface. A valid 0 V measurement is not a universal broken-wire indication.

For a two-wire current transmitter, I use an external nominal 24 V loop:

1. Loop-supply positive connects to transmitter positive.
2. Transmitter negative connects to AI_Ix.
3. AI_RETURN connects to loop-supply negative.

For an independently powered current-output transmitter, I will follow its specified output and reference topology. Rev A receives current and does not supply loop power.

The 200 Ω Kelvin shunt develops 0.8–4 V over 4–20 mA. A TPS26611 series protector precedes the permanent shunt; TMUX protection is only in the sense branch. Receiver burden is up to 4.25 V at 20 mA before wiring. I will check transmitter compliance, particularly at 12 V. I qualify an overrange goal up to 24 mA: the ADC's arithmetic 25.6 mA endpoint exceeds the protector's minimum current-limit bound.

I will configure low/high current alarms for the selected transmitter. Starting thresholds such as 3.6 and 21 mA apply only where its specification supports them. The receivers share MAIN_GND and are not isolated from each other.

The ±30 V signal-terminal miswire requirement is a future fault qualification target. It depends on the complete active protection and pulse-energy design; it is not the normal measurement range.

## Analog output

AO1 is a sourced voltage-command signal. It connects to a compatible actuator's voltage input, with AO_RETURN connected to the actuator's command reference. The minimum load target is 10 kΩ. The actuator uses its own power supply.

My path is DAC → local gain-four amplifier → unity driver → ADG5401F drain D → protected source S → AO1. A separate protected SFB/DFB path returns terminal voltage directly to the unity driver's inverting input. Powered disable/fault opens both field paths and closes local driver feedback. A permanent 100 kΩ pulldown and the selected POC behavior define the supported disabled state. Analog-valid status and hardware output permission qualify IN; an external pulldown makes it default off.

I target 0–10 V with ±50 mV calibrated terminal accuracy, including zero. I will qualify loading, cable capacitance, shorts, and external faults. This is not a 4–20 mA transmitter or a guaranteed current-sinking lighting interface.

I require a separate protected, attenuated terminal-readback path with powered-off isolation into the MCU ADC. The driver-feedback node becomes an internal voltage while disabled or faulted and cannot substitute for this measurement. I will verify terminal voltage with an independent meter, and qualify the readback clamps and sequencing before relying on telemetry.

## High-side outputs and relays

Each load connects from DOx to LOAD_RETURN. I target four simultaneous 0.5 A continuous outputs over the qualified supply and enclosure-temperature range. Terminal voltage includes the high-side switch and series blocking-diode drops.

The blocking diode limits ordinary positive terminal backfeed. A separate freewheel diode has its anode at LOAD_RETURN and cathode at DOx. This gives relatively slow inductive-current decay; the initial qualification covers on/off loads. Fast-release or proportional/PWM solenoid operation needs additional design and measurement.

Current telemetry is multiplexed, so channel readings are sequential. I will qualify open-load diagnostics on the complete output path because the series diodes affect the result. Overload/short behavior must latch the affected channel off and require explicit recovery. Positive backfeed protection does not imply arbitrary negative-terminal fault survival.

Each relay provides COM, NO, and NC. A deenergized coil leaves COM–NO open and COM–NC closed. I will use COM–NO where the demonstration requires deenergizing to open the load circuit. The contacts are dry and require an external load supply.

My initial contact qualification target is 30 V DC, 1 A resistive with the specified terminals. Inductive contact loads require suppression and separate qualification. A coil-command state is not measured contact feedback.

## Wired communication and command ownership

RS-485 has its own isolated supply and RS485_REF. I will map D+/D− explicitly to transceiver pins because vendor A/B labels vary. The network uses end-only 120 Ω termination and DNP external bias by default, with an optional network at one designated location. The Modbus RTU target range is 9,600–115,200 bit/s.

CAN has another isolated supply and CAN_REF. I will qualify classic CAN at 500 kbit/s first, then FD at 500 kbit/s arbitration and 2 Mbit/s data on a documented short bus with an FD-capable peer. The installation requires two end terminations and a documented reference/shield arrangement.

I keep RS485_REF and CAN_REF separate. Joining them removes port-to-port isolation. Protection returns stay in their respective domains; shield bonding is an installation decision.

I start operation disarmed. All seven actuator gates require PERMISSION: ANALOG_VALID, RESET_OK, WATCHDOG_OK, DISARM_N and ARM_STATE. Required analog-health loss also disarms digital and relay outputs; [Control and service](circuits/Control_Service.md) defines the gate network. Modbus, CAN, or the local demonstration is explicitly selected as command owner. Another interface must not silently take control.

The default owner timeout is 1 s. Owner changes, reset, watchdog failure, invalid power, update mode, or a global fault inhibit energy outputs and clear arming. Recovery requires fresh valid commands and explicit rearming.

My initial RS-485 fixture is ≤5 m with reference conductors and −7..+7 V common mode; the chosen protection narrows the transceiver family's full common-mode window. My CAN FD fixture is ≤5 m at500kbit/s arbitration and2Mbit/s data. I specify DI1's ≤3 m cable, output coils ≤100 mH/0.5 A/12.5 mJ and first qualification loads in [Field I/O](circuits/Field_IO.md).
