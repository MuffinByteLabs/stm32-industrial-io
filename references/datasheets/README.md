# Datasheet index

Every part on the board, mapped to the document it is designed against. Designators are the design
document's per-sheet numbers. Files marked **carried over** are copied from Board 1's
`references/datasheets/` (same part, same document); the fetch pass of **2026-09-14** filled in the
missing sheets from the vendors' own documents (LCSC's datasheet CDN where the vendor site blocks
robots) and replaced one wrong file — see the pre-capture deep check in `../../docs/reviews/`.

## New on this board

| Ref | Part | LCSC | Datasheet |
|---|---|---|---|
| U301 | LMR38020SDDAR synchronous buck, 80 V / 2 A | C3192337 | [BUCK_TI_LMR38020](BUCK_TI_LMR38020_80V_2A_Synchronous_Datasheet.pdf) (SNVSC40E) |
| U301 alt | LMR16020PDDAR, 60 V / 2 A non-synchronous | C190006 | [BUCK_TI_LMR16020](BUCK_TI_LMR16020_60V_2A_NonSync_Datasheet_ALTERNATE.pdf) |
| U501 | AP7361C-33E-13 LDO, 1 A, SOT-223 | C500795 | [LDO_Diodes_AP7361C](LDO_Diodes_AP7361C_1A_SOT223_Datasheet.pdf) (DS37274) |
| L301 | SRR1260-150M shielded 15 µH | C2041333 | [INDUCTOR_Bourns_SRR1260](INDUCTOR_Bourns_SRR1260_Shielded_Datasheet.pdf) |
| BR201 | KBP206 bridge, 2 A / 600 V | C2494 | [BRIDGE_MDD_KBP206](BRIDGE_MDD_KBP206_KBP2005-KBP210_2A_C2494_Datasheet.pdf) (the LCSC part's own sheet — the footprint master) · [BRIDGE_Diodes_KBP2005G-KBP210G](BRIDGE_Diodes_KBP2005G-KBP210G_2A_KBP_Datasheet.pdf) (tier-one family sheet). *The old `BRIDGE_Diodes_KBP2xx_2A_Datasheet.pdf` was actually the KBJ4005G–KBJ410G (4 A KBJ package) document — wrong part, wrong outline; delete it.* |
| K801, K802 | **HF3FF/005-1ZTF relay (Hongfa)** — UL E134517 / VDE | C2764967 | [RELAY_Hongfa_HF3FF](RELAY_Hongfa_HF3FF_10A_SPDT_Datasheet.pdf) — the footprint master (coil pins 12.2 mm, contacts on 3.4 mm) |
| K801 alt | SRD-05VDC-SL-C (Songle) — fits the footprint, not the part | C35449 | [RELAY_Songle_SRD-05VDC-SL-C](RELAY_Songle_SRD-05VDC-SL-C_Datasheet.pdf) |
| Q801, Q802 | **MMBT2222A** (buy: onsemi MMBT2222ALT1G) | **C82460** (onsemi, confirmed 2026-09-14) | [NPN_Nexperia_MMBT2222A](NPN_Nexperia_MMBT2222A_SOT23_Datasheet.pdf) (Nexperia sheet; onsemi / Diodes equivalent) |
| Q901, Q902 | AO3400A N-MOSFET | C20917 | [MOSFET_AlphaOmega_AO3400A](MOSFET_AlphaOmega_AO3400A_NchannelMOSFET_Datasheet.pdf) |
| D701–D704, D801, D802 | 1N4148W | C81598 | [DIODE_Diodes_1N4148W](DIODE_Diodes_1N4148W_SOD123_Datasheet.pdf) |
| U701–U704 | EL817S1(C)(TU)-F optocoupler, rank C | C106900 — **0 stock 2026-09-14**; drop-in **EL817S1(C)(TU)-FV C470884** (VDE option, 4,410 in stock) | [OPTO_Everlight_EL817_Series](OPTO_Everlight_EL817_Series_SMD_RankC_Datasheet.pdf) (covers -F and -FV; note VCEO is **35 V**, not 80 — the V suffix is the VDE option, not a voltage) |
| D201 | SMBJ43A TVS | C315993 | [TVS_Littelfuse_SMBJ_Series](TVS_Littelfuse_SMBJ_Series_600W_Datasheet.pdf) (SMBJ43A: standoff 43 V, clamp 69.4 V @ 8.7 A) |
| F201 | MF-RX110 (Bourns) / 60R110 (Littelfuse) 1.1 A 60 V PPTC | **C208495** (MF-RX110 — listed, 0 stock 2026-09-14; DigiKey fallback stands) | [FUSE_Bourns_MF-RX110](FUSE_Bourns_MF-RX110_Radial_PPTC_60V_C208495_Datasheet.pdf) · Littelfuse 60R sheet blocked to robots — fetch by hand from littelfuse.com only if the 60R110 is what gets bought |
| D709–D712 | BZT52C4V7-7-F Zener (Diodes) | C260907 | [ZENER_Diodes_BZT52C_Series](ZENER_Diodes_BZT52C_Series_SOD123_Datasheet.pdf) (DS30117; C4V7: 4.4–5.0 V @ 5 mA, 500 mW) |
| C201, C901 | 470 µF 63 V / 100 µF 25 V, 105 °C long-life radial | verify at freeze | [CAP_Nichicon_UPW](CAP_Nichicon_UPW_LowImpedance_Radial_Electrolytic_Datasheet.pdf) (the first-named series; fetch ZLH/FR equivalents only if the buy changes) |
| J201, J701, J801, J802, J901 | Degson DG128-5.0 screw terminals (UL/VDE) | C711349 (2P) · C691861 (3P) · **4P/5P not stocked at LCSC (checked 2026-09-14) — Phoenix MKDS 1.5/x-5.08 from DigiKey is the live fallback** | [CONN_Degson_DG128-5.0](CONN_Degson_DG128-5.0_ScrewTerminal_Drawing.pdf) (customer drawing, all pole counts, PCB layout — the footprint master) |
| RV801, RV802 | TDK/EPCOS S07K35 MOV (B72207S0350K101) — DNP | verify | [MOV_TDK_SIOV_StandarD](MOV_TDK_SIOV_Leaded_StandarD_S07K35_Datasheet.pdf) (SIOV leaded StandarD series) |
| — (optional, Rev B) | TI ISO1211 isolated 24 V digital-input receiver | — | [REF_TI_ISO1211_OPTIONAL](REF_TI_ISO1211_Isolated_24V_Digital_Input_Datasheet_OPTIONAL.pdf) — the modern certified-Type-1/3 alternative, recorded by the audit |

Still deferred to freeze on purpose: the named-maker red/green 0805 indicator LEDs (D705–D708, D803/D804,
D903/D904, D302) and the anti-surge 1.6 kΩ family sheet (Yageo PA / Panasonic ERJ-P08 — both vendors
block robot fetches; pull the sheet when the maker is picked).

## Carried over from Board 1 (same part, same document)

| Ref | Part | LCSC | File |
|---|---|---|---|
| U601 | ESP32-S3-WROOM-1-N8 | C2913198 | `ESP32S3_Espressif_WROOM-1_WROOM-1U_Module_Datasheet_v1.8.pdf` |
| — | ESP32-S3 Hardware Design Guidelines | — | `ESP32S3_Espressif_Hardware_Design_Guidelines_2026-06-23.pdf` |
| — | **ESP32-S3 SoC datasheet v2.2** (Table 2-1 reset states, Table 2-2 power-up glitches — the output-pin choice) | — | `ESP32S3_Espressif_SoC_Datasheet_v2.2.pdf` (fetched 2026-09-14; v2.2 Table 2-1: IO9–IO13 no pull at reset ✔ — and note IO1/IO2 are listed IE-only, not pulled up) |
| U501 alt | AP2112K-3.3 (Board 1's regulator, the BOM alternate) | C51118 | `LDO_Diodes_AP2112K-3.3_600mA_3V3_Regulator_Datasheet.pdf` |
| U401 | USBLC6-2SC6 | C7519 | `ESD_ST_USBLC6-2SC6_USB2_DataLine_Protection_Datasheet.pdf` |
| D401 | SMF5.0A | C2980403 | `TVS_MDD_SMF5_0A_5V_Unidirectional_Datasheet.pdf` |
| D301, D402, D901, D902 | SS14 | C2480 | `DIODE_SS14_Schottky_1A40V_Family_Datasheet.pdf` |
| F401 | 1206L075/16WR | C371166 | `FUSE_Littelfuse_1206L_Resettable_PPTC_Datasheet_2024.pdf` |
| J401 | TYPE-C-31-M-12 | C165948 | `USBC_TYPE-C-31-M-12_Receptacle_C165948_Footprint_Drawing.pdf` |
| SW601, SW602 | TS-1187A-B-A-B | C318884 | `SWITCH_XKB_TS-1187A_Tactile_SMD_5.1x5.1_H1.5_C318884_Datasheet.pdf` |
| D501, D602 | KT-0603YG / XL-0603QYGC | C2289 | `LED_XINGLIGHT_XL-0603QYGC_YellowGreen_0603_C2289_Datasheet.pdf` (LCSC brands C2289 as KENTO KT-0603YG; same 0603 yellow-green class, Board 1 proven) |
| C… | Samsung MLCC catalogue | — | `CAP_Samsung_MLCC_Catalogue_2015-11.pdf` |

## Design guidance used

| Document | Used for |
|---|---|
| LMR38020 datasheet §8–9 | RT/frequency, EN/UVLO equations, inductor and capacitor selection, layout guidelines — design doc §4 |
| LMR38020QEVM user guide (SNVU817) | Buck reference layout — fetched 2026-09-14 into [`../reference-designs/`](../reference-designs/) |
| ESP32-S3 Hardware Design Guidelines | Power entrance, decoupling, strapping pins, antenna keep-out, ADC handling |
| ESP32-S3 SoC datasheet v2.2, Table 2-1 / 2-2 | Pins pulled up at reset; power-up glitches — output pin choice (local copy, above) |
| IPC-2221 (see `../standards/`) | Trace widths for the 2 A contact paths; clearance sanity for the moat |

---

All datasheets remain the property of their respective manufacturers and are included here for
convenience. Copyrighted standards are **not** redistributed — see [`../standards/`](../standards/).
