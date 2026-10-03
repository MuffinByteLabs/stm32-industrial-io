# Layout Rules — STM32 Industrial I O Controller Rev A

Updated October 2, 2026. These requirements implement the [canonical board plan](STM32_Industrial_IO_Controller_RevA_Plan.md). They apply to a future four-layer design; no completed layout, applied rule set, or fabrication approval is claimed.

## Ground domains and isolation

- Main DC return, MCU, ADC/analog return, load return, and USB ground belong to one main electrical domain. Arrange physical current paths so actuator and converter currents do not flow through analog-return connections.
- Keep DI_COM, RS485_REF, CAN_REF, relay 1 contacts, and relay 2 contacts separate from main ground and from one another where the plan specifies separate domains. The four digital inputs share one input-common island.
- Apply isolation-barrier copper keepouts on **all four copper layers**, including zones, pads, vias, and mechanical hardware. Only selected isolation components cross their barrier. Analog signals and load outputs share main ground; they are not an isolated field island.
- Set barrier spacing from exact isolator/relay packages, intended installation, and the weakest assembly feature. Approximately 8 mm is a starting communication-barrier goal where packages support it; document resulting creepage/clearance rather than deriving a board rating from an IC rating.
- Put communication protection and termination on the matching bus-reference island. Give each port its own isolated supply. Reference/shield connections must not accidentally bridge islands.

## Four-layer reference system

Use F.Cu for parts and primary signals, In1.Cu for continuous main ground outside isolation islands, In2.Cu for planned power regions and appropriate slow routing, and B.Cu for secondary routing with defined return paths. Confirm the actual manufacturer stack-up before calculating USB geometry.

Keep USB, clocks, SPI, and sensitive signals over a continuous reference. A bottom-layer signal above fragmented In2.Cu power regions needs an explicitly designed return path. Do not cut main ground to imitate a single star-point ground system.

## Power, switching, and load paths

- Place the fuse, raw TVS, blocking FET/eFuse, controlled bulk, and input connector as a coordinated protection path. Keep the TVS discharge path short and away from signal returns. Large bulk capacitance belongs after startup control.
- Verify package-specific pinouts before placement. Follow the selected regulator's hot-loop, feedback, bootstrap, thermal-pad, and capacitor guidance; no earlier designator or pin-number recipe applies.
- Keep buck/boost hot loops compact and switch-node copper limited. Keep feedback, references, analog, USB, and crystal circuits away from inductors/switching nodes. Locate quiet analog support near the ADC/front end and away from relay drivers.
- Size input/load copper, vias, terminals, fuse, and MOSFETs for the reviewed current and fault envelope. Targets are 3 A continuous board input, approximately 3.5 A nominal electronic limit, and four 0.5 A outputs together. Include copper thickness, temperature rise, neck-downs, layer changes, and enclosure conditions.
- Fit the specified per-channel blocking diode and load-side freewheel diode. Verify orientation, current decay, positive backfeed prevention, pulse energy, and simultaneous-load heating.
- Preserve hardware output permission for high-side commands, relay drivers, and the analog disconnect. External pull-downs, reset, watchdog, invalid rails, and USB-only mode must produce the reviewed off state independently of firmware.
- Keep USB power selection in the logic service path. Check that USB cannot energize relay coils, isolated field supplies, analog auxiliary conversion, or actuators; verify signal-pin backpower during every rail sequence.

## Analog, MCU, and USB

- Place each required decoupler at its supply pin with a short return. Check every STM32 power/ground pin, analog supply, reset, boot configuration, crystal loading, and SWD connection against exact MCU/package documentation.
- Route shunt sense connections with Kelvin treatment. Keep filter/protector/ADC paths short and include resistance, leakage, input loading, reference noise, and load-return error in the error budget.
- Put terminal fault protection near its terminal. Check powered/unpowered faults, current-shunt energy, and analog-output feedback stability. Protect readback/current-sense inputs against fault voltages and unpowered MCU injection.
- Route USB as a 90 ohm differential target using the confirmed stack-up. Keep the pair short/symmetric, protection near the connector, and any signal-layer transition accompanied by a reference transition. Use the receptacle's exact drawing and two independent CC pull-downs.

## Thermal, mechanical, and assembly

- Review continuous and fault dissipation separately. Qualify full-load operation in the selected enclosure at 0–50 °C; a datasheet test-board thermal number cannot replace enclosure testing.
- Follow package guidance for exposed-pad copper, vias, and paste. Coordinate via tenting/filling and solder wicking with assembly. Exposed-pad/QFN packages are allowed and require an inspection/test strategy.
- Start near 140 × 100 mm, then fit the chosen enclosure and terminals. Verify plugs, screwdriver access, cable bends, relay height, mounting hardware, and barriers in 3D. There is no fixed 100 × 100 mm constraint.
- Prefer a consistent primary assembly side where practical. Through-hole terminals/relays can follow SMT reflow. Placement and paste rules must serve the actual manufacturing route.
- Label terminal polarity, domain/return, channels, COM/NO/NC, revision, pin 1, and service controls. State qualified low-voltage DC limits in the wiring guide. NC contacts remain closed with deenergized relays.

## Before fabrication release

Complete ERC, DRC with zone refill and schematic parity, symbol-to-package mapping, footprint/courtyard checks, isolation review, analog simulations, power/fault-energy calculations, thermal/EMC review, enclosure verification, and Gerber/drill/paste inspection. Record reviewed exceptions and evidence. A clean automated check cannot establish component suitability or measured performance.

Freeze native files, exact BOM, libraries, assembly variants, fabrication stack-up, placement, programming, and first-article procedure together. Recheck supplier availability and substitution limits for the release. Keep planning, captured, routed, assembled, and qualified status distinct.
