# Rev A schematic capture package

I have documented the Rev A circuits, exact component candidates and support values. I use this document as the entry point and the four specifications below as detailed drawing instructions. My circuit plan is concrete; the component evidence and library work below must close before I call the capture package fully frozen. Schematic/ERC review, PCB/DRC, firmware and measured qualification follow capture.

## Preparation status

| Item | Status |
| --- | --- |
| Functions, circuit connections, MCU allocation, connectors and support values | Specified in the circuit documents and four selection files |
| Rail/protection arithmetic and typical AO dynamics | Reproduced with explicitly bounded assumptions |
| Effective capacitor values at operating voltage and temperature | Open: [bank-by-bank evidence](calcs/capacitor_evidence.json) identifies 14 strict capacitance requirements |
| Missing project-local symbols and footprints | Identified in the selection files; create and compare each package before placing/wiring it |
| Captured connectivity, ERC, layout and hardware qualification | Follow the native design; these checks have not run |

I can prepare the hierarchy and libraries from these selections. I close the capacitor evidence before freezing the affected supply/reference circuits; nominal capacitance and a production listing are insufficient evidence. If the selected bank fails its minimum, I revise its part or quantity and recalculate inrush, discharge and stability together.

## Capture references

| Specification | Decisions and implementation detail |
| --- | --- |
| [Power](circuits/Power.md) | Input fuse/TVS/eFuse/FET, inrush, regulator support values, field/USB selection, auxiliary supplies and budgets |
| [Control and service](circuits/Control_Service.md) | MCU physical pins/GPIO, clock, USB-C/ESD/current limit, SWD, EEPROM, health/watchdog/ARM and crossings; [loop status](circuits/Loop_Status.md) |
| [Analog](circuits/Analog.md) | ADC/DAC support, voltage/loop protection, shunts, threshold supplies, filters, AO compensation and readback |
| [Field I/O](circuits/Field_IO.md) | DI timing, high-side diagnostics, relays, isolated supplies, bus protection/termination and mating connectors |
| [Component selections](components/README.md) | Exact ordering codes, values, ratings, packages, quantity allocations and library targets |
| [Interfaces](Interfaces.md) | External wiring and operating requirements |
| [Validation](Validation.md) | Measurements and release acceptance criteria |

I use these circuit specifications for implementation values; they supersede the earlier starting networks in my architecture review. I update related calculations and interface contracts when a design changes. The native schematic will own reference designators, connectivity and the released assembly BOM.

## Fixed scope

I am building a four-layer STM32G474VET6 controller for indoor, enclosed 0–50 °C operation from nominal 12/24 V DC, qualified over 9–30 V. It has four group-isolated DC inputs (DI1 at 20 kHz), two 0–10 V inputs, two externally powered 4–20 mA receivers, one 0–10 V source with protected terminal feedback/readback, four 0.5 A high-side channels, two low-voltage SPDT dry contacts, isolated Modbus RTU, independently isolated CAN/CAN FD, USB service and SWD.

I target 1 kSPS/channel and 100 Hz filtered publication/AO updates. Room-temperature calibrated acquisition targets are ±20 mV and ±32 µA; 0/25/50 °C targets with the same coefficients are ±50 mV and ±80 µA. AO targets ±50 mV into ≥10 kΩ. These are acceptance requirements, not established performance.

I reserve 6 W delivered from 5V_FIELD with 5.75 W in named branches. Main continuous input budget is 3 A; the initial source is current-limited to ≤4 A. My circuit documents fix finite initial cables/loads and source-fault tests. Branch capacity alone does not establish total measured consumption.

## Sheets and rails

| Sheet | Scope |
| --- | --- |
| 00_System | Hierarchy, interfaces, connector overview and shutdown truth table |
| 01_Input_Power | VIN_RAW, input protection, VFIELD, MAIN_GND |
| 02_Rails | 5V_FIELD, ADC_AVDD, 3V3_FIELD_LOGIC, 15V_ANA, VNEG, 5V_SYS, 3V3_DIG, 3V3_MCU_ANA |
| 03_Control_Service | MCU, clock, USB, SWD, EEPROM and service health/permission logic |
| 04_Analog | Voltage/current acquisition, ADC/DAC, gain/driver/switch and terminal readback |
| 05_Digital_Actuation | ISO1212 inputs, TPS4H160 channels, diodes and relay circuits |
| 06_RS485 | Dedicated 5V_RS485_ISO, RS485_REF, transceiver/protection/termination |
| 07_CAN | Dedicated 5V_CAN_ISO, CAN_REF, transceiver/protection/split termination |

