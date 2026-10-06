# Validation record template

I copy this template for each test and condition. The default status is **PENDING**. I enter actual measurements only after performing the test, preserve raw evidence and identify the exact hardware/firmware. This blank template is not a result.

## Identity and requirement

| Field | Record |
| --- | --- |
| Record ID / title | To be assigned |
| Milestone | M1 / M2 / M3 / M4, select one |
| Requirement / acceptance source | Document, section and frozen revision |
| Status | PENDING — later use PASS, FAIL or BLOCKED with evidence |
| Date / operator | To be recorded |
| Board serial / hardware revision | To be recorded |
| Assembly variant / fitted-DNP stage | To be recorded; include relevant reference designators |
| Firmware/build / host-tool version and actual transport | To be recorded; distinguish Modbus RTU/RS-485 from USB service |
| Configuration / calibration version and CRC | To be recorded |
| Enclosure / harness / fixture revision | To be recorded |

## Pre-test acceptance and limits

I freeze the acceptance criterion and the reviewed fixture before energizing the test. I state whether this record establishes nominal-condition demonstration, an electrical qualification condition or repeatability/soak evidence.

| Item | Defined value / source |
| --- | --- |
| Expected behavior / numerical pass limits | To be defined |
| Source voltage/current limit, impedance and exposure | To be defined |
| Load current/inrush/energy and suppression | To be defined |
| Ambient / mounting / enclosure condition | To be defined |
| Sample rate/filter / command lease / bus timing as applicable | To be defined |
| Stop criteria / safe load state / recovery | To be defined |
| Reviewed setup and readiness issues | To be recorded |

## Equipment and connection map

| Instrument / source / peer | Identity, configuration and calibration/uncertainty |
| --- | --- |
| Board supply and leads | To be recorded |
| Analog stimulus and independent reference measurement | To be recorded |
| Scope/probes / time alignment | To be recorded |
| Load / sensor / external loop supply | To be recorded |
| USB host / bus adapters / peers / cables | To be recorded |
| Temperature measurement | To be recorded |

I attach a connection drawing/photo and record all ground/reference bonds, including MAIN_GND, AI_RETURN/LOAD_RETURN, DI_COM, RS485_REF, CAN_REF, relay-contact circuits, USB ground, supply negatives and probe earth. I identify any bond that bridges an isolation domain. For current inputs I record external loop power and available compliance/headroom; the board is not a loop-power source. For buses I record nodes, cable/stubs, reference conductors, termination and optional bias/choke population.

Connection-map and setup-evidence locations: to be recorded.

## Procedure actually performed

I record the ordered steps, initial power/arming state, stimulus changes, timing reference, observed stop/recovery behavior and any deviation from the frozen procedure. I do not substitute a planned procedure for an execution record.

For command-loss/rearm tests I record the selected owner and last accepted valid command, configured timeout, continued read-only/invalid traffic, physical inhibition and communication return without arming. After removing the cause, I record explicit DISARM/recoverable-fault acknowledgement, self-check/READY, fresh boot/epoch/sequence guards, zero-command ARM, confirmed ARMED and fresh SET. I record relay-coil inhibition and measured COM–NO release separately. For watchdog/PWM tests I identify how service was interrupted and show that autonomous timer activity cannot preserve output permission or restore stale duty.

Performed steps: pending.

## Measurements and raw evidence

| Condition / point / channel | Acceptance criterion | Actual measurement / uncertainty | Raw evidence location | Result |
| --- | --- | --- | --- | --- |
| To be defined | To be defined before test | Not measured | None yet | PENDING |

I include units, instrument bandwidth, relevant timing alignment and sample validity. Analog verification points are independent of calibration points; I identify the coefficients used. A publication rate, ADC resolution or analytical margin is not a measured bandwidth/accuracy result. Calculations and derived plots identify their raw input evidence and method separately.

## Outcome, issues and claim boundary

| Item | Record |
| --- | --- |
| Overall result | PENDING |
| Failures / unexpected pulses / injection / resets | Not tested |
| Issue IDs and evidence | None assigned |
| Rework / changed hardware or firmware | None performed |
| Retest identity and result | Pending if required |
| Operating conditions this result establishes | None until measured |
| Targets / conditions still pending | To be listed |

I state exactly which requirement passed or failed and why. I retain failures and superseded records with their identities; a later retest does not erase the original evidence. A changed assembly, calibration or build requires the affected checks to be repeated.

## Multiunit and soak extension

For M4 repeatability I attach the per-unit records for at least three qualified units, calibration/verification comparisons and assembly/build identities. For the 24 h soak I state duration, loads, buses, temperature, logging cadence, interruptions, reset/fault counts and the retained raw-log location. Unexplained resets or missing intervals remain issues, not a passed soak result.

Multiunit/soak evidence: pending.

## Review and release use

Review date / reviewer / unresolved items: pending.

I identify the milestone/result index and any portfolio claim this record supports. Full Rev A release use requires reconciliation with the complete [qualification plan](../Validation.md); a bounded demonstration does not establish an untested supply, temperature, load or fault envelope.
