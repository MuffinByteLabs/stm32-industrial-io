# mechanical/ — enclosure, outline, 3D

A field I/O controller lives on **DIN rail** inside a modular enclosure with terminal windows along its two long edges. That decision shapes the board outline, the terminal positions, the LED positions (they must show through the lid) and the USB/button access — so it is made **before layout**, and the board is drawn to the enclosure's PCB drawing, not the other way round.

## Decision to make (before the first footprint is placed)

| Option | Size (W × H × D) | PCB it takes | Notes |
|---|---|---|---|
| **Camdenboss CNMB/6/KIT** (reference class) | 106 × 90 × 58 mm, 6 modules | per its datasheet PCB drawing (≈ 100 × 85 mm class; take the exact outline from the drawing) | polycarbonate, IP20, terminal windows both long edges, vented-lid variant CNMB/6V; Farnell/Newark/RS/CPC |
| Phoenix Contact ME / UM-PRO series | 6-module equivalents | per drawing | the industrial reference; DigiKey/Mouser; dearer |
| OKW Railtec B/C, Italtronic Modulbox XTS, generic "DIN rail PCB enclosure 6M" (AliExpress/Amazon) | ≈ 106 × 90 | per drawing | cheaper; check that a PCB drawing exists before trusting the size |

Whichever is chosen: put its PCB drawing (DXF/PDF) in this folder, import the outline into KiCad (`File → Import → Graphics` onto `Edge.Cuts`), and place the five terminals at the window positions. Keep the board inside JLC's ≤ 100 × 100 mm tier; a 6-module enclosure's PCB is inside it.

## Layout consequences (feed into `docs/Hard_Rules_Layout_RevA.md`)

- Field terminals (J201, J701, J801, J802) on one long edge; J901 (VLOAD, logic-referenced) and the USB-C on the other — the enclosure's two windows are the plan's "at most two edges" rule made physical. Antenna end of the module toward a plastic wall, ≥ 15 mm from any terminal or wire.
- LEDs (3V3, FIELD PWR, STATUS, four input LEDs, two relay LEDs, two output LEDs) in a row under the lid's window or behind light pipes; the input LEDs are on the field side of the moat by design, so the moat runs parallel to the LED row.
- BOOT / RESET buttons and the USB-C reachable with the lid on, on the logic-side edge.
- Mounting: the enclosure's PCB slots replace the four M3 holes for the enclosed build; keep the holes anyway for the bench and the demo (rule: no hole in the antenna region, Ø 6.5 mm keep-out).
- Heat: the buck, the bridge and the relays are the warm parts — they go toward the vented end if the vented-lid variant is used.

## Files this folder will hold

`<enclosure>_PCB_drawing.pdf` · `board_outline.dxf` (exported from KiCad after layout) · `ESP32S3_FieldIO_RevA.step` (KiCad 3D export, for the enclosure fit check) · photos of the fit.
