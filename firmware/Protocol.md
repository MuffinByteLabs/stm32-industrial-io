# Field I/O protocol v1

**Status: frozen design contract, protocol 1.0 / register-map revision 1. Target STM32 firmware and physical protocol tests are pending.** The host tools can be checked against a synthetic model; those checks do not establish board behavior, analog accuracy, isolation or output ratings.

This contract implements the data and command behavior defined in [Interfaces](../docs/Interfaces.md) and the [firmware plan](README.md). All six actuator gates remain subject to hardware PERMISSION. No mapped register or transport bypasses that gate. The project is a low-voltage DC prototype; protocol guards are not a safety certification or an authentication mechanism.

## Transport and encoding

The first host connection uses a USB-to-RS-485 adapter connected to the isolated RS-485 terminals. It is not a claim that the board's USB CDC firmware exists. Default Modbus RTU settings are unit address **1**, **19,200 bit/s, 8 data bits, even parity, 1 stop bit**. Configurable addresses are 1–247. The initial fixture uses the cable, reference and termination limits in [Field I/O](../docs/circuits/Field_IO.md).

Function numbers below are decimal: **03 / 0x03** reads holding registers, **04 / 0x04** reads input registers, **06 / 0x06** writes a single holding register, and **16 / 0x10** writes multiple holding registers. Addresses are **zero-based PDU offsets**, not 30001/40001 notation. Register bytes are big-endian; our multi-register u32/s32 values use the high register first. This follows the standard register encoding while explicitly fixing our application word order. [Modbus application specification](https://www.modbus.org/file/secure/modbusprotocolspecification.pdf)

RTU uses CRC-16/Modbus, with the CRC's low byte sent first. Firmware must validate frame length, address, function, byte count and CRC before handling a request. At up to 19,200 bit/s it uses the specified 1.5/3.5-character framing timers; above that it uses 750 µs / 1.75 ms. It enables the RS-485 driver only for its response and disables it after the final stop bit, with transceiver timing verified at the connector. [Modbus serial implementation guide](https://www.modbus.org/file/secure/modbusoverserial.pdf)

Only one RTU client transaction may be outstanding. Default host polling is 5 Hz at 19,200 bit/s; 100 Hz internal publication does not mean 100 full register responses per second. Unknown functions return exception 01; unmapped/cross-block/partial-write addresses return 02; invalid values or failed application guards return 03; internal persistence or unavailable-latch failures return 04. Invalid CRC/address traffic is discarded. Exceptions and reads never renew an output lease.

All unsigned measurements use scaled integers, with no floats on the wire. `0xFFFF` means unavailable for scaled u16 measurements and age fields; validity bits remain authoritative. It is **not** a sentinel for raw ADC codes. Reserved fields must be zero on write and read as zero. Incompatible major versions require a host update; additions require a map-revision update. Hosts reject unrecognized state, owner and command values.

## Identity — FC04, base 0x0000, 24 registers

| Relative offset | Field | Format / meaning |
|---|---|---|
| 0 | Protocol version | u16; 0x0100 = 1.0 |
| 1 | Register-map revision | u16; 1 |
| 2–3 | Implemented capabilities | u32 bitmask |
| 4–5 | Qualified capabilities | u32 bitmask; always a subset of implemented |
| 6 / 7 / 8 | Firmware major / minor / patch | u16 each |
| 9 / 10 | Hardware major / minor | u16; major 1 denotes Rev A |
| 11 | Assembly variant | u16; release-defined identifier |
| 12–13 | Firmware build ID | u32; maps to the release manifest / source revision |
| 14–19 | MCU UID | Three u32 words, in device UID word order |
| 20–21 | Boot ID | Nonzero persistent u32 session generation; zero inhibits guarded commands |
| 22–23 | Reserved | Zero |

Capability bits: 0 digital inputs; 1 voltage inputs; 2 current-loop inputs; 3 static high-side outputs; 4 relay coils; 5 output-current telemetry; 6 Modbus; 7 USB service; 8 classic CAN telemetry; 9 PWM; 10 CAN FD; 11 configuration commit; 12 calibration commit. Other bits are zero.

“Implemented” means the populated assembly and firmware provide the function. “Qualified” means the specific board/build has supporting physical acceptance records for its stated operating envelope. A peripheral present in the STM32 does not set either bit automatically. Development firmware starts with qualification bits clear. The host displays both masks and only requests actuator functions with both relevant bits set. Qualification is read-only release metadata, never an ordinary host configuration write.

## Atomic measurement/status snapshot — FC04, base 0x0040, 48 registers

A full read copies one immutable publication into the response and simultaneously latches the corresponding raw acquisition block on this Modbus port. Continuous acquisition keeps running. The first and final sequence values must agree. Read-only identity/configuration requests do not replace the latch; a new full snapshot read replaces it. Any write invalidates it, and it expires after 1 s.

| Relative offset | Field | Format / unit |
|---|---|---|
| 0–1 | Publication sequence | u32 |
| 2–3 | Capture uptime | u32 ms |
| 4 | State | 0 BOOT_SELF_TEST, 1 READY, 2 ARMED, 3 DRIVER_FAULT, 4 GLOBAL_FAULT, 5 RECOVERY |
| 5 | Current command owner | 0 none, 1 Modbus, 2 CAN, 3 local |
| 6–7 | Status flags | u32; table below |
| 8–9 | Latched fault flags | u32; table below |
| 10–11 | Validity flags | u32; table below |
| 12 | Digital inputs | u16; bits 0–3 = DI1–DI4 |
| 13 | Applied high-side commands | u16; bits 0–3 = DO1–DO4 |
| 14 | Applied relay-coil commands | u16; bits 0–1 = relay 1–2; not contact feedback |
| 15 | Applied PWM duty | u16 permille; zero when DO3 is static |
| 16–17 | DI1 pulse count | u32 |
| 18 / 19 | V1 / V2 acquisition | u16 mV |
| 20 / 21 | I1 / I2 acquisition | u16 µA |
| 22–25 | DO1–DO4 current | Four u16 mA; settled driver on-state measurements |
| 26 | Owner lease remaining | u16 ms; zero when disarmed |
| 27–28 | Last accepted command sequence | u32; initially zero |
| 29 | Last command result | u16; table below |
| 30–31 | Configuration revision | u32 |
| 32–33 | Calibration revision | u32 |
| 34–37 | V1, V2, I1, I2 sample ages | Four u16 ms, relative to capture uptime |
| 38–41 | DO1–DO4 current sample ages | Four u16 ms, relative to capture uptime |
| 42 | Applied PWM frequency | u16 Hz; zero in static mode |
| 43 | Configured command owner | u16; 1 Modbus, 2 CAN, 3 local |
| 44–45 | Control epoch | Nonzero u32; advances whenever control is invalidated |
| 46–47 | Repeated publication sequence | Same u32 as offsets 0–1 |

| Bit | Status | Fault | Validity |
|---|---|---|---|
| 0 | FIELD_OK | Rail invalid | DI mask valid |
| 1 | RESET_OK | Watchdog/reset failure | Pulse count valid |
| 2 | WATCHDOG_OK | High-side driver/global fault | V1 valid |
| 3 | ANALOG_VALID | Analog-health failure | V2 valid |
| 4 | DO_FAULT_OK | Owner lease expired | I1 valid |
| 5 | DISARM_N | Invalid configuration record | I2 valid |
| 6 | ARM latch set | Invalid calibration record | DO1 current valid |
| 7 | Self-test passed | EEPROM/boot-journal failure | DO2 current valid |
| 8 | Configuration record valid | CAN bus-off | DO3 current valid |
| 9 | Calibration record valid | Firmware/update fault | DO4 current valid |
| 10 | Update mode | Reserved | All four measured calibration records applied |
| 11 | USB attached | Reserved | V1 measured calibration applied |
| 12 | RS-485 ready | Reserved | V2 measured calibration applied |
| 13 | CAN ready | Reserved | I1 measured calibration applied |
| 14 | NVM commit busy | Reserved | I2 measured calibration applied |

Other bits are zero. A structurally valid nominal/factory coefficient record can set status bit 9 while measured-calibration validity bits remain clear. Validity does not establish the published accuracy target: ADC resolution, applied coefficients, uncertainty and physical qualification are distinct. Invalid/unavailable data is excluded from calculations and plotting.

Publication sequence, uptime and pulse count wrap modulo 2^32. Age/delta calculations use modulo arithmetic for intervals under 2^31; logs keep the boot ID and host UTC timestamp to distinguish reset and wrap. Ages above 65,534 ms are unavailable and invalid. ADC validity is cleared when its sample is older than 20 ms, its acquisition health is invalid, or its conversion is clipped/outside the qualified measurement path. Output-current validity also requires the documented selector/settling/on-window conditions; inactive/too-short windows are invalid, not zero-current evidence. Driver limiting/shutdown does not depend on these samples.

## Raw capture and calibration readback — FC04

`0x0080`, 16 registers, returns the raw data latched by the preceding full snapshot: offsets 0–1 sequence; 2–5 external ADC codes V1/V2/I1/I2; 6–9 corresponding range codes; 10–13 MCU ADC current-sense codes DO1–DO4; 14–15 repeated sequence. Range code 0 is unknown, 1 is unipolar 0–10.24 V, 2 is unipolar 0–5.12 V; these describe ADC pin ranges, not the field-terminal units or rating. Additional range codes require a map revision.

Read snapshot, then raw without another snapshot/write between them. Both sequences must match and the host must preserve validity, ranges, ages and capture uptime together. An absent/expired latch returns exception 04; retry the **pair**, not raw alone. This prevents a 100 Hz publisher and a slower RTU link from mixing generations. Calibration capture is read-only and requires a stated reference stimulus/uncertainty and stable disarmed fixture.

`0x0090`, 24 registers, is calibration readback: offset 0 schema=1; 1 measured-record channel mask (bits V1/V2/I1/I2); 2–3 revision; 4–7 ADC range codes; 8–23 four coefficient groups. Each group is gain u32 Q16.16 followed by offset s32 Q16.16. Engineering value = rounded `(raw × gain + offset) / 65536`, in mV for V1/V2 and µA for I1/I2. Computation uses wide intermediate arithmetic and detects saturation. Independent reference points verify a two-point fit; the host's offline fit alone never changes board coefficients or qualification.

## Actuator commands — FC16, holding base 0x0100, exactly 16 registers

The server validates the entire block before changing any actuator state. Partial FC16 writes and FC06 writes into this block are rejected. No writable individual coil/register exists for a DO, PWM or relay.

| Relative offset | Field | Required value / format |
|---|---|---|
| 0–1 | Expected boot ID | Current nonzero u32 identity |
| 2–3 | Expected control epoch | Current nonzero u32 snapshot value |
| 4–5 | Command sequence | u32; exactly last accepted sequence + 1 |
| 6 | Action | 1 DISARM, 2 ARM, 3 SET, 4 KEEPALIVE |
| 7 | Requested owner | 1, Modbus |
| 8 | Lease | 500–5,000 ms; normal 1,000 ms |
| 9 | DO mask | Bits 0–3; no higher bits |
| 10 | Relay mask | Bits 0–1; no higher bits |
| 11 | DO3 mode | 0 static, 1 PWM |
| 12 | PWM frequency | 0 for static; 100 for qualified PWM |
| 13 | PWM duty | 0 for static; 100–900 permille for PWM |
| 14–15 | Reserved | Zero |

In static mode DO3 is controlled by DO-mask bit 2. PWM mode requires that bit to be zero to avoid conflicting commands. Static OFF/ON are the explicit 0/100% endpoints; requesting PWM mode before its physical qualification is rejected even if the load is otherwise supported. Every requested nonzero DO/relay needs its implemented **and** qualified capability; PWM additionally needs bit 9. Firmware retains the same hardware gate for all modes.

ARM requires READY, no current owner, configured owner=Modbus, no latched fault, healthy status mask `0x03BF` (bits 0–5 and 7–9), ARM-latch bit clear, and update/commit bits clear. At least one of static-DO/relay capabilities must be implemented and qualified. ARM, DISARM and KEEPALIVE require all output/mode/frequency/duty fields zero. ARM only grants permission with cleared commands: it does not energize an output. SET and KEEPALIVE require ARMED, owner=Modbus, configured owner=Modbus, continued health, and a live lease. SET atomically updates the four high-side and two relay commands; KEEPALIVE preserves them. Only accepted ARM/SET/KEEPALIVE renew the supplied lease.

Normal operation and recovery use this order: remove the fault cause; explicitly DISARM to acknowledge recoverable latches; wait for self-check/READY; read fresh identity/epoch/sequence; ARM with zero outputs; confirm ARMED; then issue fresh SET. SET before ARM is rejected. PWM needs both static-high-side capability bit 3 and PWM bit 9 in the implemented and qualified masks, even when the static DO mask is zero.

Before a successful FC16 response, firmware commits the complete accepted control state and publishes its command result/sequence, epoch, owner, lease and applied fields together. Timer-boundary application must finish before that acknowledgement. The host confirms those fields against the explicit request; a matching echo/result alone cannot confirm a different epoch or partially applied command. Atomicity means one validated complete command and coherent applied-state publication; it does not assert simultaneous relay contact motion or zero electrical skew between channels. Hardware fault/disarm clears permission immediately and is never delayed for a PWM boundary or serial response.

Guarded DISARM is accepted from any current owner after boot/epoch/sequence validation. It removes permission, clears timer/GPIO/relay commands, clears ownership and lease, and advances the control epoch. A lease expiry, reset, rail/analog/watchdog/driver fault, update entry or owner change does the same before any recovery. Recovery returns through self-test and READY with zero commands; fresh ARM and SET are required. Fault diagnostics are retained; persistent hardware faults cannot be cleared by ARM. After their cause is removed, explicit DISARM acknowledges recoverable latches and initiates self-check without energizing outputs.

Under Rev A global-fault policy 1, bus-off in an **enabled** CAN mode also latches fault bit 8, clears all actuator permission/commands and advances the epoch, even while Modbus owns outputs. An inactive CAN peripheral in M1 does not generate that fault. Automatic CAN controller recovery may restore communication but cannot acknowledge the latch, rearm or replay old commands; explicit DISARM/self-check and fresh ARM/SET follow once the cause is removed.

**Unconditional disarm:** FC06 holding `0x0000` with value `0xD15A` removes all six actuator permissions from any owner, without boot/epoch/sequence checks. It is also the only accepted broadcast write at unit 0 and produces no broadcast reply. This operation cannot energize or renew anything. FC03 of `0x0000` reads zero. Other broadcast application writes are rejected/ignored without a response; no full Modbus conformance claim is made before testing this constrained behavior.

Last-command results: 0 none; 1 accepted; 2 malformed/value; 3 boot mismatch; 4 epoch mismatch; 5 sequence mismatch; 6 wrong owner; 7 wrong state; 8 health not ready; 9 unqualified capability; 10 unsupported capability/mode; 11 conflicting/output mask; 12 commit busy. Rejected requests leave last accepted sequence, outputs, owner and lease unchanged, but may update this diagnostic result. Bad CRC and unrelated-address traffic do not.

Boot ID and control epoch must not wrap/reuse while commands can be accepted. Exhaustion leaves outputs disarmed pending service. Accepted command sequences may reach 0xFFFFFFFF; the next operation must use unconditional disarm to advance the epoch and reset the per-epoch sequence to zero. Epoch changes always reset the accepted sequence. A write-response timeout is ambiguous: the host reads state before choosing a fresh explicit command, never blindly retries or auto-rearms. Repeated/stale packets do not execute or renew a lease.

## Configuration and calibration commit — reserved for staged implementation

These maps are frozen for target implementation; capability bits 11/12 remain clear until their routines and interruption tests exist. Initial host tools perform identity/snapshot/raw capture and offline calculation; configuration/calibration record readback and commit remain staged. All commits require READY/disarmed, zero applied commands, healthy required rails, update mode off, and no competing owner or pending commit. A commit never grants ARM or renews a lease.

Active configuration is FC03 `0x0200`, 32 registers: 0 schema=1; 1 unit address; 2 baud code (0=9600, 1=19200, 2=38400, 3=57600, 4=115200); 3 parity code (0=none/8N2, 1=even/8E1, 2=odd/8O1); 4 default lease ms; 5 configured owner; 6–8 DI2–DI4 debounce ms; 9 reserved; 10–13 I1-low/I1-high/I2-low/I2-high alarms µA; 14 global-fault policy=1; 15 reserved; 16–17 configuration revision; 18–19 calibration revision; 20–21 active configuration-record CRC32; 22–23 active calibration-record CRC32; 24–31 reserved. Initial debounce is 20 ms and alarms are 3,600 / 21,000 µA only for a transmitter supporting those thresholds. DI1 filtering remains separately bounded for pulse acquisition.

Configuration staging is one complete FC16 `0x0240`, 32 registers: 0–1 boot ID; 2–3 epoch; 4–5 expected configuration revision; 6 schema=1; 7 unit; 8 baud; 9 parity; 10 default lease; 11 configured owner; 12–14 DI2–DI4 debounce; 15–18 I1-low/I1-high/I2-low/I2-high alarms; 19–29 zero; 30–31 CRC32 of the first 30 registers serialized big-endian. Readback uses FC03. After readback verification, FC06 `0x0001`=`0xC0DE` commits only that staged record. Debounce is 0–1,000 ms, low<high and both alarms are within 0–24,000 µA. Unsupported command owners are rejected; classic-CAN telemetry alone does not enable CAN ownership.

Calibration staging is one complete FC16 `0x0280`, 40 registers: 0–1 boot; 2–3 epoch; 4–5 expected calibration revision; 6 schema=1; 7 measured channel mask; 8–11 ADC ranges; 12–27 coefficient groups in the readback order; 28 voltage reference uncertainty mV; 29 current reference uncertainty µA; 30–31 UTC calibration date in Unix seconds; 32–37 zero; 38–39 CRC32 of the first 38 big-endian registers. FC06 `0x0002`=`0xCA1B` commits after readback and guards. CRC32 is reflected CRC-32/ISO-HDLC (polynomial 0xEDB88320, initial/final XOR 0xFFFFFFFF). Range codes must match the acquisition setup; gain must be positive and all calibrated endpoints/intermediate arithmetic in range. Coefficient updates clear relevant physical qualification flags until verification records justify restoring them through the release/service process.

Each staged record expires after 30 s and is invalidated by reset, epoch change, any actuator command, a competing stage or a guard failure. Commit rechecks all guards, expected revision and CRC. It writes/verifies the inactive EEPROM copy before publishing a new revision; interrupted writes retain the prior complete valid copy. Both invalid copies leave outputs disarmed and service readable. Unit/line changes take effect on the next reboot; all other accepted settings publish atomically and invalidate command ownership/epoch. Commit operations are rate-limited to one per 10 s and are never part of a control heartbeat. The EEPROM-record CRC covers its schema, length, generation and persistent payload, independently of the transport-stage CRC.

## Qualification bootstrap — pending commissioning implementation

Normal external commands require qualification, so first actuator measurements need a separate, reviewed **commissioning-test firmware/procedure** before release. It is not yet implemented and adds no host write, qualification-mask override or new wire protocol. Its reported qualification flags stay zero.

A technician explicitly starts one finite test in a documented current-limited fixture with reviewed low-voltage loads, source limits, duration, termination criteria and physical disarm access. All rail/analog/self-test health, hardware ARM/PERMISSION, external watchdog and six-output inhibition obligations remain in force. The local test sequence begins disarmed with cleared commands, permits only its reviewed fixture states, and clears commands/permission at completion, expiry, fault or technician disarm. It never automatically retries, repeats, recovers into an energized state, or accepts ordinary host actuator commands for an unqualified capability. Host identity/status/raw logging may observe the test without granting output control.

Records identify the exact assembly, actuator driver code/build, supply, loads, current/energy envelope, temperature, wiring, instruments and actual results. Commissioning evidence establishes only those measured conditions. A reviewed release manifest may then set the corresponding measured capability bits; normal host tests verify the guarded command behavior with that metadata. If actuator code or assembly changes, the review decides which evidence must be repeated and clears unsupported claims. No ordinary configuration/calibration transaction sets qualification bits, and a synthetic model never qualifies a board.

## Boot freshness and EEPROM implementation gate

The existing selected part is [24LC64-I/SN](../docs/circuits/Control_Service.md), not an additional component. Its 8 KiB capacity and 32-byte page writes constrain the software partition. [Microchip datasheet](https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/24AA64-24FC64-24LC64-64-Kbit-I2C-Serial-EEPROM-DS20001189.pdf)

Proposed byte partitions: config copies `0x0000–0x03FF` / `0x0400–0x07FF`; calibration copies `0x0800–0x0BFF` / `0x0C00–0x0FFF`; service reserve `0x1000–0x17FF`; boot journal `0x1800–0x1FFF` (64 page-sized rotational records). Record schema/CRC/readback, page boundaries, write-protect sequencing, endurance at temperature, brownout and reset-loop behavior remain firmware implementation gates before outputs can be armed.

Boot ID advances in a verified journal record before a boot becomes ARM-eligible; old valid records survive interruption. A failed/uninitialized/exhausted journal publishes boot ID zero, a fault and readable service diagnostics while retaining hardware inhibition. Guarded actuator commands and energizing actions are inhibited in that condition; the unconditional FC06 disarm still removes permission without a boot-ID guard. Repeated watchdog resets must enter diagnostic recovery without continuously writing the journal; the reset-cause handling and explicit service recovery procedure must be implemented and tested before actuator enable. Configuration/calibration writes do not overwrite boot records. A RAM control epoch starts at 1 for a new boot and advances on each invalidation; old-session commands fail the boot guard and old-arm commands fail the epoch guard.

First provisioning and corrupt-record recovery require a technician-controlled SWD service build with all actuator permissions inhibited; normal host writes cannot initialize the boot journal or manufacture READY. Generation 1 is allowed only for a never-commanded MCU UID with documented first provisioning. A corrupt/replaced/erased journal on a previously used UID must not restart at 1. Recovery requires a trusted archived upper bound on **every generation that could have been committed**, then a verified new journal floor strictly above that bound. A last observed host log is insufficient when later boots could have gone unlogged. If no trustworthy bound exists, or no greater u32 generation is available, the unit stays inhibited pending controlled hardware retirement/replacement; unreadable history is not reconstructed by assumption.

The service procedure must separately seed/recover valid configuration and nominal calibration records, verify both copies/CRC and journal separation, restore write protection, and return through ordinary boot/self-test. Both configuration/calibration copies invalid cannot be repaired by pretending the normal READY-only commit guards passed. Service code, archived freshness policy, reset-retained loop counter/validity, journal layout/commit markers and power-interruption tests remain implementation gates; this contract does not claim they already exist.

## Classic CAN telemetry v1 — pending after Modbus bring-up

The first classic-CAN contract is **read-only telemetry**, 500 kbit/s, standard 11-bit identifiers, 8-byte data frames, no RTR frames. Node IDs 1–63 are fixture-defined with unique IDs. This is a custom protocol, not CANopen/J1939 or a battery/inverter gateway. CAN command ownership remains unavailable until a guarded command contract and its tests are released. Bus-off recovery never arms outputs or transfers ownership.

The fixture records node-to-MCU-UID/assembly mapping from service identity; boot/build alone is not a globally unique board serial. Receivers require a supported version 0x10 heartbeat before accepting the node's groups and reject unexpected DLC, extended/RTR/FD frames, unknown state/owner and invalid masks/duty values. Reconnect/recovery requires a fresh supported heartbeat and opening. Heartbeat/status are asynchronous diagnostics with their own receipt time; they are not silently merged into the group's atomic acquisition timestamp.

All multi-byte fields are big-endian. Each acquisition group sends one immutable captured publication at 10 Hz in this exact eight-frame order: identity opening (`0x700 + node`), the six acquisition frames (`0x540`, `0x580`, `0x5C0`, `0x600`, `0x640`, `0x680`, each plus node), then identity closing (`0x700 + node`). Opening and closing boot/build payloads must agree and boot ID must be nonzero; all six sequence-low16 values must agree, and validity values in the five validity-bearing frames must agree. Identity bracketing identifies reset/build changes that a separate 1 Hz heartbeat cannot safely resolve. The truncated telemetry sequence is not an actuator command sequence.

| Identifier | Eight-byte payload |
|---|---|
| 0x500 + node | Version 0x10, state, owner, fault-present byte, uptime_ms u32; 1 Hz heartbeat |
| 0x540 + node | sequence_low16, validity_low16, V1_mV, V2_mV |
| 0x580 + node | sequence_low16, validity_low16, I1_µA, I2_µA |
| 0x5C0 + node | sequence_low16, DI byte, DO byte, relay byte, PWM-mode byte, duty_permille u16 |
| 0x600 + node | sequence_low16, validity_low16, DI1_pulse_count u32 |
| 0x640 + node | sequence_low16, validity_low16, DO1_mA, DO2_mA |
| 0x680 + node | sequence_low16, validity_low16, DO3_mA, DO4_mA |
| 0x6C0 + node | status_flags u32, fault_flags u32; 1 Hz and on change |
| 0x700 + node | boot_id u32, build_id u32; before and after each 10 Hz group, and on startup |

The receiver starts in WAIT_OPEN. A valid own-node identity opens a fresh candidate; it then accepts exactly the six acquisition identifiers above in order, followed by the identical closing identity. Only that complete group, received within 250 ms of its opening, is published. Closing returns to WAIT_OPEN, so a consecutive identity can open the next group. An identity received during incomplete collection abandons that candidate and starts a new opening; an unexpected own-node group order, sequence/validity mismatch, invalid payload, closing mismatch or timeout abandons the candidate. Frames from other nodes are ignored by that node's assembler. Own-node heartbeat/status frames never appear inside a burst. On receiver reconnect, known identity change or bus recovery, clear all candidates and require a newly bracketed complete group. Do not join fragments using sequence-low16 alone or retain a partial group across recovery.

Validity describes the captured publication, not measurement age at peer receipt. The classic group omits per-channel ages and capture uptime; heartbeat uptime belongs to its separate diagnostic frame. Record group receipt time and expose that limitation rather than claiming a ≤20 ms end-to-end CAN sample age or simultaneous multiplexed-current measurements. Full age/raw traceability uses the Modbus snapshot/capture workflow.

The target uses one ordered transmit **FIFO**, not the identifier-priority transmit queue, and keeps one bounded software burst while streaming through the STM32G4's three hardware Tx elements. Heartbeat/status/startup identity can be inserted only between complete bursts. No newer publication replaces fields in an in-progress burst. Reset/bus-off/reinitialization or a stalled-burst deadline discards the software candidate and cancels/drains old hardware pending transmissions before a new opening; successful cancellation and HAL/LL FIFO ordering must be verified on the actual G474. A stalled burst is dropped at its assembly deadline without blocking acquisition, watchdog, disarm or Modbus service. No completion/recovery action restores permission. [RM0440 FDCAN message RAM and Tx handling](https://www.st.com/resource/en/reference_manual/rm0440-stm32g4-series-advanced-armbased-32bit-mcus-stmicroelectronics.pdf)

Measurements preserve the Modbus units/sentinels/validity semantics. Heartbeat/state alone does not prove qualification; qualification remains in release records and identity readback. CAN FD implemented bit 10 reports actual fitted hardware and implemented firmware/profile, while qualified bit 10 remains clear until the separate short-bus physical records exist. Normal released FD operation requires both; an FD-capable peripheral/transceiver alone sets neither. The FD application profile and mode-transition/peer rules remain pending before M4.

First FD evidence may use a separately reviewed, finite **disarmed technician commissioning build/fixture** with an FD-capable peer, documented traffic/profile, source/load limits, duration and stop criteria. Qualification stays clear, all actuator permissions/commands stay inhibited, and the existing health/watchdog/disarm obligations remain in force. It cannot accept actuator ownership, automatically repeat/recover into FD testing, or provide a host qualification override. The resulting physical records can support reviewed release metadata; this pending route adds no wire identifiers or host commands. USB service will reuse the common data/command model; its transport framing remains pending.

## Required protocol evidence

Before target release, verify register encoding against captured RTU bytes; source/build identity; coherent latched snapshot/raw pairs; bad CRC/length/address handling; partial writes; wrong boot/epoch/sequence/owner; ambiguous write responses; broadcast disarm; no read-only lease renewal; six-output atomic SET; lease expiry and fresh rearm; timer shutdown; invalid current windows; power/backfeed/reset/debug/update faults; EEPROM interruption and watchdog-reset loops; and independently recorded physical qualification masks. Synthetic host/model tests cover only software agreement with this contract.
