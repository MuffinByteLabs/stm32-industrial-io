# Open engineering items — Rev A

Updated October 2, 2026. The [canonical plan](STM32_Industrial_IO_Controller_RevA_Plan.md) owns the targets. These items are decisions and evidence still needed to implement them.

## Before schematic freeze

| Item | Decision or evidence required |
| --- | --- |
| Demonstration loads | Choose a compatible externally powered loop transmitter, a 12/24 V DC actuator within 0.5 A, and a voltage-input 0–10 V actuator or representative load |
| MCU resources | Verify STM32G474VET6 package pins, peripheral alternate functions, clocks, USB recovery, DMA conflicts, ADC monitoring inputs, and boot/debug access |
| Input protection | Select the blocking FET, fuse, connectors, capacitors, and exact TPS26632 ordering code; coordinate reverse-fault differential stress, current limit tolerance, surge waveform, TVS clamp, and eFuse SOA |
| Regulator details | Calculate worst-case loads and efficiency at 9/12/24/30 V; select magnetics, capacitors, compensation, startup, ripple, and thermal area |
| USB source selection | Select USB current advertisement/detection and policy, source priority, fault thresholds, and no-backfeed circuitry; prove field loads cannot run from USB |
| Analog supplies | Select 3V3_FIELD_LOGIC regulator and rail-valid hardware; verify ADC_AVDD low-impedance bleeder during protector-on/ADC-off states and every source-loss sequence |
| Digital crossings | Choose Ioff-capable buffers or otherwise proven interface protection so the USB-powered MCU cannot backpower field-only ADC/DAC circuits |
| Digital inputs | Calculate ISO1212 threshold/current networks across tolerance and temperature for OFF ≤5 V and ON ≥9 V; preserve DI1's 20 kHz target through filtering/timing, and verify reversed/unpowered behavior |
| Analog fault protection | Finalize two TMUX7462F threshold groups, S/D orientation, fault response, leakage, series impedance, pulse clamps, and ±30 V miswire energy; autonomous protection is not an output enable |
| Current inputs | Select exact 200 Ω precision shunts and filters; verify pulse/sustained faults, acquisition settling, calibration uncertainty, loop burden, and temperature error |
| Analog output | Select exact zero-POR DAC variant and default-off disconnect; verify OPA197 gain/stability, negative-bias limits, rail-loss behavior, leakage, series loss, and near-zero performance |
| AO monitoring | Protect amplifier-side readback; it cannot prove terminal voltage. Select a separately protected measurement path if terminal feedback is added |
| High-side outputs | Select blocking/freewheel diodes; verify current-limit tolerance, multiplexed current sensing, MCU protection from fault-level sense voltage, off-state diagnostics, reverse/backfeed behavior, and inductive decay |
| Relays | Verify SPDT coil/current and contact footprint; select drivers/clamps; document NO open versus NC closed while deenergized |
| Bus power | Confirm each UCC12050 island has worst-case power and thermal margin; select a regulated alternative if needed |
| Bus interfaces | Finalize termination, RS-485 polarity/bias, reference/shield strategy, connector protection, CAN timing, and actual test cable/topology |
| Output permission | Select reset/supply supervision and hardware gates for high-side inputs, relay drivers, and AO disconnect; prove permission loss without MCU cooperation |
| Mechanical | Choose actual enclosure and terminals together; determine outline, mounting, clearances, strain relief, and ventilation |
| Assembly | Verify every exact symbol/land pattern/model, handling class, paste aperture, inspection access, and assembly method |

## Before ordering

- Complete worst-case calculations and meaningful simulations for the circuits that need them; resolve each assumption with a manufacturer reference or measurement.
- Complete independent schematic and layout review, ERC/DRC/parity, mechanical fit, and appropriate EMC/thermal review.
- Freeze exact BOM and check stock, lifecycle, pricing, and substitution behavior. Obtain current quotes for the actual four-layer stack and assembly process.
- Define the limits of planned immunity tests and fault fixtures before testing. A general industrial design does not establish automotive, machinery-safety, or regulatory certification.
- Review the firmware protocol and state machine against hardware gating; define initial command owner, timeout, fault latches, and fresh rearm.

## Before portfolio claims

Publish only measured voltage/current accuracy, noise/bandwidth, load temperature, pulse rate, cable lengths, communication rates, and fault response. Qualification must include at least three working units and the chosen enclosure.

Rev A's voltage-source AO does not automatically support a current-sinking lighting interface. Rev A's on/off load channels do not demonstrate ten proportional 1.5 A solenoids. Keep those as explicit future extensions when discussing the related jobs.

Track closure by adding the evidence path, design revision, date, and reviewer beside each resolved item. Close an item after evidence exists, rather than after a component is merely selected.
