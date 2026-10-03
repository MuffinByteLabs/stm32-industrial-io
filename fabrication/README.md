# Fabrication

I plan an initial batch of five four-layer PCBs, with staged assembly and qualification of at least three working units. No fabrication package has been generated or ordered.

## Revision package

I will freeze one coherent set of files for each ordered revision:

- Native KiCad project, local libraries, and recorded tool version.
- Schematic PDF, assembly drawing, and fabrication drawing.
- Gerbers for four copper layers, masks, required paste layers, silkscreen, and board outline; plated/nonplated drill information.
- Fabricator-agreed stack-up, thickness, copper weights, finish, tolerances, and any impedance requirement.
- Exact BOM, DNP/substitution instructions, placement files, stencil specifications, and component handling notes.
- ERC, DRC, and schematic/PCB parity reports with reviewed exceptions.
- Electrical, thermal, EMC, and mechanical review records appropriate to that release.
- First-article procedure, acceptance checklist, file checksums, issue log, and ordering record.

I will inspect the manufacturing files in a Gerber viewer and cross-check assembly orientation against the footprints and BOM before ordering. Vendor selection will use current quotes for the completed design.

I will assemble in stages, starting with protected power and controller functions, then adding measurement, communication, and output circuits. I will connect each unit to its [validation records](../docs/Validation.md) through board serial numbers and build identities.

I require a complete native design and passed release checks before tagging a hardware release. I will give corrections to ordered files a new hardware revision and changelog entry.
