# Rev A implementation plan

I implement the [frozen scope](Scope.md) through the milestones below. All hardware milestones are pending. Host software can be developed and checked against the [protocol design contract](../firmware/Protocol.md) before a board exists; simulation results remain separate from physical evidence.

## M0 — close capture preparation

1. I use the complete retained rail/crossing architecture recorded in the [review record](Architecture_Review.md), then close its pin, powered-off, sequence and permission requirements before freezing the affected sheets.
2. I close each effective-capacitance requirement in [capacitor_evidence.json](calcs/capacitor_evidence.json), including hold-up, bias, temperature, startup and discharge constraints. A changed part/quantity includes revised calculations.
3. I create missing local symbols/footprints, verify exact package pin/pad numbering against manufacturer drawings, and check mating-terminal orientation.
4. I capture the complete circuit from [Schematic_Capture.md](Schematic_Capture.md), including all six actuator gates and default states. I check physical MCU pins, rail sequences, unpowered crossings and protection before accepting ERC.
5. I select the enclosure/terminal arrangement, then complete four-layer placement/routing with continuous local return paths, isolation keepouts, reviewed current paths and thermal geometry. I accept DRC and schematic parity only with documented circuit-specific exceptions.
6. I inspect the matching fabrication/assembly exports and assembly sequence before ordering. I retain the original full-load budget even when the first assembly omits replicated circuits.

**Exit evidence:** a recorded architecture disposition; closed capacitor/library gates; native schematic/PCB; review records; coherent manufacturing package and staged assembly plan. No measurements are inferred from this gate.

## M1 — complete one Modbus-controlled application

| Work | Deliverable / acceptance basis |
| --- | --- |
| Power and controller bring-up | Current-limited startup, measured rails/clock/reset, SWD programming, correct self-powered USB attach and no unintended backpower |
| Hardware output permission | All six commands inhibited on reset/invalid rails/watchdog failure; ARM is accepted with all commands zero, then a fresh SET requests the intended load state |
| Initial output commissioning | Separate, pending technician-triggered finite test routines retain all hardware gates and test reviewed bounded loads with normal external actuator commands unavailable; qualification bits stay clear until recorded results justify a reviewed nominal-envelope release |
| Acquisition | All four analog channels and digital inputs readable with raw/calibrated values, units, sample age and validity; simple DI1 count verified before the later full-frequency sweep |
| Calibration | Two-point coefficients with board identity, a documented target loading/readback method and verified recoverable storage; independent verification at the room-temperature targets in [Validation.md](Validation.md) and recorded reference uncertainty. Offline fitting alone does not complete this row |
| Static actuation | Each high-side channel and both relay circuits exercised with documented bounded loads; DO3 uses static off/on only |
| Modbus application | A host reads one coherent snapshot, controls outputs through the guarded command contract, and proves that invalid/read-only traffic does not renew the command lease |
| Service and host workflow | Build identity, diagnostic/calibration records and timestamped CSV acquisition using the [Modbus diagnostic tool](../tools/diagnostics/README.md); target USB identity/basic diagnostic service with documented framing and host-access method. USB firmware/host adaptation remain pending implementation work for this milestone |
| Application demonstration | One sensor/pulse fixture, measured analog input and qualified DC load, with command loss, fault reporting and fresh rearming shown end to end |

I exercise nominal 12 V and 24 V at recorded room temperature first. This does not establish the full 9–30 V, 0–50 °C or combined-load operating envelope. Reset/default-off and protection obligations still apply during every stage; earlier testing does not permit bypassing them.

I collect initial bounded actuator evidence using the commissioning procedure in [Validation](Validation.md), then review qualification metadata for the actual assembly and shared actuator-code identity before enabling normal Modbus actuation. I still physically test the production command/lease path afterward. Simulation capability masks and successful programming cannot supply this evidence.

**Exit evidence:** buildable target firmware, measured setup/results, host logs, calibration verification, static-load checks and a repeatable Modbus demonstration. A software simulation or tool self-test cannot close M1.

## M2 — classic CAN

I add classic 500 kbit/s telemetry with an FD-capable peripheral configured for classic frames, using the versioned message contract in [Protocol](../firmware/Protocol.md#classic-can-telemetry-v1--pending-after-modbus-bring-up). I exercise bracketed coherent measurement groups, heartbeat/build identity and bus-off/recovery on a documented short-bus fixture with two end terminations. With CAN mode enabled, bus-off is a latched global fault that disarms all outputs. Recovery alone cannot restore them: after the cause is gone I explicitly DISARM to acknowledge recoverable faults, confirm READY, ARM with zero commands, then send a fresh SET. Modbus retains actuator ownership; CAN traffic and recovery cannot renew its lease or transfer control. Guarded CAN commands require a separate released and tested command contract before CAN ownership becomes available.

**Exit evidence:** actual peer traffic/logs, decoded measurement groups and physical recovery/output-state observations. A populated CAN port, reserved identifiers or MCU FDCAN support is not completion.

## M3 — bounded DO3 PWM

I begin with the specified resistive fixture at nominal 12/24 V and recorded room temperature. I qualify frequency/duty, finite edges, current-sense timing/validity, nuisance-fault behavior, switching disturbance and hardware inhibition while the timer runs. A compatible LED fixture is included only after its inrush, dimming response and temperature are reviewed.

I enable PWM commands only for a build whose capability and qualification records allow that mode. I preserve static endpoints, reject unsupported duty/frequency combinations and clear all timer state before recovery.

**Exit evidence:** waveform/current/thermal and shutdown results for that bounded subset of [PWM qualification](Validation.md#pwm-qualification). The full supply/temperature/combined-load sweep remains M4 work. This remains a low-frequency high-side load mode rather than a general motor driver.

## M4 — close the wider qualification envelope

I complete the unchanged supply/temperature/accuracy/counting targets, four simultaneous 0.5 A outputs, relay and bus loading, enclosure thermal behavior and bounded fault fixtures. I qualify CAN FD at 500 kbit/s arbitration / 2 Mbit/s data separately. I repeat the appropriate checks across at least three physical units and complete the planned 24 h logged soak.

I review each remaining target against evidence and update any changed requirement across architecture, interfaces, circuitry, firmware, budgets and tests. Defined bench faults do not establish emissions/immunity standards compliance.

**Exit evidence:** traceable measured results and the complete [hardware-release package](../fabrication/README.md). A milestone demonstration can be shown earlier with its actual limits; a full `rev` hardware release still requires the applicable completed design and qualification gates.

## Order of work and status

| Milestone | Current status | Dependency |
| --- | --- | --- |
| M0 | Pending | Retained-architecture verification; capacitor and CAD assets; native design |
| M1 | Pending | Reviewed design, physical assembly and target firmware |
| M2 | Pending | Working M1 state/data model and qualified bus fixture |
| M3 | Pending | Static output/fault checks and timing/thermal review |
| M4 | Pending | Completed earlier modes and full physical fixtures |

I record progress as completed artifacts and test records rather than predicted percentages. I use the [portfolio evidence guide](Portfolio_Evidence.md) to select the clearest results from the implemented milestones.
