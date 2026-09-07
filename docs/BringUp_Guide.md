# Bring-Up Guide — ESP32-S3 Protected Field I/O Controller Rev A
*Written 2026-09-07 from the design document; expected values will be re-derived from the as-built schematic at freeze and measured values recorded per board. Designators are the design document's per-sheet numbers.*

**Bench kit:** multimeter · bench supply with current limit (12 V / 100 mA to start) · the 24 VAC plug-in transformer (floating, 2-pin) · oscilloscope (needed from step 1 for ripple and the SW node) · thermocouple / temperature probe · the "resistor jig" for inputs (any 12–30 V DC source and the 24 VAC transformer) · sprinkler valve · 5 V pump · a battery-powered laptop or a USB isolator for step 4.

---

## 0. Rules before anything touches the board

1. **Inspect first, power second.** ×10 loupe over the whole board against the assembly drawing: module castellations and alignment to the silk outline, every polarity mark (C201 +, C901 +, every diode band, LED cathodes, opto pin-1 dots, relay orientation, U301 pin 1), bridges between the USB-C pins, tombstoned passives, starved or excess paste. Fix with iron, flux and wick **now** — the same fault found at step 1 costs the debugging session.
2. **Meter before power:** resistance from GND to each of VBUS_DC (TP1), 5V_BUCK (TP2), 5V_SYS (TP3), +3V3 (TP4), VLOAD (TP12) — kΩ-range and climbing as the capacitors charge, never a dead short.
3. **USB and field power together only with a floating supply** (the plug-in transformer, or a bench supply whose negative is not earthed) **or a battery-powered laptop.** With an earthed supply and an earthed laptop, the USB cable's ground bypasses the bridge's return diode and carries the board's return current. Design doc §17.
4. **An external VLOAD supply is not reverse-protected.** Meter its polarity before it meets J901; VLOAD + is marked on the silk.
5. **Nothing above 36 V DC / 28 VAC on PWR IN, nothing above 30 V on any other terminal, no mains anywhere.**

## 1. Quirks to keep in mind (what is "normal" for this board)

* **Relays do not click on USB power.** 5V_BUCK exists only with field power; on USB alone TP2 reads 0 V. This is the design working, not a fault.
* **5V_SYS is ≈ 4.6 V, not 5 V** — it sits behind a Schottky from either source. The LDO needs ≥ 3.6 V and is happy.
* **The buck's turn-on and turn-off voltages are ± 12 %** (EN threshold spread): expect start somewhere in 7.6–9.3 V at the terminal and stop in 6.7–8.3 V, light load. Record the pair per board.
* **The bulk capacitor sawtooths ≈ 3 V at 120 Hz on 24 VAC under load** — expected; the buck does not care.
* **An input reads ON only above ≈ 7.6 V** (opto LED + indicator LED + the current the pull-up needs). Below that it reads OFF by design.
* **An AC input's collector node ripples ≤ 0.7 V** during each zero-crossing gap; the GPIO reads a steady LOW. If it ripples to 2 V, C70x is not the 4.7 µF part.
* **First detect on an AC input takes one cycle (≈ 25 ms); release takes ≈ 140 ms** — the RC, then the 3-sample firmware debounce on top.
* **The bridge runs warm at low DC input under full load** (1–1.5 W at 9–12 V). At 24 V and above it is cool.
* **The LDO runs warm during sustained Wi-Fi transmit** (≈ 0.46 W peaks). Thermal shutdown at 160 °C protects it; record its temperature in step 7.
* **The buck is in PFM at light load** (S variant): a faintly audible or scope-visible burst pattern with nothing connected is normal.

## 2. Probe points

| Net | TP | Backup pad | Net | TP | Backup pad |
|---|---|---|---|---|---|
| VBUS_DC | TP1 | C201 + | VLOAD | TP12 | C901 + / J901 pin 1 |
| 5V_BUCK | TP2 | C305–C307 | VIN_SENSE | TP13 | C203 |
| 5V_SYS | TP3 | C503 | PG | TP14 | U301 pin 6 |
| +3V3 | TP4 | C502 / C601 | EN | TP8 | C603 / R601 junction |
| GND | TP5, TP6\* | J901 GND pin, USB shell | IO0 | TP9 | R602 / SW601 junction |
| SW | TP7 (small) | — never probe ripple here | TXD0 / RXD0 | TP10\*, TP11\* | module pins 37 / 36 |

