# Hardware — STM32 Industrial I O Controller

The active specification is [STM32 Industrial I O Controller Rev A Plan](../docs/STM32_Industrial_IO_Controller_RevA_Plan.md). This is a fresh four-layer STM32 design. Schematic, PCB, exact library validation, and fabrication release remain implementation work.

## Future native project

Create the real KiCad project in `hardware/STM32_Industrial_IO/`:

- `STM32_Industrial_IO.kicad_pro`
- `STM32_Industrial_IO.kicad_sch`
- `STM32_Industrial_IO.kicad_pcb`
- Project-local library tables/resources and `.kicad_dru` when needed

The automated workflow uses these exact schematic/PCB paths. An absent design means checks not run; empty hardware placeholders do not establish capture/validation.

## Planned hierarchy

| Sheet | Scope |
| --- | --- |
| System | Domains, connectors, hierarchy and permission signals |
| Input power | Fuse, TVS, blocking FET/eFuse, bulk and sensing |
| Service power | Field 5 V buck, logic selection, digital/analog 3.3 V |
| Auxiliary power | Analog positive/negative rails and two independent isolated supplies |
| MCU and debug | STM32G474VET6, power, clock, reset, boot, USB and SWD |
| Digital inputs | Four group-isolated receivers, thresholds, filters and protection |
| Analog inputs | Two 0–10 V and two 4–20 mA paths, protectors, ADC and calibration |
| Analog output | DAC, amplifier, hardware disconnect, protector and readback |
| Switched outputs | Four diagnosed high-side channels, sensing, blocking/freewheel diodes |
| Relays | Two gated coil drivers and independent SPDT contact circuits |
| Communications | Separate isolated RS-485/CAN FD, protection and termination |
| Permission and service | Hardware gating, watchdog, storage, indicators and test access |

Use stable sheet filenames and unique references during capture. Labels should show direction/domain. Candidate MPNs are not yet a verified pin map or frozen purchasable BOM.

## Libraries and evidence

Check every selected symbol/footprint against the exact manufacturer package pin/mechanical drawing. Reuse previous resources only after that check; another board's assembly does not validate this design. Keep models portable and record custom-library sources, modifications, and validation.

Store exact MPN, manufacturer, datasheet, footprint, distributor references, and assembly/substitution notes in schematic properties. The real schematic becomes the BOM source of truth. Do not generate final manufacturing outputs from a placeholder design.

Follow [KiCad setup](../docs/KiCad_Settings_RevA.md), [layout rules](../docs/Hard_Rules_Layout_RevA.md), and [assembly planning](../docs/Assembly_and_Stencil_Plan.md). Readiness requires package/schematic review, calculations, routing/DRC/parity, manufacturing-file inspection, physical bring-up, and measured qualification.
