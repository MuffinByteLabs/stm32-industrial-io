# Pin Map Cheat Sheet — ESP32-S3 Protected Field I/O Controller Rev A
*Written 2026-09-07 from the design document, before capture. Designators use per-sheet numbering (2xx = sheet 02 …). If capture changes a pin, change it here the same day — this file is what the firmware is written against.*

## At a glance

* **Inputs (active LOW at the GPIO):** IN1 = **IO4** · IN2 = **IO5** · IN3 = **IO6** · IN4 = **IO7**. Opto collector nodes `IN1_L`…`IN4_L`, 47 k pull-up + 1 µF (τ = 47 ms). Field side: Zener + 2 × 1.6 k + LED + opto — IEC 61131-2 Type 1 thresholds. Debounce in firmware: 3 samples 10 ms apart.
* **Relays (active HIGH):** K1 = **IO9** (`RLY1`) · K2 = **IO10** (`RLY2`). 680 Ω base, 10 k pull-down → OFF at boot.
* **MOSFETs (active HIGH):** OUT1 = **IO11** · OUT2 = **IO12**. 100 Ω gate, 10 k pull-down → OFF at boot.
* **Status LED:** **IO13** (`STATUS_LED`, 1 k, yellow-green).
* **Input-voltage sense:** **IO8 = ADC1_CH7**, `VIN_SENSE` = VBUS_DC × 10 / 210 (**÷ 21**). 9 V → 0.43 V · 24 V → 1.14 V · 39 V → 1.86 V · 69 V clamp → 3.29 V (pin safe). Attenuation 3 (0–2.9 V), 100 nF at the pin. "Field power present" = VBUS_DC > 7 V, i.e. VIN_SENSE > 0.33 V.
* **USB (native):** IO19 = D− (`USB_DN`) · IO20 = D+ (`USB_DP`). No bridge chip.
* **Buttons:** **SW601 = BOOT** (IO0) · **SW602 = RESET** (EN). Same convention as Board 1.
* **Recovery UART:** TXD0 = IO43 → TP10 · RXD0 = IO44 → TP11 · GND → TP6 (all through-hole). 115200 baud, 3.3 V logic only.
* **Expansion (DNP header J601):** 3V3 · GND · IO14 · IO16 · IO17 · IO18.
* **Strapping pins** IO0 (pull-up, BOOT), IO3, IO45, IO46: nothing else on them. **IO1, IO2 unused on purpose** — pulled up at reset.

## Module pins used (U601, ESP32-S3-WROOM-1-N8)

| Pin | Name | Net | Role | Pull at reset |
|---|---|---|---|---|
| 1, 40, 41 | GND / EPAD | GND | Ground + thermal | — |
| 2 | 3V3 | +3V3 | Power (C601 22 µF + C602 100 nF at the pin) | — |
| 3 | EN | EN | R601 10 k up, C603 1 µF, SW602 | — |
| 4 | IO4 | IN1_L | Opto 1 | none |
| 5 | IO5 | IN2_L | Opto 2 | none |
| 6 | IO6 | IN3_L | Opto 3 | none |
| 7 | IO7 | IN4_L | Opto 4 | none |
| 9 | IO16 | EXP2 | J601 (DNP) | none |
| 10 | IO17 | EXP3 | J601 (DNP) | none |
| 11 | IO18 | EXP4 | J601 (DNP) | none |
| 12 | IO8 | VIN_SENSE | ADC1_CH7 | none |
| 13 | IO19 | USB_DN | USB D− (22 Ω R401 in line) | USB |
| 14 | IO20 | USB_DP | USB D+ (22 Ω R402 in line) | USB |
| 17 | IO9 | RLY1 | K1 driver | none |
| 18 | IO10 | RLY2 | K2 driver | none |
| 19 | IO11 | OUT1 | Q901 gate | none |
| 20 | IO12 | OUT2 | Q902 gate | none |
| 21 | IO13 | STATUS_LED | D602 | none |
| 22 | IO14 | EXP1 | J601 (DNP) | none |
| 27 | IO0 | IO0 | Boot strap, R602 10 k up, SW601 | pull-up |
| 36 | RXD0 (IO44) | RXD0 | TP11 | pull-up |
| 37 | TXD0 (IO43) | TXD0 | TP10 | pull-up |
| 8, 15, 16, 23–26, 28–35, 38, 39 | IO15, IO3, IO46, IO21, IO47, IO48, IO45, IO35–IO42, IO2, IO1 | — | Unconnected | see datasheet |

