# STM32 Industrial I/O Controller Rev A — Bring-Up Guide

Status: planned procedure for future hardware. No schematic, board, numbered test points, programmed firmware, or measurement results are established by this document.

Use [the canonical plan](STM32_Industrial_IO_Controller_RevA_Plan.md), [resource reservations](PinMap_CheatSheet.md), and [wiring guide](Interface_and_Wiring_Guide.md). Before first power, adapt this procedure to the frozen schematic, exact components, assembly drawing, instrument capabilities and as-built revision.

## Bench preparation and records

Use a current-limited DC supply, multimeter, oscilloscope with suitable probing, temperature probe, SWD probe, USB data cable, calibrated voltage/current stimuli, load resistors/electronic load, pulse source, and appropriate RS-485/CAN adapters. CAN FD tests need an FD-capable peer. Record the accuracy and limits of the calibration source/meter.

Plan stage isolation or test links while designing the board so input protection, converters and high-current paths can be powered progressively. Choose the initial current limit from the populated branch load and startup calculations. A 100 mA limit can be appropriate for an isolated power-stage check; it is not a claim that the fully populated board can start at 100 mA. Do not raise a limit repeatedly to conceal an unexplained overload.

Keep the output-inhibit control active, ARM cleared, loads disconnected and AO disabled at the start. Map scope earth, supply returns, USB ground and isolated reference islands before probing. An ordinary grounded probe can join an isolated field domain to MAIN_GND. Use suitable differential/isolated probing where preserving separation matters.

Create a record for every physical board with serial number, hardware revision, BOM/assembly variant, firmware build, date, operator, source limit, instrument/probe setup, ambient temperature, stimulus, target, measured result, uncertainty, capture/log filename, and disposition.

## Expected power states

Values below are nominal design expectations. Freeze operating bands, ripple limits, startup timing, source-current limits and valid-rail thresholds from the final calculations before using them as pass/fail limits.

| Rail/function | Field-only, valid 12/24 V input | USB-only service |
| --- | --- | --- |
| VFIELD | Near applied DC less reviewed protection losses | Inactive; no USB backfeed |
| 5V_FIELD | Nominal 5.0 V | Inactive after discharge |
| 5V_SYS | Selected source near 5 V less reviewed mux/path loss | USB-derived selected service supply |
| 3V3_DIG | Nominal 3.30 V | Nominal 3.30 V |
| 3V3_MCU_ANA | Nominal 3.30 V | Nominal 3.30 V |
| 3V3_FIELD_LOGIC | Nominal 3.30 V | Inactive |
| ADC_AVDD | Nominal 5.0 V; within ADC 4.75–5.25 V requirement including ripple | Inactive with reviewed discharge impedance |
| DAC supply | Qualified field 5 V | Inactive |
| 15V_ANA | Nominal +15 V | Inactive |
| NEG_ANA | Small negative bias near −0.232 V | Inactive |
| 5V_RS485_ISO | Regulated nominal 5 V relative to RS485_REF | Inactive |
| 5V_CAN_ISO | Independently regulated nominal 5 V relative to CAN_REF | Inactive |
| Relay coils / DO / AO | Available only after explicit permission/arming | Inhibited |

For inactive rails, record decay time, residual voltage and any leakage/injection; do not assume an instantaneous exact zero. A loaded/discharged rail rising from USB or a signal source is a stop condition until its cause is understood.

## Staged first-article sequence

Complete each stage before attaching the next load or enabling the next function. Preserve failures and rework in the record.

