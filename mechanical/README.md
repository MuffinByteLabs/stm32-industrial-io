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
| Heat removal | Ventilation and component placement evaluated at simultaneous load in the intended mounting orientation |

The mechanical release will include the enclosure ordering code and manufacturer drawing, dimensioned PCB outline, terminal/wire-access drawing, assembled STEP model, and first-article fit record.

Continuous-load qualification will use the assembled enclosure and stated ambient conditions. The [validation plan](../docs/Validation.md) connects this mechanical configuration to the thermal measurements.
