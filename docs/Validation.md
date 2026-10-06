# Verification and qualification

I use this plan to define the evidence needed to release Rev A. Schematic capture, PCB layout, firmware implementation, and bench qualification are still pending. The values below are acceptance targets, not measured performance.

My [pre-schematic review](Engineering_Review.md), [capture checklist](Schematic_Capture.md), [architecture](Architecture.md), [design decisions](Design_Decisions.md), and [interface contract](Interfaces.md) define the design under test. Before first power, I will freeze the exact schematic, BOM, assembly variant, firmware build, instrument setup, and pass/fail limits.

## Completion milestones

I follow the [fixed scope](Scope.md) and [implementation plan](Implementation_Plan.md), starting with M0 preparation before the four operating/qualification milestones. The complete hardware scope remains four digital inputs, two voltage inputs, two current receivers, four high-side outputs and two relays, with both isolated buses. Milestones sequence implementation and evidence; they do not change component selections, electrical targets or full-release requirements.

| Milestone | Conditions and operating mode | Evidence required to close the milestone |
| --- | --- | --- |
| M0 — Preparation | Capture and fabrication preparation before the first prototype order | Scope/resource/library and effective-capacitance evidence, recorded architecture disposition, complete native design/reviews and coherent manufacturing/assembly package |
| M1 — Modbus controller | Nominal 12/24 V board power and recorded room temperature; calibrated acquisition, basic pulse counting, on/off outputs and Modbus RTU; DO3 static off/on only | End-to-end fixture operation, controller USB diagnostic service and usable host/calibration workflow, channel mapping, independent analog verification at the ±20 mV / ±32 µA targets, command timeout and fresh-rearm captures, build and board identity |
| M2 — Classic CAN telemetry | The established M1 fixture plus the documented classic CAN peer/cable/termination; Modbus retains actuator ownership | Versioned peer traffic, bracketed coherent acquisition/validity, latched inhibition of all outputs on enabled-mode bus-off and no automatic restoration after recovery. Guarded CAN control remains unavailable until its separate command contract and tests are released |
| M3 — Bounded PWM | DO3 at 100 Hz, 10–90% commanded duty plus static endpoints; nominal 12/24 V and recorded room temperature first | Qualified resistive fixture, phase-aware diagnostic validity, measured pulse shape/current, shutdown while the timer runs and fresh-command/rearm behavior; a specific compatible LED assembly only after its separate review |
| M4 — Full Rev A qualification | Full 9–30 V and 0–50 °C targets, combined loading, defined faults and CAN FD | All remaining matrices below, enclosure thermal evidence, full PWM envelope, CAN FD on the specified fixture, at least three qualified units and 24 h logged operation |

I record each milestone as pending until its evidence exists. A successful M1 demonstration is a nominal-condition prototype result, not qualification of the complete supply, temperature, fault or PWM envelope. I maintain a [portfolio evidence guide](Portfolio_Evidence.md) and a [validation record template](templates/Validation_Record.md) alongside this plan.

## End-to-end fixture and service tool

I use one machine-monitor/actuator bench fixture throughout the milestones. A pulse/contact or PNP sensor represents machine state; known voltage/current stimuli represent analog sensors; a reviewed 24 V lamp or bounded coil represents an actuator. A Modbus host reads calibrated values and commands the outputs. The initial PWM load is a suitably rated resistor, rather than an unreviewed lamp, coil or electronic load. I select and document actual fixture parts before testing; this plan makes no claim about an unselected load.

| Fixture connection | Setup I record |
| --- | --- |
| Board supply | Actual connector voltage, source current limit, leads and return path; nominal 12/24 V for M1, within the existing continuous input budget |
| Voltage inputs | Independent reference/source and meter, source impedance within the interface limit, signal to AI_Vx and compatible return to AI_RETURN |
| Current inputs | Externally powered nominal 24 V loop: supply positive → transmitter/source → AI_Ix; AI_RETURN → loop-supply negative; include transmitter headroom, wiring and the receiver's up-to-4.25 V burden at 20 mA |
| Digital-input group | Positive sensor/contact stimulus relative to DI_COM; document its separate source and actual bonds. Rev A accepts sourcing/PNP signals and does not supply isolated sensor power |
| High-side outputs | Reviewed load from DOx to LOAD_RETURN; record current/inrush and suppression. Begin with one on/off path before replicated channels and combined loading |
| Relay contacts | Separate COM/NO/NC wiring and load source; use COM–NO for a demonstration that opens when deenergized. Measure contacts rather than infer them from coil-command telemetry |
| Wired peers | Cable, node/reference connections and end termination; record optional bias/choke population and the RS485_REF/CAN_REF boundaries |
| USB and instruments | Host ground, adapter isolation, supply grounds and scope/probe-earth connections; record any bond that bridges an intended domain before measurement |

