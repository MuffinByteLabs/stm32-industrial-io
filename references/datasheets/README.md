# Candidate component references

Prepared October 2, 2026. These references support the [canonical plan](../../docs/STM32_Industrial_IO_Controller_RevA_Plan.md) and [procurement process](../../docs/Procurement_Plan.md).

All 21 candidate-family PDFs are available locally and have passed PDF parsing, early-page family identity, byte-length, and SHA-256 checks. These checks do not establish exact-package pin correctness, current document revision, part availability, or board performance. The [manifest](manifest.json) records sources, hashes, check times, and limitations.

## Family index

| Candidate | Local PDF | Source and status |
| --- | --- | --- |
| STM32G474VET6 | [STM32G474VE.pdf](STM32G474VE.pdf) | [DigiKey](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/6455/STM32G474QBT6_DS.pdf); Archival; latest revision required |
| ADS8684A | [ADS8684A.pdf](ADS8684A.pdf) | [Texas Instruments](https://www.ti.com/lit/ds/symlink/ads8684a.pdf); Family identity checked; package review pending |
| TPS26632 | [TPS2663.pdf](TPS2663.pdf) | [Texas Instruments](https://www.ti.com/lit/ds/symlink/tps2663.pdf); Family identity checked; package review pending |
| LMR38020 | [LMR38020.pdf](LMR38020.pdf) | [Texas Instruments](https://www.ti.com/lit/ds/symlink/lmr38020.pdf); Family identity checked; package review pending |
| TPS62160 | [TPS62160.pdf](TPS62160.pdf) | [Texas Instruments](https://www.ti.com/lit/ds/symlink/tps62160.pdf); Family identity checked; package review pending |
| TPS7A20 | [TPS7A20.pdf](TPS7A20.pdf) | [Texas Instruments](https://www.ti.com/lit/ds/symlink/tps7a20.pdf); Family identity checked; package review pending |
| TPS2121 | [TPS2121.pdf](TPS2121.pdf) | [Texas Instruments](https://www.ti.com/lit/ds/symlink/tps2121.pdf); Family identity checked; package review pending |
| TPS55340 | [TPS55340.pdf](TPS55340.pdf) | [Texas Instruments](https://www.ti.com/lit/ds/symlink/tps55340.pdf); Family identity checked; package review pending |
| LM7705 | [LM7705.pdf](LM7705.pdf) | [Texas Instruments](https://www.ti.com/lit/ds/symlink/lm7705.pdf); Family identity checked; package review pending |
| ISO1212 | [ISO1212.pdf](ISO1212.pdf) | [Texas Instruments](https://www.ti.com/lit/ds/symlink/iso1212.pdf); Family identity checked; package review pending |
| TMUX7462F | [TMUX7462F.pdf](TMUX7462F.pdf) | [Texas Instruments](https://www.ti.com/lit/ds/symlink/tmux7462f.pdf); Family identity checked; package review pending |
| DAC80501Z | [DAC80501.pdf](DAC80501.pdf) | [Texas Instruments](https://www.ti.com/lit/ds/symlink/dac80501.pdf); Family identity checked; package review pending |
| OPA197 | [OPA197.pdf](OPA197.pdf) | [Texas Instruments](https://www.ti.com/lit/ds/symlink/opa197.pdf); Family identity checked; package review pending |
| TPS4H160B-Q1 | [TPS4H160-Q1.pdf](TPS4H160-Q1.pdf) | [Texas Instruments](https://www.ti.com/lit/ds/symlink/tps4h160-q1.pdf); Family identity checked; package review pending |
| ISO1410 | [ISO1410.pdf](ISO1410.pdf) | [Texas Instruments](https://www.ti.com/lit/ds/symlink/iso1410.pdf); Family identity checked; package review pending |
| ISO1042 | [ISO1042.pdf](ISO1042.pdf) | [Texas Instruments](https://www.ti.com/lit/ds/symlink/iso1042.pdf); Family identity checked; package review pending |
| UCC12050 | [UCC12050.pdf](UCC12050.pdf) | [Texas Instruments](https://www.ti.com/lit/ds/symlink/ucc12050.pdf); Family identity checked; package review pending |
| TPS3431 | [TPS3431.pdf](TPS3431.pdf) | [Texas Instruments](https://www.ti.com/lit/ds/symlink/tps3431.pdf); Family identity checked; package review pending |
| G5Q-1-DC5 | [G5Q.pdf](G5Q.pdf) | [Omron](https://omronfs.omron.com/en_US/ecb/products/pdf/en-g5q.pdf); Archival; latest revision required |
| 24LC64 | [24LC64.pdf](24LC64.pdf) | [Microchip Technology](https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/24AA64-24FC64-24LC64-64-Kbit-I2C-Serial-EEPROM-DS20001189.pdf); Family identity checked; package review pending |
| SMCJ33CA | [SMCJ.pdf](SMCJ.pdf) | [DigiKey](https://media.digikey.com/pdf/Data%20Sheets/Littelfuse%20PDFs/SMCJ%20Series.pdf); Archival; latest revision required |

## Archival-reference limits

- **STM32G474:** ST-authored DS12288 Rev 6, November 2021, obtained from an authorized DigiKey mirror after the official download timed out. Obtain current datasheet, errata, reference manual, and boot guidance from [ST product documentation](https://www.st.com/en/microcontrollers-microprocessors/stm32g474ve.html) before pin/resource and schematic approval.
- **G5Q:** official Omron J155-E1-16, June 2021. Confirm the current regional ordering code, coil/contact tables, drawings, and applicable approval information before selection.
- **SMCJ:** Littelfuse-authored historical catalog excerpt with 2005 metadata, obtained from DigiKey. It is retained for provenance, not as current surge-design authority. Obtain the current [Littelfuse SMCJ datasheet](https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_smcj_datasheet?assetguid=37388813-0d6d-4329-969b-1aa8b7614ac1) and verify the exact SMCJ33CA row and worst-case pulse conditions before protection approval. Direct current-document retrieval failed; see manifest provenance.

The manifest marks latest-revision verification as required for these three references. Other PDFs were downloaded from manufacturer sources during this migration, but their applicability and revisions still need checking during exact-part review.

## Retained support references

- [USB-C receptacle drawing](USBC_TYPE-C-31-M-12_Receptacle_C165948_Footprint_Drawing.pdf): possible retained USB footprint support.
- [Tactile-switch datasheet](SWITCH_XKB_TS-1187A_Tactile_SMD_5.1x5.1_H1.5_C318884_Datasheet.pdf): possible retained switch footprint support.
- [USBLC6-2SC6 USB protection](ESD_ST_USBLC6-2SC6_USB2_DataLine_Protection_Datasheet.pdf): optional protection candidate; no final assignment yet.

These assets are outside the 21-family identity manifest and do not force their legacy distributor identifiers into the new BOM.

## Implementation verification

For every selected exact MPN, verify supply/absolute-maximum conditions, startup/shutdown behavior, operating range, pinout, package drawing, land pattern, exposed pad, and required external components. Extract structured specifications when the actual schematic is captured, then cross-check critical values manually.

Use [the sync script](../../scripts/sync_reference_datasheets.py) to maintain local identities. A successful download is reference preparation, not a passed schematic review.
