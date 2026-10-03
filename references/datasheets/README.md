# Candidate component references

I keep these candidate references with my [architecture](../../docs/Architecture.md) and [design decisions](../../docs/Design_Decisions.md). This reference set was prepared on October 2, 2026; exact part and package approval remain pending.

I have saved all 21 candidate-family PDFs and checked parsing, early-page family identity, byte length, and SHA-256. These checks do not establish exact-package pin correctness, current document revision, part availability, or board performance. My [manifest](manifest.json) records the source, hash, check time, and limitations of each file.

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

- **STM32G474:** I retained ST-authored DS12288 Rev 6, November 2021, from an authorized DigiKey mirror after the official download timed out. Before pin/resource and schematic approval, I will obtain current datasheet, errata, reference manual, and boot guidance from [ST product documentation](https://www.st.com/en/microcontrollers-microprocessors/stm32g474ve.html).
- **G5Q:** I retained official Omron J155-E1-16, June 2021. I will confirm the current regional ordering code, coil/contact tables, drawings, and applicable approval information before selection.
- **SMCJ:** I retained a Littelfuse-authored historical catalog excerpt with 2005 metadata from DigiKey. I will obtain the current [Littelfuse SMCJ datasheet](https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_smcj_datasheet?assetguid=37388813-0d6d-4329-969b-1aa8b7614ac1) and verify the exact SMCJ33CA row and worst-case pulse conditions before protection approval. The current-document download failed; the manifest preserves that provenance.

I have marked latest-revision verification as required for those three references. The other family PDFs came from manufacturer sources, but I will still check applicability and revision during exact-part review.

## Retained support references

- [USB-C receptacle drawing](USBC_TYPE-C-31-M-12_Receptacle_C165948_Footprint_Drawing.pdf): possible retained USB footprint support.
- [Tactile-switch datasheet](SWITCH_XKB_TS-1187A_Tactile_SMD_5.1x5.1_H1.5_C318884_Datasheet.pdf): possible retained switch footprint support.
- [USBLC6-2SC6 USB protection](ESD_ST_USBLC6-2SC6_USB2_DataLine_Protection_Datasheet.pdf): optional protection candidate; no final assignment yet.

I keep these support drawings outside the 21-family identity manifest. They are unassigned candidates; their presence does not select a part for the BOM. Manufacturer documents retain their original attribution.

## Implementation verification

For each selected exact MPN, I will verify supply/absolute-maximum conditions, startup/shutdown behavior, operating range, pinout, package drawing, land pattern, exposed pad, and required external components. I will record critical specifications with the schematic and cross-check them against the current source document.

I maintain local file identities with [the sync script](../../scripts/sync_reference_datasheets.py). A successful download does not replace schematic review.
