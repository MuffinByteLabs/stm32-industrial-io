# Changelog

## Rev A — In development

### October 3, 2026

- I reviewed production component status and documented a conflict-free provisional MCU allocation.
- I revised current-loop protection to preserve the permanent shunt load, added protected AO terminal feedback, and selected larger independent isolated bus supplies.
- I updated the service-power budget, hardware arming/reset design, input-fault conditions, and schematic/qualification checks.
- I added a reproducible ideal DC frontend simulation with explicit model limits.

### October 2, 2026

- I defined a four-layer STM32 controller architecture with protected DC power, analog sensing, diagnosed load outputs, and separately isolated communication buses.
- I documented the electrical interfaces, fault behavior, circuit tradeoffs, and validation targets.
- I added reproducible power and measurement calculations, a manufacturer-reference manifest, and automated document and library checks.
- I organized the hardware, firmware, mechanical, and manufacturing documentation around the same electrical contract.

I have not released a hardware revision. I’ll record each release here with its matching design sources, firmware version, manufacturing package, and measured validation results.
