# Firmware

I have defined the firmware behavior alongside the hardware. Application code and a reproducible STM32 build are pending. I plan C/C++, a deterministic timer-driven scheduler and a common measurement/command model for USB, Modbus and CAN. My [protocol v1 contract](Protocol.md) freezes the initial Modbus register map, units, identity, acquisition snapshots and guarded actuator commands. This is a target specification; host-tool/model checks do not establish board behavior.

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

The planned owner is Modbus, CAN or local control. Owner changes disarm the board. The initial implemented command transport will be Modbus; the first classic-CAN protocol provides telemetry, and CAN ownership stays unavailable until guarded commands are defined and qualified. The default lease is 1 s; invalid frames, unrelated traffic and read-only requests do not renew it. I validate commands centrally and apply multi-output updates atomically.

Modbus commands include the current boot ID and control epoch, a fresh sequence, owner, bounded lease and complete output state. ARM starts with all commands zero; SET changes the four high-side and two relay commands together. A timeout, reset or fault cannot automatically rearm outputs. A separate unconditional DISARM can only remove permission. Individual writable output coils/registers are absent. Host controls use explicit verbs; read/log/calibration-capture operations do not write or run a background heartbeat.

The normal order is explicit DISARM/recoverable-fault acknowledgement, self-check/READY, fresh identity and control guards, zero-output ARM, confirmed ARMED, then fresh SET. ARM does not apply a previously sent SET. The target publishes the complete accepted/applied command state before its success reply; host confirmation checks the epoch, owner, health, live lease and intended masks/PWM together. Under global-fault policy 1, bus-off in an enabled CAN mode disarms all six gates even when Modbus owns them. M1 does not enable CAN; CAN communication recovery alone cannot acknowledge a fault or restore outputs.

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

I keep DO3 static off/on available through the same permission gate before adding PWM. The protocol reports implemented and physically qualified capabilities separately and rejects PWM mode before both support and qualification are present. I begin PWM qualification with a resistive or compatible LED load up to 0.5 A. Duty controls time at the full supply voltage; it is not an analog voltage command. The firmware rejects unsupported frequency/duty combinations. I represent 0% and 100% as explicit static states and preserve the hardware gate in every mode.

PWM requires qualified static-high-side support as well as qualified PWM support. I stage PE9 GPIO/AF, timer enable/compare/preload and diagnostic-selector changes so a mode transition cannot emit a stale or unintended pulse. Complete accepted control state is committed at the reviewed boundary before acknowledgement; current validity is cleared during mode/selector settling. This is a software transaction guarantee, not a claim that relay contacts and high-side edges move simultaneously. Fault/disarm clears hardware permission immediately without waiting for the timer, communication queue or EEPROM.

