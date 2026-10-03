# Design decisions

I use this document to explain the architecture choices that affect circuit behavior, fault handling, and the eventual measurements. I have selected an approach and candidate families; exact circuitry, schematic capture, layout, and prototype results are still pending. I distinguish a component capability from an assembled-board rating.

## Keep service power separate from field energy

I want USB access for configuration and diagnosis with the main supply disconnected. I therefore put only essential logic behind a field/USB service-power mux. I keep external ADC/DAC, analog auxiliary rails, relay coils, and isolated bus supplies on field power.

I selected TPS2121 as the source-selection candidate because reverse-current control matters when both supplies are connected. I also treat SPI, command signals, monitors, and readback as possible power paths. I will select buffers with verified powered-off behavior and check every signal crossing during source removal. A firmware flag can mark unavailable data, but it cannot stop current through an input protection diode. I require field/analog rail validity before accepting measurements or enabling AO.

I address external output backfeed separately. Each high-side channel gets a series diode so a positive source at DOx cannot ordinarily return energy through the switch body diode into VFIELD. I still need to qualify negative-terminal faults and all applicable diode stress. [TPS2121](../references/datasheets/TPS2121.pdf), [TPS4H160-Q1](../references/datasheets/TPS4H160-Q1.pdf)

## Separate operating voltage from fault survival

I specify 9–30 V continuous operation for nominal 12/24 V equipment. I treat −30 V reverse connection and +40 V input overvoltage as defined fault tests, with outputs disarmed outside the valid window.

I chose TPS26632 as an input-protection starting point, accounting for its fixed 35 V maximum output clamp and timeout. This variant does not have an adjustable overvoltage-cutoff pin. I will coordinate its external blocking FET, fast gate-discharge support, startup capacitance, fuse, and TVS against safe operating area and tolerance.

I use SMCJ33CA only as a provisional TVS class. Its 33 V stand-off number does not describe its pulse clamp voltage, and a wattage label does not establish immunity of the board. I will define waveform, source impedance, coupling, repetition, temperature, and pass criteria before final transient selection. I also keep returned inductive energy out of the main rail through the load-side freewheel path. [TPS2663](../references/datasheets/TPS2663.pdf), [reference revision status](../references/datasheets/README.md)

## Use a shared analog reference deliberately

I keep analog inputs/output, MCU, USB, and main DC return in one ground domain. This simplifies the single-ended ADC path and calibration, while making sensor-ground compatibility a stated interface requirement. I provide separate isolation for the digital-input group and each communication bus.

I do not treat the ADS8684A input-ground pins as floating negative inputs. I will use an external isolated transmitter where the sensor return potential is incompatible with MAIN_GND. I keep LOAD_RETURN and AI_RETURN physically arranged so actuator current does not flow through the local ADC reference connection. Separate terminal names describe current routing, not galvanic separation. [ADS8684A](../references/datasheets/ADS8684A.pdf)

## Protect current shunts before relying on ADC clamps

I chose 200 Ω shunts because 4–20 mA becomes a useful 0.8–4 V signal, with room for overrange on a 5.12 V ADC range. I accept the 4 V shunt burden at 20 mA and will include series/protector drops in the loop-compliance calculation. I use an external nominal 24 V loop for the demonstration.

I place active fault protection ahead of the shunt because a directly applied 24 V fault could dissipate 2.88 W in 200 Ω. I still need to calculate energy before the protector opens, secondary-clamp current, and resistor pulse limits. I separate voltage/AO and current channels into two protector groups because their normal voltage ranges need different shared thresholds.

I select high-impedance drain behavior on TMUX7462F. Its `DR` control selects drain response during a fault; it is not a commanded channel enable. I also require an ADC_AVDD discharge path that remains connected when the protector is alive and the ADC supply is absent. I start that review with a 10 kΩ bleeder against the ADC's specified low-impedance supply condition, then check complete sequencing and transient stress. [TMUX7462F](../references/datasheets/TMUX7462F.pdf), [ADS8684A](../references/datasheets/ADS8684A.pdf)

