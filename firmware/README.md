# Firmware

I have defined the controller's firmware behavior alongside the hardware architecture. Application code and a reproducible STM32 build are not implemented yet. The software design uses C/C++, a deterministic timer-driven scheduler, and STM32 startup/peripheral support, with a common data model across USB, Modbus, and CAN.

The [architecture](../docs/Architecture.md) defines the power and permission domains. [Interfaces](../docs/Interfaces.md) defines the electrical connections, and [validation](../docs/Validation.md) defines the required tests.

## Output state and ownership

| State | Output behavior |
| --- | --- |
| USB service | Controller available for diagnostics; field outputs inhibited |
| Boot/self-test | Outputs inhibited while rails, configuration, peripherals, and watchdog are checked |
| Ready | Valid power and configuration; explicit arming still required |
| Armed | One selected command owner controls the outputs and maintains a valid command lease |
| Channel fault | Affected high-side channel latched off; remaining-channel policy applied explicitly |
| Global fault | High-side commands, relay coils, and analog output inhibited |
| Recovery | Self-check repeated and a fresh arm command required |

The command owner is Modbus, CAN, or local control. Owner changes disarm the board. The default lease is 1 s; unrelated traffic, invalid frames, and read-only requests do not renew it. Commands are validated centrally and multi-output updates applied atomically.

Hardware permission gates the high-side commands, relay coils, and analog-output disconnect. Reset, watchdog failure, invalid field power, and update/recovery modes remove permission independently of the application. The external watchdog is serviced only after application health checks; a free-running timer must not conceal a stalled control loop.

## Acquisition and diagnostics

| Function | Planned implementation |
| --- | --- |
| Digital inputs | DI1 timer counting/capture; configurable debounce on DI2–DI4 |
| Analog inputs | Four external ADC channels at 1 kSPS per channel; calibrated values published at 100 Hz with timestamps, validity, and fault flags |
| Current receivers | 200 Ω shunts and 0–5.12 V ADC range; configurable low/high alarms appropriate to the connected transmitter |
| Analog output | Zero-scale DAC initialization with output disconnected; 0–10 V commands enabled after valid rails and explicit arming |
| Output current | Sequential sampling of the shared high-side current-sense signal after channel selection and settling |
| Configuration | Versioned calibration/settings, CRC checks, and recoverable copies; invalid configuration leaves the board disarmed |

FIELD_ANALOG_VALID qualifies external ADC/DAC communication, acquisition validity, and analog-output enable. USB-only operation reports unavailable field measurements as invalid. Powered-off interface protection and rail sequencing require electrical verification on the board.

Analog-output readback is taken before the hardware disconnect, on the amplifier side. It reports the internal command voltage rather than proving the terminal voltage. Relay telemetry reports coil commands; a deenergized SPDT relay opens COM–NO and closes COM–NC. High-side current readings are sequential rather than simultaneous.

Calibration retains raw samples, coefficients, units, hardware/firmware identity, date, and reference uncertainty. Two-point calibration is checked at independent verification points and does not arm outputs.

## My communication and service design

- I will use USB CDC for identification, diagnostics, configuration, calibration, and acquisition logging.
- I will implement a Modbus RTU server with explicit addressing, CRC, timing, exceptions, broadcast handling, and driver turnaround.
- I will use a versioned CAN application protocol: classic CAN at 500 kbit/s first, followed by CAN FD at 500 kbit/s arbitration and 2 Mbit/s data after bus qualification.
- I will use SWD as my primary programming/debug path and verify the package, clock, boot, and option-byte requirements before enabling ROM USB DFU.

I will freeze register addresses and CAN identifiers with the data model, keeping units, signedness, byte/register order, rollover, atomic snapshots, and validity meanings consistent across interfaces. My CAN protocol is a custom application protocol; CANopen support is outside the Rev A scope.

I will implement the software alongside hardware bring-up: controller/service functions, input acquisition, guarded output control, wired protocols, then fault and endurance tests. My software release will include exact toolchain versions, build/programming instructions, host test tools, and recorded results for resets, command loss, malformed traffic, corrupted settings, and interrupted writes.
