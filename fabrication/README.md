# Fabrication packages

Factory output files, one folder per ordered revision. Each folder will hold the **exact files uploaded
to the fab** — never a regenerated copy — so what is in here is what was manufactured.

**Nothing is ordered yet.** `revA/` is created when the Rev A order is placed.

## What `revA/` will contain (the Board 1 recipe, plus the stencil)

| File | What |
|---|---|
| `GERBER-ESP32S3_FieldIO.zip` | The uploaded gerber set: F.Cu, B.Cu, F.Mask, B.Mask, **F.Paste** (with the two windowpaned pads), F.Silkscreen, B.Silkscreen, Edge.Cuts + Excellon PTH/NPTH |
| `STENCIL_NOTES.md` | Stencil order settings: frameless, top only, **0.12 mm**, custom size, and the paste-preview screenshot |
| `BOM-ESP32S3_FieldIO.csv` | The BOM with LCSC numbers as ordered from LCSC (no PCBA line) |
| `LCSC_ORDER.csv` | The LCSC cart as checked out (quantities for 6–7 boards) |
| `ORDER_NOTES.md` | Every setting the board was ordered with, the pre-upload gate and how each item closed, the cost record |
| `production_check/` | Screenshots of the fab preview: copper, paste, silk, outline |

5 boards · 2-layer · lead-free HASL · **bare PCB + stencil — assembled on the bench.**

## Recipe

Freeze the exact uploaded zip + BOM, the LCSC order export, the stencil settings, the order confirmation, and
the git tag that produced them (`revA`). Tag the commit the fab files were generated from so the package can
always be traced back to a board file. Board 1's `fabrication/revA/ORDER_NOTES.md` is the template.
