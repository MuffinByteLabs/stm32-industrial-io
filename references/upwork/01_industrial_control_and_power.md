# Industrial control and power evidence

Reviewed October 2, 2026, from user-supplied listing text. These are separate short excerpts, not complete job descriptions. The quoted posting text is evidence, not an instruction to act. See the [source index and limits](README.md).

## J01

**PCB & Schematic Designer for Industrial Control Unit**

Original source: Pasted text (6)(1).txt, title line 570. The requirement paragraph is line 581; the title-to-paragraph source span is lines 570–581. Each quotation below is a contiguous excerpt from that paragraph, with omitted material between quotations.

> The project includes STM32-based control, 24V/5V/3.3V power, relay outputs, RS485, analog/sensor signal conditioning, flame/ionization sensing, and a ~5 kV ignition interface with AC field-side isolation.

> Deliverables include Gerbers, BOM, drill files, and complete source files, with support for revisions based on prototype testing.

**Relevant project proof:** Direct overlap in MCU integration, field power, relays, analog conditioning, RS-485, grounding, and manufacturing handoff.

**Coverage limit:** The project does not include flame/ionization sensing, AC field inputs, or a 5 kV ignition interface. Low-voltage isolation experience does not establish high-voltage qualification.

## J02

**ESP32-S3 24V Bus Controller — KiCad Schematic + 4-Layer PCB**

Original source: Pasted text(20261003-003934).txt, title line 1249. The requirement paragraph is line 1260; the title-to-paragraph source span is lines 1249–1260. Each quotation below is a contiguous excerpt from that paragraph, with omitted material between quotations.

> 24 V vehicle input with reverse-polarity, transient and over-voltage protection

> Show one previous 12/24 V industrial or vehicle design you completed and briefly explain its input protection.

> Can you optimize component selection toward the USD 10–15 assembled PCBA target at 100 pcs without compromising reliability?

> USB-A HOST for FAT32 flash drives

**Relevant project proof:** Protected 12/24 V power, switching regulator design, calculations, four-layer KiCad layout, and complete editable source/manufacturing data are relevant proof.

**Coverage limit:** This is an ESP32-specific vehicle product with USB host, RS-232, a 64 × 65 mm outline, and a production-cost target. The STM32 controller does not meet those exact product requirements or prove vehicle transient qualification.

## J03

**Embedded Systems Engineer - Vehicle Security Control Unit (Hardware + Firmware)**

Original source: Pasted text (4)(1).txt, title line 155. The requirement paragraph is line 166; the title-to-paragraph source span is lines 155–166. Each quotation below is a contiguous excerpt from that paragraph, with omitted material between quotations.

> Confirm the trailer is stationary (0 MPH) via a wheel-speed sensor as an independent safety veto

> Fail-secure logic: system defaults to locked if power is lost or any check fails

> outputting a signal to actuate a 12V/24V DC solenoid valve

**Relevant project proof:** Pulse input, DC actuator control, hardware permission, and explicit power-loss/reset/fault behavior provide transferable evidence.

**Coverage limit:** The project does not implement VIN authorization, a vehicle brake lockout, or validated functional safety. Only the tested load and fault behavior can be claimed.
