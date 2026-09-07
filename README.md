# ESP32-S3 Protected Field I/O Controller — Rev A

**Ray Malik** · [muffinbytelabs.com](https://muffinbytelabs.com) · [muffinbytelabs@gmail.com](mailto:muffinbytelabs@gmail.com)

The second board in the series after the [ESP32-S3 Plant Monitor](https://github.com/MuffinByteLabs/esp32s3-plant-monitor). A Wi-Fi board that safely **hears** 12–30 V equipment signals and safely **presses** equipment buttons: the board that HVAC thermostat wiring, 24 VAC valves and pumps, sprinkler zones, float switches and 12 V vehicle circuits are all asking for. Runs from the equipment's own power.

**Status — specification verified, schematic capture starting (2026-09-07).** The design document below is complete and every number in it has been re-derived from datasheets; the review that did that is on file. No copper exists yet. This README is written in the future tense on purpose and will be rewritten as the board becomes real.

| | |
|---|---|
| **Power in** | 12–36 V DC either polarity (guaranteed down to 10 V), or 24 VAC (18–28 VAC) — one screw terminal, fused, bridge-rectified, TVS-clamped |
| **Rails** | LMR38020 synchronous buck (80 V, 2 A) → 5 V for relays and loads · SS14 diode-OR → 4.6 V logic rail · AP7361C (1 A, SOT-223) → 3.3 V |
| **Inputs** | 4 × opto-isolated (EL817, rank C), shared COM, AC or DC, either polarity, **IEC 61131-2 Type 1 thresholds** (OFF ≤ 5 V, ON ≥ 15 V), 36 V continuous |
| **Outputs** | 2 × SPDT relay contact sets (Hongfa HF3FF, UL/VDE, AgSnO₂) on terminals, rated here ≤ 2 A / ≤ 30 V AC-DC, isolated · 2 × low-side MOSFET (AO3400A) with a 5 V-or-external VLOAD jumper |
| **MCU** | ESP32-S3-WROOM-1-N8, native USB-C for bench programming only, OTA in the field |
| **Board** | 2-layer, 1 oz, sized to a 6-module DIN-rail enclosure (≤ 100 × 100 mm), field side / logic side with a ≥ 2.5 mm moat enforced by DRC, fiducials |
| **Assembly** | Bare PCB + 0.12 mm stencil from JLCPCB, hot-plate reflow and iron on the bench (Sn63/Pb37 — not RoHS) |
| **Tools** | KiCad 10 · LCSC parts · JLCPCB fab |

## Start here

| | |
|---|---|
| 📄 **[Design document](docs/ESP32S3_FieldIO_Final_Design_Document.md)** | Every component and why it is there, organised sheet by sheet, written to be read by someone who is not a PCB engineer |
| 🔍 **[Specification review](docs/reviews/Spec_Review_RevA_2026-09-07.md)** | The pre-capture review: 4 blocking findings, 6 risky, 12 improvements, 11 numbers confirmed — and what changed because of them |
| 🔍 **[Second-opinion review](docs/reviews/Second_Opinion_Review_RevA_2026-09-07.md)** | An independent review of the same spec, weighed point by point: 9 adopted, 6 declined with arithmetic |
| 🏷 **[Industry-standard audit](docs/reviews/Industry_Standard_Audit_RevA_2026-09-07.md)** | Every part checked for lifecycle, grade and sourcing; the design checked against IEC 61131-2, IPC-2221/7351/A-610, J-STD-020/033; the repository against what an engineering organisation expects |
| 🧮 **[The arithmetic](docs/calcs/board2_calcs.py)** | One Python file that recomputes every number in the design document |
| 🧭 **[Project status](docs/PROJECT_STATUS.md)** | Where the project stands, what is decided, what is next |
| 🔧 **[Bring-up guide](docs/BringUp_Guide.md)** | Staged first power, expected voltages, record sheet |
| 🏭 **[Assembly plan](docs/Assembly_and_Stencil_Plan.md)** | Stencil, paste apertures, placement order, first-article inspection |

## One board, six use cases — nothing on the copper changes

| # | Use case | Wire it like this | Output |
|---|---|---|---|
| 1 | **HVAC runtime monitor** (listen-only, safest) | IN1 = W (heat), IN2 = Y (cool), IN3 = G (fan), COM = C; power from R and C | none — runtime data, filter reminders, short-cycle alerts |
| 2 | **Whole-house air circulation** | as above, plus K1 COM → R, K1 NO → G | relay in parallel with the fan wire |
| 3 | **AC condensate overflow supervisor** | IN4 = float switch to COM; K2 wired in series with Y through **NC**, *in addition to* the OEM float-switch interlock | a second trip and a phone alert if the pan floods; NC keeps cooling running if this board dies (fail-operational by choice — the OEM interlock stays the safety device) |
| 4 | **One sprinkler zone** | 24 VAC transformer to PWR IN; K1 COM → 24 VAC, K1 NO → valve | relay switches 24 VAC to the valve |
| 5 | **Water-leak alarm** | leak pads across IN1/COM with a 12–24 V source; buzzer between VLOAD+ and OUT1− (JP901 closed) | buzzer + phone alert |
| 6 | **Plant waterer** | Board 1's "dry" message + float switch on IN1; pump between VLOAD+ and OUT1− (JP901 closed) | pump on OUT1 |

Uses 1–3 fit one board at once: three monitor inputs + the float switch, fan relay + cooling relay. That is why the count is 4-in / 2-relay and locked.

## What this board demonstrates

- **A buck converter laid out on two layers, with the numbers** — hot loop, SW node, UVLO divider, inductor saturation against the current limit, TVS clamp against the converter's absolute maximum.
- **Isolation as a layout discipline** — a field side and a logic side, a moat the DRC enforces, and an honest isolation map (what is isolated, what is not, and why the power input is not).
- **AC-and-DC field inputs done properly** — IEC 61131-2 Type 1 thresholds from a series Zener, series resistance split for dissipation and voltage rating (anti-surge class), anti-parallel diode, and an RC that actually holds LOW through the 60 Hz gap (the arithmetic is in the reviews; the plan's first value did not).
- **Outputs that cannot chatter at boot** — pull-downs sized against the ESP32-S3's reset-state pull-ups, pins chosen from the datasheet's no-default-pull set, and a load-supply jumper that is open until someone closes it on purpose.
- **A bench that assembles its own prototypes** — stencil and hot plate, and the design rules that fall out of that (leaded packages only, through-hole for anything with a screw or a coil, windowpaned paste on exposed pads).
- **A documentation trail from day zero** — the specification was reviewed three times before capture (a number-by-number review, an independent second opinion, and an industry-standard audit), and each one changed it.

## Repository map

| Path | What |
|---|---|
| [`docs/ESP32S3_FieldIO_Final_Design_Document.md`](docs/ESP32S3_FieldIO_Final_Design_Document.md) | The full design document, per-sheet designators, BOM draft, test points, bring-up, limitations |
| [`docs/reviews/`](docs/reviews/README.md) | Review records, [indexed here](docs/reviews/README.md) |
| [`docs/calcs/board2_calcs.py`](docs/calcs/board2_calcs.py) | The arithmetic |
| [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) | Live hand-off |
| [`docs/PinMap_CheatSheet.md`](docs/PinMap_CheatSheet.md) | GPIO / net / terminal map |
| [`docs/Hard_Rules_Layout_RevA.md`](docs/Hard_Rules_Layout_RevA.md) | The graded rulebook — Board 1's, amended for a switcher and a moat |
| [`docs/KiCad_Settings_RevA.md`](docs/KiCad_Settings_RevA.md) | Board setup, netclasses, the moat DRC rule |
| [`docs/Assembly_and_Stencil_Plan.md`](docs/Assembly_and_Stencil_Plan.md) | Bench assembly, stencil, apertures, first article |
| [`docs/BringUp_Guide.md`](docs/BringUp_Guide.md) | First power, expected voltages, record sheet |
| [`hardware/`](hardware/README.md) | KiCad 10 project (to be created); verified footprints and 3D models carried over from Board 1 in `hardware/libs/` |
| [`mechanical/`](mechanical/README.md) | The DIN-rail enclosure decision, its PCB drawing, the board outline and 3D export |
| [`CHANGELOG.md`](CHANGELOG.md) | Revision history (Keep-a-Changelog format) |
| [`.github/workflows/kicad-ci.yml`](.github/workflows/kicad-ci.yml) | ERC/DRC on every push once the KiCad project exists; schematic PDF and gerbers on `rev*` tags |
| [`fabrication/`](fabrication/README.md) | Frozen fab packages, one folder per ordered revision — empty until Rev A is ordered |
| [`firmware/`](firmware/README.md) | The hardware → firmware contract; the sketch comes after bring-up |
| [`references/datasheets/`](references/datasheets/README.md) | Vendor datasheets, [indexed here](references/datasheets/README.md) |
| [`references/JLCPCB_Capabilities_2026-08.md`](references/JLCPCB_Capabilities_2026-08.md) | Capability quick-sheet used for DFM (Board 1's capture) |

## Safety notes for anyone wiring this board

1. **Never mains.** ≤ 30 V AC or DC on any terminal, ≤ 2 A through any relay contact. The silkscreen says so; so does the design.
2. **The power input and the MOSFET outputs share the board's ground; only the opto inputs and the relay contacts are isolated.** An external VLOAD supply must return to the GND pin — and **meter its polarity first**: a reversed VLOAD supply shorts through the flyback diodes. JP901 ships open; close it only to run 5 V loads from the board, never with an external supply on VLOAD+.
3. **DISCONNECT FIELD POWER BEFORE USB** — it is printed on the board. With an earthed field supply and an earthed laptop, the USB cable's ground would carry the board's return current around the bridge rectifier. The only exception is the bench with a floating supply (the plug-in 24 VAC transformer, an unearthed bench supply) or a battery-powered laptop. In the field, firmware updates are over Wi-Fi.
4. **Inductive loads on the relays** (valves, contactor coils) need the snubber/MOV footprints fitted, or a diode across a DC load. The footprints are there, unpopulated, and the design document says what goes in them.
5. **Boards assembled here use leaded solder** and are not RoHS-compliant.
6. **This board supervises equipment; it is not the equipment's safety interlock.** Leave the manufacturer's float switches, high-limit switches and fuses in circuit.

## License

Hardware design files and documentation are released under the **CERN Open Hardware Licence v2 — Permissive** (see [`LICENSE`](LICENSE)). Vendor datasheets in `references/datasheets/` remain the property of their respective manufacturers and are included for convenience only.
