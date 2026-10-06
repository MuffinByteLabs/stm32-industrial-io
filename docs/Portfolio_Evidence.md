# Portfolio evidence and application demonstration

I am developing this controller as a second portfolio piece that demonstrates industrial sensing, low-voltage actuation and complete embedded delivery. I intend to show one working system with traceable measurements. The architecture, circuit selections and calculations exist; native hardware, application firmware, target USB service and prototype results are still pending. My [diagnostic host-tool documentation](../tools/diagnostics/README.md) records the separate implementation/development-test status of its Modbus RTU CLI; simulated tool checks are not physical board evidence.

I follow the [fixed scope](Scope.md) and [implementation plan](Implementation_Plan.md). I keep the full selected hardware scope: four group-isolated digital inputs, two 0–10 V inputs, two externally powered 4–20 mA receivers, four diagnosed high-side outputs, two SPDT relays, independently isolated RS-485 and CAN, USB service and hardware output permission. I do not add unrelated blocks to collect feature names. Completion milestones sequence the same design rather than replace its electrical targets.

## One coherent application

I use a machine-monitor/actuator bench fixture: a contact or PNP/pulse sensor represents machine state, voltage/current stimuli represent analog sensors, and a reviewed 24 V lamp or bounded on/off coil represents an actuator. A Modbus host commands the board and records calibrated feedback. USB provides service/calibration visibility; a CAN peer follows after the first complete Modbus mode. DO3 PWM uses a separately reviewed resistor fixture first.

