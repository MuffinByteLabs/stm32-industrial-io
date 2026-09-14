# Pre-Capture Deep Check — 2026-09-14

*The last look before the first symbol: every datasheet in `references/datasheets/` opened and its
contents checked against the part it claims to be; the BOM draft cross-checked against the design
document and against LCSC's live listings (stock and brand read from LCSC's product API on
2026-09-14); the pin map checked pin-by-pin against the WROOM-1 module datasheet; the reset-pull and
power-up-glitch claims checked against the ESP32-S3 SoC datasheet v2.2 (fetched today);
`docs/calcs/board2_calcs.py` re-run end to end. Method: contents, not filenames — each PDF's first
page and the specific table the design leans on.*

**Verdict: the specification stands. Nothing found changes a single value in the design document.**
One reference document was the wrong part outright, one part went out of stock at LCSC with a
drop-in fix, and three factual claims in the prose need correcting. Capture can start.

## Findings

### 1 — Wrong document (would have poisoned a footprint)

**`BRIDGE_Diodes_KBP2xx_2A_Datasheet.pdf` was the KBJ4005G–KBJ410G datasheet** — the 4 A **KBJ**
package, a different outline entirely; the file contains no mention of "KBP" at all. The pre-capture
checklist draws the BR201 footprint "from its datasheet drawing", so this file was one working
session away from producing a KBJ footprint under a KBP part. Replaced with two correct documents:
the MDD KBP2005–KBP210 sheet (the exact LCSC C2494 part — the footprint master now) and the Diodes
KBP2005G–KBP210G family sheet. **Delete the old KBJ file** (a session without delete permission
added the replacements beside it).

Every other PDF in the folder checked out: the LMR38020 file is SNVSC40E Rev E (RT = 64.9 k ↔
400 kHz confirmed in its tables); SRR1260-150M row reads 15 µH / Isat 4.60 A / Irms 5.00 A / 27 mΩ
exactly as the BOM claims; the HF3FF sheet carries UL E134517 and the 5 V / 70 Ω ± 10 % coil the
drive arithmetic uses; the AP7361C pin table confirms SOT-223 pin 1 = IN, **pin 2 = GND = tab**,
pin 3 = OUT (so KiCad's `SOT-223-3_TabPin2` is right); the SS14 file's odd Title metadata is
cosmetic (contents are the SS12–SS1200 family sheet).

### 2 — Stock (LCSC, read 2026-09-14)

| Part | LCSC | Stock | Note |
|---|---|---|---|
| **EL817S1(C)(TU)-F** (U701–U704) | C106900 | **0** | Drop-in: **EL817S1(C)(TU)-FV, C470884, 4,410 in stock** — same S1 gull-wing, same rank C; per Everlight's own sheet the V suffix is the **VDE-certified option** (which suits this board), not a voltage grade |
| **CL10A105KB8NNNC** (C701–C704, C501, C603) | C15849 | **0** | Any 1 µF ≥ 16 V 0603 substitutes; picking **CL10B105KB8NNNC (X7R)** also settles the X5R/X7R inconsistency below |
| MF-RX110 (F201) | **C208495** | 0 | The open item "confirm the 60 V PPTC's LCSC number" is resolved — the number exists but has no stock, so the DigiKey fallback stands; 60R110 is not on LCSC at all |
| Degson DG128-5.0 **4P / 5P** (J901, J701) | — | not listed | 2P (C711349, 18,735) and 3P (C691861, 2,700) are fine; the 4P/5P open item is real — Phoenix MKDS 1.5/4 + 1.5/5 from DigiKey, or split the buy |
| MMBT2222A (Q801, Q802) | **C82460** | 1,855,400 | "Pick a tier-one maker's listing" is resolved: onsemi MMBT2222ALT1G |
| LMR38020SDDAR | C3192337 | 3,820 | healthy |
| HF3FF/005-1ZTF | C2764967 | 2,897 | healthy |
| AP7361C-33E-13 | C500795 | 4,348 | healthy |
| SRR1260-150M | C2041333 | 1,147 | enough for this build; re-check at freeze |
| ESP32-S3-WROOM-1-N8 | C2913198 | 1,707 | healthy |
| SMBJ43A / BZT52C4V7-7-F / KBP206 | C315993 / C260907 / C2494 | 8k / 4k / 43k | healthy |

Brand notes from the same read: C2980403 (SMF5.0A) is branded GOODWORK at LCSC, not Littelfuse/MDD;
C2289 is branded KENTO KT-0603YG (the XINGLIGHT sheet on file is the same 0603 yellow-green class).
Both are Board 1-proven commodity parts — the BOM's maker columns are just looser than the listings.

### 3 — Prose corrections (no schematic impact)

1. **EL817 collector rating**: design doc §8 says "collector rated 80 V"; Everlight's sheet says
   **VCEO 35 V** for the whole EL817 series (the -FV suffix is VDE, not 80 V). The node sits at
   3.3 V — harmless, but the sentence should say 35 V.
2. **IO1/IO2 "pulled up at reset"** (design doc §7, PROJECT_STATUS): SoC datasheet **v2.2
   Table 2-1** lists GPIO1/GPIO2 (and GPIO3) as input-enabled only at reset — **no pull-up**. The
   pulled-up-at-reset set is IO0, the SPI flash pins, and U0TXD/U0RXD (IO45/46 are pulled *down*).
   The decision stands unchanged — IO1/IO2 stay unconnected, and the five outputs on IO9–IO13 are
   confirmed no-pull-at-reset with only 60 µs *low*-level power-up glitches (Table 2-2), which is
   exactly what an active-HIGH output wants. Correct the citation when convenient.
3. **§14 firmware table** still says "the 4.7 µF makes AC a steady LOW" — a leftover from the draft
   the second review replaced with 47 kΩ + 1 µF. Same τ, wrong parts named.
4. **BOM hygiene**: the cart line "R201 R202 R304" carries two values (100 k and 91 k) in one row,
   and the C701–C704 line says X5R where design doc §12 says X7R. Both dissolve when the BOM is
   regenerated from the schematic — noted so they are not copied forward.

### 4 — Verified (a sample of what was checked and found right)

- **Pin map**: all 21 used module pins in `PinMap_CheatSheet.md` match the WROOM-1 v1.8 pin table,
  one for one, including the easy-to-miss ones (12 = IO8, 22 = IO14, 36/37 = RXD0/TXD0).
- **`board2_calcs.py` runs clean** and its outputs match the design document's numbers (UVLO
  6.9/6.1 V, VIN_SENSE 1:21 mapping 69 V → 3.29 V, relay drive 4× overdrive, 47 ms opto τ, trace
  widths, acceptance-load currents).
