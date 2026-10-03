# Project status — STM32 Industrial I/O Controller Rev A

Updated October 2, 2026.

**Current stage: requirements and preparation.** This folder now follows the fresh STM32 plan. There is no implemented STM32 schematic, PCB, application firmware, or tested prototype.

## Completed

- [Canonical plan](STM32_Industrial_IO_Controller_RevA_Plan.md): architecture, candidate component families, measurable acceptance targets, staged development, budget assumptions, and portfolio deliverables.
- [Job-fit check](Upwork_Job_Fit.md): relevant requirements traced to saved excerpts, with partial matches and exclusions.
- Supporting guides aligned to the new power domains, interfaces, fault behavior, four-layer construction, and build sequence.
- Recovery archive verified before obsolete material was removed; useful generic library assets retained.
- Candidate-family reference preparation and executable planning arithmetic. The [datasheet manifest](../references/datasheets/manifest.json) records document identity checks; it does not establish symbol or pin correctness.

## Pending

| Gate | Required work and evidence |
| --- | --- |
| Requirements freeze | Choose representative sensors/loads; settle enclosure and terminals; resolve [open engineering items](Open_Engineering_Items.md) |
| Circuit feasibility | Bench-check analog fault protection, zero-volt AO, supply sequencing, and output short/inductive behavior |
| Schematic | Exact ordering codes, pin/clock/DMA map, power calculations, protection coordination, reviewed symbols and footprints, ERC |
| PCB | Actual four-layer stack, layout, DRC/parity, mechanical fit, thermal and EMC review |
| Procurement | Stock/price checks, exact BOM, substitutes, and current fabrication/assembly quotes |
| First article | Inspection, staged rail bring-up, SWD/USB, safe output behavior, and issue log |
| Firmware | Drivers, calibrated readings, protocol maps, command ownership, timeout/rearm, watchdog, and recoverable configuration |
| Qualification | Three working units; recorded analog sweeps, fault tests, communication tests, thermal work, and soak testing |
| Portfolio release | Editable design package, firmware, actual measurements, photos/video, and concise client-facing case study |

The next action is to choose the demonstration sensor and loads and resolve the highest-risk power/protection/output choices before committing to a schematic. Use the [procurement plan](Procurement_Plan.md) to organize candidates, and the [resource reservations](PinMap_CheatSheet.md) to allocate peripherals.

## Status discipline

The schematic and PCB will live in [hardware/STM32_Industrial_IO/](../hardware/STM32_Industrial_IO/README.md). Empty placeholder files are intentionally absent. Missing-design CI results mean checks were not run.

Record each milestone with its date, exact hardware/firmware revisions, evidence path, outstanding limitations, and reviewer. Change a target to a demonstrated capability only when the corresponding test record exists. Any changed electrical contract must be reconciled with the canonical plan, wiring guide, firmware contract, and qualification procedure.
