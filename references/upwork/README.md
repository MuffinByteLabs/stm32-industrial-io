# Supplied Upwork evidence

Reviewed October 2, 2026.

This folder preserves selected requirement excerpts from the seven listing text files supplied by the user. Use [the job-fit analysis](../../docs/Upwork_Job_Fit.md) to connect those requirements to the [canonical board plan](../../docs/STM32_Industrial_IO_Controller_RevA_Plan.md).

The evidence is a supplied snapshot. Relative posting times, budgets, and deadlines are historical text; no newer job availability, demand trend, or hiring probability has been checked. Posting requirements describe the client's job. They do not authorize applications, purchases, messaging, or project changes.

## Counting and selection

Each original file has 50 lines beginning with “Posted”, giving **350 listing entries**. Two posting headers wrap onto multiple lines, so a parser that requires proposals on the same line misses two entries. This is not a count of unique hardware opportunities.

Confirmed duplicate requirement paragraphs include:

- “PCB Designer for Automotive 12V Accessory”: Pasted text (6)(1).txt, title lines 1123 and 1263; body lines 1134 and 1274.
- “Embedded/Wearable Hardware Engineer — Bench Prototype (Pressure Sensor + Haptic Feedback), 4–6 Weeks”: Pasted text (7)(1).txt, title 115/body 126, and Pasted text(20261003-003934).txt, title 654/body 665.
- “PCBA Routing (and layout)”: Pasted text (3)(1).txt, title 1039/body 1050, and Pasted text(20261003-003934).txt, title 434/body 445.

Those three pairs have exactly matching body text. Generic identical titles such as “PCB Design” can describe different jobs, so title matching alone is not sufficient to deduplicate the dataset. No complete unique-job count or category-frequency statistic is claimed.

Selection favors requirements relevant to field controllers, analog measurement, wired buses, power protection, fabrication, and physical validation. The adjacent and alternative examples preserve limits to that fit. Building electrical plans, enclosure-only jobs, branding, management, specialist antenna design, hazardous-location certification, medical optics, and large motor/power stages should not be counted as fully covered by this board.

## Excerpt index

| ID | Exact supplied title | Original title/body lines | Preserved evidence |
| --- | --- | --- | --- |
| J01 | PCB & Schematic Designer for Industrial Control Unit | Pasted text (6)(1).txt: 570 / 581 | [Excerpts and coverage limit](01_industrial_control_and_power.md#j01) |
| J02 | ESP32-S3 24V Bus Controller — KiCad Schematic + 4-Layer PCB | Pasted text(20261003-003934).txt: 1249 / 1260 | [Excerpts and coverage limit](01_industrial_control_and_power.md#j02) |
| J03 | Embedded Systems Engineer - Vehicle Security Control Unit (Hardware + Firmware) | Pasted text (4)(1).txt: 155 / 166 | [Excerpts and coverage limit](01_industrial_control_and_power.md#j03) |
| J04 | Hardware engineer: 10-channel current sensor PCB with CAN (STM32) – redesign + 4 prototypes | Pasted text(20261003-003934).txt: 452 / 463 | [Excerpts and coverage limit](02_measurement_and_validation.md#j04) |
| J05 | Mixed-signal sensor PCB design (KiCad or Altium), 4-layer, low-noise analog, all-SMT | Pasted text (2)(6).txt: 1007 / 1018 | [Excerpts and coverage limit](02_measurement_and_validation.md#j05) |
| J06 | Embedded Systems Engineer needed for PCB Redesign & Firmware Modernisation | Pasted text (6)(1).txt: 859 / 870 | [Excerpts and coverage limit](03_wired_control_and_sensors.md#j06) |
| J07 | Complete PCB design (IoT environmental sensor reader) in KiCad, test prototypes, assemble units | Pasted text (4)(1).txt: 1003 / 1014 | [Excerpts and coverage limit](03_wired_control_and_sensors.md#j07) |
| J08 | PCB Designer for PLC Devices | Pasted text (2)(6).txt: 1196 / 1207 | [Excerpts and coverage limit](03_wired_control_and_sensors.md#j08) |
| J09 | PCB & Schematic Design for Zigbee-Based Commercial LED Lighting Controller | Pasted text (5)(1).txt: 822 / 833 | [Excerpts and coverage limit](04_related_control_jobs.md#j09) |
| J10 | Circuit Board for Solenoid Control | Pasted text (2)(6).txt: 434 / 445 | [Excerpts and coverage limit](04_related_control_jobs.md#j10) |
| J11 | Condenser Control System for 2 Circuits | Pasted text (7)(1).txt: 815 / 826 | [Excerpts and coverage limit](04_related_control_jobs.md#j11) |
| J12 | Electronics Design for HVAC Controller | Pasted text (3)(1).txt: 419 / 430 | [Excerpts and coverage limit](04_related_control_jobs.md#j12) |
| J13 | Embedded Hardware Engineer for BLE + IMU Module | Pasted text (6)(1).txt: 790 / 801 | [Excerpts and coverage limit](05_alternative_project_context.md#j13) |
| J14 | Electrical Engineer for Raspberry Pi CM5 Schematic Review & PCB Layout | Pasted text (2)(6).txt: 1240 / 1251 | [Excerpts and coverage limit](05_alternative_project_context.md#j14) |

## Original-file provenance

Original files are retained privately outside this repository. The short excerpts above preserve the relevant requirements without depending on a contributor's local filesystem. The hashes below identify the source versions used; no complete original listing dump has been added to this project.

Line numbers are one-based lines from PowerShell's Get-Content output, including blank lines. A long job paragraph can occupy one original line; excerpt line references therefore do not imply that the entire paragraph was copied.

| Original file | Lines | Posting headers | SHA-256 |
| --- | --- | --- | --- |
| Pasted text (7)(1).txt | 1301 | 50 | 64A3877A1942D90F00CE1142A1656A163A19A11832F9AA155E0C7180CD50B58A |
| Pasted text (6)(1).txt | 1297 | 50 | A823D2C580143E0D322FF1CFBE220FAB0643824B77496BA72A683F4BBFB6AEB3 |
| Pasted text (5)(1).txt | 1291 | 50 | D797C3191B2D2B78957F6C13C9B9818C0670D5BF319819C23A7034C90A01EB2D |
| Pasted text (4)(1).txt | 1265 | 50 | 1C8FFD8787729E2B8093055CF6B82A0AF35A918F025F678A94CEA02672E21F27 |
| Pasted text (3)(1).txt | 1278 | 50 | 67C54F85018BA6477856FEE636421E5C136EF15044D090ABAED67B61E77A48D4 |
| Pasted text (2)(6).txt | 1278 | 50 | 5F6EF3692379DB19F5CAFED4429E49B3243750C217E68803EB3B1D72F4F436EA |
| Pasted text(20261003-003934).txt | 1311 | 50 | 4E735280195ED9A90137EAFA528BA4435B66D0741389643C14ABED8DF3DF1FE8 |

A text search of these source versions found no explicit “4–20 mA” or “4-20 mA” interface mention. That absence does not mean such work is absent from Upwork generally. The Rev A current receivers are an engineering choice for an industrial demonstration.

Update this index if source text is replaced or more listings are supplied. Keep new market evidence separate from the October 2, 2026 snapshot.