I define the actual fixture, source limits and safe load state before testing. I document external nominal 24 V current-loop power and receiver burden, compatible MAIN_GND analog returns, separate DI_COM and bus references, termination and all host/probe ground bonds. Rev A does not power its current loops, its analog inputs are not isolated, and connecting a grounded host/instrument can bridge an intended domain. I use the connection map in [validation](Validation.md#end-to-end-fixture-and-service-tool) to make the demonstrated wiring reproducible.

## Milestone evidence

| Milestone | Complete operating result I intend to show | Evidence I retain |
| --- | --- | --- |
| M0 — Preparation | Native design and fabrication preparation are complete before ordering; physical operation remains pending | Scope/resource/library and effective-capacitance evidence, architecture disposition, native design/reviews and coherent manufacturing/assembly package |
| M1 — Nominal Modbus controller | Calibrated acquisition, basic pulse counting and guarded on/off actuation at nominal 12/24 V and recorded room temperature; DO3 static off/on only | Buildable firmware, controller USB diagnostic service, usable host/calibration workflow, Modbus contract, independent analog verification at ±20 mV / ±32 µA, real command-loss/reset/watchdog inhibition and fresh rearming |
| M2 — Classic CAN telemetry | The established application publishes measurements to a classic CAN peer while Modbus retains actuator ownership | Versioned telemetry, peer/cable/termination setup, coherent data/validity, latched output inhibition on bus-off and explicit fresh rearming after recovery; CAN commands remain pending until a separate guarded contract and tests are released |
| M3 — Bounded PWM | Existing DO3 controls a reviewed resistive load at 100 Hz, 10–90% commanded duty and static endpoints | Pulse/current captures, on-state diagnostic validity, observed temperature and shutdown/rearm while the timer runs; a specific compatible LED fixture only after separate review |
| M4 — Full Rev A qualification | The documented 9–30 V/0–50 °C/combined-load/fault, DI1 20 kHz and CAN FD targets are closed | Full matrices, enclosed thermal measurements, fault/recovery evidence, at least three qualified units and 24 h logged operation |

Every milestone remains pending until its evidence is collected. I can publish an M1 case study clearly labeled with its measured nominal conditions while M2–M4 remain pending. I do not claim the wider rating from a nominal demonstration, a component datasheet or a calculated margin. The [qualification plan](Validation.md) remains the authority for acceptance and full-release requirements.

## Diagnostic and calibration service

I use a small host tool that makes the controller reviewable and useful during bring-up. My initial [diagnostic CLI](../tools/diagnostics/README.md) follows the [Modbus design contract](../firmware/Protocol.md) over RS-485. Its simulated responses and transport tests support host development; they do not establish implemented target firmware, USB communication or qualified hardware. A command-line tool or small desktop panel is sufficient; an onboard display is not required for this application.

I separately implement and document the controller's USB diagnostic/configuration/calibration service and its host-access method for M1. USB CDC framing/commands and any host adapter need their own contract and actual target tests. I do not claim that the initial Modbus CLI already speaks an undocumented USB protocol.

Initial actuator qualification uses the pending, finite technician-triggered [commissioning procedure](Validation.md#commissioning-before-normal-actuator-commands), with zero qualification flags, reviewed current-limited loads and every existing hardware gate retained. Narrow physical records and matching assembly/shared-actuator-code identity justify reviewed qualification metadata before normal Modbus actuator tests. This avoids using fabricated qualification flags to bootstrap the first bench test; commissioning itself is not M1 completion or a full board rating.

The tool will:

- Identify board serial/revision, assembly variant, firmware/build and configuration/calibration version.
- Display raw and calibrated inputs with units, timestamps, validity and faults; show output commands and current-diagnostic sample age/validity separately.
- Provide explicit owner selection, arm/disarm and allowed output commands without silently renewing a lease through read-only traffic.
- Validate configuration/coefficient edits, record the calibration source and uncertainty, and export independent verification data.
- Export time-stamped machine-readable logs and CSV data that can be tied to test records and plots.

I preserve the register/message contract, tool usage examples and reproducible build/programming instructions with the release. I distinguish commanded relay state from measured contact position and sequential on-state output current from simultaneous precision or average-current measurement.

## Demonstration sequence

1. I identify the actual hardware/firmware and connection map, power the board externally, and show disarmed startup. USB alone does not power the controller.
2. I apply known analog values and a pulse/contact input, show calibrated/valid measurements over Modbus and USB, and explain the compatible sensor/reference wiring.
3. I confirm READY and select the Modbus owner, ARM with all commands zero, confirm ARMED, then send a fresh SET for a reviewed load. I show the physical load response and diagnostic data.
4. I stop valid commands while keeping read-only monitoring active. I capture drive inhibition within the configured lease, initially 1 s, plus relay-coil command and mechanical COM–NO release separately.
5. I resume communication and show that outputs remain inhibited. After removing the fault cause, I explicitly DISARM to acknowledge recoverable latches, confirm READY and read fresh boot/epoch/sequence values. I ARM with all commands zero, confirm ARMED, then send a fresh SET. I repeat reset/watchdog inhibition with instrument evidence; a video alone does not establish the timing or independent hardware path.
6. I add classic CAN in M2 and bounded resistor-fixture PWM in M3 only after their acceptance evidence exists. I show PWM timer shutdown and rejection of stale duty after recovery.

I follow the detailed [command-loss/rearm test](Validation.md#command-loss-and-rearm-demonstration). Any unexpected pulse, injection/backpower condition or stale-command restoration becomes a tracked issue before demonstration work proceeds.

## Evidence package clients can inspect

| Artifact | What it establishes |
| --- | --- |
| Application explanation and connection drawing | Purpose, compatible sensors/loads, actual domain bonds and tested limitations |
| Board/enclosure photographs and short video | Actual assembled prototype, accessible terminals/service and end-to-end behavior |
| Calibration/verification plots | Independent residuals with reference uncertainty, coefficients, filter and switching conditions |
| Rail/output/reset/watchdog/PWM captures | Physical timing and state under a stated fixture, rather than telemetry alone |
| Thermal/combined-load records | Component/probe positions, enclosure/mounting/ambient, actual loads and measured temperatures |
| Editable native design and manufacturing package | Schematic/PCB/library identity, reviewed ERC/DRC exceptions, BOM/assembly/fabrication parity and reproducible handoff |
| Firmware, host tool and protocol documentation | Reproducible builds, register/message interpretation, each transport's documented service usage and recovery behavior |
| Per-unit test/issue index | Board/build/revision traceability, pending/pass/fail status, rework and repeatability/soak evidence |

I copy the [validation record template](templates/Validation_Record.md) for each test/condition. I preserve raw data/captures alongside derived plots and link each case-study claim to its record. I do not populate a results table with predicted numbers or convert an unresolved failure into a pass.

## Claims and scope boundaries

I use “planned,” “calculated,” “implemented” and “measured” deliberately. For measured performance I state the hardware/firmware, condition, uncertainty and evidence location. A clean documentation audit is not ERC/DRC success or electrical validation.

My analog formats are a coherent industrial application choice; they do not prove expertise in every analog specialty. The planned 16-bit ADC does not establish 16-bit system accuracy, and 100 Hz publication does not establish 100 Hz input bandwidth. The analog design targets useful bandwidth up to 20 Hz.

The high-side outputs are bounded DC load control. DO3's initial PWM fixture is not a motor drive, a proportional-solenoid regulator, universal fan control or arbitrary LED dimming. The relay contacts remain low-voltage DC. Hardware permission and watchdog behavior are not certified functional safety, and bench fault survival is not standards certification.

I retain both relays in the final hardware. One may be unpopulated during staged assembly, with its unavailable function and assembly identity recorded. Wireless, Ethernet, battery management and other separate product objectives remain future application decisions rather than additions to this release.

My [manufacturing](../fabrication/README.md) and [mechanical](../mechanical/README.md) records remain part of the final handoff. A completed milestone is useful portfolio evidence; a full Rev A release still requires the complete qualified design and all recorded release gates.
