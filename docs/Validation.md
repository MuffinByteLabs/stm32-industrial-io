# Verification and qualification

I use this plan to define the evidence needed to release Rev A. Schematic capture, PCB layout, firmware implementation, and bench qualification are still pending. The values below are acceptance targets, not measured performance.

My [pre-schematic review](Engineering_Review.md), [capture checklist](Schematic_Capture.md), [architecture](Architecture.md), [design decisions](Design_Decisions.md), and [interface contract](Interfaces.md) define the design under test. Before first power, I will freeze the exact schematic, BOM, assembly variant, firmware build, instrument setup, and pass/fail limits.

## Design review before assembly

I will review exact component ordering codes, package drawings, pin assignments, required support components, rail limits, startup/shutdown behavior, and worst-case power and thermal budgets. The review includes the MCU peripheral allocation, ADC error budget, current-loop burden, protector thresholds, isolated-supply loading, and hardware output-inhibit path.

I will run ERC and DRC against the matching native design files and inspect the four-layer layout for return paths, switching loops, current-carrying geometry, isolation boundaries, and connector protection. Exceptions require a recorded circuit-specific justification. I will verify the exported manufacturing package against the frozen source revision before ordering.

The repository audit checks documents, reference identity, hashes, and local library paths. It does not establish electrical correctness. The KiCad workflow reports missing native files as checks not run.

## First-article bring-up

I will use a current-limited DC supply, multimeter, oscilloscope, temperature probes, SWD probe, calibrated voltage/current stimuli, suitable loads, pulse source, and RS-485/CAN peers. I will document USB, supply, probe-earth, and isolated-domain connections before taking measurements.

I will begin disarmed with external loads disconnected and all output commands disabled. Each stage must complete before I enable the next circuit block.

| Stage | Evidence I will collect |
| --- | --- |
| Assembly and continuity | Part values/orientation, solder joints, exposed pads, rail shorts, terminal mapping, and separation of DI_COM, RS485_REF, CAN_REF, and relay contacts |
| Input protection | Startup current, protected voltage, reverse-blocking behavior, and current-limit operation with controlled branch loading |
| Service rails | Loaded voltage, ripple at device pins, startup order, reset timing, and validity signals |
| MCU and USB | SWD identity/programming, clocks/reset, diagnostic firmware, USB service behavior, and build identity |
| Power and USB sequencing | External-power startup/removal with USB absent/connected; USB attach/detach while powered; USB-connected/unpowered state; injection and rail decay |
| Field analog supplies | ADC and field-logic rails, +15 V and protection-threshold rails, and protector-on/ADC-off behavior |
| Inputs and outputs | DI thresholds/counting, raw analog acquisition, each on/off output, DO3 PWM, current telemetry and relay contacts |
| Wired communication | RS-485/Modbus, classic CAN, then CAN FD with recorded cables, references, termination, and recovery behavior |
| Combined loading | Four simultaneous 0.5 A outputs, active communication, switching disturbance, enclosure temperature, and command/watchdog interruption |

USB alone must not power the MCU or field circuits. The self-powered USB device must attach only with valid external power and VBUS, and disconnect correctly when either prerequisite disappears. I will measure residual voltages and injection paths rather than assuming an unpowered rail is instantly zero. Unexpected backpower, output pulses, excessive current, unstable rails, or a domain short stop the sequence until resolved.

## Analog accuracy and timing

I will calibrate each input at two points, then verify independent points with the source/meter uncertainty recorded. Calibration records will include board identity, coefficient version, and CRC. I will reject calibration that conceals clipping, an incorrect shunt, or an unstable reference.

| Function | Stimulus and condition | Acceptance target |
| --- | --- | --- |
| 0–10 V inputs | 0, 2.5, 5, 7.5, and 10 V after room-temperature calibration | ±20 mV |
| 4–20 mA inputs | 4, 8, 12, 16, and 20 mA after room-temperature calibration | ±32 µA |
| Input temperature behavior | Repeat at 0, 25, and 50 °C using the room-temperature coefficients | Voltage ±50 mV; current ±80 µA |
| Acquisition and reporting | All four input channels active | 1 kSPS/channel acquisition; 100 Hz calibrated publication |
| Pulse input DI1 | 20 kHz, 50% duty cycle, documented 12/24 V source and cable | No lost or extra counts over the recorded interval |

