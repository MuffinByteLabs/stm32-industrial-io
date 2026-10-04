# Rev A component selections

I record the selected parts and support values before drawing the schematic. These files include exact ordering codes, packages, ratings, tolerances, purpose, manufacturer evidence and intended KiCad assets. They are capture specifications, not a released assembly BOM or an inventory claim.

| Selection file | Circuit instructions |
| --- | --- |
| [Power](power.json) | [Power](../circuits/Power.md) |
| [Control/service](control_service.json) | [Control/service](../circuits/Control_Service.md), including [loop status](../circuits/Loop_Status.md) |
| [Analog](analog.json) | [Analog](../circuits/Analog.md) |
| [Field I/O](field_io.json) | [Field I/O](../circuits/Field_IO.md) |

My October 4 scope uses external board power, self-powered USB data service and DO3 timer PWM. The active selections retain all four analog inputs, independently isolated RS-485/CAN, relays, current diagnostics and rail supervision.

I allocate quantities within each block and identify off-board mating plugs and optional/DNP parts separately. Repeated MPNs represent separate placements. Control pull/bypass counts include a small placement allocation; actual reference designators replace them after capture. I do not use pre-capture counts as ordering quantities.

I distinguish existing library candidates from project-specific assets to create/check. These identifiers do not certify footprints or assert missing symbols already exist. I verify physical pins during placement, then approve land patterns before layout.

I copy selected data into schematic properties. The native schematic owns production quantities and BOM exports; substitutions require electrical, pin, sequencing and package review. My [manufacturer references](../../references/datasheets/README.md) and [validation requirements](../Validation.md) record the evidence and remaining checks.

I track unresolved effective-capacitance requirements in my [capacitor evidence report](../calcs/capacitor_evidence.json). Exact ordering codes do not establish operating-bias capacitance. I close those requirements before freezing the affected supply/reference circuits.