| Stage | Action and expected evidence | Stop criteria |
| --- | --- | --- |
| 1. Unpowered inspection | Check component values/orientation, MCU pins, exposed pads, diode directions, terminal mapping, assembly bridges and mechanical clearance against frozen files. | Wrong part/package, solder bridge, unexplained polarity/pad mismatch. |
| 2. Unpowered continuity | Measure rail-to-return resistance, output shorts and ground-domain continuity. Capacitor charging behavior is interpreted from the circuit. Verify DI_COM, RS485_REF, CAN_REF and relay contacts are not unintentionally joined to MAIN_GND or each other. | Hard short or unintended domain bond; resistance checks alone do not prove dielectric qualification. |
| 3. Input protection | Start at 12 V DC with branch loading controlled. Measure raw/protected voltage, startup current and eFuse behavior while outputs stay inhibited. | Unexpected current-limit operation, rising temperature, excessive protected-rail voltage or unintended output pulse. |
| 4. Service rails | Qualify 5V_FIELD, 5V_SYS, MCU rails and their ripple at device pins. Check startup/order and validity signals. Use short probe returns for ripple. | Any rail outside its frozen operating band, unexplained reset/hiccup, missing decoupling or regulator overheating. |
| 5. MCU/debug | Read MCU identity via SWD; program a minimal output-inhibited diagnostic build. Confirm clocks, reset, indicators, watchdog and build identity. | Debug unrecoverable, wrong part identification, clock/reset instability, permission active during boot/halt. |
| 6. USB service | Field source absent; verify essential rails only. Confirm current/enumeration/suspend behavior with implemented firmware. Attempt field commands: they must be refused/inhibited. | Field rail/backfeed, coil energization, DO/AO activation, invalid field readings shown as valid. |
| 7. Source sequencing | Test USB only, field only, both, either removed, and hot-plug. Measure source currents and inactive rails; repeat with debugger connected. | Source backfeed, loss of hardware inhibit, unintended output pulses, absent supplies energized through signals. |
| 8. Auxiliary rails | Check positive/negative analog supply, field logic, ADC/DAC power and both separately referenced isolated supplies with representative loads. | Wrong polarity/range, excessive ripple, shared isolated returns, insufficient loaded bus-side supply. |
| 9. Analog sequencing | Exercise protector powered with ADC_AVDD absent/collapsing; field removal while USB keeps MCU alive; all relevant startup/decay orders. Check AVDD discharge, buffered interfaces, input peaks and validity. | Pin stress outside reviewed limits, electrical backpower, valid data/AO enable before FIELD_ANALOG_VALID. |
| 10. Digital inputs | Sweep each DC input against DI_COM. Confirm OFF at 0–5 V and ON at 9–30 V. Measure current, transitions, delay and reversed-input behavior. | Threshold outside target, excess input heating, unexpected default or missing isolation. |
| 11. Pulse input | Compare DI1 timer count with a 20 kHz, 50% duty-cycle 12/24 V source over a recorded interval and cable. High/low intervals are 25 µs. | Lost/extra counts, receiver/filter distortion or counter rollover mishandling. |
| 12. Analog acquisition | Apply known voltage/current stimuli. Check raw conversion range, reference, scan timing, settling and invalid/fault status before calibration. | Unexpected gain/offset, excessive noise, mixed-up channels, saturation within normal range. |
| 13. Analog output | Keep disconnect off first; verify zero-scale startup, bias and amplifier-side readback. Then explicitly arm into ≥10 kΩ and measure actual terminal voltage with an independent meter. | Unintended startup output, oscillation, wrong range, invalid permission or readback presented as terminal feedback. |
| 14. One load output | Test a resistive load below the 0.5 A rating; measure terminal drop, current sense and gating. Repeat each channel. | Fault/noise/reset at ordinary load, unexpected backfeed, sense instability, poor thermal behavior. |
| 15. Relay outputs | Observe coil drivers and suppression; meter COM–NO/NC deenergized and energized. Then test the reviewed low-voltage DC resistive load. | Incorrect contact map, spontaneous energization, coil transient beyond reviewed limits. |
| 16. Wired ports | Qualify RS-485 with a second node and deliberate termination/bias, then classic CAN, then CAN FD. Record cable, references, termination and adapter. | Persistent lockup, erroneous commands, missing error recovery, collapse of isolated supply. |
| 17. Integrated operation | Use the actual sensor/load/AO actuator demo; measure switching disturbance, all four 0.5 A loads, enclosure temperatures and watchdog/command loss. | Unexplained reset, missed commands, accuracy/temperature outside the declared tested rating. |

Absence of USB enumeration on an unprogrammed device is not automatically a board failure. Distinguish SWD access, reviewed ROM recovery, and an implemented CDC application.

## Analog calibration and acceptance

Calibrate each input at two points using traceable source values, then verify independent points. Store coefficients with board identity, version, CRC and uncertainty. Do not accept a calibration that absorbs a fault, clipping, unstable reference or wrong shunt value.

