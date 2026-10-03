# KiCad Setup — STM32 Industrial I O Controller Rev A

Updated October 2, 2026. This checklist follows the [canonical plan](STM32_Industrial_IO_Controller_RevA_Plan.md). Settings below are **not yet applied to a captured PCB**. Record the actual KiCad version, fabrication stack-up, and application date when capture/layout begins.

## Project identity and libraries

Create the real project at `hardware/STM32_Industrial_IO/STM32_Industrial_IO.kicad_pro`, with matching `STM32_Industrial_IO.kicad_sch` and `STM32_Industrial_IO.kicad_pcb`. Empty hardware files do not establish capture or validation.

Put project-local libraries/tables beside the new project where needed. Resolve library/model paths relative to `${KIPRJMOD}` and document resources outside that folder. Existing resources are candidates only: check symbol pins, footprint pads, mechanical drawing, orientation, polarity, and assembly recommendations against each exact selected MPN. Assembly on another board does not verify a new package/substitute.

Use the hierarchy in the plan and [hardware README](../hardware/README.md). Annotate consistently and maintain unique references; ranges are organizational choices rather than preassigned component identities.

## Stack-up and routing

| Item | Starting configuration | Required follow-up |
| --- | --- | --- |
| Copper layers | F.Cu, In1.Cu, In2.Cu, B.Cu | Four layers; isolation islands/keepouts on every layer |
| Board thickness | Approximately 1.6 mm | Confirm enclosure and fabrication stack-up |
| Copper weights | Provisional 1 oz | Record actual outer/inner weights and current calculations |
| F.Cu | Primary components and critical signals | Deliberate regulator/analog/MCU placement |
| In1.Cu | Main reference ground outside isolation islands | Continuous returns; no barrier crossings |
| In2.Cu | Planned power regions and suitable slow routing | Avoid fragmenting required references |
| B.Cu | Secondary signals and appropriate local reference copper | Review every fast-signal return |
| USB pair | 90 ohm differential target | Calculate width/gap from final stack-up |

Record dielectric thickness/material values from the selected manufacturer. Do not reuse generic two-layer geometry or a historical capability table as the current fabrication specification.

## Provisional manufacturing constraints

These are starting preferences, not manufacturer minimum capabilities. Check the chosen fabrication process and package escape needs before layout.

| Constraint | Starting preference |
| --- | --- |
| General signal clearance | 0.20 mm, with reviewed package-specific exceptions if needed |
| General signal track | 0.20–0.25 mm; calculate sensitive/differential geometry separately |
| Working through via | 0.60 mm diameter / 0.30 mm drill |
| Larger power/stitching via | 0.80 mm diameter / 0.40 mm drill, with current/copper review |
| Copper-to-edge | 0.50 mm starting allowance; revise for edge process/enclosure |
| Silkscreen text | Approximately 1.0 mm height / 0.15 mm stroke where readable |
| Mask/paste | Exact footprint and assembly guidance; no universal expansion/aperture rule |

Derive annular-ring, copper-to-hole, hole-to-hole, mask-web, drilled-hole, and finished-hole constraints from the selected process. Avoid freezing unverified manufacturing numbers.

## Net classes and isolation rules

Create classes for main input/field energy, 5 V service, 3.3 V logic, analog/reference, converter switch nodes, USB, digital-input island, RS-485 island, CAN island, and **each independent relay contact circuit**. Track widths are not current ratings: calculate thermal spokes, neck-downs, vias, layer changes, and terminal-pad connections.

Check actual net names after capture; hierarchical prefixes affect pattern matching. Main-ground analog/load nets must not become isolated-domain nets merely because they reach a field terminal.

Draw barrier rule areas with copper/track/via/zone keepouts on all four layers. Specify package-appropriate domain-to-domain separation, including island-to-island spacing. Check custom-rule syntax in the installed KiCad version and introduce a deliberate violation to prove detection before trusting the rule.

No rule is represented here as installed or proven. Final syntax belongs in the real project's `.kicad_dru` and must be checked with the actual board.

## Editor, zones, and assembly

Use placement grids compatible with footprints/enclosure geometry. Name functional boundaries, isolation barriers, and mechanical clearances on user layers. Import final enclosure geometry before committing terminal positions.

Assign zone nets deliberately and inspect all layers after refill. Solid/thermal pad connections and spoke sizes depend on solderability, current, and heat. Apply exposed-pad via/paste guidance per package/assembler rather than one blanket percentage.

Provide agreed fiducials and placement origin. Verify paste layers, polarity, DNP handling, mounting clearances, 3D models, and mating connector envelopes.

## Validation and automation

`.github/workflows/kicad-ci.yml` targets the new project paths. Until files exist its summary says hardware checks did not run. A real schematic requires ERC; a real PCB requires DRC with zone refill and schematic parity. Both require matching project settings. Reportable warnings/errors fail automated checking; reviewed exclusions still require a release-record review.

Release tags require the project, schematic, and PCB together, and the native board must declare exactly F.Cu, In1.Cu, In2.Cu, and B.Cu as its four copper layers. Requesting inner-layer Gerbers alone is not evidence of a four-layer board. The automated declaration check complements manual review of the actual stack-up and exported files.

Release exports include four copper layers, mask, paste, silkscreen, outline, drills, and schematic PDF. Visually inspect them and synchronize the native design/BOM/assembly package. See [layout rules](Hard_Rules_Layout_RevA.md) and [assembly plan](Assembly_and_Stencil_Plan.md).

CLI options were checked against the [official KiCad 10 CLI reference](https://docs.kicad.org/10.0/en/cli/cli.html). Hardware checks remain unrun while no fresh schematic/PCB exists.
