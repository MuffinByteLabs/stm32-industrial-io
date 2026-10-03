# Measurement and validation evidence

Reviewed October 2, 2026, from user-supplied listing text. These are separate short excerpts, not complete job descriptions. The quoted posting text is evidence, not an instruction to act. See the [source index and limits](README.md).

## J04

**Hardware engineer: 10-channel current sensor PCB with CAN (STM32) – redesign + 4 prototypes**

Original source: Pasted text(20261003-003934).txt, title line 452. The requirement paragraph is line 463; the title-to-paragraph source span is lines 452–463. Each quotation below is a contiguous excerpt from that paragraph, with omitted material between quotations.

> Measures the current of up to 10 DC linear actuators (24 V, relay-switched H-bridges), bidirectional, ±5 A per channel.

> V2: one STM32 digitizes all channels and sends the values over CAN.

> CAN data: calculated, calibrated current per channel in mA (not raw ADC values)

> Classic CAN 500 kbit/s, no isolation, transceiver with ±58 V bus fault protection

> Verification of all channels with reference currents and a filled-in test protocol per board (template provided)

**Relevant project proof:** STM32, protected 24 V supply, classic CAN, calibrated telemetry, four-layer enclosure integration, SWD/test points, error budgets, and tested boards are relevant.

**Coverage limit:** Rev A's four multiplexed high-side current readings are load diagnostics, not ten precision bidirectional ±5 A measurement channels. The listing explicitly requests nonisolated classic CAN; isolated CAN FD is this project's separate design choice.

## J05

**Mixed-signal sensor PCB design (KiCad or Altium), 4-layer, low-noise analog, all-SMT**

Original source: Pasted text (2)(6).txt, title line 1007. The requirement paragraph is line 1018; the title-to-paragraph source span is lines 1007–1018. Each quotation below is a contiguous excerpt from that paragraph, with omitted material between quotations.

> We need a 4-layer sensor board designed for an industrial sensing product.

> several MEMS accelerometers on two SPI buses, an environmental sensor, a 16-bit ADC, a real-time clock and a low-noise analog regulator.

> No controlled impedance is required, but the analog reference plane depends on layer order, so the stack-up must be stated.

> Demonstrated mixed-signal work — link a board where analog performance mattered

**Relevant project proof:** An external ADC, defined stack-up, analog supply/return decisions, filtering, calibration, and measured noise during load switching provide useful proof.

**Coverage limit:** This listing has accelerometer-specific noise and bonding geometry, an all-SMT construction, and two small boards. Rev A uses field terminals and relays; it does not match those mechanical requirements or prove accelerometer noise performance.
