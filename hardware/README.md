# Hardware

I am developing a four-layer STM32G474 controller for 12/24 V sensors and actuators. I have defined the circuit architecture, interfaces, power domains, and qualification targets. Schematic capture and PCB layout are the next implementation stages.

The [architecture](../docs/Architecture.md) describes the system, and [design decisions](../docs/Design_Decisions.md) explain the component and protection choices.

I retain the complete channel/port baseline in [Scope](../docs/Scope.md). I close the [rail/crossing architecture disposition](../docs/Architecture_Review.md) before freezing affected sheets, then follow the [implementation milestones](../docs/Implementation_Plan.md). Static Modbus operation comes before classic CAN and PWM; CAN FD and the wider operating envelope need separate physical qualification.

## Circuit organization

| Block | Design scope |
| --- | --- |
| Field power | Protected 9–30 V input, eFuse, reverse-current blocking, surge suppression, 5 V conversion, and supply monitoring |
| Service and auxiliary power | Externally supplied MCU/field analog rails and independent isolated bus supplies |
| Controller | STM32G474VET6, clock, reset, boot configuration, USB, SWD, watchdog, and configuration storage |
| Measurement | Four group-isolated digital inputs; two 0–10 V inputs and two 4–20 mA receivers through an external ADC |
| Actuation | Four current-diagnosed high-side channels, DO3 timer PWM and two SPDT relays, all hardware permission-gated |
| Communications | Separately isolated RS-485 and CAN, selectable termination, connector protection, and bus references |
| Output permission | Hardware gating derived from field-power validity, reset state, watchdog health, and explicit arming |

I power the entire board from the protected external DC supply. USB provides self-powered data service with VBUS detection. I retain qualified signal crossings between independently derived rails and verify sequencing/injection during brownout.

I use [KiCad project-local libraries](libs/README.md) to keep assets portable. Each selected component will have an exact ordering code, package-verified symbol and footprint, and sourcing information in its schematic properties. The schematic will own the released BOM.

The [native project directory](STM32_Industrial_IO/README.md) contains library configuration. Electrical checks, layout checks, and measured qualification are defined in [validation](../docs/Validation.md); the current repository does not establish tested hardware ratings.
