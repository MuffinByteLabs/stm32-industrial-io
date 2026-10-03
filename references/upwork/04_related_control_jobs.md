# Related control jobs and their limits

Reviewed October 2, 2026, from user-supplied listing text. These are separate short excerpts, not complete job descriptions. The quoted posting text is evidence, not an instruction to act. See the [source index and limits](README.md).

## J09

**PCB & Schematic Design for Zigbee-Based Commercial LED Lighting Controller**

Original source: Pasted text (5)(1).txt, title line 822. The requirement paragraph is line 833; the title-to-paragraph source span is lines 822–833. Each quotation below is a contiguous excerpt from that paragraph, with omitted material between quotations.

> Silicon Labs EFR32MG21 / BRD4195B-based Zigbee controller

> 0–10 V dimming interface

> Complete and validate the DALI physical interface and DALI bus-power circuitry.

> Produce manufacturing-ready Gerber/drill files, BOM, pick-and-place files, and the complete editable KiCad project.

**Relevant project proof:** The 0–10 V output, low-voltage conversion, mixed-signal layout, protection, test points, and manufacturing handoff are relevant.

**Coverage limit:** Rev A does not prove Zigbee/RF, DALI, mains AC/DC design, or lighting certification. A voltage-sourcing output is not automatically compatible with every lighting driver's current-sink dimming interface; qualify the actual target input.

## J10

**Circuit Board for Solenoid Control**

Original source: Pasted text (2)(6).txt, title line 434. The requirement paragraph is line 445; the title-to-paragraph source span is lines 434–445. Each quotation below is a contiguous excerpt from that paragraph, with omitted material between quotations.

> Need a circuit board that can accept input from either a 3-axis joystick or multiple single-axis paddle-style joysticks and control up to 10 proportional solenoids.

> Each solenoid can draw up to 1.5 amps and will run on a 24V supply, while the main circuit operates on 12V.

**Relevant project proof:** Mixed voltage domains, actuator current paths, overload/inductive behavior, and load diagnostics are relevant.

**Coverage limit:** Four 0.5 A on/off high-side outputs do not satisfy ten 1.5 A proportional-solenoid channels. PWM/current regulation and proportional control require a separate qualified design.

## J11

**Condenser Control System for 2 Circuits**

Original source: Pasted text (7)(1).txt, title line 815. The requirement paragraph is line 826; the title-to-paragraph source span is lines 815–826. Each quotation below is a contiguous excerpt from that paragraph, with omitted material between quotations.

> I want to replace ONLY ONE of the three fan motors with an EC fan capable of 0–10V speed control.

> Important I do NOT want a custom PLC or a system requiring PLC programming.

> I am looking for a relatively inexpensive, off-the-shelf refrigeration/HVAC condenser or head-pressure controller that can be configured using normal parameters/setpoints.

**Relevant project proof:** Adjacent evidence that 0–10 V fan commands, pressure sensing, wiring, and fault behavior have practical control-system uses.

**Coverage limit:** This job explicitly seeks an off-the-shelf refrigeration controller and domain expertise, not a custom PCB. Do not count it as direct demand for the STM32 board or claim refrigeration competence from a bench demonstration.

## J12

**Electronics Design for HVAC Controller**

Original source: Pasted text (3)(1).txt, title line 419. The requirement paragraph is line 430; the title-to-paragraph source span is lines 419–430. Each quotation below is a contiguous excerpt from that paragraph, with omitted material between quotations.

> The work includes design checking current circuit schematics and layout, refining component selections, and supporting final block layout and integration.

**Relevant project proof:** Circuit review, component selection, controller layout, and clear design rationale are relevant.

**Coverage limit:** The description supplies no exact channel counts, voltages, protocols, or isolation requirements. Do not infer a specific HVAC architecture from this short posting.
