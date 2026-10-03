# Design decisions

I use this document to explain the architecture choices that affect circuit behavior, fault handling, and the eventual measurements. I have selected an approach and candidate families; exact circuitry, schematic capture, layout, and prototype results are still pending. I distinguish a component capability from an assembled-board rating.

## Keep service power separate from field energy

I want USB access for configuration and diagnosis with the main supply disconnected. I therefore put only essential logic behind a field/USB service-power mux. I keep external ADC/DAC, analog auxiliary rails, relay coils, and isolated bus supplies on field power.

I selected TPS2121 as the source-selection candidate because reverse-current control matters when both supplies are connected. I also treat SPI, command signals, monitors, and readback as possible power paths. I will select buffers with verified powered-off behavior and check every signal crossing during source removal. A firmware flag can mark unavailable data, but it cannot stop current through an input protection diode. I require field/analog rail validity before accepting measurements or enabling AO.

I address external output backfeed separately. Each high-side channel gets a series diode so a positive source at DOx cannot ordinarily return energy through the switch body diode into VFIELD. I still need to qualify negative-terminal faults and all applicable diode stress. [TPS2121](../references/datasheets/TPS2121.pdf), [TPS4H160-Q1](../references/datasheets/TPS4H160-Q1.pdf)

## Separate operating voltage from fault survival

I specify 9–30 V continuous operation for nominal 12/24 V equipment. I treat −30 V reverse connection and an initial +36 V positive fault at 25 °C as defined fault tests, with outputs disarmed outside the valid window.

I chose TPS26632 as an input-protection starting point, accounting for its fixed 35 V maximum output clamp and timeout. This variant does not have an adjustable overvoltage-cutoff pin. I will coordinate its external blocking FET, fast gate-discharge support, startup capacitance, fuse, and TVS against safe operating area and tolerance.

I use SMCJ33CA as a provisional TVS and limit the initial positive DC fault to 36 V at 25 °C with a defined source and duration. A 40 V sustained source can heat this TVS independently of eFuse shutdown. I also calculate negative differential stress with charged output capacitance; the eFuse's −85 V/10 ms condition cannot be inferred from a 100 V FET alone. Its 33 V stand-off number does not describe its pulse clamp voltage, and a wattage label does not establish immunity of the board. I will define waveform, source impedance, coupling, repetition, temperature, and pass criteria before final transient selection. I also keep returned inductive energy out of the main rail through the load-side freewheel path. [TPS2663](../references/datasheets/TPS2663.pdf), [reference revision status](../references/datasheets/README.md)

## Use a shared analog reference deliberately

I keep analog inputs/output, MCU, USB, and main DC return in one ground domain. This simplifies the single-ended ADC path and calibration, while making sensor-ground compatibility a stated interface requirement. I provide separate isolation for the digital-input group and each communication bus.

I do not treat the ADS8684A input-ground pins as floating negative inputs. I will use an external isolated transmitter where the sensor return potential is incompatible with MAIN_GND. I keep LOAD_RETURN and AI_RETURN physically arranged so actuator current does not flow through the local ADC reference connection. Separate terminal names describe current routing, not galvanic separation. [ADS8684A](../references/datasheets/ADS8684A.pdf)

## Preserve current-loop loading through protection

I chose 200 Ω shunts because 4–20 mA becomes 0.8–4 V. Each terminal passes through a TPS26611DDFR to a permanently connected shunt. I put TMUX7462F only in the high-impedance measurement branch. This avoids letting an open fault switch drive an external current source to its compliance voltage and prevent normal recovery. I use an external nominal 24 V loop for the demonstration.

The TPS26611 limit is 25–40 mA, not a guaranteed 30 mA. I rate the precision shunt at least 1 W against 0.32 W at 40 mA and separately verify fast-trip pulse energy. The protector adds up to 0.25 V at 20 mA, making the receiver burden 4.25 V before wiring. I qualify up to 24 mA overrange; the ADC endpoint corresponds arithmetically to 25.6 mA but the series protector can limit sooner. EN defaults low through an external pulldown; qualified field/analog power enables measurement without requiring actuator arming. I will define explicit negative-fault recovery and safely interface any status outputs. [TPS2661](../references/datasheets/TPS2661.pdf)

I select high-impedance drain response on the TMUX sense branches. Its DR pin selects fault response, not channel enable. I keep separate voltage and current threshold groups, and include the ADC's 2.5 V-biased effective input loading in calibration. ADC_AVDD has a permanent starting 10 kΩ bleeder to meet its powered-off low-impedance supply condition; I still check complete sequencing and transient stress. [TMUX7462F](../references/datasheets/TMUX7462F.pdf), [ADS8684A](../references/datasheets/ADS8684A.pdf)

