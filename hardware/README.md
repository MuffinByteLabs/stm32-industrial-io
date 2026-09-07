# hardware/ — KiCad 10 project (to be created)

Create the project **in this folder** as `ESP32S3_FieldIO` (File → New Project → `hardware/ESP32S3_FieldIO.kicad_pro`). The project-local library tables are already here and point at `${KIPRJMOD}/libs/`, so KiCad picks up the libraries the moment the project exists.

## Sheet plan (one sheet per design-document section; designators = sheet × 100)

| Sheet file | Design doc | Designators |
|---|---|---|
| `ESP32S3_FieldIO.kicad_sch` (root, 01_System) | §2 | — (hierarchy only) |
| `02_Field_Power_Entry.kicad_sch` | §3 | 2xx |
| `03_Buck_5V.kicad_sch` | §4 | 3xx |
| `04_USB_C_Input.kicad_sch` | §5 | 4xx |
| `05_3V3_Power.kicad_sch` | §6 | 5xx |
| `06_ESP32S3_Core.kicad_sch` | §7 | 6xx |
| `07_Opto_Inputs.kicad_sch` | §8 | 7xx |
| `08_Relay_Outputs.kicad_sch` | §9 | 8xx |
| `09_MOSFET_Outputs.kicad_sch` | §10 | 9xx |
| `10_Mechanical.kicad_sch` | §11 | H1–H4, G1 |

Set *Annotate → Use first free number after* per sheet (200, 300, …) **before** placing the first symbol.

## `libs/` — carried over from Board 1, renamed

`FieldIO_JLC.pretty`, `FieldIO_JLC.kicad_sym` and `FieldIO_JLC.3dshapes` are Board 1's `PlantMonitor_JLC` library with the name changed and the VEML7700 files dropped. What is in it and why it matters:

| Footprint / symbol | Verified on Board 1 | Note |
|---|---|---|
| `USB_C_Receptacle_HRO_TYPE-C-31-M-12` + STEP | assembled, 5 boards | shell overhang ≈ 1 mm per the HRO drawing |
| `SW-SMD_4P-L5.1-W5.1-P3.70-LS6.5-TL_H1.5` + symbol `TS-1187A-B-A-B` | assembled | **pads renumbered 1/1/2/2** — the 4-pad pairing trap is already solved |
| `D_SMA`, `D_SOD-123F`, `Fuse_1206_3216Metric` | assembled | SS14, SMF5.0A, 1206L075 |
| `logos/logos.pretty` (`muffinByteLogo`, `_2x`) | on Board 1's silk | use the 2× |

New footprints for this board (draw or import, then check each against its datasheet drawing per Board 1's `Footprint_Check` method): LMR38020 HSOIC-8 (TI DDA), SRR1260, KBP, Hongfa HF3FF (from the Hongfa drawing), EL817S1 SMD-4, Degson DG128 terminals ×4 sizes, radial PPTC, Ø 12.5 mm radial electrolytic, 07D MOV; from KiCad stock: SOT-223-3_TabPin2 (AP7361C), **SolderJumper_2_Open** (JP901 ships open), TestPoint pads.

## Housekeeping (Board 1 lessons)

- `.gitignore` already excludes backups, autosaves, `fp-info-cache`, `hardware/jlcpcb/` and `hardware/.history/`.
- Keep 3D model paths `${KIPRJMOD}`-relative.
- Save (Ctrl-S) before every check — git, scripts and the fab read the disk, not the editor.
