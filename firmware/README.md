# Firmware

I have defined the firmware behavior alongside the hardware. Application code and a reproducible STM32 build are pending. I plan C/C++, a deterministic timer-driven scheduler and a common measurement/command model for USB, Modbus and CAN.

My [architecture](../docs/Architecture.md), [interfaces](../docs/Interfaces.md) and [validation matrix](../docs/Validation.md) define the design contract.

## Output state and ownership

| State | Output behavior |
| --- | --- |
| Boot/self-test | Inhibited while power, configuration, peripherals and watchdog are checked |
| Ready | Valid power/configuration; explicit arming required |
| Armed | One owner controls outputs and maintains a command lease |
| Driver fault | Global hardware FAULT clears ARM and inhibits all six actuator gates; firmware records the source before recovery |
| Global fault | All high-side commands/PWM and relay coils inhibited |
| Recovery | Timer and GPIO commands cleared, self-check repeated, fresh commands and arm transition required |

The owner is Modbus, CAN or local control. Owner changes disarm the board. The default lease is 1 s; invalid frames, unrelated traffic and read-only requests do not renew it. I validate commands centrally and apply multi-output updates atomically.

Hardware permission gates all four high-side command inputs and both relay drivers through an asynchronously cleared ARM latch. Reset, invalid required rails and external-watchdog failure remove permission independently of application software. A running PWM timer cannot keep the watchdog healthy; I service it only after application health checks. After any disarm I clear timer compare/output state before rearming, so stale duty cannot restore a load command.

## Acquisition and PWM

| Function | Planned implementation |
| --- | --- |
| Digital inputs | DI1 timer count/capture; configurable debounce on DI2–DI4 |
| Analog inputs | Four external ADC channels at 1 kSPS/channel; calibrated 100 Hz reports with timestamps, validity and faults |
| Current receivers | 200 Ω shunts; transmitter-specific low/high alarms; acquisition independent of actuator arming |
| DO1/DO2/DO4 | Guarded on/off commands |
| DO3 PWM | PE9 / TIM1_CH1 / AF2, 100 Hz; 10–90% commanded duty plus static 0/100% endpoints |
| Current diagnostics | Select, settle, sample and tag the shared high-side sense channel; phase-aware timing for DO3 |
| Configuration | Versioned coefficients/settings with CRC and recoverable copies; invalid settings leave outputs disarmed |

I begin PWM qualification with a resistive or compatible LED load up to 0.5 A. Duty controls time at the full supply voltage; it is not an analog voltage command. The firmware rejects unsupported frequency/duty combinations. I represent 0% and 100% as explicit static states and preserve the hardware gate in every mode.

For DO3 diagnostics I sample during a settled on-window, account for switch/current-sense and receiving-filter settling, and schedule around the multiplexed selector. A reading is on-state current with a timestamp and validity flag. I report duty separately; I calculate duty-average current only for a qualified load model. An unavailable short sampling window marks telemetry invalid, rather than turning an unsettled value into an apparent fault-free reading. Current limiting and shutdown remain hardware functions. A reported driver fault initially disarms every actuator; any selective restart follows recorded fault diagnosis, cleared commands and a fresh arm transition.

ANALOG_VALID qualifies field acquisition, with CROSS_OK and DO_CS_ENABLE defining their receiving-domain paths in [Control and service](../docs/circuits/Control_Service.md). I discard the first MCU ADC result after an idle interval over 1 ms where required by the STM32 errata. Calibration includes raw data, coefficients, units, revision/serial, date and reference uncertainty; independent verification points follow two-point calibration.

## Communication and service

- I use self-powered USB CDC for identification, diagnostics, configuration, calibration and logs. External board power and detected USB VBUS are required before attachment; USB cannot run the controller by itself.
- I implement a Modbus RTU server with CRC, timing, addressing, exceptions, broadcast handling and controlled driver turnaround.
- I use a versioned custom CAN protocol: classic 500 kbit/s first, then qualified FD at 500 kbit/s arbitration / 2 Mbit/s data.
- I use SWD/SWO for primary programming/debugging and check ROM DFU entry against the exact device and current boot guidance.

I freeze register addresses, CAN identifiers, units, signedness, byte/register order, rollover and snapshot/validity semantics with the data model. PWM mode, frequency, duty, on-state current and diagnostic validity use explicit fields. Relay telemetry reports coil commands, not measured contact position.

My release will include exact toolchain versions, reproducible build/programming instructions and tests of malformed traffic, command loss, timer shutdown, resets, corrupted settings and interrupted writes. I record the 144 MHz core / 48 MHz USB clock plan and silicon errata in the [control specification](../docs/circuits/Control_Service.md).
