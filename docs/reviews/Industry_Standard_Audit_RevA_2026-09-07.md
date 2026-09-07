# Industry-Standard Audit — ESP32-S3 Protected Field I/O Controller, Rev A

*The last check before schematic capture, 2026-09-07. Three questions, asked of every part, every circuit and the repository itself: is it a current, reliable, multi-sourced part from a recognised maker; is the design what an industrial-controls engineer would recognise as standard practice; and is anything missing that such an engineer would expect. Sources: manufacturer datasheets in `../../references/datasheets/`, LCSC/DigiKey listings on the day, and the standards named in §3. Arithmetic in [`../calcs/board2_calcs.py`](../calcs/board2_calcs.py) §7 (revised here).*

**Outcome: every semiconductor and magnetic part is current, active and industry-recognised. Four parts were commodity-grade and are upgraded to industry-grade equivalents in the same footprints (relay, transistor, terminals, and the input network — which now meets IEC 61131-2 Type 1). Six process items were missing and are added (MSL handling, IPC-A-610 acceptance, fiducials, an enclosure decision, a changelog, CI). Nine further items are recorded as optional or Rev B, with the reason each is not in Rev A.**

---

## 1. Component audit

Legend — **Grade:** *industrial* = recognised maker, full datasheet, UL/VDE where relevant, −40 °C rating; *commodity* = generic part, thin datasheet, hobby-module heritage. **Status** from the manufacturer's product page on the day.

### Active parts

