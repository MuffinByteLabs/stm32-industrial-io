# Schematic capture checklist

I use this checklist to turn the reviewed architecture into a schematic. The allocations and starting networks below are design inputs. I have not captured or tested the complete board, and I will freeze component values only after pin, timing, tolerance, sequencing, and fault reviews. My [architecture](Architecture.md), [interface contract](Interfaces.md), and [validation plan](Validation.md) define the resulting behavior.

## MCU allocation and clock

I select STM32G474VET6 in LQFP100. This provisional allocation reserves USB and debug before assigning the acquisition and communication peripherals. The package numbers come from DS12288 Table 12; I will check them against the actual KiCad symbol and STM32CubeMX project before connecting nets.

| Function | MCU signal | LQFP100 pin | Selection |
| --- | --- | --- | --- |
| USB D− / D+ | PA11 / PA12 | 72 / 73 | USB peripheral |
| SWDIO / SWCLK / SWO | PA13 / PA14 / PB3 | 76 / 77 / 90 | Debug; retain throughout bring-up |
| HSE crystal | PF0 / PF1 | 12 / 13 | OSC_IN / OSC_OUT |
| Reset | PG10–NRST | 14 | Preserve reset function in option bytes |
| Boot strap | PB8–BOOT0 | 95 | Reserve; document boot option bytes |
| SPI clock / receive / transmit | PA5 / PA6 / PA7 | 27 / 28 / 29 | SPI1, AF5 |
| External ADC / DAC chip selects | PE2 / PE3 | 1 / 2 | GPIO; default high at receiving devices |
| RS-485 TX / RX / DE | PD5 / PD6 / PD4 | 87 / 88 / 86 | USART2, AF7 |
| CAN RX / TX | PD0 / PD1 | 82 / 83 | FDCAN1, AF9 |
| EEPROM clock / data | PC8 / PC9 | 67 / 68 | I2C3, AF8 |
| Fast DI1 | PA0 | 20 | TIM2_CH1, AF1; counter/capture |
| DI2–DI4 | PC0 / PC1 / PC2 | 15 / 16 / 17 | GPIO inputs |
| AO readback / high-side current sense | PB0 / PB1 | 32 / 33 | ADC1_IN15 / ADC1_IN12 |
| ARM clock / software disarm / AO command | PE4 / PE5 / PE6 | 3 / 4 / 5 | GPIO with explicit external defaults |
| DO1–DO4 commands | PE7–PE10 | 38–41 | GPIO through hardware permission gates |
| Relay commands | PE11 / PE12 | 42 / 43 | GPIO through hardware permission gates |