\* Through-hole 1.0 mm pads. **Recovery UART:** adapter TXD → TP11 (RXD0), adapter RXD → TP10 (TXD0), GND → TP6; 115200 baud; to flash, hold BOOT (SW601) and tap RESET (SW602). 3.3 V logic only — never connect an adapter's 5 V / 3V3 power pins.

## 3. Sequence (staged — film the last step)

**A — no power**
1. Inspection per rule 0.1; polarity table ticked.
2. Resistance checks per rule 0.2.

**B — 12 V DC, current-limited, no loads, no USB**
3. Bench supply 12.0 V, limit 100 mA, either polarity into J201. Expected: **TP1 ≈ 10.5 V** (12 − 2 × 0.7), FIELD PWR LED on, **TP2 = 5.00 V ± 3 %** (4.85–5.15), **TP3 ≈ 4.6 V**, **TP4 = 3.30 V**, 3V3 LED on, input current ≈ 30–60 mA (module booting, PFM). Swap the input polarity: identical.
4. Scope on TP2 (AC-coupled, 20 mV/div, 1 µs/div, short ground spring): ripple **< 50 mVpp** (expect ≈ 10–20 mV with the probe's own pickup). Scope on TP7 (SW, ×10 probe, 10 V/div): a clean 0 → ≈ 10.5 V rectangle at 400 kHz in PWM, or bursts in PFM; overshoot < 3 V. Note the frequency.
5. 24 V DC then 36 V DC: rails again (TP1 ≈ 22.6 / 34.6 V), SW amplitude follows the bus, ripple still < 50 mVpp, U301 and L301 warmth by touch after two minutes.
6. **UVLO:** from 12 V, lower the supply slowly. Record the terminal voltage at which the FIELD PWR LED dies (**expect 6.7–8.3 V, ≈ 7.6 V typical**) — it must stop cleanly, no flicker. Raise it slowly; record the restart (**expect 7.6–9.3 V, ≈ 8.5 V typical**). Then the 10 V DC cold start: supply preset to 10.0 V, switch on — the board must start.

**C — 24 VAC**
7. Plug-in 24 VAC transformer into J201. TP1 on the scope (DC-coupled): ≈ 30–34 V with a ≈ 1 V sawtooth unloaded; rails as in step 3. Leave it five minutes; C201 and BR201 warmth by touch (barely).
8. Load 5V_BUCK with ≈ 0.8 A (a 6 Ω / 5 W resistor across TP2–GND, or the pump + both relays later): TP1 sawtooth grows to ≈ 3 V at 120 Hz, TP2 stays 5.00 ± 3 %, ripple < 50 mVpp. Buck and bridge temperatures with the probe after five minutes — record.

**D — USB only**
9. Field power off, USB in from a battery laptop. Expected: **TP3 ≈ 4.6 V, TP4 = 3.30 V, TP2 = 0 V, TP12 = 0 V.** Board enumerates as a USB serial device; flash a blink build. Command a relay: it must **not** click (no supply). This step proves the split rail.
10. Field power on again with USB still in (floating transformer): rails unchanged, no reset, both Schottkys sharing TP3.

**E — inputs**
11. 24 V DC between IN1 and COM, either polarity: field LED D705 lights, firmware reads ON, TP-less check of IN1_L at C701: ≈ 0.1 V. Reverse the polarity: identical. Repeat IN2–IN4.
12. 24 VAC between IN1 and COM: LED lights (half-wave, looks steady), firmware reads a **steady ON**; scope IN1_L at C701: a sawtooth that never exceeds ≈ 0.7 V. Remove the source: reads OFF after ≈ 150 ms.
13. 12 V DC on each input (the low corner): LED dim but visible, firmware reads ON, IN1_L < 0.3 V. 7 V DC: reads OFF (below threshold, by design).

**F — outputs**
14. Relay click test from firmware, K1 then K2; the coil LED follows. Meter continuity NO–C and NC–C in both states. Then the real sprinkler valve on K1 NO / C from the 24 VAC transformer: it opens and closes; no reset on the board (watch TP2 on the scope at the click — a few tens of mV dip at most).
15. Pump on OUT1 with JP901 closed: runs; note the inrush dip on TP2 (should stay > 4.7 V thanks to C901). OUT2 with a buzzer or LED.

**G — torture and demo**
16. **10-minute torture loop:** Wi-Fi ping flood from the laptop, both relays toggling at 1 Hz, pump on. Watch the log's reset reason; zero resets is the pass. At minute 10, temperatures with the probe: U301, L301, BR201, U501, K801/K802 coil area, C201 — record all six.
17. **The demo take,** one cut: 24 VAC transformer → float switch trips IN1 and its LED → K1 clicks the valve open → pump runs on OUT1 → scope shots of TP2 ripple and TP7 → thermal check.

## 4. Troubleshooting quick table

| Symptom | First suspects |
|---|---|
| Nothing at TP1 | F201 tripped (let it cool), BR201 orientation, J201 wire not clamped |
| TP1 fine, TP2 = 0, FIELD PWR LED off | UVLO divider (R304/R305 values, EN pin voltage < 1.25 V?), R301 (RT) open or wrong → the part stays off, U301 pin 1 not grounded, C303 missing |
| TP2 wrong voltage | R302/R303 swapped (2.5 V or 8 V tells you which), FB trace tapped at the inductor |
| TP2 fine but noisy / > 50 mVpp | probe ground lead too long (use the spring); C305–C307 not X7R / wrong voltage rating; hot-loop layout |
| Buck restarts every few seconds (hiccup) | output short, L301 saturating (wrong inductor), C201 reversed |
| Board resets when a relay closes | 5V_SYS sag: D301 / C503; check TP3 on the scope at the click |
| Relay clicks on USB power | D301 / D402 wiring — 5V_BUCK is tied to 5V_SYS somewhere it should not be |
| Input never reads ON | R701/R702 open, D701 backwards (steals the current), opto orientation, R709 missing |
| Input reads ON with nothing connected | C70x leaking / opto collector-emitter swapped, pull-up missing |
| AC input chatters | C70x is 1 µF not 4.7 µF; firmware debounce not running |
| Relay energised at boot | wrong pin (a pull-up-at-reset pin), R802/R804 missing |
| MOSFET output stuck on | R902/R904 missing, gate pin with a default pull-up |
| No USB enumeration | cable, J401 GND pins, D+/D− continuity through R401/R402, drivers — Board 1's table |
| LDO very hot | sustained TX at the 4.6 V rail is ≈ 0.46 W; airflow/copper; brief is fine |

## 5. Record sheet (one per board)

| Item | Expected | Board 1 | Board 2 | Board 3 | Board 4 | Board 5 |
|---|---|---|---|---|---|---|
| TP1 at 12 V DC | ≈ 10.5 V | | | | | |
| TP2 5V_BUCK | 4.85–5.15 V | | | | | |
| TP2 ripple at 0.8 A | < 50 mVpp | | | | | |
| SW frequency | ≈ 400 kHz | | | | | |
| TP3 5V_SYS | ≈ 4.4–4.85 V | | | | | |
| TP4 +3V3 | 3.30 V ± 2 % | | | | | |
| UVLO stop / start (terminal) | ≈ 7.6 / ≈ 8.5 V | | | | | |
| 10 V DC cold start | yes | | | | | |
| 24 VAC TP1 sawtooth at 0.8 A | ≈ 3 V | | | | | |
| USB-only: TP2 | 0 V, relays silent | | | | | |
| IN1–IN4 at 24 V DC / 24 VAC / 12 V DC | ON / ON / ON | | | | | |
| IN1_L ripple on AC | ≤ 0.7 V | | | | | |
| Torture loop resets | 0 | | | | | |
| Temps: U301 / L301 / BR201 / U501 | record | | | | | |