I will repeat analog checks with outputs inactive, switching, and fully loaded. I will record settled errors and switching transients separately, together with filter settings and useful bandwidth. ADC resolution does not establish system accuracy.

For current inputs, I budget up to 4.25 V receiver burden at 20 mA plus wiring and verify startup with the current source already connected, recovery from compliance, and any negative-fault reset.

## PWM qualification

| Test | Condition and evidence |
| --- | --- |
| Frequency/duty | DO3 at 100 Hz and commanded 10/25/50/75/90%, plus static off/on; capture input command, gated input, output voltage and current |
| Finite edge behavior | 9/12/24/30 V and 0/25/50 °C, with three other channels loaded; compare measured delays, rise/fall, plateaus and delivered load power against calculations |
| Load compatibility | Rated resistor fixture first, then a specific LED assembly; ≤0.5 A instantaneous load, bounded inrush and recorded light/power response |
| Current diagnostics | Phase-aware settled on-window, selector changes, disabled states and invalid sample windows; compare on-state samples with an independent current measurement |
| Thermal | PWM switching plus three continuous 0.5 A channels in the intended enclosure; high-side package, diodes, supply and PCB temperatures within reviewed margins |
| Shutdown/recovery | Remove rails, command lease or watchdog health while timer runs; hardware gate removes drive and no stale duty returns after recovery without fresh command/arm |

I set measured timing tolerances and thermal limits from the captured circuit and fixture before asserting a qualified envelope. Calculated 100 Hz feasibility is not an already demonstrated system rating. Motors and proportional-solenoid PWM require separate qualification.

## Fault and recovery qualification

I define source impedance, limits, duration, energy, bandwidth and recovery criteria before fault injection, beginning with low-energy characterization.

| Planned test | Condition and required behavior |
| --- | --- |
| Supply range | 9/12/24/30 V connector input under combined rated loading; VFIELD ≥8.4 V at 9 V, remaining input-current margin, rail validity and acceptable temperatures |
| Main supply faults | Initial −30 V reverse connection from discharged rails and +36 V at 25 °C under documented source/duration limits; monitored TVS/protection behavior and fresh rearming |
| Analog miswire | ±30 V at each input terminal, powered/unpowered, 60 s in a reviewed current-limited fixture; no damage/backpower and accurate recovery |
| Load short/overload | Controlled fixture per channel, including PWM on-window; hardware current limiting then latched command-off and explicit recovery |
| Inductive switch-off | Specified on/off load; measured decay and diode/switch energy/temperature within reviewed limits |
| Positive output backfeed | External supply absent; no unintended VFIELD or logic-rail rise |
| Reset, debug halt, update and watchdog interruption | Physical permission removed; fresh valid commands and arming required |
| Command-owner timeout | Valid commands stop; inhibit outputs within configured timeout, initially 1 s |
| Configuration corruption/interruption | Recover a valid copy or remain disarmed with reported fault |
| Protocol faults | Malformed traffic, CRC errors, load and CAN bus-off; no unintended output changes |
| Repeatability/soak | At least three boards and 24 h logged operation; repeatable calibration and no unexplained resets |

I plan ESD, EFT, surge and emissions tests separately for the intended installation. Bench faults and component isolation ratings do not establish standards compliance or automotive qualification.

## Test records and release claims

Each record will identify the board serial/revision, assembly variant, firmware build, date, equipment, wiring/probes, ambient temperature, stimulus, acceptance limit, measurement uncertainty, captures/logs, result, and rework. An unperformed test stays pending.

I will publish operating limits and performance claims only for the conditions actually qualified. If a target changes, I will update the architecture, interfaces, firmware bounds, and test plan together.