*Verify pin numbers against the module datasheet in `references/datasheets/` during capture — the table follows Board 1's verified numbering for the pins it shares (2, 3, 13, 14, 27, 36, 37) and the datasheet's order for the rest.*

## Net glossary

| Net | Meaning |
|---|---|
| FLD_PWR_A / FLD_PWR_B | Power terminal pins, before F201 and the bridge; either polarity, or AC |
| VBUS_DC | Rectified bus, 7–39 V; TP1 |
| VIN_SENSE | VBUS_DC ÷ 21 → IO8; TP13 |
| 5V_BUCK | Buck output 5.02 V — relay coils, JP901/VLOAD, FIELD PWR LED; TP2 |
| 5V_SYS | Logic rail ≈ 4.6 V, OR of 5V_BUCK (D301) and USB_5V_PROT (D402); TP3 |
| USB_VBUS / USB_5V_PROT | USB 5 V before / after F401 + D401 |
| +3V3 | AP7361C output; TP4 |
| VLOAD | Load supply terminal: 5V_BUCK via JP901 (open by default), or external 8–12 V; TP12 |
| SW / BOOT / FB / EN_BUCK / RT / PG | Buck nodes; SW → TP7 (small pad), PG → TP14 |
| IN1–IN4, FLD_COM | Field-side input nets (isolated) |
| IN1_L–IN4_L | Logic-side opto collector nodes (active LOW) |
| RLY1 / RLY2, K1_COIL / K2_COIL | GPIO drives / transistor collectors |
| K1_NO / K1_COM / K1_NC, K2_… | Relay contact nets (isolated, field side) |
| OUT1 / OUT2, OUT1_D / OUT2_D | GPIO drives / MOSFET drains (terminal pins) |
| EN / IO0 / TXD0 / RXD0 / USB_DP / USB_DN | Board 1's names, unchanged |

## Terminals (all 5.08 mm screw terminals)

| Ref | Positions | Labels (left → right) | Side | Notes |
|---|---|---|---|---|
| J201 | 2 | PWR IN A · B | field | 12–36 V DC either way (10 V guaranteed floor), or 24 VAC (18–28) |
| J701 | 5 | IN1 · IN2 · IN3 · IN4 · COM | field | 12–30 V AC/DC signals to COM, either polarity; IEC 61131-2 Type 1 (OFF ≤ 5 V, ON ≥ 15 V; threshold ≈ 8 V); 36 V continuous max |
| J801 | 3 | K1: NO · C · NC | field | ≤ 2 A, ≤ 30 V AC/DC, isolated |
| J802 | 3 | K2: NO · C · NC | field | same |
| J901 | 4 | VLOAD+ · GND · OUT1− · OUT2− | **logic** | not isolated; VLOAD = 5 V only with JP901 closed, else external 8–12 V returned to GND; **meter polarity first** |
| J401 | — | USB-C | logic | bench programming only — **DISCONNECT FIELD POWER BEFORE USB** (silk) |
| J601 | 6 | 3V3 · GND · IO14 · IO16 · IO17 · IO18 | logic | DNP |

## Test points

TP1 VBUS_DC · TP2 5V_BUCK · TP3 5V_SYS · TP4 +3V3 · TP5 GND · TP6 GND (THT) · TP7 SW (small) · TP8 EN · TP9 IO0 · TP10 TXD0 (THT) · TP11 RXD0 (THT) · TP12 VLOAD · TP13 VIN_SENSE · TP14 PG.
