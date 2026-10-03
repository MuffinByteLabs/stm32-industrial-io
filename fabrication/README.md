# Fabrication releases — STM32 Industrial I/O Controller

No STM32 fabrication package has been generated or ordered. The intended first batch is five four-layer PCBs with staged assembly and at least three fully working units, as defined in the [canonical plan](../docs/STM32_Industrial_IO_Controller_RevA_Plan.md).

Use [KiCad settings](../docs/KiCad_Settings_RevA.md), [layout rules](../docs/Hard_Rules_Layout_RevA.md), and the [assembly plan](../docs/Assembly_and_Stencil_Plan.md) before preparing a release.

## Freeze one coherent revision

Create a dated revision directory only when the implementation is ready. Include:

- Native KiCad project, complete schematic hierarchy, PCB, local libraries, and the tool version used.
- Schematic PDF and assembly/fabrication drawings.
- Gerbers for F.Cu, In1.Cu, In2.Cu, B.Cu, solder masks, required paste layers, silkscreen, and Edge.Cuts; drill files with plated/nonplated interpretation.
- Exact stack-up, thickness, copper weights, finish, tolerances, and any controlled-impedance requirement agreed with the fabricator.
- Exact exported BOM with DNP/substitution instructions and placement/CPL files appropriate to the selected assembler.
- Paste/stencil requirements, exposed-pad decisions, assembly notes, polarity markings, inspection access, and package handling.
- ERC, DRC, and schematic/PCB parity reports with reviewed exceptions, plus electrical/thermal/EMC/mechanical review records.
- A first-article test procedure and a revision-specific acceptance checklist.
- Checksums, hardware revision, issue log, and ordering/quote record.

Use a Gerber viewer to check all four copper layers, outline, hole registration, masks, paste, and text. Confirm assembly orientation against the real footprints and BOM. CI exports alone do not establish manufacturability.

Choose the vendor after obtaining current quotes for the actual design. No old two-layer price, size limit, assembly catalog, or copied capability sheet applies automatically.

Release tags must not be used before the matching native design exists and required checks pass. Keep ordered files immutable; place corrected designs in a new revision directory and update the changelog.