The board does not supply current-loop power. AI_RETURN and LOAD_RETURN are both MAIN_GND, with different routed current paths; the analog inputs are not galvanically isolated. DI_COM, RS485_REF and CAN_REF remain their own domains unless the documented fixture intentionally bonds them. I do not claim isolation from a test whose host, adapter, power supply or probe bridges the barrier.

I require a usable diagnostic/calibration workflow and controller USB diagnostic service for M1. My initial [host tool](../tools/diagnostics/README.md) uses Modbus RTU over RS-485; it is not a USB CDC adapter. Its development simulation cannot close a hardware test. I document the USB service framing, supported commands and host-access method before testing that transport; the target USB service and any USB host adapter remain pending until implemented and measured.

The complete workflow will identify the board and firmware, display raw/calibrated inputs with units, timestamps and validity, expose explicit arm/disarm and permitted on/off commands, report current/fault status, and export recorded data. Calibration edits must be validated and tied to versioned coefficients and independent verification points. Read-only tool traffic must not acquire command ownership or renew an actuator lease. I record which transport/tool produced each result. Logs support the record; I use instrument captures where physical voltage/current or timing must be established.

## Commissioning before normal actuator commands

Normal Modbus commands require implemented and physically qualified actuator capabilities. I collect the first bounded physical evidence through a separate, pending commissioning-test build/procedure, rather than pretending those capabilities are qualified before testing. Its qualification flags remain zero and it advertises no external energizing-command capability.

After the native design review and unloaded power/default-off checks, I use reviewed current-limited loads and a finite technician-triggered internal test sequence. The test retains all health/watchdog/PERMISSION/ARM requirements, uses the shared actuator code intended for the operating firmware, stops in a disarmed state and cannot repeat or rearm through unattended traffic. I record fitted channels, exact code/assembly identity, stimulus limits, maximum test duration, stop conditions, output captures and recovery. This procedure and firmware still need implementation and review before any first load test.

I use those narrow measured records to justify a reviewed, read-only qualification-metadata update for the matching assembly and actuator-code identity. The normal host configuration path cannot set qualification flags. A capability bit is not permission to claim an untested channel or wider load/supply/temperature envelope; staged population or testing of one replicated path alone does not qualify the complete mapped function.

Only then do I test normal guarded Modbus ARM/SET/timeout/disarm/recovery on the actual target. The commissioning evidence does not replace production-command-path tests, M1 completion or M4 qualification. A changed actuator implementation or assembly requires review/retest before its metadata can be reused.

## Command-loss and rearm demonstration

I close this part of M1 before claiming a usable controller. I start with a reviewed low-energy resistive or lamp load, validate configuration/power and READY, and select the Modbus owner. I ARM with all commands zero, confirm ARMED, then send a fresh SET for the intended load. I record the last accepted owner command, configured lease (initially 1 s), PERMISSION/gated command transitions, load voltage/current and relay contact behavior where fitted.

1. I stop valid owner commands while continuing read-only monitoring; I also exercise invalid/unrelated traffic separately. Neither traffic class may renew the lease.
2. I require actuator drive inhibition within the configured timeout, capture the physical high-side response and the relay-coil command, and record mechanical COM–NO release separately. Relay command telemetry is not contact-position feedback.
3. I resume traffic without arming and verify outputs stay inhibited. I clear/discard stale commands and timer state. After the cause is removed, I explicitly DISARM to acknowledge recoverable latches, confirm READY and read fresh boot/epoch/sequence values. I ARM with all commands zero, confirm ARMED, then send a fresh SET restoring only the intended outputs.
4. I repeat a bounded active-output shutdown with reset and an intentional watchdog-service interruption. Loss/recovery of health must clear ARM; a stale GPIO or automatically running timer must not restore permission. PWM repeats these checks in M3.

