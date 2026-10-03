# Hardware

I am developing a four-layer STM32G474 controller for 12/24 V sensors and actuators. I have defined the circuit architecture, interfaces, power domains, and qualification targets. Schematic capture and PCB layout are the next implementation stages.

The [architecture](../docs/Architecture.md) describes the system, and [design decisions](../docs/Design_Decisions.md) explain the component and protection choices.

## Circuit organization

| Block | Design scope |
| --- | --- |
| Field power | Protected 9–30 V input, eFuse, reverse-current blocking, surge suppression, 5 V conversion, and supply monitoring |
| Service and auxiliary power | Field/USB logic supply selection, MCU rails, field analog rails, and independent isolated bus supplies |
| Controller | STM32G474VET6, clock, reset, boot configuration, USB, SWD, watchdog, and configuration storage |
| Measurement | Four group-isolated digital inputs; two 0–10 V inputs and two 4–20 mA receivers through an external ADC |
| Actuation | Four current-diagnosed high-side channels, two SPDT relays, and a protected 0–10 V output with a hardware disconnect |
| Communications | Separately isolated RS-485 and CAN, selectable termination, connector protection, and bus references |
| Output permission | Hardware gating derived from field-power validity, reset state, watchdog health, and explicit arming |

I’m separating USB-powered service from field power. My architecture allows USB to power the controller, while the external ADC/DAC, field outputs, relay coils, and isolated bus-side circuits require the field supply. I’m including electrical protection between these domains to prevent back-powering.

I use [KiCad project-local libraries](libs/README.md) to keep assets portable. Each selected component will have an exact ordering code, package-verified symbol and footprint, and sourcing information in its schematic properties. The schematic will own the released BOM.

The [native project directory](STM32_Industrial_IO/README.md) contains library configuration. Electrical checks, layout checks, and measured qualification are defined in [validation](../docs/Validation.md); the current repository does not establish tested hardware ratings.
