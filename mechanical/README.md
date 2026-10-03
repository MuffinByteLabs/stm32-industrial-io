# Mechanical integration — STM32 Industrial I/O Controller

The [canonical plan](../docs/STM32_Industrial_IO_Controller_RevA_Plan.md) starts with a **140 × 100 mm** four-layer board envelope. This is provisional. No enclosure model, production outline, mounting drawing, or verified terminal arrangement exists yet.

Select the enclosure and pluggable terminals together before final placement. A suitable insulated enclosure with an optional DIN-rail mount should leave room for field wiring, debug access, inspection, and heat removal.

## Geometry to settle before routing

- Actual inside width, depth, height, PCB supports, screw positions, and tool access from the enclosure drawing.
- Terminal body/mating-plug height and wire exit, including screwdriver clearance, wire bend radius, connector retention, and strain relief.
- Clearance around relays, power magnetics, isolated power/transceivers, USB, and SWD cable.
- Insulating supports and hardware placement that preserve each isolation boundary and prevent a metal DIN rail or mounting screw from shorting separate domains.
- Field-input common, shared analog/load returns, and separate RS-485/CAN references marked consistently with the [wiring guide](../docs/Interface_and_Wiring_Guide.md).
- Access to fuses and configuration/termination links without exposing unintended conductors.
- Ventilation and hot-component placement for simultaneous load tests in the intended mounting orientation.

Choose a compatible voltage-input actuator for AO. An enclosure demonstration does not establish compatibility with every lighting or HVAC controller.

## Deliverables

Save the selected enclosure's manufacturer drawing and ordering code, a dimensioned board outline, terminal/wire-access drawing, assembled STEP model, and a fit-check record. Include maximum component height and an actual first-article fit test.

Thermal qualification must use the assembled enclosure and stated ambient conditions. A successful bare-board bench test alone cannot establish enclosed continuous-load ratings.
