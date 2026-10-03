# Assembly and Stencil Plan — STM32 Industrial I O Controller Rev A

Updated October 2, 2026. Assembly follows the [canonical board plan](STM32_Industrial_IO_Controller_RevA_Plan.md). No order, stencil, populated prototype, or assembly qualification is complete. Select the route after package/BOM/layout review.

## Procurement and process

Plan five four-layer PCBs and at least three fully working, individually traceable units. Qualify the first article before completing the others. Obtain current fabrication, stencil, assembly, shipping, and component quotes from the exact native design/BOM; historical price tiers and shared-shipment assumptions do not apply.

Prefer machine assembly for mixed leaded/exposed-pad packages when practical. Hand or staged assembly is acceptable when inspection/rework limits are understood. Through-hole terminals and relays may follow SMT reflow. A consistent primary SMT side is useful, but there is no blanket ban on leadless packages or restriction to a particular hot plate.

Order mating plugs, enclosure/mounting hardware, debug connection, demonstration sensor/load, suppression, and selected spares with PCB components. Mark assembly variants/DNP explicitly in BOM and placement exports.

## Stencil and footprints

Evaluate a 0.10–0.12 mm stencil with the assembler for the selected fine-pitch MCU, USB, exposed pads, inductors, and larger pads. Thickness remains provisional until area ratios, paste release, package guidance, and process capability are reviewed.

- Use package-specific exposed-pad aperture patterns/coverage. Coordinate thermal-via tenting/filling and paste distribution to manage wicking, float, and voiding.
- Check small apertures for release/bridging. Do not assume every aperture should equal pad size.
- Provide agreed fiducials, board support, alignment, panel features, and placement origin. Exclude tall through-hole parts from reflow unless the process supports them.
- Inspect exported paste/copper in a Gerber viewer and the manufacturer's preview. A 3D view checks geometry but cannot establish stencil print quality.

## Storage and handling

Record moisture-sensitivity level, floor-life conditions, packaging, storage, and reflow limits for each exact package. Keep sensitive parts in specified sealed packaging until use; record opening dates and humidity indicators where applicable.

If drying is required, follow the applicable manufacturer procedure using controlled equipment and compatible carriers. Do not apply a universal bake temperature/time to parts, reels, connectors, or relays. Match paste storage, thawing, alloy, mesh, and reflow profile to the actual process.

Use appropriate ESD handling and retain lot/date traceability for each unit.

## First article

1. Check bare-board outline, holes, finish, mask, barriers, and fabrication stack-up against the release.
2. Check stencil registration and paste print under magnification; clean/reprint defective deposits.
3. Place to released coordinates/polarity drawing. Independently check MCU pin 1, IC orientation, diode direction, connectors, and relay footprint before reflow.
4. Measure a board profile satisfying paste/component limits, including high/low thermal-mass locations. Equipment set-point alone is not board temperature.
5. Inspect/rework SMT before fitting through-hole parts. Use optical inspection and X-ray where available for hidden joints. Functional continuity alone cannot establish exposed-pad solder quality.
6. Install through-hole parts with a process that wets power/terminal connections without damaging the board or adjacent components.
7. Check cleanliness, polarity, bridges, lifted pads, tombstones, alignment, seating, and hidden-joint evidence before power.

Use an agreed assembly acceptance standard/edition and class with the assembler where appropriate. Keep actual criteria/results in the release record; this plan does not claim IPC certification or reproduce acceptance tables from memory.

## Electrical inspection and staged power

Check supply resistance, domain separation/continuity, relay contact mapping, fuse path, and accessible critical pins before power. Follow the canonical staged bring-up with a current-limited supply: input protection, service rails, MCU/debug, auxiliary/isolated rails, inputs, analog output, load outputs, relays, and communications.

Keep hardware output permission inhibited initially. Verify no field energy is enabled by USB, reset, bootloader, or incomplete firmware; check signal-pin backpower into unpowered rails.

At each stage record identity, firmware, setup, rail readings, scope evidence, defects, and rework. Complete first-article fault resolution before populating remaining units.

## Evidence and release

Store a descriptive dated first-article report under `docs/reviews/`. Include PCB/BOM revision, part/supplier lots, stencil/paste, measured profile, inspection method, defects, rework, and staged electrical results.

Program/calibrate at least three units repeatably and retain per-unit calibration/qualification records. Complete load, fault, source-sequencing, accuracy, and enclosure thermal testing before advertising ratings or issuing the manufacturing release.
