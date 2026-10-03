# Manufacturer guidance and reference designs

I use manufacturer reference designs to study implementation details, then verify them against my exact device, package, load, and board geometry. The original documents retain their manufacturer attribution.

## Retained local reference

I retained the [TI LMR38020 evaluation-module guide](REF_TI_LMR38020QEVM_UserGuide_SNVU817.pdf) for my buck-family study. Its values and layout are examples; I will recalculate and review the implementation for this board. Primary source: [TI SNVU817](https://www.ti.com/lit/ug/snvu817/snvu817.pdf).

## Guidance to consult during capture

- [STM32G474VE product documentation](https://www.st.com/en/microcontrollers-microprocessors/stm32g474ve.html): exact package datasheet, reference manual, errata, and hardware-development guidance.
- [STM32 system-memory boot guidance, AN2606](https://www.st.com/resource/en/application_note/an2606-stm32microcontroller-system-memory-boot-mode-stmicroelectronics.pdf): verify recovery interfaces and entry requirements for the exact device.
- Candidate-family [local datasheet index](../datasheets/README.md): regulator layout, analog protection orientation/thresholds, isolated-power constraints, and peripheral timing.

Before adopting a reference circuit, I will record its revision, applicable ordering code, differences from my conditions, recalculated values, and schematic/layout evidence. I will add evaluated circuits and fixture records as they become available.

My [architecture](../../docs/Architecture.md) integrates the STM32 directly on the PCB.