| Check | Stimulus | Planned acceptance |
| --- | --- | --- |
| Voltage input | 0, 2.5, 5, 7.5 and 10 V | ±20 mV after room-temperature calibration |
| Current input | 4, 8, 12, 16 and 20 mA | ±32 µA after room-temperature calibration |
| Current diagnostics | Selected values below/above valid range; up to intended overrange | Values/flags match the supported transmitter and protection range |
| Input temperature | Repeat at 0/25/50 °C using room-temperature coefficients | Voltage ±50 mV; current ±80 µA, including stated uncertainty |
| AO | Zero, intermediate values and full scale into ≥10 kΩ | ±50 mV at terminal; stable, default-off behavior demonstrated |
| Switching disturbance | Repeat with outputs off/switching/fully loaded and both ports active | Meet the published accuracy condition; report transient and settled errors separately |

Record useful bandwidth, filtering and publication rate. The goals are 1 kSPS/channel acquisition and 100 Hz calibrated publication, with approximately 50–100 Hz useful sensor bandwidth. A 16-bit converter does not establish 16-bit system accuracy.

Use a nominal 24 V externally powered current loop for the demo. A 200 Ω shunt develops 0.8–4 V at 4–20 mA and dissipates 80 mW at 20 mA; protection resistance adds to its 4 V burden. Verify the entire loop compliance budget.

## Controlled qualification after bring-up

Before fault injection, freeze the fault fixture, source impedance/current limit, duration, instrument bandwidth, expected protection response and energy calculations. Begin with non-destructive low-energy characterization before the specified full test. Ordinary bring-up does not prove fault survival.

| Test | Condition to qualify | Required evidence |
| --- | --- | --- |
| Supply range | 9, 12, 24, 30 V under rated combined loading | Valid rails and specified operation |
| Main reverse/overvoltage | −30 V reverse; +40 V positive fault under documented source limits | Loads disarm; reviewed clamp/disconnect; recovery requires rearm |
| Analog miswire | ±30 V on each signal terminal, powered/unpowered, 60 s | No damage/backpower; accurate recovery; peak stress within reviewed limits |
| AO faults | Open, return short, cable capacitance, external ±30 V | Stable/protected behavior and explicit rearming |
| Output overload/short | Reviewed controlled fixture per channel | Immediate hardware current limit, firmware fault latch, no uncontrolled retries |
| Inductive load | Specified real 24 V load, individual/simultaneous switch-off | Current-decay/voltage captures and diode/switch temperature/energy |
| Positive DO backfeed | Rated positive terminal source with board field source absent | No unintended rise of VFIELD or service supplies |
| Reset/halt/update/watchdog | Each interruption while outputs commanded | Physical permission removed and fresh arming required |
| Owner timeout | Stop selected owner's valid commands | Energy outputs inhibited within configured timeout; default 1 s |
| Configuration faults | Corrupt/interrupt configuration write | Valid copy recovered or board disarmed with clear fault |
| Protocol robustness | Invalid frames, CRC errors, traffic load, CAN errors/bus-off | No unintended output changes, controlled recovery |
| Soak/repeatability | ≥24 h recorded operation and repeat calibration on ≥3 boards | No unexplained resets/faults; traceable repeatable results |

IEC-style ESD/EFT/surge work requires a separately frozen installation/test plan and reviewed protection energy. Do not infer compliance from a component rating or the bench matrix.

## Measurement sheet

Create one copy per board/test session; blank entries are unmeasured, not passed.

| Measurement | Target/source of limit | Value/capture | Pass/fail and action |
| --- | --- | --- | --- |
| Assembly/continuity/domain inspection | Frozen schematic/BOM/assembly | | |
| Supply/input current and startup | Frozen power budget and source limit | | |
| Each field/service rail and ripple | Nominal table plus frozen limits | | |
| USB-only inactive rails and leakage | No reviewed path backpower | | |
| Permission/reset/watchdog timing | Hardware contract | | |
| Analog collapse/protector-on stress | ADC/interface absolute limits | | |
| DI thresholds/current | OFF ≤5 V; ON ≥9 V | | |
| DI1 count/delay | 20 kHz recorded source | | |
| AI points/noise/uncertainty | Calibration targets | | |
| AO terminal/readback/stability | ±50 mV; ≥10 kΩ | | |
| Output drop/current/temperatures | Four × 0.5 A tested condition | | |
| Relay contact/coil behavior | Reviewed 30 V DC, 1 A resistive goal | | |
| Port cable/termination/error behavior | Specified Modbus/CAN settings | | |
| Fault/setup/recovery captures | Frozen qualification fixture | | |
| Soak/reset/command log | 24 h and versioned record | | |

Do not move to the next stage while a stop condition is unresolved. If a target changes, update the canonical plan, wiring guide, firmware bounds, test procedure and portfolio claim together.
