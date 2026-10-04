# Changelog

## Rev A — In development

### October 4, 2026

- I revised Rev A around external board power and self-powered USB data service.
- I removed the analog voltage-command stage, its dedicated bias/reference circuits and USB source-transfer circuitry from the active design.
- I retained precision inputs, both isolated buses, power supervision, relays and current diagnostics.
- I added DO3 timer PWM with a bounded 100 Hz load/timing target, phase-aware current sensing and explicit shutdown/rearming behavior.
- I separated receiving-domain buffer enables, added global driver-fault ARM clearing and coordinated low-line rail monitoring with the post-protection power margin.
- I updated circuit specifications, component selections, references, calculations and qualification requirements together. Native schematic/PCB implementation and measured ratings remain pending.

### October 3, 2026

- I completed circuit capture specifications and exact component/support-value selections for power, control/service, analog and field I/O.
- I matched the auxiliary boost to light-load operation, completed rail-health and domain-crossing details, and added bounded AO manufacturer-model checks.
- I fixed connector pairs/pin orders, finite load/cable fixtures and the 5.75 W service allocation.
- I added explicit pre-capture capacitor evidence and library gates, including a bank-by-bank report of unresolved capacitance minima.

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
