# STM32 Industrial I/O Controller Rev A — Firmware

Status: requirements and implementation plan only. No STM32 firmware, reproducible build, protocol implementation, or programmed hardware has been completed. This folder contains the software contract for the new board.

The authoritative scope is [the board plan](../docs/STM32_Industrial_IO_Controller_RevA_Plan.md). Use [resource reservations](../docs/PinMap_CheatSheet.md) until the package-specific allocation is frozen, [the wiring guide](../docs/Interface_and_Wiring_Guide.md) for external connections, and [bring-up](../docs/BringUp_Guide.md) for measurements. Component capabilities and planned behavior are not measured board results.

## Implementation approach

Use C/C++ for STM32G474VET6 with STM32Cube-generated startup and HAL support where useful. Begin with a deterministic timer-driven scheduler. Add an RTOS only when the application requires it. Select and record the exact compiler, SDK/HAL, generator version, linker configuration, and build commands before creating the release build.

SWD is the primary programming/debug/recovery route. USB CDC is the service interface. USB ROM DFU is a planned recovery route whose boot activation, package pins, clocks, and option bytes must be checked before capture. Firmware development can begin on suitable STM32 development hardware while the schematic is completed; drivers must be adapted and tested on the final board.

Organize future code into board support, device drivers, calibrated acquisition, output management, fault handling, protocol adapters, configuration storage, and demonstration logic. The names and directories are implementation choices, not existing code.

## Hardware contract

| Function | Required behavior |
| --- | --- |
| Boot and reset | Command outputs default off. Hardware pull-downs and permission logic keep high-side channels, relay coils, and AO disconnect inactive independently of firmware. |
| Output permission | Hardware expression equivalent to FIELD_VALID AND RESET_OK AND WATCHDOG_OK AND ARM gates every energy-output command. Diagnostic enable is not a global output disable. |
| Analog permission | FIELD_ANALOG_VALID must qualify the external ADC/DAC interfaces, acquisition validity, and AO enable. The analog disconnect also requires general output permission. |
| Field power | Normal target is 9–30 V DC. Use reviewed rail/window monitors; do not infer valid field power from one uncalibrated software threshold. |
| USB service | MCU/service logic may operate. Field analog supplies, relay coils, isolated bus-side supplies, and load outputs stay inactive. Field values unavailable because rails are invalid carry an explicit invalid status. |
| Electrical sequencing | Powered-off interface isolation and protected monitoring prevent signal injection between live USB logic and absent field supplies. Firmware inactivity alone cannot establish this. |
| Digital inputs | Translate receiver polarity from the final schematic into logical ON/OFF. DI1 uses timer counting/capture; DI2–DI4 use configurable software debounce. |
| ADC | Acquire four external channels at 1 kSPS/channel and publish calibrated/filtered values at 100 Hz. Tag samples with channel, time, range, validity, and faults. |
| DAC/AO | Initialize the zero-scale DAC with AO disconnected. Enable only after valid rails, self-check, and explicit arming. Bound commands to 0–10 V. |
| AO telemetry | Readback is taken on the protected amplifier side, before the disconnect. It cannot prove terminal voltage or detect every wiring fault. |
| Load diagnostics | Select and settle the shared current-sense path before sampling each channel. Four current readings are sequential, not simultaneous. |
| Relay state | Deenergized coil means COM–NO open and COM–NC closed. Software reports coil command; it does not imply measured contact feedback. |
| Reset/watchdog | Reset, watchdog failure, invalid power, update mode, and global faults remove permission and clear arming. Old commands are never restored automatically. |
| Command loss | Default active-owner timeout is 1 s, within reviewed configuration bounds. Expiry inhibits all commanded energy outputs and requires a fresh arm sequence. |
| Channel fault | Overload/short faults latch the affected channel off. Do not continually retry into a short. Unaffected-channel policy must be explicit. |
| Configuration | Version, board compatibility, ranges, CRC, and recoverable copies are checked before arming. Invalid configuration leaves the board disarmed. |

The external ADC/DAC are field-powered. ADC_AVDD and DAC supply derive from 5V_FIELD; ADC digital supply and field-side interface buffers use 3V3_FIELD_LOGIC. MCU digital/analog supplies derive from the USB/field-selected 5V_SYS. The permanent ADC_AVDD discharge path, buffer behavior, clamps, and rail sequencing must be validated electrically, including a live protector with the ADC supply off.

