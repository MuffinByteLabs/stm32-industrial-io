# Changelog — ESP32-S3 Protected Field I/O Controller

All notable changes to this hardware project are recorded here. Format follows [Keep a Changelog](https://keepachangelog.com/); hardware revisions are letters (Rev A, Rev B), document and firmware changes are dated.

## [Unreleased] — Rev A, pre-capture

### 2026-09-14 — pre-capture deep check; datasheet set completed; final part picks

- **Deep check** (`docs/reviews/PreCapture_Deep_Check_2026-09-14.md`): every datasheet's contents verified against its part — one wrong file caught and replaced (the "KBP" bridge sheet was the 4 A KBJ document); pin map verified pin-by-pin against the WROOM-1 datasheet; reset-pull claims re-checked against the SoC datasheet v2.2; `board2_calcs.py` re-run clean; BOM cross-checked against live LCSC listings. **No design values changed.**
- Eleven documents fetched into `references/` (EL817 series, Littelfuse SMBJ, Diodes BZT52C, MDD + Diodes KBP families, Bourns MF-RX110, Nichicon UPW, TDK SIOV S07K35, Degson DG128-5.0 drawing, ESP32-S3 SoC datasheet v2.2, LMR38020QEVM guide) plus the Phoenix MKDS 1,5 catalog sheet; index updated.
- **Final part picks:** optos → EL817S1(C)(TU)-FV C470884 (VDE option; -F at 0 stock) · Q801/Q802 → onsemi MMBT2222ALT1G C82460 · terminals → Phoenix MKDS 1,5 family 5.0 mm, DigiKey (Degson DG128-5.0 same-footprint alternate) · F201 → Bourns MF-RX110 (DigiKey) · indicator LEDs → Lite-On LTST-C170KRKT / LTST-C170KGKT · R701–R708 → Panasonic ERJ-P08F1601V · 1 µF 0603 → Samsung CL10B105KA8NNNC C29936 (X7R; old X5R number stockless) · C201/C901 → Nichicon UPW series. One small DigiKey line joins the LCSC checkout.
- Corrections: EL817 collector rating is 35 V (was written 80 V — the V in -FV is VDE, not a voltage); IO1/IO2 are no-pull at reset per SoC DS v2.2 (pin choices unchanged); firmware-contract table's stale "4.7 µF" → 47 kΩ + 1 µF; J201 wire range restated for the MKDS 1,5 (0.14–1.5 mm², 26–16 AWG).

### 2026-09-07 — specification verified, repository created

- Repository skeleton mirroring Board 1 (`hardware/`, `docs/`, `fabrication/`, `firmware/`, `references/`, plus `mechanical/`).
- `docs/ESP32S3_FieldIO_Final_Design_Document.md` written before capture; every number re-derived in `docs/calcs/board2_calcs.py`.
- **Specification review** (`docs/reviews/Spec_Review_RevA_2026-09-07.md`): 4 blocking findings against plan v7.3 §4 — opto input RC (τ 10 ms → 47 ms), UVLO/9 V contradiction (→ 7.0/6.1 V, 10 V guaranteed floor), PPTC 0.5 A → 1.1 A/60 V, buck LMR36015 (leadless) → **LMR38020SDDAR** (80 V, 2 A, synchronous, HSOIC-8). Rail split into 5V_BUCK / 5V_SYS; 10 kΩ output pull-downs; VIN_SENSE added; series field-side input LEDs.
- **Second-opinion review** (`docs/reviews/Second_Opinion_Review_RevA_2026-09-07.md`): adopted AP7361C-33E-13 SOT-223 regulator, 47 kΩ + 1 µF input filter, VIN_SENSE 1:21, JP901 open by default, J901 = VLOAD+ · GND · OUT1− · OUT2−, silk "DISCONNECT FIELD POWER BEFORE USB", published input 12–36 V DC, 1.25 A acceptance load, bring-up current-limit split, supervisory wording for the condensate use case. Declined with arithmetic: LM5012, 100 V bulk cap, LTV-814, 100 kΩ pull-downs, 30 VAC, SS14 coil flyback.
- **Industry-standard audit** (`docs/reviews/Industry_Standard_Audit_RevA_2026-09-07.md`): relays → Hongfa HF3FF/005-1ZTF; transistors → MMBT2222A; inputs → BZT52C4V7 + 2 × 1.6 kΩ anti-surge (IEC 61131-2 Type 1); terminals → Degson DG128 / Phoenix MKDS; fiducials; DIN-rail enclosure decision before layout; MSL / IPC-A-610 / ESD in the assembly plan; long-life electrolytics named; `CHANGELOG.md`, `mechanical/`, KiCad ERC/DRC CI added.
- Board 1's verified footprints, symbols and 3D models carried over as `hardware/libs/FieldIO_JLC`.

### Next entries

- Capture complete (sheets 01–10, ERC clean, BOM regenerated) — date
- Layout complete (DRC 0 / unconnected 0 / parity 0, moat rule passing) — date
- Rev A frozen and ordered (`fabrication/revA/`) — date
- First article assembled and brought up — date

## Revision history (hardware)

| Rev | Date | Status | Notes |
|---|---|---|---|
| A | — | in design | first revision |
