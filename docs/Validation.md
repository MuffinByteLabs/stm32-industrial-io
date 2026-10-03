# Verification and qualification

I use this plan to define the evidence needed to release Rev A. Schematic capture, PCB layout, firmware implementation, and bench qualification are still pending. The values below are acceptance targets, not measured performance.

My [pre-schematic review](Engineering_Review.md), [capture checklist](Schematic_Capture.md), [architecture](Architecture.md), [design decisions](Design_Decisions.md), and [interface contract](Interfaces.md) define the design under test. Before first power, I will freeze the exact schematic, BOM, assembly variant, firmware build, instrument setup, and pass/fail limits.

## Design review before assembly

I will review exact component ordering codes, package drawings, pin assignments, required support components, rail limits, startup/shutdown behavior, and worst-case power and thermal budgets. The review includes the MCU peripheral allocation, ADC error budget, current-loop burden, protector thresholds, isolated-supply loading, and hardware output-inhibit path.

I will run ERC and DRC against the matching native design files and inspect the four-layer layout for return paths, switching loops, current-carrying geometry, isolation boundaries, and connector protection. Exceptions require a recorded circuit-specific justification. I will verify the exported manufacturing package against the frozen source revision before ordering.

The repository audit checks documents, reference identity, hashes, and local library paths. It does not establish electrical correctness. The KiCad workflow reports missing native files as checks not run.

## First-article bring-up

I will use a current-limited DC supply, multimeter, oscilloscope, temperature probes, SWD probe, calibrated voltage/current stimuli, suitable loads, pulse source, and RS-485/CAN peers. I will document USB, supply, probe-earth, and isolated-domain connections before taking measurements.

I will begin disarmed with external loads disconnected and AO disabled. Each stage must complete before I enable the next circuit block.

| Stage | Evidence I will collect |
| --- | --- |
| Assembly and continuity | Part values/orientation, solder joints, exposed pads, rail shorts, terminal mapping, and separation of DI_COM, RS485_REF, CAN_REF, and relay contacts |
| Input protection | Startup current, protected voltage, reverse-blocking behavior, and current-limit operation with controlled branch loading |
| Service rails | Loaded voltage, ripple at device pins, startup order, reset timing, and validity signals |
| MCU and USB | SWD identity/programming, clocks/reset, diagnostic firmware, USB service behavior, and build identity |
| Source sequencing | Field only, USB only, both present, either source removed, and hot-plug; source currents and inactive-rail decay |
| Field analog supplies | ADC/DAC and field-logic rails, positive/negative analog supplies, and protector-on/ADC-off behavior |
| Inputs and outputs | DI thresholds/counting, raw analog acquisition, AO stability/terminal voltage, each load output, current telemetry, and relay contacts |
| Wired communication | RS-485/Modbus, classic CAN, then CAN FD with recorded cables, references, termination, and recovery behavior |
| Combined loading | Four simultaneous 0.5 A outputs, active communication, switching disturbance, enclosure temperature, and command/watchdog interruption |

USB-only operation must leave field outputs inhibited and field measurements unavailable. I will measure residual voltages and injection paths rather than assuming an unpowered rail is instantly zero. Unexpected backpower, output pulses, excessive current, unstable rails, or a domain short stop the sequence until resolved.

## Analog accuracy and timing

I will calibrate each input at two points, then verify independent points with the source/meter uncertainty recorded. Calibration records will include board identity, coefficient version, and CRC. I will reject calibration that conceals clipping, an incorrect shunt, or an unstable reference.

| Function | Stimulus and condition | Acceptance target |
| --- | --- | --- |
| 0–10 V inputs | 0, 2.5, 5, 7.5, and 10 V after room-temperature calibration | ±20 mV |
| 4–20 mA inputs | 4, 8, 12, 16, and 20 mA after room-temperature calibration | ±32 µA |
| Input temperature behavior | Repeat at 0, 25, and 50 °C using the room-temperature coefficients | Voltage ±50 mV; current ±80 µA |
| 0–10 V output | Zero, intermediate points, and full scale into at least 10 kΩ | ±50 mV at the actual terminal |
| Acquisition and reporting | All four input channels active | 1 kSPS/channel acquisition; 100 Hz calibrated publication |
| Pulse input DI1 | 20 kHz, 50% duty cycle, documented 12/24 V source and cable | No lost or extra counts over the recorded interval |

I will repeat analog checks with outputs inactive, switching, and fully loaded. I will record settled errors and switching transients separately, together with filter settings and useful bandwidth. ADC resolution does not establish system accuracy.

I will compare the independently protected AO terminal readback against a calibrated meter; the switch's internal feedback node is not terminal proof when disabled. I will check enabled accuracy, disabled behavior, load and cable effects, and local-feedback transfer during faults. For current inputs, I budget up to 4.25 V receiver burden at 20 mA plus wiring and verify startup with the current source already connected, recovery from compliance, and any negative-fault reset.

## Fault and recovery qualification

I will define source impedance, current limits, duration, fixture energy, measurement bandwidth, and recovery criteria before fault injection. I will start with low-energy characterization, then perform the reviewed qualification condition.

| Planned test | Condition and required behavior |
| --- | --- |
| Supply range | 9, 12, 24, and 30 V under combined rated loading; valid operation and acceptable temperatures |
| Main supply faults | −30 V reverse input and initial +36 V positive fault at 25 °C under documented source limits/duration; TVS current/temperature, protected behavior, and fresh rearming; other temperatures require a separate reviewed limit |
| Analog miswire | ±30 V at each signal terminal, powered and unpowered, for 60 s; no damage/backpower and accurate recovery |
| Analog output faults | Open circuit, return short, reviewed cable capacitance, and external ±30 V; stable protection and explicit recovery |
| Load short/overload | Controlled fixture per channel; hardware current limiting followed by a latched fault and explicit recovery |
| Inductive switch-off | Specified real load; terminal voltage/current decay and diode/switch energy and temperature within reviewed limits |
| Positive output backfeed | Field supply absent; no unintended rise of VFIELD or service rails |
| Reset, debug halt, update, and watchdog interruption | Physical output permission removed; fresh valid commands and arming required |
| Command-owner timeout | Stop the selected owner's valid commands; inhibit energy outputs within the configured timeout, initially 1 s |
| Configuration interruption/corruption | Recover a valid configuration copy or remain disarmed with a reported fault |
| Protocol faults | Invalid frames, CRC errors, traffic load, and CAN bus-off; no unintended output change and controlled recovery |
| Repeatability and soak | At least three boards and at least 24 h of logged operation; no unexplained resets and repeatable calibration |

I will treat ESD, EFT, surge, and emissions work as a separate application-specific test plan. Bench miswire survival and component isolation ratings do not establish standards compliance or automotive qualification.

## Test records and release claims

Each record will identify the board serial/revision, assembly variant, firmware build, date, equipment, wiring/probes, ambient temperature, stimulus, acceptance limit, measurement uncertainty, captures/logs, result, and rework. An unperformed test stays pending.

I will publish operating limits and performance claims only for the conditions actually qualified. If a target changes, I will update the architecture, interfaces, firmware bounds, and test plan together.