First actuator measurements require the [bounded commissioning-test route](Protocol.md#qualification-bootstrap--pending-commissioning-implementation), which is still an implementation gate. Qualification flags remain zero while a technician triggers finite fixture tests with reviewed current-limited loads and all health, watchdog, ARM and disarm protections retained. Recorded measurements on the exact assembly/actuator code support reviewed release metadata before normal external host commands are enabled; the host has no qualification-mask write or automatic qualification path.

For DO3 diagnostics I sample during a settled on-window, account for switch/current-sense and receiving-filter settling, and schedule around the multiplexed selector. A reading is on-state current with a timestamp and validity flag. I report duty separately; I calculate duty-average current only for a qualified load model. An unavailable short sampling window marks telemetry invalid, rather than turning an unsettled value into an apparent fault-free reading. Current limiting and shutdown remain hardware functions. A reported driver fault initially disarms every actuator; any selective restart follows recorded fault diagnosis, cleared commands and a fresh arm transition.

ANALOG_VALID qualifies field acquisition, with CROSS_OK and DO_CS_ENABLE defining their receiving-domain paths in [Control and service](../docs/circuits/Control_Service.md). I discard the first MCU ADC result after an idle interval over 1 ms where required by the STM32 errata. Calibration includes raw data, coefficients, units, revision/serial, date and reference uncertainty; independent verification points follow two-point calibration.

## Communication and service

- I will bring up SWD/SWO and self-powered USB identification/log diagnostics first, then the Modbus RTU map and the shared acquisition/fault model. External board power and detected USB VBUS are required before USB attachment; USB cannot run the controller by itself. USB service framing beyond this common model remains pending.
- My initial host tool uses an adapter connected to isolated RS-485, with read-only identification, status, CSV logging and calibration capture. It does not require implemented board USB CDC. Default Modbus is unit 1 at 19,200 bit/s, 8E1; CRC, timing, addressing, exceptions, broadcast disarm and driver turnaround must be checked on target hardware.
- I will qualify classic CAN telemetry at 500 kbit/s after Modbus bring-up, then DO3 PWM on bounded fixtures, then CAN FD at 500 kbit/s arbitration / 2 Mbit/s data. The protocol's first CAN stage does not yet accept actuator commands.
- I will verify recoverable configuration/calibration records and a bounded boot-generation journal in the existing EEPROM before permitting outputs. Page writes, write protection, endurance, interrupted commits and watchdog-reset-loop handling remain implementation gates.
- I will check ROM DFU entry against the exact device and current boot guidance and keep all output permissions removed during update or debug recovery.

The [protocol](Protocol.md) fixes zero-based register addresses, CAN telemetry identifiers, units, signedness, byte/register order, rollover and snapshot/raw-latch semantics. PWM mode, frequency, duty, on-state current and diagnostic validity use explicit fields. Relay telemetry reports coil commands, not measured contact position. Calibration capture and offline fitting are read-only in the initial host tool; coefficient commits require separate implemented, guarded and interruption-tested service capability. ADC resolution and coefficient storage do not establish analog accuracy.

Classic CAN emits one captured publication as an ordered, identity-bracketed eight-frame burst. The peer accepts only all six matching acquisition frames between equal boot/build openings and closings; reset/recovery/timeout clears partial groups. The G4 has only three hardware transmit elements, so a bounded software burst streams through transmit FIFO completion, using FIFO order rather than identifier-priority queue mode. I cancel/drain stale pending transmissions on bus-off/reinitialization before starting another burst. [RM0440 FDCAN message RAM/Tx handling](https://www.st.com/resource/en/reference_manual/rm0440-stm32g4-series-advanced-armbased-32bit-mcus-stmicroelectronics.pdf)

The baseline has 80 acquisition/identity frames plus two periodic heartbeat/status frames per second per node. A conservative analytical reservation of 160 bits per frame gives about 2.6% of a 500 kbit/s bus before extra status changes, other nodes, retries and errors. This estimate is not measured bus loading; the 1–63 node identifier range is not a promise that 63 full-rate nodes fit. I freeze the actual peer traffic/load and verify deadlines, loss, cancellation and recovery on the qualification fixture. The CAN FD application profile, mode transition and peer assembler remain a separate implementation gate before M4; retained FD hardware alone does not define those software behaviors.

FD implemented and qualified flags stay separate. A finite, reviewed disarmed technician commissioning build/peer fixture can collect initial FD evidence with qualification clear and all actuator commands inhibited; its profile and procedure must be defined first. It adds no host command/qualification override or new identifiers. Normal released FD operation follows only with implemented support and reviewed physical qualification; automatic bus recovery cannot restart a commissioning test.

## Target implementation gates

The following work is planned, with no target application/build checked in yet. It uses the selected pins/peripherals and preserves every retained board feature; no additional hardware is assumed.

| Area | Implementation and evidence needed |
| --- | --- |
| Reproducible target | Freeze Cube/HAL/LL and compiler versions, linker/startup/options and generated pin/clock configuration; build for the exact G474VET6 and record source/build/silicon identity |
| Startup/default-off | Assert DISARM_N and zero PE commands/timer state before peripheral configuration; keep EEPROM_WP high; validate required rails/record copies, then verified boot freshness and self-test. Enter READY only after releasing DISARM_N with commands zero and reading ARM_STATE clear; leave unqualified command paths inhibited |
| Scheduler/priority | Hardware asynchronous inhibition is independent of software; bound fault/lease checking, SPI acquisition and timer work ahead of USB/RTU/CAN formatting and EEPROM operations; feed WDI only after actual application health checks, never from an autonomous timer |
| Acquisition | SPI1 DMA/interrupt state machine and timer-driven 1 kSPS/channel scheduling; one complete immutable publication/raw generation; preserve channel/range/age/clipping, selector settling and errata-related ADC discard rules |
| Actuator commit | Central guard evaluation, zero-output ARM then SET, PE GPIO/TIM1 mode sequencing, complete applied-state publication before reply, and proof of no stale pulse during reset/fault/mode transitions |
| RTU | Bounded 256-byte frames with hardware reception/error handling, 1.5/3.5-character timers, USART2 driver enable through the last stop bit, CRC/exception/address handling and immutable response copy; parser/traffic must not starve lease or watchdog tasks |
| USB service | Self-powered attach/detach with stable qualified rails/clocks/VBUS, explicit framing and bounded buffers; full USB characteristics require3.0–3.6 V digital supply. Detach on required power-health/clock loss, discard incomplete service/calibration transactions and require fresh stable startup before reattachment. G30 does not guarantee exact3.0 V undervoltage detection; independent digital-rail collapse needs a measured policy. Removal or a stalled host cannot block acquisition/shutdown |
| CAN | FIFO completion-driven eight-frame stream, bounded immutable group buffer, filters/DLC/byte order, strict peer assembler and cancellation on recovery; actual G4 HAL/LL ordering and supported FD mode/profile must be demonstrated |
| NVM commits | Page-bounded writes/ACK polling with measured deadlines, verified inactive-copy commit/CRC/generation selection, write protection, no blocking inside critical interrupt paths and no actuator-enable side effect |
| Boot/service recovery | CRC-checked reset-retained loop detection plus verified EEPROM journal; output-inhibited SWD-only first provisioning/service recovery, archived freshness bound and refusal to reuse generations after unreadable history |

First provisioning may start generation 1 only on a documented never-commanded UID. Corrupt-journal recovery needs a new verified floor above an archived upper bound on every possibly committed generation; a last logged ID is insufficient. If that bound is unknown or exhausted, I retain inhibition. Likewise, invalid configuration/calibration copies require output-inhibited service recovery rather than bypassing normal READY-only commit guards. The exact persistent record schemas, commit markers, recovery build and power-interruption/reset-loop tests remain pending.

The current host encloses snapshots with two identity reads for traceability. At 19,200 bit/s, its three RTU transactions move 231 bytes, roughly 132 ms of line time before silence/turnaround/software overhead. At 9,600 bit/s that doubles. I budget command preflight, post-confirmation and explicit renewal against the selected lease; a requested 5 Hz poll or 500 ms lease is not a guarantee at every baud/adapter. Read-only polling never renews a lease. Physical timing and watchdog/lease deadlines require instrument captures on target hardware.

My release will include exact toolchain versions, reproducible build/programming instructions and tests of malformed traffic, command loss, timer shutdown, resets, corrupted settings and interrupted writes. I record the 144 MHz core / 48 MHz USB clock plan and silicon errata in the [control specification](../docs/circuits/Control_Service.md).

The implementation review must apply [ES0430 Rev 9, June 2024](https://www.st.com/resource/en/errata_sheet/es0430-stm32g471xx473xx474xx483xx484xx-device-errata-stmicroelectronics.pdf) to the actual silicon and selected peripheral configuration. Keep FDCAN edge filtering (EFBI) disabled (§2.19.1, p. 30) and use transmit FIFO alone, avoiding a mix with dedicated transmit buffers (§2.19.2, pp. 30–31). Bound the SPI shutdown sequence and honor TXE/BSY handling (§2.18.1, p. 29). If USB remote resume is implemented, apply the specified 3 ms SUSP-interrupt masking (§2.20, p. 31); copied PMA CRC16 bytes are not host/application payload evidence. Initial independent edge-aligned PWM avoids the reviewed affected timer configurations, but the generated timer settings still need an errata cross-check. These are implementation gates and documented workarounds, not measured target results.
