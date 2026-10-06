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

## Assembly and qualification milestones

I retain the complete Rev A hardware: four digital inputs, two voltage inputs, two externally powered current receivers, four high-side outputs and two relays, plus both isolated communication ports. I use staged assembly to localize bring-up issues; temporarily leaving the second relay or replicated channels unpopulated is a recorded assembly stage, not a reduction of the released design or a change to its component quantities.

I assemble protected power and controller/service circuits first, then one complete measurement and on/off load path before their replicated channels. I check safe default-off behavior before connecting an actuator load. Each intermediate assembly record lists fitted/DNP reference designators and known unavailable functions; I do not test or advertise a function whose support circuit is absent.

| Milestone | Manufacturing/assembly evidence I retain |
| --- | --- |
| M1 — Nominal Modbus controller | Board serial and assembly-stage identity, nominal 12/24 V room-temperature bring-up, calibrated input/on-off output fixture, host logs, USB service records and timeout/rearm captures |
| M2 — Classic CAN | Complete port population, peer/cable/termination configuration and classic-CAN recovery records |
| M3 — Bounded PWM | Existing DO3 path, qualified 100 Hz resistive fixture, diagnostic/timing/shutdown evidence and actual thermal conditions |
| M4 — Full Rev A qualification | Complete released population and 9–30 V/0–50 °C/combined-load/fault/CAN FD evidence; repeatability across at least three units and 24 h logged operation |

The [fixed scope](../docs/Scope.md) and [implementation plan](../docs/Implementation_Plan.md) define M0 preparation and the complete milestone sequence; the [validation plan](../docs/Validation.md) owns acceptance targets and the exact test order. M1 uses DO3 only for static off/on, with PWM following in M3. I connect every record and raw capture to board serial, hardware revision, assembly variant and firmware build using the [record template](../docs/templates/Validation_Record.md). A milestone completed on one assembly does not qualify a different population or a full operating envelope.

I require a complete native design and passed release checks before tagging a hardware release. I will give corrections to ordered files a new hardware revision and changelog entry.

I publish a [portfolio evidence package](../docs/Portfolio_Evidence.md) for a completed milestone with its measured conditions and pending work plainly stated. A prototype demonstration does not replace the coherent manufacturing handoff above or the complete qualification evidence needed for a full Rev A release. No fabricated, assembled or measured result is claimed by this plan.