- **SMBJ43A row** in the fetched Littelfuse sheet: standoff 43 V, breakdown 47.8–52.8 V, clamp
  69.4 V @ 8.7 A — the TVS-vs-85 V-buck argument holds as written.
- **MF-RX110 row** in the fetched Bourns sheet: 60 V, 40 A max interrupt, 1.10 A hold / 2.20 A trip.
- **BZT52C4V7 row**: 4.4–5.0 V at 5 mA, 500 mW.
- **Degson drawing** covers every pole count 02P–XXP with the PCB layout — the terminal footprints
  can be drawn even though LCSC only stocks 2P/3P.
- Library plumbing: `fp-lib-table` / `sym-lib-table` syntax correct, `${KIPRJMOD}`-relative; the
  five carried-over footprints and the renumbered TS-1187A symbol are present; `.gitignore` and the
  CI workflow are sound (CI skips gracefully until the project exists).

## What changed in the repository

Eleven documents added on 2026-09-14 (vendor originals; LCSC's datasheet CDN where the vendor site
blocks robots): EL817 series, Littelfuse SMBJ series, Diodes BZT52C series, MDD KBP206 and Diodes
KBP2005G–KBP210G, Bourns MF-RX110, Nichicon UPW, TDK SIOV StandarD (S07K35), Degson DG128-5.0
drawing, ESP32-S3 SoC datasheet v2.2 — all in `references/datasheets/` — plus the LMR38020QEVM
user guide (SNVU817) in `references/reference-designs/`. The datasheet index README was updated to
match (fetched files linked, stock flags, resolved LCSC numbers, the KBJ deletion note).

Still open, none blocking capture: delete the KBJ file; decide -F vs **-FV** for the optos at freeze
(or sooner, in the BOM draft); pick the 1 µF 0603 replacement; settle Degson-vs-Phoenix for 4P/5P;
choose the DIN enclosure before layout; name the LED maker and the anti-surge resistor family at
freeze (their sheets are the two the robots could not fetch: littelfuse.com 60R, Yageo/Panasonic
resistor pages).
