# STM32 Industrial I/O Controller Rev A — Resource Reservations

Status: provisional allocation before schematic capture. No final MCU port names, package pin numbers, connector pin order, component designators, or numbered test points are assigned here.

Use [the canonical plan](STM32_Industrial_IO_Controller_RevA_Plan.md) for requirements. STM32G474VET6 in LQFP100 is the base MCU. The larger package supports diagnostics and a goal of at least ten spare usable GPIO after allocation.

## Resources to reserve

| Function | Reservation | Constraint to resolve before freeze |
| --- | --- | --- |
| MCU supplies | Every VDD/VSS, analog/reference, backup, and required support pin | Package-specific datasheet; each decoupling/return connection |
| System clock | HSE crystal/oscillator pins; optional LSE footprint | Clock tree, load capacitance, startup, USB and CAN tolerances |
| Debug | SWDIO, SWCLK, optional SWO, NRST, target voltage reference, grounds | Keyed 10-pin header and access with outputs inhibited |
| Recovery | Reviewed boot selection and recovery UART; USB ROM DFU provision | Package, alternate functions, option bytes, and ROM clock requirements |
| USB device | D+/D−, VBUS detection, CC pull-downs and service-power control | Reserved USB pins, differential routing, enumeration/suspend limits |
| ADC acquisition | SPI SCLK/MOSI/MISO/CS, reset, alarm if used | ADC protocol, timing, DMA-accessible memory and powered-off buffering |
| DAC | SPI instance preferred, CS/control as required | DAC80501Z interface/range; shared SPI only after mode/timing review |
| Field analog validity | FIELD_ANALOG_VALID and relevant rail/fault monitors | Hardware qualification of ADC/DAC access and AO enable |
| Digital inputs | DI1 timer count/capture; DI2–DI4 GPIO/interrupt inputs | Receiver polarity, debounce and pulse filtering |
| High-side commands | Four GPIO routed through hardware permission gates | Off at reset; no bypass via peripheral/alternate function |
| High-side diagnostics | Shared sense ADC input plus channel selection/enable/control | Multiplexed settling and protected fault/unpowered behavior |
| Relay commands | Two GPIO through permission gates | Coil drivers and pull-down defaults |
| Analog output | DAC control; independent default-off disconnect control | AO also qualified by FIELD_ANALOG_VALID |
| AO readback | Protected MCU ADC channel before commanded disconnect | Amplifier-side value only; no terminal-voltage claim |
| RS-485 | USART TX/RX and driver-enable | Half-duplex turnaround, reset driver-disable, bus-side supply |
| CAN | One FDCAN RX/TX pair | USB/boot/debug conflicts; bit timing and bus-off policy |
| Rail monitoring | Raw/protected field, service, analog and isolated-supply status as required | Divider/clamp/current injection under all power states |
| Other monitoring | Temperature, status/fault inputs, external watchdog | Measurement/diagnostic limitations |
| Service controls | User button, inhibit switch/status, indicators | Hardware inhibit independent of firmware |
| Configuration | I2C EEPROM bus and write protection as selected | Pull-up domain, boot recovery, interrupted-write behavior |
| Expansion | At least ten usable reserved GPIO goal | Confirm no restricted/special pins counted as freely available |

Budget roughly 45–60 signal pins until allocation is complete. Peripheral counts do not prove that the chosen functions fit simultaneously on the package. Complete CubeMX allocation, then manually cross-check the datasheet alternate-function and pin tables, reset states, timer/DMA resources, analog channels, and package bonding.

## Proposed net names and domains

These are functional names to use consistently in the schematic and firmware board support. They are not finalized pin assignments.

| Name | Meaning/domain |
| --- | --- |
| VIN_RAW / VIN_RETURN | Main DC terminal supply before protection |
| VFIELD | Protected 9–30 V operating field rail |
| MAIN_GND | Common DC negative, MCU, analog returns, load returns, USB ground |
| 5V_FIELD | Field-only service power for relays, isolated converters, ADC/DAC and analog conversion |
| 5V_SYS | USB/field-selected essential logic supply |
| 3V3_DIG | MCU digital/interface rail from 5V_SYS |
| 3V3_MCU_ANA | MCU analog support rail from 5V_SYS |
| 3V3_FIELD_LOGIC | External ADC digital/field-buffer rail from 5V_FIELD |
| ADC_AVDD | Qualified filtered field 5 V with permanent reviewed discharge impedance |
| 15V_ANA / NEG_ANA | Field-only amplifier/protector auxiliary rails |
| 5V_RS485_ISO / RS485_REF | Dedicated RS-485 bus-side supply and isolated return |
| 5V_CAN_ISO / CAN_REF | Separate CAN bus-side supply and isolated return |
| DI_COM | Shared digital-input field return, isolated from MAIN_GND |
| DI1–DI4 | DC input terminals; decoded logic polarity set from final circuit |
| AI_V1 / AI_V2 | Two single-ended 0–10 V terminals |
| AI_I1 / AI_I2 | Two externally powered current-loop receiver terminals |
| AI_RETURN / AO_RETURN | Analog return terminals in MAIN_GND domain |
| AO1 | Protected analog output terminal |
| AO_READBACK | Protected amplifier-side monitor, before commanded disconnect |
| DO1–DO4 / LOAD_RETURN | High-side output terminals and main-domain load returns |
| RELAY1_CMD / RELAY2_CMD | Gated coil commands |
| COM1/NO1/NC1; COM2/NO2/NC2 | Separate dry-contact circuits |
| FIELD_VALID / RESET_OK / WATCHDOG_OK / ARM | General hardware permission factors |
| FIELD_ANALOG_VALID | Relevant external analog rails valid; additional AO qualification |
| AO_ENABLE | Commanded disconnect control qualified by required permission conditions |

Hardware and firmware must distinguish VFIELD, 5V_FIELD and 5V_SYS; live USB logic does not imply live field electronics. Keep isolated references separately named. AI_RETURN and LOAD_RETURN share electrical ground but require physical paths that keep load current out of acquisition returns.

## Test access to allocate

Provide labeled access for VIN_RAW, VFIELD, every rail, MAIN_GND, reset, watchdog, general/analog validity, ARM, AO disconnect state, raw DI logic, SPI, diagnostics, and amplifier-side readback. Give each isolated island its own reference/probe access. Expose converter switching nodes only where probing/layout justify it.

Do not copy old test-point numbers or schematic designators. Assign them after capture and update bring-up/assembly documents together.

## Pin-allocation release checklist

- Export the final CubeMX resource assignment and clock tree.
- Match MCU part/package, symbol pin numbers and footprint pad numbers to the manufacturer documentation.
- Confirm all power/reference pins, boot options, reset/debug reservations and recovery interfaces.
- Confirm timer count/capture, ADC channels, DMA mapping and memory placement.
- Review every pull/default and alternate-function transition affecting an output.
- Check powered-off interface isolation, monitor injection and FIELD_ANALOG_VALID behavior.
- Record exact connector pin order, designators and test points from the captured design.
- Replace this provisional sheet with an approved pin table and version it with the schematic.

Until that checklist is complete, firmware should use development-board definitions or symbolic resource reservations. This document does not establish a verified pin map.
