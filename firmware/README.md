# Firmware — Rev A

**Status: no code yet — by design.** Board 1's sketch was written against its hardware contract before the boards landed; this board follows the same order: the contract first, here, then the sketch after the schematic is frozen and the pin map is final, then measurements from the first article replace every "expected" number.

The sketch will live in `field_io/`, Arduino IDE, split across files exactly like Board 1's `plant_monitor/` (`config.h` for every number the board imposes, `secrets.h` gitignored, `net.cpp` reused for Wi-Fi, MQTT and Home Assistant discovery). Pin assignments are in [`../docs/PinMap_CheatSheet.md`](../docs/PinMap_CheatSheet.md).

---

## The hardware contract

What the *board* requires of the firmware, written down before any code exists so the safety behaviour is on record either way.

| Duty | Rule | Why, and where it comes from |
|---|---|---|
| **Outputs at boot** | IO9, IO10 (relays) and IO11, IO12 (MOSFETs) are left as inputs (high-impedance) until firmware deliberately drives them; hardware 10 kΩ pull-downs hold everything OFF. Configure outputs only after the first VIN_SENSE reading. Never write a HIGH as part of "initialise". | Design doc §9, §10 — no relay chatter at boot, ever. The pins were chosen from the ESP32-S3's no-default-pull set; the pull-downs handle the ≈ 60 µs power-up glitches |
| **Field-power gating** | `field_power_present = VIN_SENSE_volts > 7.0`. Below it: report it, refuse output commands with a reason, keep listening. | The relays physically cannot work without 5V_BUCK (they hang on the buck output, not the USB-fed logic rail); this makes the log say why |
| **VIN_SENSE scaling** | `V_bus = adc_mV × 21 / 1000` (2 × 100 k / 10 k divider; ADC1_CH7, attenuation 3, 0–2900 mV). Calibrate the ratio against a meter on TP1 at bring-up and store it as `VIN_TRIM`. | Design doc §3 |
| **Input debounce** | An input changes state only after **3 consecutive samples 10 ms apart** agree. Inputs are active LOW at the GPIO. Works identically for AC and DC sources — the 4.7 µF makes 60 Hz a steady LOW; the debounce cleans the edge. | Design doc §8 |
| **Relay interlocks** | Deployment config declares mutually exclusive relays (heat vs cool) and a **minimum off-time per relay (default 300 s)** — the compressor short-cycle lockout. Enforced before any relay write, including from MQTT. | Use cases 2–3 |
| **Supervisory, never the safety device** | The condensate use case trips K2 (NC) and alerts *in series with* the OEM float-switch interlock. Nothing in the firmware, the logs or the Home Assistant entity names calls this board an interlock or a safety device. | Second-opinion review, item 10 |
| **Safe state on link loss** | Per relay: hold / open / close after N minutes without the broker. Default **hold**. Per MOSFET output: default **off** after N minutes. | An overflow guard must not stop guarding because Wi-Fi dropped; a pump must not run forever because the broker died |
| **OTA** | ArduinoOTA (or ESP-IDF OTA) enabled, password-protected, on the field network. **USB is a bench port** — the silk says DISCONNECT FIELD POWER BEFORE USB. | Design doc §17: ground loop through USB with an earthed field supply |
| **Watchdog** | Task watchdog enabled on the main loop; **reset reason** read at boot and published with the first status message. | Torture-loop acceptance criterion: zero resets, and proof of it |
| **Telemetry** | Publish: `vin_volts`, `field_power`, `in1..in4`, `k1`, `k2`, `out1`, `out2`, `reset_reason`, `uptime`, `rssi`, `temp` (internal sensor). Retained status, Home Assistant discovery for every entity. | Board 1's `net.cpp` pattern |
| **Indicator LEDs** | STATUS LED (IO13): slow blink = booting/connecting, solid = connected, fast blink = no field power. Relay and output LEDs are hardware — they follow the drive pins with no code. Input LEDs are hardware on the field side. | Design doc §7–§10 |
| **Never** | drive an output HIGH from an interrupt or a callback without passing the interlock; PWM a MOSFET output above 1 kHz; assume USB is present in the field. | |

## What one loop iteration does

There is a `loop()` on this board — it is powered, always on, and must react within tens of milliseconds.

1. Sample the four inputs (every 10 ms), run the debounce, publish on change.
2. Read VIN_SENSE (every 1 s), update `field_power_present`.
3. Service MQTT / commands; every output write passes the interlock and the field-power gate.
4. Age the link-loss timers; apply safe states if they expire.
5. Feed the watchdog. Publish the status heartbeat every 60 s.

## Bring-up firmware, in order

1. **blink** — STATUS LED only, over USB with no field power (bring-up step 9).
2. **rails** — prints VIN_SENSE and the internal temperature; used through steps 3–8.
3. **inputs** — prints raw and debounced input states; used in steps 11–13.
4. **outputs** — serial commands `k1 on`, `pump on` … with the interlock active; steps 14–15.
5. **torture** — the full sketch plus a ping-flood target and a 1 Hz relay toggle; step 16.

## Board settings (Arduino IDE, same as Board 1)

ESP32S3 Dev Module · USB CDC On Boot **Enabled** · USB Mode **Hardware CDC and JTAG** · Flash 8 MB · PSRAM **Disabled** (N8) · partition **8M with spiffs** · 240 MHz. If it will not enter the bootloader on its own: hold **SW601 (BOOT)**, tap **SW602 (RESET)**, release, upload.
