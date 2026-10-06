# Mechanical integration

I am starting with a 140 × 100 mm board envelope and an insulated enclosure with optional DIN-rail mounting. The final outline and component placement depend on the selected enclosure and pluggable terminals. Enclosure CAD and a physical fit check are pending.

## Integration requirements

| Area | Design requirement |
| --- | --- |
| Field wiring | Accessible terminal screws, retained mating plugs, wire-bend clearance, and strain relief |
| Service | USB and SWD access without disturbing field wiring |
| Mounting | Insulated supports and screw positions that preserve the input and bus isolation boundaries |
| Component height | Clearance for relays, magnetics, connectors, and isolated supplies |
| Identification | Terminal labels consistent with the [interface definitions](../docs/Interfaces.md), including separate RS-485 and CAN references |
| Connector coding | Unique verified header/plug coding within the repeated MC2, MC3, MSTB3 and MSTB4 families; colours and labels supplement coding but do not prove exclusion |
| Heat removal | Ventilation and component placement evaluated at simultaneous load in the intended mounting orientation |
| Fixture access | Usable access to test points, diagnostic/calibration service and documented harness connections while preserving the intended domain boundaries |

The mechanical release will include the enclosure ordering code and manufacturer drawing, dimensioned PCB outline, terminal/wire-access drawing, assembled STEP model, and first-article fit record.

I record **13 terminal harness identities**: power; AI_V1, AI_V2, AI_I1 and AI_I2; the DI1/DI2 and DI3/DI4 group connectors; RS-485; CAN; DO1/DO2 and DO3/DO4; and each relay. The release drawing specifies a compatible manufacturer coding profile and insertion pattern on **both** halves of each repeated-family pair, including the four identical two-position analog connectors. I test attempted cross-mating, including partial insertion of fewer-position plugs, with power removed. Final coding article numbers/patterns remain pending this physical fit review; I do not order arbitrary coding pieces from a different connector family.

The intended enclosure is insulated. I may reserve an isolated `CHASSIS_FE` lug/pad area if an actual installation needs a functional-earth or shield termination, but it has no default bond to MAIN_GND, DI_COM or either port reference. No protective-earth function is assigned. I do not automatically fit 1 MΩ/4.7 nF links among the isolated islands: resistors create DC paths and the DI example's total coupling allowance is much smaller. Any coupling network requires a defined installation, rated isolation/spacing, total barrier capacitance and measured EMC review. [ISO1212 §8.2.1.2.5](https://www.ti.com/lit/ds/symlink/iso1212.pdf)

Continuous-load qualification will use the assembled enclosure and stated ambient conditions. The [validation plan](../docs/Validation.md) connects this mechanical configuration to the thermal measurements.

## Fixture and milestone configuration

I document one machine-monitor/actuator bench fixture so the mechanical arrangement supports the [portfolio demonstration](../docs/Portfolio_Evidence.md) as well as qualification. Its drawing identifies the supply, external current-loop power, sensor and load harnesses, RS-485/CAN cables, USB service access, instrument/probe connections, wire strain relief and connector view/pin 1. I keep AI_RETURN and LOAD_RETURN labels consistent with their shared MAIN_GND reference and show the separate DI_COM, RS485_REF and CAN_REF wiring. Any intentional domain bond is recorded rather than hidden by the enclosure or fixture.

I follow the [fixed scope](../docs/Scope.md) and [implementation plan](../docs/Implementation_Plan.md). I begin M1 with nominal 12/24 V and recorded room temperature, using reviewed low-energy on/off loads and accessible diagnostics; DO3 remains static off/on. M2 adds the classic CAN peer and its recorded cable arrangement. M3 uses the reviewed resistor fixture for bounded 100 Hz DO3 PWM. M4 closes the full 9–30 V/0–50 °C and combined-load thermal envelope, fault fixtures and CAN FD. These milestones do not change the full board outline requirement, six actuator paths or electrical limits.

An open-bench temperature result establishes only that mounting/cooling condition. I repeat the required continuous/PWM combined-load thermal tests in the intended insulated enclosure, mounting orientation and ambient conditions before claiming its enclosed rating. I identify enclosure and harness revisions in each [test record](../docs/templates/Validation_Record.md), retain temperature-sensor/probe positions and photographs, and record any fit/rework issue.

I may leave a relay or replicated channel unpopulated during staged assembly. I still reserve the final two-relay component height, terminal access and wiring space; this is not a mechanically reduced final variant. CAD fit checks, the assembled STEP model and the first-article physical fit record remain pending until the native board and selected enclosure exist.
