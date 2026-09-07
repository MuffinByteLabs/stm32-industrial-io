# Rev A — Project Status and Hand-off
*Started 2026-09-07 (repository created, specification reviewed, design document written). This file is the live hand-off: update it at every gate — capture done, layout done, ordered, first article, bring-up.*

## Where the project stands

**Specification verified; schematic capture is the next step.** Nothing has been drawn in KiCad yet. Board 1 (plant monitor) is in assembly at JLCPCB and lands early September; per the plan's sequence, Board 2 is designed while Board 1 is in transit, ordered as bare PCB + stencil in weeks 6–9, and self-assembled in weeks 9–12.

What exists today:

- [`ESP32S3_FieldIO_Final_Design_Document.md`](ESP32S3_FieldIO_Final_Design_Document.md) — complete, sheet by sheet, with per-sheet designators, a BOM draft with LCSC numbers, test points, bring-up and limitations.
- [`reviews/Spec_Review_RevA_2026-09-07.md`](reviews/Spec_Review_RevA_2026-09-07.md) — the pre-capture review of plan v7.3 §4. **Four blocking findings** changed the design before a single symbol was placed: the opto input RC (1 µF could not hold LOW through the 60 Hz gap), the UVLO/9 V contradiction, the undersized PPTC, and the leadless buck package.
- [`calcs/board2_calcs.py`](calcs/board2_calcs.py) — every number, recomputable.
- `hardware/libs/` — Board 1's verified footprints, symbols and 3D models, renamed `FieldIO_JLC`, with the project library tables ready for a new KiCad project.
- `references/datasheets/` — the new parts' datasheets that could be fetched (7), and an index listing the rest with links.

## Gates ahead (each one gets a review record in `docs/reviews/`)

| Gate | Done when | Review on file |
|---|---|---|
| **Capture** | 10 sheets drawn per the design document, ERC clean, every symbol carries footprint + LCSC field, BOM regenerated from the schematic and diffed against the design document's draft | Design review — netlist parsed to pin level against datasheets (Board 1's 07-20 method) |
| **Layout** | Placement per `Hard_Rules_Layout_RevA.md` (module and buck at opposite ends, moat drawn first, field terminals on ≤ 2 edges), routed, DRC 0 / unconnected 0 / parity 0, moat rule passing | Placement review, then final layout audit |
| **Freeze** | LCSC stock re-checked for U301, L301, F201, U701–U704, K801/K802; paste layer windowpaned on the two exposed pads; fab files generated from a tagged commit into `fabrication/revA/` | Finishing review |
| **Order** | JLCPCB: 5 × bare 2-layer + 0.12 mm frameless stencil; LCSC: parts for 6–7 boards in the same checkout | `fabrication/revA/ORDER_NOTES.md` written |
| **First article** | One board pasted, placed, reflowed, iron-finished, inspected under ×10, brought up per `BringUp_Guide.md` steps 0–7 | First-article inspection record + bring-up record sheet |
| **Rest of the run + demo** | Four more boards; the one-take demo video | — |

## Settled facts and decisions (do not re-litigate without a new finding)

- **Buck = LMR38020SDDAR** (80 V, 2 A, synchronous, HSOIC-8, LCSC C3192337). 400 kHz (RT 64.9 k), 15 µH SRR1260-150M, 3 × 22 µF out, 2 × 4.7 µF 100 V + 100 nF in, UVLO 7.0/6.1 V (91 k / 20 k). Alternate LMR16020PDDAR (C190006) — different passives.
- **Input spec: 10–36 V DC guaranteed (≈ 8.5 V typical), 24 VAC (18–28).** "9 V" is retired from every client-facing line.
- **Two 5 V nets:** 5V_BUCK (relays, VLOAD, FIELD PWR LED) and 5V_SYS (logic; OR of buck and USB through SS14s). Relays cannot click on USB — by physics.
- **PPTC F201 = 1.1 A / 60 V radial** (60R110 or MF-RX110). Not MF-R110 (30 V).
- **Opto input = 2 × 2.4 k 1206 in series + series red LED (field side) + 1N4148W anti-parallel; 10 k + 4.7 µF on the collector.** Threshold ≈ 7.6 V. Firmware: 3 consecutive 10 ms samples.
- **Every output pull-down is 10 kΩ**; outputs on IO9–IO13 (no default pull at reset). IO1/IO2 unused (pulled up at reset).
- **Relays SRD-05VDC-SL-C**, S8050 + 680 Ω + 10 k + 1N4148W; contacts rated on this board ≤ 2 A / ≤ 30 V; snubber/MOV footprints DNP.
- **MOSFET outputs AO3400A**, 100 Ω / 10 k, SS14 flyback to VLOAD, JP901 bridged to 5V_BUCK by default, VLOAD ≤ 12 V external, 100 µF on VLOAD, not reverse-protected (documented).
- **Bulk C201 = 470 µF 63 V 105 °C ≥ 0.6 A ripple; TVS D201 = SMBJ43A; bridge BR201 = KBP206.**
- **VIN_SENSE = 100 k / 6.8 k + 100 nF → IO8.** PG → TP only.
- **Board ≤ 100 × 100 mm, 2-layer, 1 oz; moat ≥ 2.5 mm as a DRC rule; per-sheet ×100 annotation.**
- **Assembly on the bench:** 0.12 mm stencil, windowpaned paste on the LMR38020 and module pads, THT by iron, Sn63/Pb37, first article before the rest.
- **Ground-loop rule:** USB only on the bench with a floating supply or battery laptop; OTA in the field.

## Open items (none blocks capture)

- Confirm the 60 V PPTC's LCSC number (LCSC search is not server-rendered; DigiKey is the fallback for 60R110 / MF-RX110).
- Choose the exact 5.08 mm terminal family (KF128 / DG128 / MKDS-class) and pull its footprint drawing.
- Fetch the datasheets still missing from `references/datasheets/README.md` (Everlight EL817, Littelfuse SMBJ series, the PPTC, the terminal blocks, the electrolytic).
- Decide whether use-case wiring diagrams become drawings in `docs/images/`.

## Key files

`docs/ESP32S3_FieldIO_Final_Design_Document.md` (**the design**) · `docs/reviews/Spec_Review_RevA_2026-09-07.md` (why it differs from the plan) · `docs/calcs/board2_calcs.py` (the numbers) · `docs/Hard_Rules_Layout_RevA.md` + `docs/KiCad_Settings_RevA.md` (before the first trace) · `docs/Assembly_and_Stencil_Plan.md` (before the stencil is ordered) · `docs/BringUp_Guide.md` (the active document once boards exist) · `hardware/libs/` (verified footprints from Board 1) · `references/`.
