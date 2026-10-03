# Wired control and sensor evidence

Reviewed October 2, 2026, from user-supplied listing text. These are separate short excerpts, not complete job descriptions. The quoted posting text is evidence, not an instruction to act. See the [source index and limits](README.md).

## J06

**Embedded Systems Engineer needed for PCB Redesign & Firmware Modernisation**

Original source: Pasted text (6)(1).txt, title line 859. The requirement paragraph is line 870; the title-to-paragraph source span is lines 859–870. Each quotation below is a contiguous excerpt from that paragraph, with omitted material between quotations.

> The controller board communicates over an RS485 multi-drop bus, receives commands from a master PC, triggers electronic locks, and monitors latch status.

> A Windows PC application for configuring, commanding, monitoring, and stress-testing the V2 controller over RS485.

> modern SMD components, improved firmware, a formal communication protocol, and full documentation.

**Relevant project proof:** Working RS-485 multidrop, output/feedback logic, a documented data model, host stress tests, and manufactured SMD hardware are relevant.

**Coverage limit:** Rev A is a fresh design, not reverse engineering of this deployed locker platform. Modbus and the planned host tools do not establish compatibility with the client's legacy protocol or 30-door variants.

## J07

**Complete PCB design (IoT environmental sensor reader) in KiCad, test prototypes, assemble units**

Original source: Pasted text (4)(1).txt, title line 1003. The requirement paragraph is line 1014; the title-to-paragraph source span is lines 1003–1014. Each quotation below is a contiguous excerpt from that paragraph, with omitted material between quotations.

> Then I would like a batch of prototypes ordered from JLCPCB, and for those units to be fully tested.

> The main MCUs used on this board are: -Nordic nRF54L15 (as Raytac AN54LV-U15) - Nordic nRF9151 - STM32U073RCT6

> RS-485 for industrial sensors

> pulse counting for tipping bucket rain gauges and irrigation flow meters

> 0-5V ADC for analogue sensors

**Relevant project proof:** STM32 integration, industrial sensor interfaces, pulse counting, analog measurement, KiCad manufacture, and multiple tested units are relevant.

**Coverage limit:** The listing also needs Nordic radios, cellular connectivity, SDI-12, 1-wire, several power-source types, and a proprietary impedance reader. Those are not Rev A features. A 0–5 V sensor can be a supported test case without changing the board into a full environmental gateway.

## J08

**PCB Designer for PLC Devices**

Original source: Pasted text (2)(6).txt, title line 1196. The requirement paragraph is line 1207; the title-to-paragraph source span is lines 1196–1207. Each quotation below is a contiguous excerpt from that paragraph, with omitted material between quotations.

> Design PCB layouts for daughterboard / expansion modules that mount to M5Stack Core-series hardware, working within available enclosure form factors.

> Integrate sensor and I/O circuitry.

> Ability to produce manufacturing-ready outputs: Gerbers, BOM, assembly drawings

> Experience with load cell circuits and RTD/thermocouple signal conditioning

**Relevant project proof:** Sensor/I/O integration, compact enclosure planning, power management, and manufacturing documents are relevant general capabilities.

**Coverage limit:** The board is not an M5Stack daughterboard and does not contain raw load-cell, RTD, or thermocouple front ends. Those are preferred specializations, not reasons to add more Rev A channels.
