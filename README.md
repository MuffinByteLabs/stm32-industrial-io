# STM32 Industrial I/O Controller — Rev A

**Ray Malik** · [muffinbytelabs.com](https://muffinbytelabs.com) · [muffinbytelabs@gmail.com](mailto:muffinbytelabs@gmail.com)

[![Project audit](https://github.com/MuffinByteLabs/stm32-industrial-io/actions/workflows/project-audit.yml/badge.svg)](https://github.com/MuffinByteLabs/stm32-industrial-io/actions/workflows/project-audit.yml)
[![KiCad checks](https://github.com/MuffinByteLabs/stm32-industrial-io/actions/workflows/kicad-ci.yml/badge.svg)](https://github.com/MuffinByteLabs/stm32-industrial-io/actions/workflows/kicad-ci.yml)

A second portfolio project after the [ESP32 plant monitor](https://github.com/MuffinByteLabs/esp32s3-plant-monitor): a four-layer controller that measures industrial sensors, switches DC actuators, communicates over wired buses, and reports faults.

**Status, October 2, 2026: planning and reference preparation.** The new plan and supporting guides are in place. The new schematic, PCB, firmware, enclosure, and measured qualification have not been completed. All ratings below are engineering targets.

The project audit checks documents and planning arithmetic. At this stage the KiCad workflow reports native hardware checks as not run.

| Function | Planned Rev A |
| --- | --- |
| Controller | STM32G474VET6 directly on the PCB, LQFP100 |
| Field supply | Nominal 12/24 V DC; 9–30 V operating target; reverse-polarity, surge, and current protection |
| Sensor inputs | Four group-isolated DC digital inputs, including one pulse input; two 0–10 V inputs; two externally powered 4–20 mA loop receivers |
| Actuator outputs | Four diagnosed high-side outputs, 0.5 A each simultaneously; two SPDT dry-contact relays; one protected 0–10 V voltage-source output |
| Communication | Separately isolated RS-485/Modbus and CAN; USB service and SWD |
| Reliability | Hardware output permission, reset supervision, external watchdog, command timeout, and recoverable calibration |
| PCB and enclosure | Four layers; approximately 140 × 100 mm starting envelope; insulated mounting and labeled pluggable terminals |
| Completion evidence | At least three working units, calibration, fault tests, thermal results, firmware, and a reproducible manufacturing handoff |

The [job-fit review](docs/Upwork_Job_Fit.md) checks the scope against the supplied listings and connects each capability to finished evidence. It also records the gaps: proportional solenoids, ten-channel precision current sensing, wireless products, automotive qualification, and high-voltage ignition need additional work.

## Start here

1. Read the [complete board plan](docs/STM32_Industrial_IO_Controller_RevA_Plan.md), the source of truth for architecture and acceptance targets.
2. Read the [project status](docs/PROJECT_STATUS.md) and [open engineering items](docs/Open_Engineering_Items.md) before starting schematic capture.
3. Use the [resource reservations](docs/PinMap_CheatSheet.md), [wiring guide](docs/Interface_and_Wiring_Guide.md), and [firmware contract](firmware/README.md) to keep hardware and software aligned.
4. Complete the [layout rules](docs/Hard_Rules_Layout_RevA.md), [KiCad setup](docs/KiCad_Settings_RevA.md), [assembly plan](docs/Assembly_and_Stencil_Plan.md), and [bring-up guide](docs/BringUp_Guide.md) in that order.

## Repository map

| Location | Purpose |
| --- | --- |
| [docs/](docs/PROJECT_STATUS.md) | Requirements, engineering decisions, implementation guides, and status |
| [docs/calcs/](docs/calcs/README.md) | Executable planning arithmetic with explicit assumptions |
| [docs/reviews/](docs/reviews/README.md) | Migration record and future design-review evidence |
| [hardware/](hardware/README.md) | Future KiCad project, retained candidate footprints, models, and branding |
| [firmware/](firmware/README.md) | Implementation contract; application source is pending |
| [mechanical/](mechanical/README.md) | Enclosure, terminals, mounting, and thermal integration plan |
| [fabrication/](fabrication/README.md) | Release-package requirements; no ordered revision yet |
| [references/datasheets/](references/datasheets/README.md) | Candidate-family manufacturer PDFs and identity/hash manifest |
| [references/reference-designs/](references/reference-designs/README.md) | Manufacturer guidance and relevant reference designs |
| [references/standards/](references/standards/README.md) | Standards applicable to later design and qualification decisions |
| [references/upwork/](references/upwork/README.md) | Saved job excerpts and exact source locations |
| [scripts/](scripts/README.md) | Reference maintenance and repository checks |
| [.github/workflows/kicad-ci.yml](.github/workflows/kicad-ci.yml) | Future native-design checks and four-layer release exports |
| [CHANGELOG.md](CHANGELOG.md) | Revision history |
| [GitHub project guide](docs/GitHub_Project_Guide.md) | Repository, roadmap, checks, and release process |

The previous design, empty KiCad placeholders, obsolete sourcing draft, and superseded references were removed from the active project. A verified recovery archive was saved outside this folder; its location and hash are recorded in the [migration review](docs/reviews/Folder_Migration_2026-10-02.md).

Keep performance claims tied to measurements from the finished hardware. Manufacturer ratings and successful document checks alone do not qualify a board.

## License and third-party material

Original project design sources and documentation use [CERN-OHL-P-2.0](LICENSE). Manufacturer datasheets, job excerpts, and imported CAD/library assets remain attributed to their respective owners and retain their original terms. See the [local library notices](hardware/libs/README.md) for KiCad-derived assets.
