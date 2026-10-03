# Pre-schematic engineering review

I reviewed the Rev A architecture on October 3, 2026 against manufacturer product status, electrical tables, interface requirements, power arithmetic, and a provisional MCU resource allocation. My corrected architecture is ready for schematic capture. I have not yet approved a completed circuit, PCB, production BOM, or assembled-board rating.

I separate three kinds of evidence: manufacturer-specified device capabilities, my calculations and design assumptions, and measurements still to be collected. I cannot run ERC, DRC, extracted-layout analysis, or whole-board simulation before the native design exists. My [capture checklist](Schematic_Capture.md) and [qualification plan](Validation.md) define the next gates.

## Component lifecycle and selection

I checked the following manufacturer pages on October 3, 2026. The semiconductor families below are Active, In Production, or Recommended for New Designs. An older publication date alone does not make a supported component obsolete. Lifecycle status also does not guarantee distributor inventory or future availability; I will check exact ordering codes and stock when I freeze the assembly BOM.

| Circuit | Selected family or exact candidate | Manufacturer evidence |
| --- | --- | --- |
| MCU | STM32G474VET6, LQFP100 | [ST: Active](https://www.st.com/en/microcontrollers-microprocessors/stm32g474ve.html) |
| Main input eFuse | TPS26632RGER | [TI: Active](https://www.ti.com/product/TPS2663/part-details/TPS26632RGER) |
| Field buck | LMR38020 | [TI: Active](https://www.ti.com/product/LMR38020) |
| Logic buck / MCU analog LDO | TPS62160 / TPS7A20 | [TPS62160](https://www.ti.com/product/TPS62160), [TPS7A20](https://www.ti.com/product/TPS7A20) |
| Field/USB power selection | TPS2121 | [TI: Active](https://www.ti.com/product/TPS2121) |
| Analog auxiliary rails | TPS55340 / LM7705 | [TPS55340](https://www.ti.com/product/TPS55340), [LM7705](https://www.ti.com/product/LM7705) |
| Group-isolated digital inputs | Two ISO1212 | [TI: Active](https://www.ti.com/product/ISO1212) |
| Four-channel 16-bit acquisition | ADS8684A | [TI: Active](https://www.ti.com/product/ADS8684A) |
| Analog sense protection | TMUX7462F | [TI: Active](https://www.ti.com/product/TMUX7462F) |
| Current-loop series protection | Two TPS26611DDFR, 8-pin DDF | [TI: Active](https://www.ti.com/product/TPS2661/part-details/TPS26611DDFR) |
| Zero-scale POR DAC | DAC80501ZDQFR | [TI: Active](https://www.ti.com/product/DAC80501/part-details/DAC80501ZDQFR) |
| Gain and output driver | OPA2197IDR, dual SOIC-8 | [TI: Active](https://www.ti.com/product/OPA2197/part-details/OPA2197IDR) |
| AO disconnect and protected feedback | ADG5401FBCPZ-RL7, 10-lead LFCSP | [ADI: Recommended for New Designs](https://www.analog.com/en/products/adg5401f.html) |
| Four diagnosed high-side outputs | TPS4H160BQPWPRQ1 | [TI: Active](https://www.ti.com/product/TPS4H160-Q1/part-details/TPS4H160BQPWPRQ1) |
| Isolated bus transceivers | ISO1410 / ISO1042 | [ISO1410](https://www.ti.com/product/ISO1410), [ISO1042](https://www.ti.com/product/ISO1042) |
| Independent isolated port power | Two UCC33421QDHARQ1 | [TI: Active, production](https://www.ti.com/product/UCC33421-Q1/part-details/UCC33421QDHARQ1) |
| External watchdog | TPS3431 | [TI: Active](https://www.ti.com/product/TPS3431) |
| MCU reset / hardware ARM memory | TPS3808G33DBVR / SN74LVC1G74DCUR | [TPS3808](https://www.ti.com/product/TPS3808/part-details/TPS3808G33DBVR), [SN74LVC1G74](https://www.ti.com/product/SN74LVC1G74/part-details/SN74LVC1G74DCUR) |
| Permission gates / powered-off buffers | SN74LVC2G08DCUR / SN74LVC2G125DCUR | [SN74LVC2G08](https://www.ti.com/product/SN74LVC2G08/part-details/SN74LVC2G08DCUR), [SN74LVC2G125](https://www.ti.com/product/SN74LVC2G125/part-details/SN74LVC2G125DCUR) |
| MCU diagnostic analog isolation | TMUX1511PWR, 14-pin TSSOP | [TI: Active](https://www.ti.com/product/TMUX1511/part-details/TMUX1511PWR) |
| Rail windows / ADC rail window | TPS3700DDCR / TPS3702CX50DDCR | [TPS3700](https://www.ti.com/product/TPS3700/part-details/TPS3700DDCR), [TPS3702](https://www.ti.com/product/TPS3702/part-details/TPS3702CX50DDCR) |
| Negative-bias monitor reference / health conditioning | REF3325AIDBZR / SN74LVC2G17DBVR | [REF3325](https://www.ti.com/product/REF3325/part-details/REF3325AIDBZR), [SN74LVC2G17](https://www.ti.com/product/SN74LVC2G17/part-details/SN74LVC2G17DBVR) |
| Calibration/configuration storage | 24LC64 | [Microchip: In Production](https://www.microchip.com/en-us/product/24lc64) |
| SPDT relay | G5Q-1 DC5 | [Aratas: In Production](https://www.aratas.com/us-en/products/relays/G5Q) |

I retain SMCJ33CA as a provisional input TVS. Littelfuse lists it in its [current SMCJ datasheet](https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_smcj_datasheet.pdf?assetguid=37388813-0d6d-4329-969b-1aa8b7614ac1); I did not obtain an explicit lifecycle badge for that exact diode. I do not equate a catalog listing with a complete surge-design approval. My support candidates include CSD19537Q3, BSS138P,215 and STPS2H100A; I will check their operating point, temperature, pulse energy, and package against the captured circuit.

I retain proven production families where they meet the requirement. I replaced UCC12050 because its capacity did not close my bus-side load budget, rather than because that family is obsolete. Exact voltage/frequency suffixes, packages, connector codes, passives, crystals, and footprints still need selection during capture.

## Corrections I made before capture

### Current-loop startup and protection

I replaced the earlier arrangement that put a TMUX fault switch ahead of the 200 Ω shunt. An open switch lets an external current source rise toward its compliance voltage; that voltage can keep the switch faulted even after board power returns.

My revised current path is **terminal → TPS26611 → permanent 200 Ω Kelvin shunt → MAIN_GND**. Only the high-impedance shunt-sense branch passes through TMUX7462F to the ADC. The TPS26611 monitors its load-side overvoltage, supplies current limiting, and remains default off through an external EN pulldown until field/analog power is qualified. It does not require the actuator ARM state to acquire inputs. I will implement explicit recovery where a negative fault latches the protector.

The TPS26611 limit is 25–40 mA, 32 mA typical. At its 40 mA upper bound, the shunt dissipates 0.32 W. I specify a precision shunt rated at least 1 W, then separately review fast-trip pulse energy and enclosure derating. At 20 mA, a 12.5 Ω maximum protector resistance adds 0.25 V to the shunt's 4 V burden. I therefore use **4.25 V plus wiring** in the loop-compliance budget. I qualify a 24 mA overrange target; the ADC's arithmetic 25.6 mA endpoint is not a guaranteed receiver operating limit. [TPS2661 datasheet](../references/datasheets/TPS2661.pdf)

The ADC input is biased toward 2.5 V through its effective input resistance; I include that loading in calibration. At the 1 MΩ typical value, the 200 Ω receiver reads approximately +1.7 µA at 4 mA and −1.5 µA at 20 mA before calibration. A voltage source with 1 kΩ total series impedance can lose about 8.8 mV at 10 V using the ADC's 0.85 MΩ minimum input resistance. I will define permitted source impedance and include protection resistance in the ±20 mV budget. [ADS8684A datasheet](../references/datasheets/ADS8684A.pdf)

### Port power and service budget

The ISO1410 bus side can require 160 mA at 5 V under the specified 54 Ω, 500 kbit/s test condition. A nominal 500 mW UCC12050 does not supply that worst-case load. I selected a separate **UCC33421QDHARQ1** for each bus; its nominal 5 V/300 mA output has suitable capacity for the planned transceiver load. I still need to close conversion loss, bias current, cable loading, startup, and thermal limits. [ISO1410](../references/datasheets/ISO1410.pdf), [UCC33421-Q1](../references/datasheets/UCC33421-Q1.pdf)

I increased the service-electronics allocation to **6 W delivered from the field buck**, while retaining four 0.5 A load outputs and a 3 A continuous input target. My [calculation](calcs/controller_budget.py) keeps named branch reservations and labels efficiency as an assumption. At 9 V and 85% field-buck efficiency, the estimate is 2.784 A before protection losses and small additional input currents. This is a useful margin for capture, not a demonstrated thermal or inrush pass.

### Precision AO with a controlled disconnected state

I selected **OPA2197IDR** for two stages: a local gain-four amplifier followed by a unity-gain output driver. **ADG5401F** switches both the output path and a protected Kelvin feedback path from the terminal. Its internal local-feedback path keeps the unity driver closed-loop when the powered switch is disabled or faulted. I hold IN low unless hardware AO permission is valid; both external source pins face the field wiring.

I place the gain-setting divider wholly around the first amplifier. The switch's secondary feedback resistance must not become part of that divider: a typical 600 Ω added to a 30 kΩ/10 kΩ gain network would change a 10 V command to 10.15 V. The second stage instead senses the terminal at a high-impedance amplifier input, compensating the main switch and reviewed series-impedance drop. This is my application of ADI's protected-feedback arrangement, not an already validated OPA2197 reference circuit. [ADG5401F datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/adg5401f.pdf), [ADI application discussion](https://www.analog.com/en/resources/design-notes/precision-solutions-with-protection-and-robustness.html)

I power the switch from +15 V/GND and the amplifiers from +15 V/LM7705 negative bias. The 0–10 V signal fits the switch's VDD−2 V headroom. I use POC grounded for its weak powered-but-disabled pulldown, plus a reviewed external terminal pulldown; IN also has an external pulldown. I still need to validate capacitive-load compensation, endpoint headroom over temperature, fault transitions, and independently protected terminal readback. DAC zero-scale POR does not eliminate its possible startup glitch, so AO remains disconnected through initialization and settling.

I select TMUX1511PWR for receiving-domain analog isolation on terminal readback and shared high-side current telemetry. Its powered-off signal range is limited to 0–3.6 V; I must attenuate and independently clamp field faults before it. A pre-isolator clamp into MCU 3.3 V would create the backpower path I am preventing. SEL is qualified by receiving-domain reset/rail validity so brownout also opens the path. Divider loading from the ADC pulldown and effective current-sense burden belong in the captured-circuit calculation. [TMUX1511 datasheet](https://www.ti.com/lit/ds/symlink/tmux1511.pdf)

### MCU pins, clocks, and reset behavior

I found a conflict-free provisional resource allocation in the G474 datasheet. I reserve PB8 for BOOT0, keep PG10 as NRST, use PD0/PD1 for FDCAN1, PD4–PD6 for USART2/RS-485, PC8/PC9 for I2C3, and PA5–PA7 for shared SPI1. USB, SWD, the external crystal, and DI1 timer acquisition have separate pins. I use an 8 MHz HSE planning point with a 144 MHz system clock and exact 48 MHz USB clock; maximum 170 MHz operation is optional and needs a different USB clock strategy. My [capture checklist](Schematic_Capture.md) records the full allocation and relevant errata.

I add a hardware ARM latch with asynchronous clearing. Holding a GPIO high must not reenable outputs when field power returns. The reset supervisor's nominal threshold is 3.07 V for TPS3808G33; I do not substitute an assumed 2.93 V value. I select partial-power-down buffers at MCU/field crossings and monitor actual analog rail windows before declaring acquisition or AO valid.

### Input-fault claims and surge coordination

I removed the unqualified +40 V main-input test. SMCJ33CA has a 36.7–40.6 V breakdown range at 25 °C, so a sustained 40 V source can heat the raw TVS even if the eFuse disconnects. My initial positive DC fault target is **36 V at 25 °C**, with defined source limit, duration, actual terminal voltage, and TVS temperature/current monitoring. I will set other temperatures and waveforms from a completed protection analysis.

I also review the eFuse's negative differential stress with output capacitance still charged. A −53.3 V catalog TVS clamp combined with +30 V retained output is already 83.3 V across the relevant path, close to the stated −85 V/10 ms condition; a +35 V retained output would exceed it. Component voltage labels alone do not establish bipolar surge survival. [TPS2663 datasheet](../references/datasheets/TPS2663.pdf)

## Industry practice and the next design gates

I checked accuracy feasibility separately from ADC/DAC resolution. ADS8684A's maximum ±2 LSB INL corresponds to ±0.3125 mV on the voltage range and ±0.78125 µA through the current shunt. DAC80501's ±1 LSB maximum INL corresponds to ±0.153 mV at a 10 V terminal span. These terms fit comfortably inside my calibrated targets, but do not include the complete protection, resistor, reference, drift, noise, and calibration budgets. I avoid counting total unadjusted error twice with its constituent errors. [ADS8684A](../references/datasheets/ADS8684A.pdf), [DAC80501](../references/datasheets/DAC80501.pdf)

I also distinguish credible zero-output headroom from a guaranteed temperature proof. LM7705 supplies at least the specified −209 mV negative bias at 5 V over its temperature table. OPA2197's quoted 125 mV maximum output headroom at a 10 kΩ load is a 25 °C row, and its guaranteed open-loop-gain test region does not reach my exact zero endpoint. I will verify zero, load, temperature, and startup on the assembled circuit; a unipolar DAC's positive zero-code offset cannot always be digitally nulled. [LM7705](../references/datasheets/LM7705.pdf), [OPAx197](../references/datasheets/OPA197.pdf)

My interface choices are established industrial conventions: positive DC inputs, 0–10 V, externally powered 4–20 mA, RS-485/Modbus RTU, CAN/CAN FD, dry contacts, and protected load switching. I use the Modbus Organization's current application V1.1b3 and serial implementation V1.02 guidance. I updated my land-pattern reference to IPC-7352; IPC lists IPC-7351 as no longer maintained. These references guide implementation and do not certify my board. [Modbus specifications](https://www.modbus.org/modbus-specifications), [IPC revision table](https://www.ipc.org/ipc-document-revision-table)

Before layout, I will close every exact pin/package choice, regulator support network and compensation, tolerance/error budget, rail monitor, hardware inhibit truth table, transient-energy path, and ERC result. Before fabrication, I will close DRC, isolation geometry, thermal/current-carrying design, manufacturability, and source/export consistency. After assembly, I will collect calibrated analog results, real-load and cable behavior, startup/miswire/fault recovery, communication, and repeatability evidence.

My architecture review establishes a feasible starting design with explicit margins and known remaining work. It does not establish automotive qualification, functional-safety certification, EMC compliance, or a guaranteed field rating. I keep the [validation matrix](Validation.md) tied to the actual revision I will build.
