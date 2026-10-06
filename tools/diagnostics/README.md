# FieldIO host diagnostics

The Python CLI reads identity, coherent acquisition/status snapshots and latched raw ADC captures, records CSV, and sends explicit actuator commands against [protocol 1.0 / map revision 1](../../firmware/Protocol.md). Target STM32 firmware is still pending. The runnable simulator supplies synthetic register/frame examples for developing the host software. Its output is marked **SIMULATED** and cannot support a board rating, accuracy result or prototype qualification.

## Start with simulation

Run from the repository root with Python 3.12 or later. These commands need only the standard library:

```powershell
python tools/diagnostics/fieldio_cli.py --simulate
python tools/diagnostics/fieldio_cli.py --simulate identity
python tools/diagnostics/fieldio_cli.py --simulate raw
python tools/diagnostics/fieldio_cli.py --simulate log --csv out/diagnostics/SIMULATED-acquisition.csv --samples 25
python -m unittest discover -s tools/diagnostics/tests -v
```

Omitting the command selects a read-only snapshot. CSV creation refuses to overwrite an existing file. Every row includes evidence type, receipt UTC, UID, firmware/build/hardware identity, boot ID, implemented/qualified masks, acquisition sequence/uptime, validity, faults, units and sample ages. Unavailable or stale samples become empty fields. A snapshot is enclosed by identity reads; a reset or build/capability change discards the ambiguous sample and retries up to three times. Repeated instability stops the recording. A failure can leave a usable partial CSV containing only earlier completed rows.

Polling defaults to 5 Hz. Publication in target firmware is planned at 100 Hz, while the host observes snapshots at the rate permitted by the serial link. Host UTC marks receipt; capture uptime and ages describe acquisition timing. Identity reads do not replace the raw latch, so raw capture preserves one matching generation across both blocks.

## Explicit command exercise

The simulator starts READY, disarmed, with synthetic static-output/relay qualification bits. Its PWM qualification is clear. An optional state file lets separate invocations share the same simulated device:

```powershell
python tools/diagnostics/fieldio_cli.py --simulate --simulation-state out/diagnostics/SIMULATED-state.json arm --lease-ms 5000
python tools/diagnostics/fieldio_cli.py --simulate --simulation-state out/diagnostics/SIMULATED-state.json set --outputs 0b1001 --relays 0b10 --lease-ms 5000
python tools/diagnostics/fieldio_cli.py --simulate --simulation-state out/diagnostics/SIMULATED-state.json snapshot
python tools/diagnostics/fieldio_cli.py --simulate --simulation-state out/diagnostics/SIMULATED-state.json disarm
```

Run SET within the explicit lease. ARM clears all commands and grants permission without energizing an output. SET specifies the complete DO1–DO4 and relay1–2 masks; omitted masks mean all off. The example selects DO1, DO4 and relay2 coil. Relay telemetry reports coil commands, not measured contact position.

Reads and CSV logging do not renew the lease. There is no automatic arming, recovery, command retry or background heartbeat. `keepalive` is an explicit one-shot verb that preserves commands and renews only an already valid Modbus-owned lease. Expiry disarms the simulated device, clears output commands and advances the epoch; explicit DISARM acknowledges its recoverable lease fault before fresh ARM/SET. Simulation files contain synthetic state only and are not board configuration records.

The host confirms accepted sequence/result together with unchanged session/epoch, ARMED ownership/health/live lease and the complete requested applied state. A target that echoes a write but publishes a different epoch/state/mask is reported as an uncertain outcome, without another mutation. Explicit rearming follows READY → ARM with zero commands → confirmed ARMED → SET; no output command is queued before ARM.

The normal `disarm` uses the guarded atomic command. `disarm --unconditional` sends the documented FC06 stop to the selected unicast address without boot/epoch/sequence guards; it cannot energize or renew an output. This CLI disables broadcasts. Unconditional disarm also provides the per-epoch command-sequence exhaustion escape. An exhausted control epoch leaves commands inhibited pending service.

`set --pwm-permille 500` would request 100 Hz / 50% DO3 PWM. It is rejected unless both high-side and PWM capabilities are implemented **and physically qualified** in device identity. DO3's static bit must be clear for PWM. Static DO3 OFF/ON use the ordinary DO mask. The tests model a future qualified PWM identity; there is no CLI option that changes a physical device's qualification metadata.