## Control and sense the actual voltage-command terminal

I selected a sourced 0–10 V output for compatible high-impedance actuator inputs. I verify the receiving device's electrical requirements; current-sinking lighting controls and current transmitters require different interfaces.

I use DAC80501Z followed by OPA2197IDR: one local gain-four stage and one unity driver. ADG5401F switches the output and a separate protected terminal-feedback path. Its powered disabled/fault state opens both field paths and reconnects local driver feedback. I hold enable low through initialization and use qualified analog power plus hardware output permission to enable it.

I keep the switch's secondary feedback resistance out of the gain-setting divider. At 10 V into 10 kΩ, uncompensated 50 Ω series resistance loses the entire 50 mV allowance. The unity driver's terminal feedback instead compensates the main-switch and reviewed series-impedance drop; the remaining error budget includes DAC/reference error, gain ratio, amplifier offsets, drift, and feedback leakage. I use +15 V/GND for the switch and +15 V/LM7705 bias for both amplifiers. My ideal DC model demonstrates the feedback principle, while actual amplifier compensation and cable capacitance remain to be validated.

I ground POC for the switch's weak powered disabled pulldown and add a permanent 100 kΩ terminal pulldown. Independently protected terminal readback has its own attenuation and unpowered-MCU isolation. The switch's internal feedback node cannot prove the terminal value when disabled or faulted. [DAC80501](../references/datasheets/DAC80501.pdf), [OPAx197](../references/datasheets/OPA197.pdf), [ADG5401F](https://www.analog.com/media/en/technical-documentation/data-sheets/adg5401f.pdf), [Engineering review](Engineering_Review.md)

## Accept diode losses and qualify diagnostics

I chose series blocking and freewheel diodes for the initial on/off load stage. I selected STPS2H100A as the starting diode. Its manufacturer 125 °C conduction-loss model gives about 0.291 W/channel at 0.5 A; this is a model, not a guaranteed maximum over production and temperature. I still close the complete loss and leakage budget. The freewheel path gives slow inductive decay, so I will characterize release time for the selected load. Faster release or proportional PWM would require a revised energy/clamp design.

I expect the series diode to alter off-state/open-load diagnostics. I will use on-state current and the actual load to establish useful detection thresholds rather than assume the IC's unmodified diagnostic behavior survives the added diode. I also protect the MCU sense input from fault-level voltage and unpowered states.

I accept one multiplexed current-sense output for four channels. Firmware must select, settle, sample, and tag each reading; the result is sequential diagnostic telemetry rather than simultaneous precision measurement. Hardware current limiting acts immediately, while software latches a fault and requires explicit recovery. I will analyze short-circuit heating separately from normal conduction: a 24 V short near a 0.7 A limit can momentarily dissipate about 17 W in the switch. [TPS4H160-Q1](../references/datasheets/TPS4H160-Q1.pdf)

## Remove output permission independently of application software

I combine field validity, reset status, external watchdog status, and an asynchronously cleared ARM latch in hardware. A stale GPIO cannot restore permission when field power returns; a fresh valid arm transition is required. I gate the high-side command inputs, relay drivers, and AO disconnect; diagnostic enable is not an output-power inhibit. I require analog rail validity for AO as well.

I service the watchdog only after application health checks, so a stalled program cannot remain healthy through a free-running timer output. I clear arming on owner changes and global faults and require fresh commands after recovery. I define the relay's deenergized state electrically: COM–NO opens and COM–NC closes. Coil-command telemetry alone does not prove contact position. [TPS3431](../references/datasheets/TPS3431.pdf), [G5Q reference status](../references/datasheets/README.md)

## Preserve return paths across the four-layer layout

I chose four layers to make main-ground continuity, power distribution, and isolation boundaries explicit. I plan a main ground plane on the first inner layer, power/slow routing on the second, and controlled placement/routing on the outer layers. I will check the adjacent reference for each fast route; a bottom-layer signal does not automatically reference the first inner plane through an intervening power layer.

I keep switching loops compact and route high-current returns toward the input power path. I preserve local ADC return continuity and avoid a board-wide ground split through the shared analog domain. Isolation barriers instead receive copper keepouts on every layer. I will verify actual package geometry, clearances, thermal copper, and the fabricator's stack before release.

I connect these decisions to [Architecture](Architecture.md), [Interfaces](Interfaces.md), and [Validation](Validation.md). I will update each choice when calculations, schematic review, or measured results provide a reason to change it.
