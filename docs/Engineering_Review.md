# Pre-schematic engineering review

I reviewed component lifecycle and core electrical selections on October 3, 2026 and revised the scope/PWM checks on October 4, 2026 against manufacturer product status, electrical tables, interface requirements, power arithmetic, and a provisional MCU resource allocation. My corrected architecture is specified for capture; [preparation status](Schematic_Capture.md#preparation-status) identifies the capacitor-evidence and library gates still open before full freeze. I have not yet approved a completed circuit, PCB, production BOM, or assembled-board rating.

I separate three kinds of evidence: manufacturer-specified device capabilities, my calculations and design assumptions, and measurements still to be collected. I cannot run ERC, DRC, extracted-layout analysis, or whole-board simulation before the native design exists. My [capture checklist](Schematic_Capture.md) and [qualification plan](Validation.md) define the next gates.

My October 6 [external-review verification](External_Review_Verification.md) is the latest review. It corrects the buffer output map, fitted power connector, reset supervisor/oscillator and digital-regulator package, adopts conditional PGOOD sequencing and records current sourcing and rejected redesign assumptions. The October 4 [deep pre-schematic verification](Pre_Schematic_Review.md) records the earlier corrections and remaining capacitor/sequence/library gates. Historical codes below describe their dated baseline; current selections and the latest record govern capture.

## Component lifecycle and selection

I checked the following manufacturer pages on October 3, 2026. The semiconductor families below are Active, In Production, or Recommended for New Designs. An older publication date alone does not make a supported component obsolete. Lifecycle status also does not guarantee distributor inventory or future availability; I will check exact ordering codes and stock when I freeze the assembly BOM.

| Circuit | Selected family or exact candidate | Manufacturer evidence |
| --- | --- | --- |
| MCU | STM32G474VET6, LQFP100 | [ST: Active](https://www.st.com/en/microcontrollers-microprocessors/stm32g474ve.html) |
| Main input eFuse | TPS26632RGER | [TI: Active](https://www.ti.com/product/TPS2663/part-details/TPS26632RGER) |
| Field buck | LMR38020 | [TI: Active](https://www.ti.com/product/LMR38020) |
| Logic buck / MCU analog LDO | TPS62160 / TPS709 | [TPS62160](https://www.ti.com/product/TPS62160), [TPS709](https://www.ti.com/product/TPS709) |
| Positive analog auxiliary | TPS61040 / TPS7A16 | [TPS61040](https://www.ti.com/product/TPS61040), [TPS7A16](https://www.ti.com/product/TPS7A16) |
| Group-isolated digital inputs | Two ISO1212 | [TI: Active](https://www.ti.com/product/ISO1212) |
| Four-channel 16-bit acquisition | ADS8684A | [TI: Active](https://www.ti.com/product/ADS8684A) |
| Analog sense protection | TMUX7462F | [TI: Active](https://www.ti.com/product/TMUX7462F) |
| Current-loop series protection | Two TPS26611DDFR, 8-pin DDF | [TI: Active](https://www.ti.com/product/TPS2661/part-details/TPS26611DDFR) |
| Four diagnosed high-side outputs | TPS4H160BQPWPRQ1 | [TI: Active](https://www.ti.com/product/TPS4H160-Q1/part-details/TPS4H160BQPWPRQ1) |
| Isolated bus transceivers | ISO1410 / ISO1042 | [ISO1410](https://www.ti.com/product/ISO1410), [ISO1042](https://www.ti.com/product/ISO1042) |
| Independent isolated port power | Two UCC33421QDHARQ1 | [TI: Active, production](https://www.ti.com/product/UCC33421-Q1/part-details/UCC33421QDHARQ1) |
| External watchdog | TPS3431 | [TI: Active](https://www.ti.com/product/TPS3431) |
| MCU reset / hardware ARM memory | TPS3808G30DBVR / SN74LVC1G74DCUR, reset selection corrected October 6 | [TPS3808](https://www.ti.com/product/TPS3808/part-details/TPS3808G30DBVR), [SN74LVC1G74](https://www.ti.com/product/SN74LVC1G74/part-details/SN74LVC1G74DCUR) |
| Permission gates / powered-off buffers | SN74LVC2G08DCUR / SN74LVC2G125DCUR | [SN74LVC2G08](https://www.ti.com/product/SN74LVC2G08/part-details/SN74LVC2G08DCUR), [SN74LVC2G125](https://www.ti.com/product/SN74LVC2G125/part-details/SN74LVC2G125DCUR) |
| MCU diagnostic analog isolation | TMUX1511PWR, 14-pin TSSOP | [TI: Active](https://www.ti.com/product/TMUX1511/part-details/TMUX1511PWR) |
| Rail windows / ADC rail window | TPS3700DDCR / TPS3702CX50DDCR | [TPS3700](https://www.ti.com/product/TPS3700/part-details/TPS3700DDCR), [TPS3702](https://www.ti.com/product/TPS3702/part-details/TPS3702CX50DDCR) |
| Health conditioning | SN74LVC2G17DBVR | [SN74LVC2G17](https://www.ti.com/product/SN74LVC2G17/part-details/SN74LVC2G17DBVR) |
| Calibration/configuration storage | 24LC64 | [Microchip: In Production](https://www.microchip.com/en-us/product/24lc64) |
| SPDT relay | G5Q-1 DC5 | [Aratas: In Production](https://www.aratas.com/us-en/products/relays/G5Q) |

I retain SMCJ33CA as a provisional input TVS. Littelfuse lists it in its [current SMCJ datasheet](https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_smcj_datasheet.pdf?assetguid=37388813-0d6d-4329-969b-1aa8b7614ac1); I did not obtain an explicit lifecycle badge for that exact diode. I do not equate a catalog listing with a complete surge-design approval. My support candidates include CSD19537Q3, BSS138P,215 and STPS2H100A; I will check their operating point, temperature, pulse energy, and package against the captured circuit.

I retain proven production families where they meet the requirement. I replaced UCC12050 because its capacity did not close my bus-side load budget, rather than because that family is obsolete. I have now selected voltage/frequency suffixes, packages, connector pairs, support passives and a CMOS clock in the detailed [capture package](Schematic_Capture.md). Missing local CAD assets and capacitor DC-bias confirmation remain preparation gates; captured connectivity and measured qualification follow implementation.

## Corrections I made before capture

### Current-loop startup and protection

I replaced the earlier arrangement that put a TMUX fault switch ahead of the 200 Ω shunt. An open switch lets an external current source rise toward its compliance voltage; that voltage can keep the switch faulted even after board power returns.

My revised current path is **terminal → TPS26611 → permanent 200 Ω Kelvin shunt → MAIN_GND**. Only the high-impedance shunt-sense branch passes through TMUX7462F to the ADC. The TPS26611 monitors its load-side overvoltage, supplies current limiting, and remains default off through an external EN pulldown until field/analog power is qualified. It does not require the actuator ARM state to acquire inputs. I will implement explicit recovery where a negative fault latches the protector.

The TPS26611 limit is 25–40 mA, 32 mA typical. At its 40 mA upper bound, the shunt dissipates 0.32 W. I specify a precision shunt rated at least 1 W, then separately review fast-trip pulse energy and enclosure derating. At 20 mA, a 12.5 Ω maximum protector resistance adds 0.25 V to the shunt's 4 V burden. I therefore use **4.25 V plus wiring** in the loop-compliance budget. I qualify a 24 mA overrange target; the ADC's arithmetic 25.6 mA endpoint is not a guaranteed receiver operating limit. [TPS2661 datasheet](../references/datasheets/TPS2661.pdf)

The ADC input is biased toward 2.5 V through its effective input resistance; I include that loading in calibration. At an illustrative 1 MΩ ADC resistance, the selected 200 Ω shunt plus 1008.3 Ω sense path gives about +10.258 µA at 4 mA and −9.051 µA at 20 mA before calibration. These are loading examples, not guaranteed converter errors. The selected voltage path has 1108.3 Ω illustrative total resistance; at 10 V and the ADC's 0.85 MΩ minimum equivalent resistance it gives about −9.766 mV of loading error. I will define permitted source impedance and include protection resistance in the ±20 mV budget. [ADS8684A datasheet](../references/datasheets/ADS8684A.pdf)

### Port power and service budget

The ISO1410 bus side can require 160 mA at 5 V under the specified 54 Ω, 500 kbit/s test condition. A nominal 500 mW UCC12050 does not supply that worst-case load. I selected a separate **UCC33421QDHARQ1** for each bus; its nominal 5 V/300 mA output has suitable capacity for the planned transceiver load. I still need to close conversion loss, bias current, cable loading, startup, and thermal limits. [ISO1410](../references/datasheets/ISO1410.pdf), [UCC33421-Q1](../references/datasheets/UCC33421-Q1.pdf)

I increased the service-electronics allocation to **6 W delivered from the field buck**, while retaining four 0.5 A load outputs and a 3 A continuous input target. My [calculation](calcs/controller_budget.py) keeps named branch reservations and labels efficiency as an assumption. At 9 V and 85% field-buck efficiency, the estimate is 2.784 A before protection losses and small additional input currents. This is a useful margin for capture, not a demonstrated thermal or inrush pass.

### Low-line power and rail-health margin

FIELD_OK measures VFIELD after input protection. I use 180 kΩ+10 kΩ over 10 kΩ for its UV network: nominal 8.0 V release, with calculated release corners 7.89084–8.10975 V and falling corners 7.71140–8.02950 V. I require VFIELD ≥8.4 V at the 9 V connector/combined-load fixture, leaving at least 0.290 V release and 0.370 V falling margin. At assumed 80% main-buck efficiency, the full load/service budget plus nominal bleeders and 20 mA operating reserve is approximately 2.916 A before remaining effects. Hot/tolerance input-path drop and real consumption remain explicit qualification gates.

### PWM timing and diagnostics

I add DO3 PWM through TPS4H160B using PE9 / TIM1_CH1 / AF2, verified against STM32G474 DS12288 Rev6. TPS4H160B's switching/current-sense tables and TI's [PWM application guidance](../references/reference-designs/README.md) support evaluating this mode. I use 100 Hz and 10–90% commanded duty plus static endpoints as an initial qualification target for resistive or compatible LED loads up to 0.5 A.

I calculate finite edge/settling windows and switching heat in [pwm_checks.py](calcs/pwm_checks.py). Published timing is measured under manufacturer-specific conditions; the selected 9–30 V supply, 3.3 V command and approximately 0.7 A current limit require prototype verification. I make no precise duty-to-power, motor or proportional-solenoid claim.

I retain the protected OPA2320/TMUX1511 receiving path for multiplexed current diagnostics. I sample PWM during a settled on-window and mark unavailable windows invalid. On-state current and duty are separate observations. Current limiting and hardware permission remain independent of sampling success.

### MCU pins, clocks, and reset behavior

I found a conflict-free provisional resource allocation in the G474 datasheet. I reserve PB8 for BOOT0, keep PG10 as NRST, use PD0/PD1 for FDCAN1, PD4–PD6 for USART2/RS-485, PC8/PC9 for I2C3, and PA5–PA7 for shared SPI1. USB, SWD, the external CMOS clock, and DI1 timer acquisition have separate pins. I use an 8 MHz HSE bypass selection with a 144 MHz system clock and exact 48 MHz USB clock; maximum 170 MHz operation is optional and needs a different USB clock strategy. My [capture checklist](Schematic_Capture.md) records the full allocation and relevant errata.

I add a hardware ARM latch with asynchronous clearing. Holding a GPIO high must not reenable outputs when field power returns. The October 6 correction selects TPS3808G30 with a 2.79 V nominal falling threshold and a conservatively screened 2.903 V maximum release. The former G33 has a 3.07 V nominal falling threshold; it was not a 2.93 V device and its maximum release conflicted with the digital-rail lower bound. I select partial-power-down buffers at MCU/field crossings and monitor actual analog rail windows before declaring acquisition and current diagnostics valid.

### Input-fault claims and surge coordination

I removed the unqualified +40 V main-input test. SMCJ33CA has a 36.7–40.6 V breakdown range at 25 °C, so a sustained 40 V source can heat the raw TVS even if the eFuse disconnects. My initial positive DC fault target is **36 V at 25 °C**, with defined source limit, duration, actual terminal voltage, and TVS temperature/current monitoring. I will set other temperatures and waveforms from a completed protection analysis.

I also review the eFuse's negative differential stress with output capacitance still charged. A −53.3 V catalog TVS clamp combined with +30 V retained output is already 83.3 V across the relevant path, close to the stated −85 V/10 ms condition; a +35 V retained output would exceed it. Component voltage labels alone do not establish bipolar surge survival. [TPS2663 datasheet](../references/datasheets/TPS2663.pdf)

## Revised scope and remaining gates

I froze major functions after the October 4 portfolio comparison and added the [scope baseline](Scope.md), [implementation milestones](Implementation_Plan.md) and [architecture review record](Architecture_Review.md). I subsequently chose to retain the entire current board and recorded that disposition. The current exact circuit/component selections remain the electrical baseline; their capacitor, package, sequence and physical-test requirements are still open. The nominal-supply Modbus milestone, classic CAN, bounded PWM and full qualification have separate completion evidence.

I power every board rail from the protected external supply and retain USB as a self-powered data interface. I removed the analog voltage-command circuit, its negative bias/reference monitoring and USB power-transfer circuitry from the active component selections, calculations and references. The +15 V and threshold supplies remain essential to input protection. Both isolated buses, power supervision, calibration, relays and load diagnostics remain in Rev A.

I check accuracy separately from ADC resolution. ADS8684A's maximum ±2 LSB INL corresponds to ±0.3125 mV on the voltage range and ±0.78125 µA through the 200 Ω shunt. Protection/loading, reference, drift, noise and calibration uncertainty still need a complete error budget. My [analog calculations](calcs/analog_checks.py) and ideal DC simulation cover only their stated assumptions.

I use positive DC inputs, voltage/current sensor interfaces, Modbus RTU, CAN/CAN FD, dry contacts and protected load switching. My [standards references](../references/standards/README.md) guide implementation; they do not certify the board.

I can begin schematic hierarchy and package preparation from the revised [capture package](Schematic_Capture.md). Effective capacitor evidence and missing local CAD assets remain preparation gates. Before layout I close captured pins/networks, rail sequencing, permission/default truth tables, transient paths and ERC. Before fabrication I close DRC, isolation geometry, thermal/current-carrying design and manufacturing exports. Measurements then establish accuracy, PWM behavior, real-load/fault response, communication and repeatability.

I have no native schematic or PCB to review yet. My document, part-index, arithmetic and bounded simulation checks are not a whole-board verification. I tie every release claim to [recorded qualification](Validation.md) on the actual revision.
