# Manufacturer guidance and reference designs

Use reference designs to understand implementation details, then verify them against the exact selected device, package, load, and board geometry.

## Retained local reference

[TI LMR38020 evaluation-module guide](REF_TI_LMR38020QEVM_UserGuide_SNVU817.pdf) supports the selected buck-family study. Its component values and layout are examples, rather than a finished design for this board. Primary source: [TI SNVU817](https://www.ti.com/lit/ug/snvu817/snvu817.pdf).

## Guidance to consult during capture

- [STM32G474VE product documentation](https://www.st.com/en/microcontrollers-microprocessors/stm32g474ve.html): exact package datasheet, reference manual, errata, and hardware-development guidance.
- [STM32 system-memory boot guidance, AN2606](https://www.st.com/resource/en/application_note/an2606-stm32microcontroller-system-memory-boot-mode-stmicroelectronics.pdf): verify recovery interfaces and entry requirements for the exact device.
- Candidate-family [local datasheet index](../datasheets/README.md): regulator layout, analog protection orientation/thresholds, isolated-power constraints, and peripheral timing.

Before adopting any reference circuit, record the document revision, applicable ordering code, differences from its conditions, recalculated values, and schematic/layout evidence. Add actual evaluated circuits or fixture records here as they become available.

The previous radio development-board reference was removed from the active project because the new board integrates an STM32 directly.