I allocate remaining GPIOs for watchdog service, diagnostic selection, protection flags, rail health, buffer enables, and LEDs after the full net list is available. I keep PC13–PC15 away from load-driving duties. PB6 is not I2C1_SCL on this MCU; this allocation uses PC8/PC9 and avoids the shared PB8 boot function. [STM32G474 datasheet](https://www.st.com/resource/en/datasheet/stm32g474ve.pdf)

I start with an 8 MHz HSE: PLLM = 2, PLLN = 72, PLLR = 2 produces a 144 MHz core, and PLLQ = 6 produces the 48 MHz USB/FDCAN clock. I will check the voltage scale, flash wait states, bus clocks, and peripheral clock selections in the generated configuration. A 170 MHz core does not produce 48 MHz from the same 340 MHz VCO and integer Q divider. HSI48 with CRS is an alternative requiring a separate clock-accuracy review. [RM0440](https://www.st.com/resource/en/reference_manual/rm0440-stm32g4-series-advanced-armbased-32bit-mcus-stmicroelectronics.pdf)

I connect every VDD/VSS pair, VDDA/VSSA, VREF+, and VBAT according to the package requirements; place local bypass capacitors and bulk storage; and preserve an accessible reset/SWD path. I size crystal load capacitors from the selected crystal and measured/estimated stray capacitance. USB VBUS detection receives its own protected sensing circuit, and I verify USB-C sink resistors, ESD protection, routing, and behavior with the MCU unpowered. SWD is my initial programming method; ROM USB DFU requires a separate AN2606 and option-byte check.

## Reset, watchdog, and output permission

I use TPS3808G33DBVR on service 3.3 V. Its nominal threshold is 3.07 V, with an open-drain RESET output and an external pullup of at least 10 kΩ. CT open gives a nominal 20 ms release delay, with a 12–28 ms specified range. I connect this reset to NRST and derive RESET_OK through a reviewed logic path. The device does not replace MCU brownout configuration or the field rail monitors. [TPS3808](https://www.ti.com/lit/gpn/tps3808)

I use SN74LVC1G74DCUR as the ARM memory, powered from service 3.3 V so it remains alive during USB service. D and inactive PRE are high; CLR is asynchronously driven low by reset, watchdog failure, invalid field/analog power, or software disarm. CLK has an external pulldown and receives a fresh firmware arm pulse only after initialization. Q cannot become high merely because power health returns. I verify CLR release, CLK setup/hold, pulse width, and reset recovery in the implemented circuit. [SN74LVC1G74](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf)

I condition slow open-drain health signals with SN74LVC2G17DBVR Schmitt buffers, then combine permission with SN74LVC2G08DCUR gates. The final command gates are powered in the receiving field logic domain and have external output pulldowns. High-side IN pins, relay drivers, and ADG5401F IN receive the gated commands. I use the external TPS3431 watchdog output in the asynchronous clear path and feed its WDI only after application health checks. I do not use the high-side diagnostic enable as a power inhibit. [Schmitt buffer](https://www.ti.com/lit/ds/symlink/sn74lvc2g17.pdf), [AND gates](https://www.ti.com/lit/ds/symlink/sn74lvc2g08.pdf), [TPS3431](https://www.ti.com/lit/ds/symlink/tps3431.pdf)

I keep field health separate from MCU NRST so USB-only diagnostics can run. Every loss of field or analog health clears ARM; recovery requires a fresh arm transition and fresh output commands. Acquisition protection may be enabled by qualified analog power while actuator ARM remains clear.

## Rail-health implementation

I power the monitors from service 3.3 V. Their low-active outputs receive service-domain pullups and Schmitt conditioning before the latch-clear/gate network. The analog-valid combination also includes field-derived 3.3 V logic validity. These monitors qualify operation; their response delays do not substitute for surge clamps or protection ICs.

| Monitored node | Starting implementation | Nominal behavior |
| --- | --- | --- |
| VFIELD | TPS3700DDCR; independent upper/lower dividers, each with 10 kΩ bottom resistor | UV branch 210 kΩ top: release 8.80 V, assert about 8.68 V; OV branch 770 kΩ top: assert 31.20 V, release about 30.77 V |
| ADC_AVDD | TPS3702CX50DDCR, SENSE directly on ADC 5 V, SET tied high | UV assert 4.80 V; OV assert 5.20 V; fixed window, no divider |
| +15 V analog | TPS3700DDCR; 10 kΩ bottom resistors | UV top 320 kΩ: release 13.20 V, assert about 13.02 V; OV top 400 kΩ: assert 16.40 V |
| Negative analog bias | TPS3700DDCR plus REF3325AIDBZR; reference branch described below | Negative-bias loss asserts at about −0.170 V; recovery at about −0.177 V |
| Field-derived 3.3 V logic | Separate TPS3808G33DBVR | Receiving logic must be valid before buffer enables or acquisition are asserted |

For TPS3700, I use INA for undervoltage and INB for overvoltage and join the two open-drain health outputs only after confirming polarity. I begin with 0.1% divider resistors. Its reference threshold accuracy and up-to-12 mV hysteresis require a full bound calculation. VFIELD's thresholds provide starting guard bands around the 9–30 V qualification range; I will publish measured/tolerance-bounded FIELD_VALID trip and release limits. Exact 9.000/30.000 V cutoff claims are incompatible with these tolerances and hysteresis. [TPS3700](https://www.ti.com/lit/ds/symlink/tps3700.pdf)

The ADC monitor's ±0.9% accuracy gives conservative 4.755–5.245 V trip extremes around its nominal ±4% window. Its hysteresis is 0.3–0.8%, allowing recovery around nominal 5 V. I check regulator tolerance, ripple, monitor delay, and ADC sampling validity together; I do not substitute a 4.65 V supervisor for a 4.75 V ADC operating limit. [TPS3702](https://www.ti.com/lit/ds/symlink/tps3702.pdf)

For negative bias, I connect INB between 68.1 kΩ to the service-powered 2.5 V REF3325 output and 18.5 kΩ to VNEG. The node voltage is `(18.5 × VREF + 68.1 × VNEG) / 86.6`. A second comparator verifies the reference using a 50 kΩ/10 kΩ divider, releasing around 2.4 V, so an absent reference cannot falsely qualify VNEG. I add a VNEG discharge resistor and bound monitor error, reference error/drift, resistor tolerance, leakage, and startup. I require the resulting worst-case loss threshold to remain below −0.15 V and normal LM7705 bias to clear it. The REF3325 receives 1 µF input/output capacitors, within its specified stability range. [REF33](https://www.ti.com/lit/gpn/REF33), [LM7705](https://www.ti.com/lit/ds/symlink/lm7705.pdf)

## Prevent powered-off backfeed

I use SN74LVC2G125DCUR receiving-domain buffers for digital signals crossing between service and field logic. Each buffer runs at the receiving 3.3 V supply, has OE default high, and gives its destination an external safe pull resistor. I buffer SPI clock, MOSI, chip selects, and returning SDO/status as required by direction and sequencing. I qualify OE through hardware rail validity and reset, then enable communication in firmware. I review every remaining crossing, including output commands and diagnostic selection. Ioff is finite leakage, not a guarantee of zero current. [SN74LVC2G125](https://www.ti.com/lit/ds/symlink/sn74lvc2g125.pdf)

I select TMUX1511PWR for receiving-ADC-domain analog isolation on independent AO terminal readback and shared TPS4H160 current sense. It is powered from MCU/ADC 3.3 V; SEL defaults low and is qualified by reset plus receiving/field domain validity. Its powered-off input protection is limited to 0–3.6 V, so attenuation and independent secondary clamps precede it. I do not clamp an upstream field node directly into an absent MCU rail. [TMUX1511](https://www.ti.com/lit/ds/symlink/tmux1511.pdf)

The AO readback starting path is terminal → spare TMUX7462F protected S → D → 200 kΩ/68 kΩ divider → independently referenced secondary clamps → TMUX1511 → MCU ADC, with a 47 kΩ ADC pulldown. This pulldown loads the divider: nominal attenuation is about 0.122, giving about 1.22 V at a 10 V terminal. I include switch/clamp leakage, ADC acquisition settling, capacitor loading, and the powered-off TMUX1511 leakage bound: 2 µA through 47 kΩ is 94 mV. Faulted/off readback is marked invalid rather than interpreted as terminal zero. Clamp values and their unpowered discharge path still need capture-level analysis. [TMUX7462F](https://www.ti.com/lit/ds/symlink/tmux7462f.pdf)

For high-side current sense, I attenuate the possible 6.5 V CS fault state below 3.6 V ahead of the isolator, including the effective CS resistor and ADC pulldown in the transfer ratio. I then check normal-current resolution, switching/selection settling, clamp current, and USB-only behavior.

## Analog capture and timing checks

I keep each TPS26611DDFR before its permanent 200 Ω shunt, with TMUX7462F only in the high-impedance ADC sense branch. The TMUX S pin faces the fault-exposed node; D faces the ADC. DR selects the drain fault response and is configured for high impedance. EN on TPS26611 has an external pulldown despite its internal pullup. I check supply/threshold sequencing, loop burden, negative-fault recovery, and 1 W precision-shunt pulse derating. [TPS2661](https://www.ti.com/lit/ds/symlink/tps2661.pdf)

I configure ADS8684A voltage channels for 0–10.24 V and current channels for 0–5.12 V. The 1 kSPS/channel target is 4 kSPS aggregate. At the starting 1.125 MHz SPI clock, four 32-bit frames per millisecond use about 11.4% of the bus before command overhead. I verify SPI edge mode and complete frame/CS timing for both devices. I allow reference startup time, fit reference capacitors, include the ADC's 2.5 V-biased input loading in calibration, and fit the starting 10 kΩ AVDD bleeder before evaluating powered-off protection. [ADS8684A](https://www.ti.com/lit/ds/symlink/ads8684a.pdf)

My AO path is DAC80501Z → OPA2197 A gain four → OPA2197 B unity driver → ADG5401F D/S → terminal. SFB/DFB returns terminal feedback directly to the unity driver's minus input. The switch's secondary resistance stays outside the gain divider. Powered OFF/fault restores local D–DFB feedback; POC is grounded and a permanent 100 kΩ terminal pulldown remains. I use +15 V/GND on the switch and +15 V/LM7705 bias on both amplifiers. Compensation, cable capacitance, transient clamps, short heating, and zero-command behavior require simulation and measurements before value freeze. [OPAx197](https://www.ti.com/lit/ds/symlink/opa197.pdf), [ADG5401F](https://www.analog.com/media/en/technical-documentation/data-sheets/adg5401f.pdf), [manufacturer application](https://www.analog.com/en/resources/design-notes/precision-solutions-with-protection-and-robustness.html)

I retain DI1's 20 kHz target, corresponding to 25 µs high and low at 50% duty. ISO1212 propagation and minimum pulse specifications make the IC compatible, while the actual filter, sensor waveform, and cable still need qualification. I use timer counting/capture instead of slow-channel debounce. ISO1410's 500 kbit/s capability accommodates 115.2 kbit/s Modbus, and ISO1042's 5 Mbit/s capability accommodates the 2 Mbit/s CAN FD target. I qualify the complete isolated supplies, termination, wiring, and timing. [ISO1212](https://www.ti.com/lit/ds/symlink/iso1212.pdf), [ISO1410](https://www.ti.com/lit/ds/symlink/iso1410.pdf), [ISO1042](https://www.ti.com/lit/ds/symlink/iso1042.pdf)

## Firmware and release checks

I record silicon REV_ID and review ES0430 against the selected startup code and drivers. I discard the first internal ADC conversion after the specified long-idle/calibration condition, disable FDCAN edge filtering where affected, review transmit-buffer ordering, and use bounded SPI timeouts. USB remote-wakeup and flash/cache limitations are checked if those features are enabled. [STM32G474 errata](https://www.st.com/resource/en/errata_sheet/es0430-stm32g471xx473xx474xx483xx484xx-device-errata-stmicroelectronics.pdf)

Before layout, I require a reviewed CubeMX allocation/clock file, exact symbols and footprints, rail/logic truth tables, worst-case threshold calculations, ADC/AO error budgets, and power-off injection analysis. Before manufacture, I require completed schematic/ERC and PCB/DRC reviews, regulator and protection calculations, AO stability evidence, fabrication outputs tied to a revision, and the [validation plan](Validation.md). I will replace assumptions with measured evidence as bring-up proceeds.