I use VFIELD for the protected main input: any block notation VIN_PROTECTED means this same rail and is renamed VFIELD at capture. AI_RETURN/AO_RETURN/LOAD_RETURN join MAIN_GND with controlled routing. DI_COM, RS485_REF and CAN_REF remain separate; each relay contact group is also independent.

FIELD5V_VALID is the service-powered AND of FIELD_OK and ADC5_OK. It enables both isolated converters and the positive boost after field5V settles. ADC_AVDD is independent of that boost, avoiding a startup cycle. ANALOG_VALID adds +15 V, VNEG, reference and field3V3 validity. ACQ_ENABLE_CMD controls loop-protector recovery through a hardware-qualified gate. RS-485 direction uses CROSS_OK, so configuration/status remains available while actuators are disarmed.

## Capture order

1. I place input protection and every complete rail, including support passives, bleeders, enables and test points.
2. I place MCU power/clock/reset/debug/USB/storage from the full physical-pin table, then check a generated CubeMX allocation and peripheral clocks.
3. I draw supervisors, Schmitt stages, watchdog, ARM memory, twelve service AND gates, receiving-domain buffers and ten field command/acquisition/threshold gates. I check USB-only, missing rails, watchdog disable and recovery without a fresh ARM pulse.
4. I draw analog channels completely, including permanent shunts, threshold regulators, ADC reference/filter support, protected output feedback, compensation and independent buffered/clamped readback.
5. I draw DI, high-side/relay circuits and both isolated buses with the exact connector schedule, filtering, protection and termination.
6. I compare the captured netlist with these documents, review all domain crossings/defaults, run ERC, and replace allocation quantities with actual BOM reference counts.

## Libraries and checks

I populate MPN, Manufacturer, Datasheet, Package, Tolerance, Rating and selection evidence in each symbol. I create/check missing project-local symbols while placing the corresponding IC, before wiring its pins. Existing library names are candidates until compared with the package-specific datasheet. I check every footprint before layout, particularly UCC33421 DHA0016A, TPS4H160 PWP0028V, ADG5401F feedback pins, isolated transceiver package variants and relay bottom-view numbering. The selection index does not assert missing assets already exist.

I record the selected capacitor banks/voltage ratings as concrete candidates and verify manufacturer effective capacitance before freezing their schematic values. Nominal capacitance is not effective capacitance. I check exact procurement status and stock before ordering; the selection files are not inventory or fabrication releases.

I reproduce power/measurement arithmetic in [controller_budget.py](calcs/controller_budget.py) and supervisor/USB bounds in [support_checks.py](calcs/support_checks.py). The [analog specification](circuits/Analog.md) records a manufacturer OPAx197 typical-model check with bounded cable capacitance and resistive switch approximations. Simulations and document audits do not verify the complete board or destructive fault energy.

## Gates after capture

I require a reviewed native schematic/netlist and ERC before electrical implementation approval. Before layout/release I close symbol/footprint accuracy, effective capacitor values, isolation spacing, actual thermal paths, fuse/inrush/FET SOA, AO switching/cable transients, regulator ripple/sequencing, USB inrush/suspend, source-removal injection and complete power margins. I run DRC on the PCB and follow the prototype validation matrix.

The initial positive-input fault fixture is 36 V at 25 °C, measured tolerance ±0.1 V, 0.5 A source limit, outputs disarmed and 60 s maximum exposure only after protector timing/TVS-temperature checks. Reverse connection starts at −30 V, ≤0.1 A and 60 s. I do not claim sustained +40 V survival, certified surge/EMC compliance, mains operation or arbitrary cables/loads.

I have fixed the intended circuit architecture and recorded concrete component choices. The capacitor and library preparation gates above are still open. Implementation review and measurements may require controlled revisions; this package does not prove assembled hardware performance.