| Ref | Part (maker) | Introduced / status | Grade | Temp | Sources | Verdict |
|---|---|---|---|---|---|---|
| U301 | **LMR38020SDDAR** (TI) | 2021, active, automotive sibling -Q1 | industrial | −40…125 °C junction | TI only (single-source is normal for a converter; LMR16020 is the pin-different alternate in the BOM) | ✓ modern, correct fit: 80 V, 2 A, synchronous, internally compensated, leaded package |
| U501 | **AP7361C-33E-13** (Diodes Inc.) | 2016, active (DS37274 rev 5, 2020) | industrial | −40…85 °C | Diodes; TI TLV1117LV33 is a footprint-compatible SOT-223 alternate | ✓ (adopted from the second review) |
| U601 | **ESP32-S3-WROOM-1-N8** (Espressif) | 2021, active, Espressif longevity commitment | industrial (FCC/CE/IC-certified module) | −40…85 °C | Espressif | ✓ the de-facto Wi-Fi IoT module of this decade; MSL 3 — see §2 |
| U401 | **USBLC6-2SC6** (ST) | active | industrial | −40…125 °C | ST; Nexperia PRTR5V0U2X, TI TPD2E001 as alternates | ✓ the standard USB 2.0 ESD array |
| U701–U704 | **EL817S1(C)(TU)-F** (Everlight) | mature, active | industrial (UL/VDE recognised, 5 kV RMS) | −30…100 °C | Everlight; Lite-On LTV-817S, Vishay/Sharp PC817X — same footprint | ✓ the PC817 is a 40-year industry standard precisely because it is boring; rank C specified |
| BR201 | **KBP206** (MDD / Diodes KBP206G / Vishay) | mature, active | industrial | −55…150 °C | ≥ 4 makers | ✓ multi-sourced bridge in the ubiquitous KBP outline |
| Q901, Q902 | **AO3400A** (Alpha & Omega) | active | industrial | −55…150 °C | AOS; Vishay Si2302, Diodes DMN2075U, onsemi NTR4501 as SOT-23 alternates | ✓ |
| Q801, Q802 | S8050 (generic Chinese) | commodity, thin datasheets, vague hFE bins | **commodity** | | | **✗ → MMBT2222A** (onsemi MMBT2222ALT1G / Nexperia MMBT2222A,215 / Diodes MMBT2222A-7-F): the 2N2222 in SOT-23, 600 mA, hFE ≥ 100 at 150 mA, three tier-one sources. Same footprint, same 680 Ω / 10 kΩ network (forced β 21 against hFE ≥ 90 at 79 mA). BC817-40 is the equally standard alternate. |
| D201 | **SMBJ43A** (Littelfuse) | active | industrial | −55…150 °C | Littelfuse, Vishay, Bourns, SMC | ✓ |
| D401 | **SMF5.0A** (Littelfuse / MDD) | active | industrial | | multi | ✓ (Board 1) |
| D301, D402, D901, D902 | **SS14** (MDD / Vishay / onsemi / Diodes) | mature, active | industrial | | ≥ 4 makers | ✓ |
| D701–D704, D801, D802 | **1N4148W** (ST Semtech at LCSC; Diodes 1N4148W-7-F, Nexperia 1N4148W) | active | industrial | | ≥ 4 makers | ✓ |
| D709–D712 (new) | **BZT52C4V7** (Diodes BZT52C4V7-7-F, LCSC C260907) | active | industrial | | Diodes (originator), Nexperia, Vishay, onsemi | ✓ added — see §2.1 |
| LEDs | red 0805 ×8, yellow-green 0603 ×2, green 0805 ×1 | — | commodity by default | | | ✓ acceptable; for an industry-grade BOM specify a named maker (Everlight, Kingbright, Würth, Lite-On) at freeze |
| K801, K802 | SRD-05VDC-SL-C (Songle) | commodity (hobby-module heritage), **−25…70 °C**, no VDE, contact life stated loosely | **commodity** | −25…70 °C | | **✗ → Hongfa HF3FF/005-1ZTF** (LCSC C2764967, 2,360 in stock, ≈ $0.80): same 19 × 15.2 mm "T73" outline and coil (5 V, 70 Ω ± 10 %, 3.8 V pick-up), **AgSnO₂ contacts** (the right material for inductive loads), **UL E134517 / VDE R50148356 / CQC**, **−40…85 °C**, 1 × 10⁷ mechanical operations, 1500 VAC coil-to-contact. Hongfa is a top-three relay maker worldwide; Songle is the clone. The driver arithmetic is unchanged. |
| L301 | **SRR1260-150M** (Bourns) | active | industrial | −40…125 °C | Bourns; Würth 744771115 (WE-PD), Coilcraft MSS1260-153 as alternates | ✓ |
| F201 | **60R110** (Littelfuse) / **MF-RX110** (Bourns) | active | industrial (UL recognised) | −40…85 °C | two makers | ✓ |
| F401 | **1206L075/16WR** (Littelfuse) | active | industrial | | Littelfuse, Bourns MF-MSMF075 | ✓ (Board 1) |
| J401 | TYPE-C-31-M-12 (HRO) | commodity | commodity, **proven on Board 1** | | GCT USB4085, Amphenol 12401610E4#2A, Würth 632723300011 are the industry names | ✓ keep — verified footprint, five assembled boards; note the alternates in the BOM |
| J201, J701, J801, J802, J901 | "KF128 / generic" screw terminals | commodity | **commodity** | | | **✗ → Degson DG128 family** (UL/VDE-recognised, 5.0 mm pitch at LCSC: 2P C711349, 3P C691861 — 4P/5P in the same family) **or Phoenix Contact MKDS 1.5/x-5.08** (the original, DigiKey). One family for all five; the pitch (5.0 vs 5.08) only matters to the footprint. Pluggable Degson 2EDG / Phoenix MSTB is the installation-grade variant (§4). |
| SW601, SW602 | TS-1187A-B-A-B (XKB) | commodity, proven on Board 1 | commodity | | C&K PTS645, Omron B3FS, Panasonic EVQ are the industry names | ✓ keep — verified 1/1/2/2 footprint; bench-only buttons |
| C201 | 470 µF 63 V 105 °C radial | — | depends on maker | | | ✓ **specify a long-life industrial series**: Nichicon UPW1J471MPD, Rubycon 63ZLH470MEFC12.5X20, Panasonic EEU-FR1J471 (all 105 °C, ≥ 5,000 h). At 45 °C ambient a 10,000 h part projects to > 50 years; a no-name 2,000 h part to ≈ 14. |
| C901 | 100 µF 25 V | — | | | | ✓ same rule (Nichicon UPW / Rubycon ZLH / Panasonic FR) |
| C301, C302, C303 | 4.7 µF 100 V 1210 X7R; 100 nF 100 V 0603 X7R | — | industrial | | Murata GRM32ER72A475KA12, TDK C3225X7R2A475K, Samsung CL32B475KCJ | ✓ X7R only, no Y5V anywhere on the board |
| C305–C307, C601 etc. | X7R/X5R 25 V ceramics | — | industrial | | Samsung/Murata/TDK/Yageo | ✓ (Board 1 numbers) |
| R701–R708 | 1206 thick film | — | industrial | | Yageo, Panasonic, Vishay, KOA | ✓ — and for the eight field-facing resistors specify the **anti-surge (pulse-withstanding) thick-film class**: Yageo PA/AC series or Panasonic ERJ-P08. Same footprint, same price class, survives the IEC 61000-4-5 surge that a plain thick film cracks under. |
| other R | 0603/0805 1 % thick film | — | industrial | | Yageo RC0603FR (Board 1's C98220 class) | ✓ |
| RV801, RV802 (DNP) | 07D560K | — | commodity name | | TDK/EPCOS **S07K35** (B72207S0350K101) or Littelfuse V-series are the industry parts | ✓ specify TDK S07K35 in the BOM notes |
| JP901, TPs, FIDs, H1–H4 | KiCad stock | — | — | | | ✓ |

### Lifecycle summary

No part on the board is NRND, EOL or last-time-buy. The oldest designs (KBP bridge, PC817-class opto, SS14, 1N4148, 2N2222) are alive because they are the industry's commodity standards with four or more makers each; the newest (LMR38020, 2021; ESP32-S3, 2021; AP7361C, 2016) are the current generation of their families. Single-source parts: the buck (normal; alternate in BOM), the module (normal), the relay (Hongfa — Omron G5LE / Panasonic JS are pin-different alternates).

## 2. Design audit against the standards an industrial-controls engineer would apply

### 2.1 Digital inputs — IEC 61131-2 (the PLC input standard) → **changed**

IEC 61131-2 defines what a "24 V digital input" is. Type 1 (the common class): **ON = 15–30 V at 2–15 mA; OFF = −3 to +5 V**; a 5 V signal must read OFF. The channel as it stood after the second review (two LED drops and a 47 kΩ pull-up) had a threshold of ≈ 3.5–4 V that depended on the optocoupler's CTR — a 5 V stray would read ON, and the threshold was not a number anyone could put on a datasheet.

**Fix, adopted:** one **BZT52C4V7 Zener (D709–D712) in series** with the two LEDs, and the series resistance lowered from 2 × 2.4 kΩ to **2 × 1.6 kΩ (1206, anti-surge class)**. The Zener's knee sets the threshold; the resistors set the current:

| Input | Current | Type 1 requirement | Result |
|---|---|---|---|
| ≤ 5 V | 0 mA (below the Zener + LED knee, ≈ 7.75 V) | OFF, ≤ 15 mA | ✓ OFF |
| 12 V | 1.33 mA (opto has 6.6× the sink margin it needs) | — (Type 1 transition band 5–15 V) | reads ON (threshold ≈ 8–8.4 V) |
| 15 V | **2.27 mA** | ON, ≥ 2 mA | ✓ ON |
| 24 V | 5.1 mA | 2–15 mA | ✓ |
| 30 V | 6.95 mA | ≤ 15 mA | ✓ |
| 36 V | 8.8 mA; 125 mW per 1206 (50 %), 41 mW in the Zener (8 %) | — | survives |

The AC behaviour is unchanged in kind: on 24 VAC the channel conducts from 14° to 166° of each positive half-cycle (7.0 ms on, 9.7 ms off), and the 47 kΩ + 1 µF node rises to 0.61 V during the gap — still a steady LOW. The README can now say, truthfully, **"inputs meet IEC 61131-2 Type 1 thresholds."** Cost: four SOD-123 diodes.

### 2.2 Clearance and isolation — IPC-2221B, IEC 60664-1

IPC-2221B table 6-1, external uncoated conductors, 31–50 V: 0.6 mm. The moat is ≥ 2.5 mm, enforced by DRC. The optocoupler's 5 kV RMS and the relay's 1500 VAC coil-to-contact are far beyond the 40 V peak in play. This is **functional insulation** on a ≤ 40 V board; the design document says so and claims nothing about reinforced insulation or mains — correct posture. ✓

### 2.3 Conductor sizing — IPC-2221B

Relay contact paths ≥ 1.5 mm (3.2 A at a 10 °C rise for the 2 A rating), 5V_BUCK / VLOAD / bus ≥ 0.8 mm (2.0 A). ✓ (`Hard_Rules` 11.)

### 2.4 Footprints — IPC-7351B

KiCad's stock library footprints are IPC-7351-derived; the five carried over from Board 1 were verified against datasheets and assembled at JLC. Every new footprint (LMR38020 DDA, SRR1260, KBP, HF3FF, EL817S1, DG128, PPTC, electrolytic, MOV, SOT-223) gets the same datasheet check before layout (`Hard_Rules` 32, `KiCad_Settings` §1). ✓ process exists.

### 2.5 Fabrication — IPC-6012 Class 2 (JLC's standard) ✓. Assembly acceptance — **IPC-A-610 Class 2** → added to the first-article inspection: fillet criteria, chip-component side overhang ≤ 50 % of termination width, no end overhang, no tombstones, THT fillets ≥ 270° wetting. (`Assembly_and_Stencil_Plan` §6.)

### 2.6 Moisture sensitivity — **J-STD-020 / J-STD-033 → added**

The ESP32-S3-WROOM-1 is **MSL 3**: "after unpacking, the module must be soldered within 168 hours at 25 ± 5 °C / 60 % RH; otherwise it must be baked." The buck (HSOIC) and the optocouplers are typically MSL 3 as well. A bench that buys parts weeks before assembly will exceed the floor life. Rule added to the assembly plan: **keep MSL-3 parts in their sealed bag with desiccant until assembly day; if the bag has been open > 168 h, bake per J-STD-033 (125 °C for 24 h for a module of this thickness — or the manufacturer's instruction) before reflow.** A "popcorned" module is a cracked module, and the crack is under the hidden ground pad where it cannot be seen.

### 2.7 Soldering — J-STD-001 (leaded process allowed; Sn63/Pb37 or Sn62/Pb36/Ag2), profile per the paste maker; the module's datasheet gives a lead-free (SAC305, 235–250 °C peak) profile only — the leaded profile (210–220 °C peak) is *below* it and safe for every part on the board. ✓ Documented.

### 2.8 ESD — ANSI/ESD S20.20 bench practice → **added to the bench kit**: an ESD mat and wrist strap (≈ $15). The plan's silicone mat is not an ESD mat. The module, the buck and the optos are all ESD-sensitive.

### 2.9 EMC immunity — IEC 61000-4-2 / -4 / -5 → **documented as not tested**

The inputs have 3.2 kΩ of series resistance (which alone limits an 8 kV contact discharge to ≈ 2.5 A for nanoseconds) and diodes on both polarities; the power entry has the TVS. No surge (61000-4-5) test is claimed. If a client ever requires it: bidirectional TVS (SMBJ33CA) across each IN–COM, and a common-mode choke at the power entry — both are Rev B footprints, listed in §4.

### 2.10 Product safety — UL 508 / IEC 61010 → **not pursued, but UL-recognised components used**

Relay (UL E134517), PPTC (UL), terminals (Degson UL/VDE), TVS, optocouplers (UL/VDE) — every part that touches field wiring carries a recognition mark. The board itself is not listed and the README does not say it is. ✓ honest posture.

### 2.11 RoHS — leaded assembly, stated. ✓ Environmental — every active part rated −40 °C; the relay upgrade removes the one −25 °C / 70 °C part; the electrolytic is specified 105 °C long-life. ✓

### 2.12 Mechanical — **DIN rail → added**

An industrial field controller lives on DIN rail in a modular enclosure with terminal windows along the long edges. Nothing in the plan sized the board to one. Added `mechanical/README.md`: pick the enclosure **before layout** (reference class: Camdenboss CNMB/6, 106 × 90 × 58 mm, 6 modules; Phoenix ME/UM, OKW Railtec, Italtronic Modulbox are equivalents), take the board outline and the terminal positions from the enclosure's PCB drawing, and keep the ≤ 100 × 100 mm fab tier. The plan's "field terminals on at most two edges" is exactly what a DIN enclosure's two terminal windows want.

### 2.13 Assembly fiducials → **added**: three 1 mm copper / 2 mm mask fiducials (FID1–FID3, KiCad `Fiducial_1mm_Mask2mm_SilkRing`) in three corners of the top side. Free; they align the stencil on the bench and are mandatory the day JLC assembles a batch.

## 3. Repository and documentation audit

What an engineering organisation expects a hardware repository to contain, checked against this one:

| Expected | Present | Note |
|---|---|---|
| README with status, architecture, safety notes, license | ✓ | |
| `hardware/` (CAD source), `firmware/`, `docs/`, `fabrication/` (frozen outputs), `references/` | ✓ | mirrors Board 1 — a family convention is itself a standard |
| `mechanical/` (enclosure, outline, 3D) | **added** | DIN-rail enclosure decision lives here |
| `CHANGELOG.md` (revision history, Keep-a-Changelog format) | **added** | Rev A entries start today |
| Design reviews with findings tables | ✓ | three on file before capture |
| Requirements / design document with calculations | ✓ | + the calc script (reproducible arithmetic is rarer than it should be) |
| BOM with **manufacturer, MPN, description, quantity, refdes, alternates** | partly | cart draft restated with a Manufacturer column; the final BOM is generated from the schematic at freeze with all six columns |
| Test / bring-up procedure with expected values and record sheet | ✓ | `BringUp_Guide.md` |
| Assembly documentation (process, MSL, acceptance criteria) | ✓ after this audit | |
| License for hardware (CERN-OHL-P v2) | ✓ | |
| Continuous integration (ERC/DRC on every push) | **added** (`.github/workflows/kicad-ci.yml`) | runs `kicad-cli sch erc` and `pcb drc` once the project exists; fails the build on errors — modern practice, costs nothing |
| `.gitignore` for KiCad noise | ✓ | |
| Issue/decision log | ✓ | `PROJECT_STATUS.md` "settled facts" |

Verdict: the structure is what a reviewer of open hardware expects (it is close to the KiCad and OSHWA project conventions), and with `mechanical/`, a changelog and CI it is what a hiring engineer expects.

## 4. Optional and Rev B — recorded, not adopted

| Item | Why it is industry practice | Why not in Rev A |
|---|---|---|
| **TI ISO1211 / ISO1212** isolated 24 V digital-input receivers (SOIC-8 / SSOP-16) | The modern, certified IEC 61131-2 Type 1/3 input in one chip: fixed current limit, defined thresholds, 2.5 kV isolation, no opto ageing | DC-oriented (an AC input would need firmware envelope detection), ≈ $2.50 per channel, and the discrete channel now meets Type 1 for $0.30. The datasheet is in `references/datasheets/` as `REF_…OPTIONAL`. |
| **TPL7407L** (7-ch low-side NMOS driver, 40 V, flyback diodes) or **TPS27S100** (protected high-side switch with current limit and fault flag) | Protected outputs with diagnostics are what industrial I/O sells | The two AO3400A outputs are specified for pumps and buzzers at ≤ 1 A; protection is the PPTC and the buck's current limit. Rev B if outputs grow. |
| Bidirectional TVS per input (SMBJ33CA) and a power-entry common-mode choke | IEC 61000-4-5 surge immunity | No compliance claim in Rev A; add as DNP footprints if the field-side layout has room. |
| **Pluggable terminal blocks** (Degson 2EDGV/2EDGK, Phoenix MSTB 2,5/x-G-5.08 + plugs) | Installation and service: the wiring stays on the plug | +$0.50–1.00 per position; fixed screw terminals are standard on relay boards. Same pitch — a footprint swap if a client asks. |
| **Conformal coating** (acrylic spray, e.g. MG Chemicals 419D) | Furnace closets and attics are humid; coating is routine for HVAC electronics | Post-assembly step, not a design change; mask the terminals and the USB. Do it on the deployed board, not the demo board. |
| **Firmware toolchain: PlatformIO** (or ESP-IDF) instead of the Arduino IDE | Pinned toolchain and library versions in `platformio.ini` = reproducible builds, the industry expectation | Board 1's sketch is Arduino-IDE; keep the Arduino API but build it under PlatformIO from Board 2 on. Documented in `firmware/README.md`. |
| **MQTT over TLS, signed OTA images, unique per-device credentials** | Baseline IoT security practice (and increasingly regulation) | Firmware scope; noted in the firmware contract. |
| Grounded mounting holes / chassis bond | EMC practice in metal enclosures | Plastic DIN enclosure; not applicable. |
| Voltage supervisor / external watchdog IC | Belt-and-braces reset supervision | The ESP32-S3's internal brown-out detector and task watchdog cover it; the input UVLO makes the 5 V rail clean by construction. |

## 5. Changes applied to the design because of this audit

K801/K802 → **HF3FF/005-1ZTF** · Q801/Q802 → **MMBT2222A** (BC817-40 alt) · D709–D712 **BZT52C4V7** added, R701–R708 → **1.6 kΩ 1206 anti-surge** (inputs now IEC 61131-2 Type 1) · terminals → **Degson DG128 / Phoenix MKDS** family, UL/VDE · **FID1–FID3** · C201/C901 long-life series named · MOV named (TDK S07K35) · assembly plan: **MSL/J-STD-033**, **IPC-A-610 Class 2**, **ESD mat** · `mechanical/README.md` (DIN enclosure before layout) · `CHANGELOG.md` · `.github/workflows/kicad-ci.yml` · cart draft with a Manufacturer column. Parts count: 116 placed (was 112), 14 DNP, 14 TPs, 3 fiducials, 4 holes.
