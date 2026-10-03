# Folder migration review — October 2, 2026

The user's request was to update the entire project for the newly recommended board, check its fit against the supplied relevant Upwork jobs, and remove obsolete material.

## Result

The active folder now describes a four-layer STM32G474 industrial sensor/actuator controller. The [canonical plan](../STM32_Industrial_IO_Controller_RevA_Plan.md) owns the proposed architecture and acceptance targets. The [project status](../PROJECT_STATUS.md) identifies implementation gates.

Updated root documentation and the hardware, firmware, wiring, resource reservations, power/analog decisions, layout, KiCad setup, assembly, bring-up, procurement, mechanical, fabrication, references, calculations, and future CI contracts. Existing author branding and license were retained.

## Cleanup and recovery

A recovery ZIP was created before edits, outside the project. Its inventory and integrity were checked: **80 files, 58,073,397 uncompressed bytes**. The archive includes the old design documents, references, sourcing material, and empty KiCad files. Git and protected internal directories were excluded. The final check re-read the ZIP, verified its SHA-256, and tested all entries for corruption.

Recovery archive filename: `FieldIO_before_STM32_migration_2026-10-02_941f918c.zip`. It is stored privately outside this repository and is not included in GitHub downloads.

SHA-256: F98563A27BE9816995926222E00C128FFA104BA7FC33ACFAAFAF5C06D9518167.

The [migration manifest](migration_manifest.json) records **42 removed targets**, including directories. It also records two library renames. Removals included the old specification, old sourcing CSV, old calculation script and review claims, superseded capability/reference documents, unused part PDFs, old library tables/custom symbol, and empty native-design placeholders. Removal targets were resolved inside the authorized project before deletion.

Retained reusable assets include the LMR38020 evaluation-module guide, USB/switch support drawings, optional USB ESD reference, generic footprints/models, and logo footprints. Their retention does not verify an exact new-board part assignment.

## Fit verification

The [job-fit review](../Upwork_Job_Fit.md) traces representative client requirements to required finished evidence. The evidence index records 350 raw entries, including duplicates and unrelated jobs; it does not claim 350 relevant opportunities or a hiring probability.

Saved evidence covers 14 exact titles and 45 short quotations. Excerpts were checked against original source text with no mismatches. Strong overlap includes STM32, protected field power, analog conditioning, wired communication, four-layer design, fabrication handoff, and prototype validation.

Partial coverage is explicit: proportional solenoids, ten precision bidirectional current channels, wireless connectivity, automotive/high-voltage qualification, and the off-the-shelf condenser request. Rev A AO is a sourced voltage command; current-sinking lighting interfaces require separate compatibility work.

## Checks and practical limits

Repository checks cover local links and anchors, PDF identity/hashes, expected cleanup, and local library/model paths. Planning arithmetic covers selected budgets and load fixtures. CI shell syntax and four-layer release-gate behavior were checked; the complete GitHub Actions workflow has not run.

The [saved repository audit](Project_Audit_2026-10-02.json) reports no failures. All 21 candidate PDFs passed identity/hash checks, and four project-relative library/model references resolved. Four additional retained PDF references parsed successfully. All three Python scripts compiled; default planning arithmetic ran; Git whitespace checks passed after text normalization. Independent reviews found the new documentation consistent with the canonical plan. A missing digital-input closure item was added during final review.

Candidate PDF identity means a file parses and identifies the intended family. It does not establish the latest revision, exact suffix, pin mapping, or circuit suitability. Some archived PDFs have age/provenance limits recorded in the [reference index](../../references/datasheets/README.md).

The new schematic, PCB, application firmware, BOM export, assembled hardware, and enclosure CAD do not exist yet. ERC/DRC, SPICE, physical thermal/EMC work, source-sequence testing, calibration, and fault qualification are pending. The project is not ready to order.
