# Symbol and footprint preparation before capture

I use KiCad 10 and create the native project in `hardware/STM32_Industrial_IO/`. The [project tables](../hardware/STM32_Industrial_IO/README.md) register `IndustrialIO` with project-relative paths. Its symbol collection is initially empty. Existing USB/button footprints are candidates; registration and file existence do not establish package approval.

My four [selection files](components/README.md) are the authority for exact CAD identifiers, MPNs, quantities and values. I removed descriptive placeholders from the identifiers and keep creation/verification notes separately. Stock-library candidates also need a manufacturer pin/pad comparison; a matching family name is insufficient.

## First capture steps

1. I create `STM32_Industrial_IO.kicad_pro` in the designated directory, then the matching hierarchical schematic. I retain the supplied library tables and project-relative paths. The native files are not present yet.
2. I create the eight sheets listed in [Schematic capture](Schematic_Capture.md#sheets-and-rails). I place connector/domain labels and draw the power/permission overview before detailed wiring.
3. Before wiring an IC, I create or inspect its exact-package symbol and record every physical pin, type, active-low label, supply, exposed pad and intentional no-connect against the source drawing. I use the circuit document's physical pin table and the manufacturer together.
4. Before accepting its footprint, I compare pin/pad numbering, viewing direction, dimensions, pitch, exposed-pad/thermal-via treatment, solder-mask/paste and connector orientation with the exact package drawing. I check cable/mating-plug fit and record provenance.
5. I place the approved symbol with MPN, Manufacturer, Datasheet, Package, Tolerance, Rating and selection/review evidence. Native reference designators and actual placements replace the preliminary quantity allocation.
6. I capture one complete path at a time, including bypasses, defaults, fault handling and returns. I review the permission/default truth table and powered-off paths before accepting ERC. Native ERC success does not approve electrical behavior or footprints.

## Custom asset work list

The October 6 availability audit checks 150 positive-quantity board component groups and finds missing assets in 30. Several groups share an asset. The exact machine-readable list comes from [audit_capture_readiness.py](../scripts/audit_capture_readiness.py); I rerun it after library changes rather than use this count as a release check. All installed stock candidates were checked for presence; none is approved by presence alone.

| Circuit | Missing custom work |
| --- | --- |
| Main power | LMR38020F DDA symbol; TPS70933 DBV symbol; XFL3012 footprint |
| Analog/protection | ADS8684A DBT, TPS26611 DDF, TMUX7462F PW, TPS7A1601 DGN, OPA2320 D, LM4040 AIM3, TMUX1511 PW and BAS70-04 symbols; TPS7A16 DGN exposed-pad footprint |
| Control/health | TPS3808G30 DBV6, TPS3700 DDC6, TPS3702CX50 DDC6, TPS3431S DRB8 and SN74LVC1G74 DCU8 symbols; TPS3431 DRB8 footprint |
| Loop status | SN74AUP1T17 DCK5 symbol |
| Clock/service | SiT8008 3.2 × 2.5 mm ST-option footprint; exact Samtec FTSH-105-01-L-DV-K SMT footprint/cable check; TYPE-C-31-M-12 symbol; TPD2E2U06 DCK3 symbol |
| Digital inputs/load outputs | ISO1212 DBQ symbol; TPS4H160B PWP symbol and exact PWP0028V footprint |
| Isolated ports | ISO1410 DW16, ISO1042 DWV8, PESD2CANFD24V-T and UCC33421 DHA16 symbols; exact ISO1042 DWV8 and UCC33421 DHA0016A footprints |
| Field terminals | Exact unflanged MSTB1759017, 1759020 and 1759033 footprints; compare connector view, polarity and mating plugs. MC1844210/1844223/1844236 now use exact installed stock candidates, with pin/pad/mating approval still pending |

ACT45B choke assets are a zero-quantity optional selection; I verify them before a variant fits that part. Optional tuning/DNP parts and off-board mates remain in the selection index even when this positive-quantity board audit omits them.

The October 6 [verification](External_Review_Verification.md) confirms the corrected LVC2G125 stock symbol and leaded TPS62160DGK candidate. For DGK I compare the exact DGK0008A drawing to the selected MSOP-8 land pattern and omit an exposed-pad/pin 9. Stock MSTBA and flanged MSTB-GF alternatives are different from the selected unflanged MSTB articles. Procurement needs a workable MCU and isolated-power-module route before package freeze; available tube transceiver carriers are separately recorded in the [stock snapshot](../references/procurement/README.md).

The selected HRO USB footprint already exists under `IndustrialIO`, but connector tab/pad numbering still needs comparison. The tactile-switch footprint/model also needs the original-source/license review recorded in the [library notes](../hardware/libs/README.md). I do not treat the imported model as an approved part drawing.

## Availability check and package-review record

~~~text
python scripts/audit_capture_readiness.py
python scripts/audit_capture_readiness.py --require-assets
~~~

The normal report rejects malformed identifiers and absent registered collections, and explicitly lists missing selected assets. It can pass those structural checks while the asset gate remains open. `--require-assets` fails while a fitted selection lacks an asset or stock availability cannot be checked. I can supply `--kicad-library-root` with the directory containing `symbols/` and `footprints/`. Neither mode verifies geometry, circuit connectivity or electrical ratings.

For each created/approved asset I keep this record with the library review:

| Field | Required entry |
| --- | --- |
| Exact part/package | Ordering code, package drawing identifier and revision |
| Source | Manufacturer document/page and retrieval date; source hash where saved |
| Symbol check | Physical pin table, pin types, active levels and exposed-pad/NC treatment |
| Footprint check | Pad map, dimensions/tolerances, assembly view, thermal/paste handling and courtyard |
| Integration check | Connector mate/cable, polarity, isolation/current/thermal requirements and model alignment |
| Provenance | Author/source, redistribution terms and preserved notices |
| Disposition | Pending, corrected or approved; reviewer/date, native placement and unresolved issues |

I require these records before approving the manufacturing library. A zero missing-asset count is an availability result, not a package review result.