## States and command ownership

| State | Meaning |
| --- | --- |
| USB service | Essential logic available; field outputs inhibited; invalid field readings identified. |
| Boot/self-test | Outputs inhibited while rails, configuration, interfaces, and watchdog are checked. |
| Ready | Valid power/configuration and no blocking faults; permission still off. |
| Armed | A selected command owner explicitly armed the board and maintains valid fresh commands. |
| Channel fault | A diagnosed output is off and latched; other outputs follow the documented policy. |
| Global fault | All high-side commands, relay coils, and AO inhibited. |
| Recovery | Fault removed and self-check passed; fresh arm command required. |

Choose one owner: Modbus, CAN, or local demonstration mode. A USB service command may configure/read the board without silently taking control. Owner changes disarm outputs. Invalid frames, unrelated traffic, or read-only requests must not renew the command lease accidentally.

Validate commands centrally and apply multi-output commands atomically. Protocol callbacks must not write output GPIO directly. Hardware permission remains authoritative through debugger halt, bootloader entry, reset, and firmware update.

Feed the external watchdog only after software health checks pass. A free-running timer or unrelated interrupt must not conceal a stalled application.

## Interfaces to implement

| Interface | Initial behavior |
| --- | --- |
| USB CDC | Board/version information, configuration, calibration, diagnostics, acquisition logging, and service actions. Observe enumeration/current/suspend rules. |
| Modbus RTU | Half-duplex server; first qualify 19,200 and 115,200 bit/s. Implement addressing, CRC, timing, exceptions, broadcast behavior, driver turnaround, and supported functions against the official specification. |
| CAN | Custom application protocol; qualify classic CAN at 500 kbit/s, then FD at 500 kbit/s arbitration and 2 Mbit/s data on the documented bus. |
| Common data model | Same units, validity, configuration, output state, and fault meanings across all interfaces. |
| Host tools | Future Python tools/dashboard with versioned logs, stimuli, protocol stress tests, plots, and reproducible reports. |

Document CAN identifiers, sequence handling, byte order, scaling, and timeout rules. This protocol is not CANopen unless CANopen is actually implemented. Record CAN bus-off/error counters; recovery requires fresh commands and explicit rearming.

Do not freeze Modbus register addresses or CAN identifiers before the data model is reviewed. Use millivolts, microamps, milliamps, pulse counts, and explicit validity/fault fields. Define signedness, register ordering, rollover, and atomic snapshots.

## Acquisition, calibration, and demonstration

Voltage channels use the planned 0–10.24 V ADC range. Current channels use 200 Ω shunts and the 0–5.12 V range, covering 0–25.6 mA. Publish configurable low/high current alarms for the chosen transmitter; approximately 3.6/21 mA are starting values, not universal sensor semantics. A 0 V voltage reading alone does not establish a disconnected wire.

Keep raw samples available for noise/settling analysis. Store calibration coefficients, units, date, hardware/firmware versions, and source uncertainty. Use two-point calibration and independent verification points. Calibration must not arm outputs or apply a stale actuator command.

The initial demonstration combines a real external 24 V current loop, a voltage stimulus/sensor, pulse counting, a rated DC load, a high-impedance 0–10 V actuator, and wired telemetry. High-frequency PWM and proportional-solenoid drive are future qualified extensions.

## Development and acceptance sequence

1. Freeze package/resource allocation, power/interface domains, and hardware permission behavior.
2. Bring up debug, reset, clock, watchdog, indicators, and USB with outputs physically inhibited.
3. Add rail monitoring and validity handling; test USB-only and every source insertion/removal order.
4. Add input receivers/timer capture and external ADC drivers with fault/status reporting.
5. Add DAC, amplifier-side readback, and AO arming only after electrical qualification.
6. Add high-side diagnostics and relay control through the common output manager.
7. Add Modbus, classic CAN, CAN FD, configuration storage, and host tests.
8. Verify resets, debugger halt, communication loss, bad frames, corrupt configuration, and interrupted writes.
9. Run the canonical qualification matrix on at least three boards and a 24 h recorded soak.

Acceptance data must include board serial/revision, firmware build identity, test fixture, stimulus, expected target, measured result, and uncertainty. A future release must include reproducible build instructions and programming/recovery steps. No claim in this README establishes completed or tested software.
