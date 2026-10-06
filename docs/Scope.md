# Rev A scope and completion priorities

I use this baseline to finish one useful industrial sensing-and-actuation controller. I froze the major functions on October 4, 2026 after reviewing the supplied freelance-job sample. Circuit capture, layout, target firmware and physical qualification remain pending; a frozen function list does not approve the circuit or establish a board rating.

The active design is **STM32G474VET6 Industrial I/O Controller**. The local workspace may retain the older ESP32S3 folder name. My native design belongs in `hardware/STM32_Industrial_IO/`.

## Retained hardware

| Function | Rev A baseline |
| --- | --- |
| Controller and PCB | Directly integrated STM32G474VET6; four copper layers |
| Power | Protected external nominal 12/24 V DC; retained 9–30 V qualification target and 3 A continuous input budget |
| Digital acquisition | Four inputs sharing isolated DI_COM; DI1 pulse counting; positive signals from PNP/sourcing sensors or externally powered contacts |
| Analog acquisition | Two single-ended 0–10 V inputs, two externally powered 4–20 mA receivers, external ADC and calibration |
| Actuation | Four diagnosed high-side outputs, 0.5 A each simultaneously; two low-voltage SPDT dry-contact relays |
| Wired communication | Independently supplied/isolated RS-485 and CAN ports; configurable termination |
| Service | Self-powered USB-C data, SWD/SWO, buttons, status/fault LEDs, test points and recoverable settings |
| Fault response | Rail supervision, external watchdog, asynchronous ARM clearing, hardware permission, command-owner timeout and explicit fresh rearming |

I retain both relay circuits and their existing power allocation. I may populate one relay first during staged assembly; that does not reduce the final channel count, change the released assembly variant, or justify using a smaller budget without review.

## Implementation and qualification order

| Milestone | Complete operating scope | Limits of the evidence |
| --- | --- | --- |
| M0 — capture preparation | Verify the retained architecture; close library/package and capacitor gates; complete native schematic and layout reviews | Documents and arithmetic do not establish physical operation |
| M1 — useful Modbus controller | Nominal 12/24 V, room-temperature acquisition, static outputs/relays, hardware shutdown, Modbus commands, service identity/diagnostics, host logging and calibration workflow | Record the actual loads, reference accuracy and tested conditions; no full 9–30 V/temperature claim |
| M2 — classic CAN | Versioned telemetry at 500 kbit/s with a documented peer/cable/termination fixture; Modbus retains actuator ownership | Does not establish CAN command control, CAN FD operation or universal cable length |
| M3 — bounded PWM | DO3 at 100 Hz and 10–90% command duty plus static endpoints, with qualified timing/current diagnostics and resistor/compatible LED fixture | Does not establish motor, proportional-solenoid or arbitrary lighting compatibility |
| M4 — full qualification | Close 9–30 V, 0–50 °C, combined loads, counting/accuracy, defined fault fixtures, CAN FD, enclosure, multiunit repeatability and soak targets | Publish only the conditions passed on the actual build |

DO3 operates as a static high-side output in M1/M2. Firmware rejects PWM mode until its implemented and qualified capabilities permit it. FD-capable silicon and populated transceivers do not make FD a tested capability. Supported functions, populated hardware and qualified functions need separate records.

M1 requires a working end-to-end application, not just successful programming or an attractive PCB render. I use the [implementation plan](Implementation_Plan.md), [protocol contract](../firmware/Protocol.md), [validation plan](Validation.md) and [portfolio evidence guide](Portfolio_Evidence.md) to record its completion.

## Deliberately outside this revision

I do not add wireless radios, Ethernet/PoE, battery charging/BMS, analog command outputs, a display, onboard loop power, mains interfaces, or a motor inverter to this revision. They require an application-specific scope change rather than a spare connector or an untested feature declaration.

The existing 0–10 V/4–20 mA inputs remain because they form a coherent industrial acquisition application. Their exact formats and channel counts are product choices; the [market review](Market_Alignment.md) does not establish repeated demand for those exact arrangements.

A later connected-I/O extension can be considered after the base controller works, especially if my earlier portfolio piece does not already demonstrate wireless design. An external gateway proves system integration; it does not establish onboard RF layout or battery-power expertise.

## Retained architecture and verification gates

On October 4, 2026 I chose to retain the complete current board and all selected functions. My [architecture review record](Architecture_Review.md) records that disposition and the remaining verification obligations. The current circuit documents and selection files are the electrical baseline; I do not plan a narrower variant for this capture.

I preserve the true DI/bus isolation boundaries, protection paths, powered-off behavior and hardware output inhibition. The auxiliary/threshold rails and receiving-domain buffers have real obligations in the selected design. Removing individual parts without resolving those obligations is not an accepted simplification.

Reduced assembly is a bring-up stage with its assembly identity recorded. It does not change the final specification or close the full-load verification requirements.

## Completion evidence

I require native CAD, matching assembly/manufacturing files, buildable target firmware, a diagnostic/calibration workflow, physical measurements and a concise application demonstration. Simulated host-tool outputs are labeled as development checks and cannot replace bench results.

My [validation record template](templates/Validation_Record.md) identifies the serial/revision, assembly variant, firmware, instruments, wiring, stimulus, uncertainty, observations and pass/fail result. Unperformed tests remain pending. Wider qualification and full hardware-release requirements remain in [validation](Validation.md) and [fabrication](../fabrication/README.md).
