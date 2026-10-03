# Procurement plan — STM32 Industrial I/O Controller Rev A

Updated October 2, 2026.

These are design candidates, not an orderable BOM. Exact ordering suffixes, packages, support components, availability, lifecycle, distributor prices, and assembly quotes remain to be verified. The [canonical plan](STM32_Industrial_IO_Controller_RevA_Plan.md) defines functionality; the [open engineering items](Open_Engineering_Items.md) identify selection risks.

## Major candidates per board

| Function | Candidate | Starting quantity | Selection gate |
| --- | --- | --- | --- |
| MCU | STM32G474VET6 | 1 | LQFP100 pin/resource map, clocks, debug, and boot |
| Four-channel ADC | ADS8684A | 1 | Interface, supplies, acquisition/filter settling, and fault limits |
| Input eFuse | TPS26632 | 1 | Fixed-clamp variant, exact package, blocking FET, surge and thermal coordination |
| Raw TVS | SMCJ33CA family | 1 | Defined surge and worst-case clamp; not selected solely by nominal voltage |
| 5 V field buck | LMR38020 | 1 | Magnetics, caps, operating frequency, startup, heat |
| 3.3 V digital buck | TPS62160 | 1 | Exact output variant/package and MCU load |
| MCU quiet supply | TPS7A20 3.3 V variant | 1 | Noise, dropout, load, and capacitor requirements |
| Logic power mux | TPS2121 | 1 | USB/field insertion, current limits, source priority, no backfeed |
| Positive analog boost | TPS55340 | 1 | 15 V output, compensation, ripple, worst-case current |
| Negative bias | LM7705 | 1 | Input maximum, startup, output current, zero-output behavior |
| Digital input receivers | ISO1212 | 2 | Four group-isolated channels; thresholds and pulse timing |
| Analog fault protection | TMUX7462F | 2 | Separate voltage/current threshold groups; S/D orientation and pulse energy |
| DAC | DAC80501Z variant | 1 | Zero-scale power-on behavior, package/interface |
| AO amplifier | OPA197 | 1 | Gain, stability, bias, loading, and rail-loss behavior |
| Four high-side channels | TPS4H160B-Q1 | 1 | Current-sensing B variant, package thermal area, diagnostic interface protection |
| SPDT relay | G5Q-1 DC5 or equivalent | 2 | Actual SPDT variant, 5 V coil budget, footprint, chosen DC load |
| RS-485 transceiver | ISO1410 | 1 | Half-duplex pinout, protection, isolated bus supply |
| CAN transceiver | ISO1042 wide-body variant | 1 | Bus supply, timing, protection, isolation geometry |
| Independent bus power | UCC12050 or qualified regulated alternative | 2 | Worst-case load, efficiency, derating, thermal behavior |
| Watchdog | TPS3431 | 1 | Hardware permission response and development policy |
| Configuration EEPROM | 24LC64 family | 1 | Exact voltage/package, write protection, endurance and recovery |

The [reference manifest](../references/datasheets/manifest.json) links family PDFs to their source URLs and file hashes. Family PDFs do not prove an exact suffix's pinout or the correctness of a KiCad asset.

## Parts still requiring selection

- External 100 V-class input blocking MOSFET, fuse, bulk/input capacitors, and all regulator magnetics/support parts.
- Separate field-logic supply, analog rail supervision, Ioff-compatible buffers, hardware output-permission gates, and default-off AO disconnect.
- Two 200 Ω precision shunts, gain-setting resistors, pulse-rated resistors/clamps, filtering, and ADC_AVDD discharge path.
- High-side backfeed-blocking/freewheel diodes, relay drivers/clamps, protected sense interface, and bus/USB protection.
- Oscillator parts, local decoupling, calibration memory support, debug/boot/reset hardware, status indicators.
- All mating connectors, plugs, terminals, wire, enclosure, insulated mounts, and fixture hardware.

A retained USB or switch footprint is only a candidate asset. It does not force its old distributor number into this design.

## Sourcing process

1. Choose exact manufacturer ordering codes while resolving circuit and package requirements.
2. Store manufacturer, MPN, datasheet URL, footprint, distributor part numbers, substitution constraints, and assembly notes on each schematic symbol. Export the BOM from the implemented schematic.
3. Check authorized distributors for quantity breaks, genuine stock, lead times, lifecycle, MOQ, and packaging. Record the check date. Compare alternatives only after pin, thermal, electrical, and diagnostic behavior have been reviewed.
4. For the five-board batch, buy the required populated quantity plus deliberate spare quantities. Keep expensive IC spares tied to expected repair risk, rather than applying a blanket multiplier.
5. Select bare-board/stencil or assembly service after reviewing the actual BOM, packages, and inspection access. Record whether components are consigned, distributor-sourced, or assembler-sourced.
6. Obtain current quotes for the frozen four-layer stack, tooling, stencil, assembly, shipping, taxes, and any part substitutions.
7. Inspect received markings/packages and maintain traceability for critical parts and each assembled unit.

## Planning allowance

The canonical plan reserves approximately **$1,080–$2,180** for the project, excluding major bench equipment, adapters, and optional evaluation boards. This is an engineering allowance, not a distributor or fabrication quote.

Prioritize feasibility experiments before purchasing the entire batch: supply-source behavior, analog miswire protection, zero-volt AO, and high-side fault/inductive behavior can expose expensive redesigns early.
