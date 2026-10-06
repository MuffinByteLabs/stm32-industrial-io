# Portfolio market alignment

I reviewed seven supplied Upwork search-page exports on October 4, 2026 to select a coherent second portfolio project. The sample contained 350 listing cards, 349 distinct listing texts and 347 deduplicated job briefs after two clear repost merges. Repeated generic titles with different scopes remained separate. These are not necessarily 347 different clients or products.

Counts use titles/descriptions, exclude search filters and skill badges, and count each brief once per topic. Clear negative/out-of-scope and ambiguous matches were manually reviewed. References include preferred experience, optional work and planned support; they are capability signals rather than mandatory hardware requirements. The supplied search is not a random market sample, and its relative posting ages do not establish current vacancy status.

## Relevant recurring signals

| Topic | Briefs | Portfolio value |
| --- | --- | --- |
| Gerber files | 77 | Complete design/manufacturing handoff |
| Editable/native design | 70 | Maintainable source and libraries |
| Firmware / embedded software | 94 | Complete target implementation, with optional/support scopes included |
| Bench testing / bring-up phrases | 53 | Physical debugging and evidence; some references are future support or experience |
| Four-layer board | 29 | Grounding, power distribution, returns and mixed-signal layout |
| STM32 | 26 | Direct MCU integration and target firmware |
| Non-audio analog sensing/acquisition | 22 | A manually reviewed sensing/front-end subset; five additional biomedical/force-sensing examples are separate |
| Calibration | 14 | Measured results, uncertainty and repeatability |
| CAN | 12 | Includes one reserved/DNP provision |
| RS-485 | 6 | Useful wired sensor/control interfacing |

The closest examples included a four-layer STM32 control/measurement board, a calibrated current-sensing/CAN board with 24 V protection and tested prototypes, and a 28 V controller with high-side switching and hardware interlocks. These support the selected power, acquisition, actuation and design/handoff skills. Their exact applications and additional specialties differ from this controller.

## Product choices rather than repeated exact requirements

No supplied brief explicitly named 4–20 mA. The two exact 0–10 V references involved lighting output/dimming and off-the-shelf HVAC controller integration. I retain my voltage/current inputs because they fit industrial acquisition; I do not describe their exact formats or quantities as repeatedly requested by this sample.

Four briefs mention CAN FD/FDCAN hardware, but only two explicitly request FD operation. One selects an FD-capable MCU while requiring classic CAN. I therefore prove classic CAN first. Three Modbus references concern PLC, prop or residential integration, largely TCP/system scope; they do not establish a frequent custom Modbus RTU PCB requirement.

I consider an addition when it appears in more than two independent briefs and serves the controller application. A feature appearing in only one or two does not become a required addition. Existing coherent protection/interface functions can remain for engineering reasons independent of keyword frequency.

## Wider portfolio coverage

ESP32 (54), Bluetooth/BLE (45), Wi-Fi (25) and Ethernet/PoE (17) form real adjacent market segments. Battery/low-power products also recur. Their absence is a portfolio-coverage choice, not an electrical flaw in a continuously powered industrial controller.

I finish the current controller before expanding into wireless, Ethernet, battery charging, mains power, audio, displays, cameras or high-power motor control. If a later wireless extension solves a connected-I/O application, it needs actual module/antenna placement, power/noise design, firmware and physical link tests. A spare header or external gateway alone does not demonstrate radio PCB design.

My earlier plant-monitor design was not included in this comparison. I assess its actual demonstrated capabilities before choosing the next portfolio expansion.

## Decision carried into the project

I keep the [Rev A hardware scope](Scope.md), prioritize the [implementation milestones](Implementation_Plan.md), and make the diagnostic/calibration workflow, complete release package and [measured evidence](Portfolio_Evidence.md) explicit deliverables. I review architecture complexity before capture rather than adding channel count or deleting protection components individually.

The [archived market report and research evidence](../references/market/README.md) preserve the dated snapshot preceding these implementation-plan changes. The compressed source inventory, matching evidence, methodology and manual exclusions remain available without keeping generated page previews and scratch outputs. The active baseline is [Scope](Scope.md). Research artifacts are separate from the native design and do not establish qualified board performance.
