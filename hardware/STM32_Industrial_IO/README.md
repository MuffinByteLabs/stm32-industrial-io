# KiCad project

This directory is the designated location for the STM32 controller's native design. Library tables are present; the schematic, PCB, and project settings have not yet been captured.

| File | Purpose |
| --- | --- |
| STM32_Industrial_IO.kicad_pro | Project settings and electrical/layout rules |
| STM32_Industrial_IO.kicad_sch | Hierarchical schematic and component properties |
| STM32_Industrial_IO.kicad_pcb | Four-layer board layout |
| fp-lib-table | Project-relative candidate footprint collections |
| sym-lib-table | IndustrialIO registration; its symbol library is initially empty, with missing symbols explicitly pending |

The project-relative footprint paths resolve through the adjacent [libs](../libs/README.md) directory. Stock KiCad model paths use the installed library variable.

I create the native project here using the exact filenames above and KiCad 10. The registered library is a destination for verified custom symbols, not a completed symbol collection. I follow the [library preflight](../../docs/Library_Preflight.md) before wiring each selected package.

The [hardware overview](../README.md) describes the circuit organization. [Architecture](../../docs/Architecture.md), [interfaces](../../docs/Interfaces.md), and [validation](../../docs/Validation.md) define the design contract and acceptance evidence.
