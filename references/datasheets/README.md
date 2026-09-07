# Datasheet index

Every part on the board, mapped to the document it is designed against. Designators are the design
document's per-sheet numbers. Files marked **carried over** are copied from Board 1's
`references/datasheets/` (same part, same document); files marked **to fetch** are not in the folder
yet — fetch them before capture and rename to the same pattern.

## New on this board

| Ref | Part | LCSC | Datasheet |
|---|---|---|---|
| U301 | LMR38020SDDAR synchronous buck, 80 V / 2 A | C3192337 | [BUCK_TI_LMR38020](BUCK_TI_LMR38020_80V_2A_Synchronous_Datasheet.pdf) (SNVSC40E) |
| U301 alt | LMR16020PDDAR, 60 V / 2 A non-synchronous | C190006 | [BUCK_TI_LMR16020](BUCK_TI_LMR16020_60V_2A_NonSync_Datasheet_ALTERNATE.pdf) |
| U501 | AP7361C-33E-13 LDO, 1 A, SOT-223 | C500795 | [LDO_Diodes_AP7361C](LDO_Diodes_AP7361C_1A_SOT223_Datasheet.pdf) (DS37274) |
| L301 | SRR1260-150M shielded 15 µH | C2041333 | [INDUCTOR_Bourns_SRR1260](INDUCTOR_Bourns_SRR1260_Shielded_Datasheet.pdf) |
| BR201 | KBP206 bridge, 2 A / 600 V | C2494 | [BRIDGE_Diodes_KBP2xx](BRIDGE_Diodes_KBP2xx_2A_Datasheet.pdf) (Diodes Inc. family sheet; MDD's is equivalent) |
| K801, K802 | SRD-05VDC-SL-C relay | C35449 | [RELAY_Songle_SRD-05VDC-SL-C](RELAY_Songle_SRD-05VDC-SL-C_Datasheet.pdf) |
| Q901, Q902 | AO3400A N-MOSFET | C20917 | [MOSFET_AlphaOmega_AO3400A](MOSFET_AlphaOmega_AO3400A_NchannelMOSFET_Datasheet.pdf) |
| D701–D704, D801, D802 | 1N4148W | C81598 | [DIODE_Diodes_1N4148W](DIODE_Diodes_1N4148W_SOD123_Datasheet.pdf) |
| U701–U704 | EL817S1(C)(TU)-F optocoupler, rank C | C106900 | **to fetch** — [LCSC product page](https://www.lcsc.com/product-detail/Optocouplers_Everlight-Elec-EL817S1-C-TU-F_C106900.html) (datasheet link on the page) |
| D201 | SMBJ43A TVS | C315993 | **to fetch** — [Littelfuse SMBJ series](https://www.littelfuse.com/products/overvoltage-protection/tvs-diodes/surface-mount/smbj/smbj43a) |
| F201 | 60R110 (Littelfuse) / MF-RX110 (Bourns) 1.1 A 60 V PPTC | verify | **to fetch** — [Littelfuse 60R110](https://www.littelfuse.com/products/fuses-overcurrent-protection/polyswitch-resettable-pptc-devices/radial-leaded-polyswitch-resettable-pptc-devices/60r/60r110) · [Bourns MF-RX110](https://www.newark.com/bourns/rx110/fuse-ptc-reset-60v-1-1a-radial/dp/05B2444) |
| Q801, Q802 | S8050 NPN | verify (JLC Basic C2146) | **to fetch** — any S8050 SOT-23 sheet (hFE ≥ 85 at 50 mA is the number used) |
| C201 | 470 µF 63 V 105 °C low-ESR radial | verify | **to fetch** — the chosen family's sheet (ripple rating at 120 Hz is the number used) |
| J201, J701, J801, J802, J901 | 5.08 mm screw terminals | verify | **to fetch** — the chosen family's drawing (pin spacing, footprint) |
| RV801, RV802 | 07D560K MOV | verify | **to fetch** |

## Carried over from Board 1 (same part, same document) — copy into this folder

| Ref | Part | LCSC | Board 1 file name |
|---|---|---|---|
| U601 | ESP32-S3-WROOM-1-N8 | C2913198 | `ESP32S3_Espressif_WROOM-1_WROOM-1U_Module_Datasheet_v1.8.pdf` |
| — | ESP32-S3 Hardware Design Guidelines | — | `ESP32S3_Espressif_Hardware_Design_Guidelines_2026-06-23.pdf` |
| U501 alt | AP2112K-3.3 (Board 1's regulator, the BOM alternate) | C51118 | `LDO_Diodes_AP2112K-3.3_600mA_3V3_Regulator_Datasheet.pdf` |
| U401 | USBLC6-2SC6 | C7519 | `ESD_ST_USBLC6-2SC6_USB2_DataLine_Protection_Datasheet.pdf` |
| D401 | SMF5.0A | C2980403 | `TVS_MDD_SMF5_0A_5V_Unidirectional_Datasheet.pdf` |
| D301, D402, D901, D902 | SS14 | C2480 | `DIODE_SS14_Schottky_1A40V_Family_Datasheet.pdf` |
| F401 | 1206L075/16WR | C371166 | `FUSE_Littelfuse_1206L_Resettable_PPTC_Datasheet_2024.pdf` |
| J401 | TYPE-C-31-M-12 | C165948 | `USBC_TYPE-C-31-M-12_Receptacle_C165948_Footprint_Drawing.pdf` |
| SW601, SW602 | TS-1187A-B-A-B | C318884 | `SWITCH_XKB_TS-1187A_Tactile_SMD_5.1x5.1_H1.5_C318884_Datasheet.pdf` |
| D501, D602 | KT-0603YG / XL-0603QYGC | C2289 | `LED_XINGLIGHT_XL-0603QYGC_YellowGreen_0603_C2289_Datasheet.pdf` |
| C… | Samsung MLCC catalogue | — | `CAP_Samsung_MLCC_Catalogue_2015-11.pdf` |

The ESP32-S3 SoC datasheet (pin reset states, Table 2-1/2-2, used for the output-pin choice) is at
[documentation.espressif.com/esp32-s3_datasheet_en.pdf](https://documentation.espressif.com/esp32-s3_datasheet_en.pdf).

## Design guidance used

| Document | Used for |
|---|---|
| LMR38020 datasheet §8–9 | RT/frequency, EN/UVLO equations, inductor and capacitor selection, layout guidelines — design doc §4 |
| ESP32-S3 Hardware Design Guidelines | Power entrance, decoupling, strapping pins, antenna keep-out, ADC handling |
| ESP32-S3 datasheet Table 2-1 / 2-2 | Pins pulled up at reset; power-up glitches — output pin choice |
| IPC-2221 (see `../standards/`) | Trace widths for the 2 A contact paths; clearance sanity for the moat |

---

All datasheets remain the property of their respective manufacturers and are included here for
convenience. Copyrighted standards are **not** redistributed — see [`../standards/`](../standards/).