## Define AO as a sourced voltage command

I selected a voltage-source 0–10 V output for compatible high-impedance actuator inputs. I will verify the receiving device's electrical requirements rather than infer compatibility from a “0–10 V” label. Current-sinking lighting controls and 4–20 mA transmitters would require different interfaces.

I use the zero-scale POR DAC80501Z, an amplifier gain near four, and a small negative supply to give the zero-volt endpoint headroom. I add a separately controlled default-off disconnect because the fault protector does not supply that function. I will qualify disable leakage, startup, rail loss, cable capacitance, and output stability as well as steady accuracy.

I include resistance through the disconnect and protector in the terminal error budget. At 10 V into 10 kΩ, 1 mA flowing through 50 Ω loses 50 mV, already consuming the entire target allowance. I will resolve the signal path against that limit before freezing the circuit. I use protected amplifier-side readback before the disconnect; it cannot establish terminal voltage or external wiring continuity. Any future terminal feedback needs independent fault and unpowered-MCU protection. [DAC80501](../references/datasheets/DAC80501.pdf), [OPA197](../references/datasheets/OPA197.pdf)

## Accept diode losses and qualify diagnostics

I chose series blocking and freewheel diodes for the initial on/off load stage. At 0.5 A and an estimated 0.3–0.5 V drop, a blocking diode dissipates 0.15–0.25 W. The freewheel path gives slow inductive decay, so I will characterize release time for the selected load. Faster release or proportional PWM would require a revised energy/clamp design.

I expect the series diode to alter off-state/open-load diagnostics. I will use on-state current and the actual load to establish useful detection thresholds rather than assume the IC's unmodified diagnostic behavior survives the added diode. I also protect the MCU sense input from fault-level voltage and unpowered states.

I accept one multiplexed current-sense output for four channels. Firmware must select, settle, sample, and tag each reading; the result is sequential diagnostic telemetry rather than simultaneous precision measurement. Hardware current limiting acts immediately, while software latches a fault and requires explicit recovery. I will analyze short-circuit heating separately from normal conduction: a 24 V short near a 0.7 A limit can momentarily dissipate about 17 W in the switch. [TPS4H160-Q1](../references/datasheets/TPS4H160-Q1.pdf)

## Remove output permission independently of application software

I combine field validity, reset status, external watchdog status, and explicit arming in hardware. I gate the high-side command inputs, relay drivers, and AO disconnect; diagnostic enable is not an output-power inhibit. I require analog rail validity for AO as well.

I service the watchdog only after application health checks, so a stalled program cannot remain healthy through a free-running timer output. I clear arming on owner changes and global faults and require fresh commands after recovery. I define the relay's deenergized state electrically: COM–NO opens and COM–NC closes. Coil-command telemetry alone does not prove contact position. [TPS3431](../references/datasheets/TPS3431.pdf), [G5Q reference status](../references/datasheets/README.md)

## Preserve return paths across the four-layer layout

I chose four layers to make main-ground continuity, power distribution, and isolation boundaries explicit. I plan a main ground plane on the first inner layer, power/slow routing on the second, and controlled placement/routing on the outer layers. I will check the adjacent reference for each fast route; a bottom-layer signal does not automatically reference the first inner plane through an intervening power layer.

I keep switching loops compact and route high-current returns toward the input power path. I preserve local ADC return continuity and avoid a board-wide ground split through the shared analog domain. Isolation barriers instead receive copper keepouts on every layer. I will verify actual package geometry, clearances, thermal copper, and the fabricator's stack before release.

I connect these decisions to [Architecture](Architecture.md), [Interfaces](Interfaces.md), and [Validation](Validation.md). I will update each choice when calculations, schematic review, or measured results provide a reason to change it.