I document how accepted-command timestamps and captures are synchronized, measurement uncertainty and observed delays. A demonstration video alone does not establish a timeout limit or the hardware watchdog path. An unexpected pulse, backpower condition or restoration without fresh arming stops the test and creates a tracked issue.

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
| Service rails | Loaded voltage/ripple, startup order, G30 trip/release/reset delay, ADC5_OK trip AND re-entry margins, DGKR regulator/inductor heat and validity signals |
| MCU and USB | SWD identity/programming, clocks/reset, diagnostic firmware, USB service behavior, and build identity |
| Power and USB sequencing | External-power startup/removal with USB absent/connected; PGOOD-to-EN levels/leakage, rapid collapse EN≤VIN+0.3 V and complete boost bulk precharge; USB attach/detach, unpowered leakage and independent digital-rail collapse. Full USB characteristics require3.0–3.6 V; G30 does not enforce an exact3.0 V detach threshold |
| Field analog supplies | ADC and field-logic rails, +15 V and protection-threshold rails, and protector-on/ADC-off behavior |
| Inputs and outputs | DI thresholds/counting, raw analog acquisition, each on/off output, current telemetry and relay contacts for M1; DO3 PWM follows in M3 |
| Wired communication | RS-485/Modbus in M1, classic CAN in M2, then CAN FD in M4 with recorded cables, references, termination, and recovery behavior |
| Combined loading | Begin bounded nominal loading, then qualify four simultaneous 0.5 A outputs, active communication, switching disturbance, enclosure temperature, and command/watchdog interruption in M4 |

USB alone must not power the MCU or field circuits. The self-powered USB device must attach only with valid external power and VBUS, and disconnect correctly when either prerequisite disappears. I will measure residual voltages and injection paths rather than assuming an unpowered rail is instantly zero. Unexpected backpower, output pulses, excessive current, unstable rails, or a domain short stop the sequence until resolved.

## Analog accuracy and timing

I will calibrate each input at two points, then verify independent points with the source/meter uncertainty recorded. Calibration records will include board identity, coefficient version, and CRC. I will reject calibration that conceals clipping, an incorrect shunt, or an unstable reference.

M1 establishes the room-temperature nominal-supply result and basic pulse acquisition. The full DI1 20 kHz fixture is an M4 technical target. M4 repeats the same room-temperature coefficients at the temperature/supply/combined-load conditions below; I do not recalibrate each temperature and describe that as performance with unchanged coefficients.

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

M3 begins the bounded nominal-supply, room-temperature qualification. The full supply/temperature/combined-load matrix remains an M4 requirement; the selected hardware, frequency, duty window and initial load restrictions remain unchanged.

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

M1 includes the reviewed command-loss/reset/watchdog demonstration above. Broader electrical faults require the completed protection/thermal review and their defined fixtures; they are not an early bring-up shortcut. M4 closes every remaining requirement below. I retain the full multiunit and soak targets even when an earlier portfolio milestone has a smaller evidence set.

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
| Protocol faults | Malformed/CRC-invalid/read-only traffic cannot renew the lease; enabled-mode CAN bus-off disarms and latches all outputs; recovery cannot restore them without explicit acknowledgement, zero-command ARM and fresh SET |
| Repeatability/soak | At least three boards and 24 h logged operation; repeatable calibration and no unexplained resets |

I plan ESD, EFT, surge and emissions tests separately for the intended installation. Bench faults and component isolation ratings do not establish standards compliance or automotive qualification.

## Test records and release claims

Each record will identify the milestone, board serial/revision, assembly variant, firmware build, date, equipment, wiring/probes, ambient temperature, stimulus, acceptance limit, measurement uncertainty, captures/logs, result, and rework. I copy the [record template](templates/Validation_Record.md) for each test/condition and keep the actual record with its evidence. An unperformed test stays pending; an analytical estimate, a prepared procedure and a measured pass have separate status.

I will publish operating limits and performance claims only for the conditions actually qualified. If a target changes, I will update the architecture, interfaces, firmware bounds, and test plan together.

Before a full Rev A release I reconcile every requirement with passed evidence or a formally revised contract. I verify repeatability across at least three units, calibration identities and 24 h logged operation with no unexplained resets. An unresolved failure or a pending required test is not converted into a pass by completing a demonstration milestone.