## Connect to a future target

Install the local optional dependency only for a serial connection:

```powershell
python -m pip install -r tools/diagnostics/requirements.txt
python tools/diagnostics/fieldio_cli.py --port COM5 identity
python tools/diagnostics/fieldio_cli.py --port COM5 snapshot
python tools/diagnostics/fieldio_cli.py --port COM5 raw
python tools/diagnostics/fieldio_cli.py --port COM5 log --csv out/diagnostics/acquisition.csv --samples 100
```

Choose the actual USB-to-RS-485 adapter port. Defaults are unit 1, 19,200 bit/s and 8E1; `--address`, `--baud` and `--timeout` are explicit overrides. The adapter must handle half-duplex direction and provide responses without local transmit echo. Wiring, RS485_REF, termination, external board power and the disarmed fixture follow [Interfaces](../../docs/Interfaces.md) and [Validation](../../docs/Validation.md). This serial adapter connection does not implement the board's future USB CDC service.

The codec checks CRC, address, function, exception shape, byte count, exact response length and write echo. The serial adapter spaces transactions and bounds response reads. Physical turnaround/intercharacter timing, noise recovery, adapter behavior and target frame handling remain bench checks. A write timeout or malformed response can occur after the target accepted a command: the CLI reports an uncertain outcome and never retries that mutation. Read state or choose a fresh explicit disarm.

Use a verified adapter without local echo: an FC06 response is byte-identical to its request, so echo alone cannot prove target acknowledgement. Full state readback confirms inhibited outputs; physical stop timing still needs connector/load measurements. The driver rejects nonfinite or nonpositive response deadlines. The traceable snapshot requires 231 request/response bytes before RTU gaps/turnaround, so 5 Hz is a requested ceiling; slower baud or adapter timing extends each cycle. Choose and measure a lease that covers command preflight/confirmation and explicit renewals, rather than assuming a 500 ms lease works with every supported baud.

Device observations are labeled **SERIAL_DEVICE_OBSERVATION_UNQUALIFIED**. A device-reported qualification bit must trace to release records; running this tool alone cannot establish qualification. Target commands require compatible identity, nonzero boot/epoch, fresh per-epoch sequence, permitted owner/state, health and qualified requested actuator capabilities. Physical PERMISSION remains a target/hardware requirement.

## Calibration capture and offline fit

Use `raw` in a stable disarmed fixture with a stated reference stimulus and uncertainty, keeping the identity, snapshot, ranges, validity, ages and raw codes together. Raw ADC `0xFFFF` can be a valid full-scale code; its validity and range fields determine interpretation. Raw data is accepted only when its sequence matches the latched snapshot. The simulator's fixed values are parsing examples.

Calculate a two-point engineering gain/offset without opening a device connection:

```powershell
python tools/diagnostics/fieldio_cli.py calibration-fit --raw-low 100 --reference-low 0 --raw-high 64100 --reference-high 10000 --unit mV
```

The equation is `engineering_value = gain_per_raw_code × raw_adc_code + offset`. The CLI accepts mV or µA references and rejects identical/raw-out-of-range points, nonfinite references and nonpositive slopes. This output is an offline calculation, with no device write. Device Q16.16 quantization, range matching, coefficient-record readback/CRC/commit, reference uncertainty, independent verification points and temperature qualification remain staged target work. The CLI does not write configuration or calibration records.

## Files and verification limits

`fieldio_cli.py` contains the CLI/CSV/offline fit; `fieldio.py` implements the application map and guards; `rtu.py` encodes and checks frames; `serial_transport.py` imports optional pySerial only on live connection; `simulation.py` provides synthetic device state. The standard-library tests cover malformed frames/CRC, response matching, immutable snapshot/raw generation, validity/staleness, read-only logging and resets, guarded commands/ownership, epoch/sequence handling, lease expiry and PWM prerequisites. Additional cases reject an accepted-result response with a different applied epoch/state/mask, invalid serial deadlines and overflowing offline coefficients. These are host/model software tests. No target firmware, serial adapter or PCB has been validated by them.

Protocol/adapter references: [Modbus application specification](https://www.modbus.org/file/secure/modbusprotocolspecification.pdf), [Modbus serial guide](https://www.modbus.org/file/secure/modbusoverserial.pdf), [pySerial API](https://pyserial.readthedocs.io/en/latest/pyserial_api.html).
