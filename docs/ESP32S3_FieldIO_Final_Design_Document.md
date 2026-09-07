# ESP32-S3 Protected Field I/O Controller — Rev A Design Document

**Board:** target ≈ 100 × 70 mm (must stay ≤ 100 × 100 mm) · **2-layer**, 1 oz · 1.6 mm · lead-free HASL · bare PCB + stencil from JLCPCB, **assembled on the bench** (Sn63/Pb37 hot-plate reflow, through-hole by iron)

**Status:** written 2026-09-07, **before schematic capture** · verified against PCB Freelance Plan v7.3 §4 — every departure from that spec is recorded in [`reviews/Spec_Review_RevA_2026-09-07.md`](reviews/Spec_Review_RevA_2026-09-07.md) · a second, independent review the same day was weighed point by point in [`reviews/Second_Opinion_Review_RevA_2026-09-07.md`](reviews/Second_Opinion_Review_RevA_2026-09-07.md) and its adopted items are folded in below · both are summarised in Addendum A · the arithmetic behind every number is in [`calcs/board2_calcs.py`](calcs/board2_calcs.py)

> **Reference designators use per-sheet numbering** (sheet 02 → 2xx, sheet 03 → 3xx …). Set KiCad's *Annotate → Use first free number after* to 200 / 300 / … per sheet and the designators below survive capture unchanged. If the schematic ends up numbered differently, regenerate the BOM from the schematic and record the cross-map in an Addendum — exactly as Board 1 had to.

*This document is the single complete description of the board: what it does, how each circuit works, every component and why it is there, and how the design will be captured, manufactured, assembled and brought to life. It is organised to match the KiCad hierarchical schematic sheets, so each section becomes one sheet.*

*Plain-language rule used throughout, as on Board 1: every abbreviation is expanded where it appears, and repeated later, so no section requires remembering a definition from another section.*

## 1. Project Overview

Goal: a Wi-Fi board that safely **hears** 12–30 V equipment signals and safely **presses** equipment buttons. It is the board that HVAC thermostat wiring, 24 VAC valves and pumps, sprinkler zones, float switches and 12 V vehicle circuits are all asking for. It runs from the equipment's own power — 24 VAC from the furnace transformer, or 10–36 V DC — and reports and acts over Wi-Fi.

The board is the second portfolio project. Its **one new hard thing** is a buck converter laid out on two layers; everything else is either a block copied from Board 1 (the ESP32-S3 core, the USB-C block, the 3.3 V regulator) or a forgiving three-to-five-part circuit (opto input, relay driver, MOSFET switch). It is also the first board assembled on the bench rather than at the fab, so the design carries the assembly method's rules: every reflowed part on the top side, nothing finer than 0.5 mm pitch, no leadless packages that cannot be inspected, and through-hole for anything with a screw, a coil or a can.

### What the board does

- Accepts **12–36 V DC (either polarity) or 24 VAC** on a screw terminal — guaranteed to start and run at full load from 10 V DC — and makes its own 5 V and 3.3 V from it.
- Reads **four opto-isolated inputs** on a shared common: "is 12–30 V present on this wire?" — AC or DC, either polarity, galvanically separated from the logic, with **IEC 61131-2 Type 1 thresholds** (OFF ≤ 5 V, ON ≥ 15 V).
- Switches **two relay contact sets** (single-pole double-throw, NO/COM/NC all on terminals), rated on this board for ≤ 2 A at ≤ 30 V AC or DC, galvanically separated from the logic.
- Switches **two low-side MOSFET outputs** for pumps, buzzers and LED strips that share the board's ground, from the board's 5 V or from an external 8–12 V supply.
- Is programmed over **USB-C** on the bench; the same port never powers the field loads.
- Reports its own **input voltage** so "the board keeps resetting" can be diagnosed from the log.
- Wakes with **every output OFF**, every time, by hardware — no relay chatter at boot.

### One board, six use cases (nothing on the copper changes)

| # | Use case | Wired to | Output | Job cluster |
|---|---|---|---|---|
| 1 | HVAC runtime monitor (listen-only) | IN1–IN3 = W/Y/G, COM = C | none — runtime data, filter reminders, short-cycle alerts | HVAC wiring, read-only |
| 2 | Whole-house air circulation | schedule | K1 in parallel with the fan wire | HVAC (additive control) |
| 3 | AC condensate overflow supervisor | IN4 = float switch | K2 in series with the cooling wire (NC), **in addition to** the OEM float-switch interlock, never instead of it | HVAC + safety switches |
| 4 | One sprinkler zone | schedule / Board 1's "dry" message | K1 switches 24 VAC to the valve | irrigation |
| 5 | Water-leak alarm | IN = leak pads | buzzer on OUT1, phone alert | flood alarms |
| 6 | Plant waterer | Board 1 + float switch | pump on OUT1 | dispensers |

Use cases 1–3 fit one physical board at once (three monitor inputs + the float switch = four inputs; fan relay + cooling relay = two relays). That is why the count is 4-in / 2-relay and locked.

### What the board refuses, permanently

Mains voltage of any kind. RS-485. Battery operation. Current sensing. More channels. Per-channel fusing. The relay contact rating is stated as **≤ 2 A at ≤ 30 V** on the silkscreen and in this document, whatever the relay's own datasheet prints.

### Success criteria (the bench acceptance, in order)

1. 5V_BUCK = **5.00 V ± 3 %**, ripple **< 50 mV peak-to-peak** at a **1.25 A** test load (design point 1.1 A continuous, worst-case budget 0.95 A), on 12 V DC, 36 V DC and the 24 VAC wall transformer.
2. Clean cold start at **10 V DC** (the guaranteed floor behind the published 12 V) and on the 24 VAC transformer; clean shutdown and restart when the input is ramped down and up (no chatter).
3. Flashes over USB with **no field power**, and with USB alone the relays and VLOAD are dead.
4. All four inputs read a 24 V DC and a 24 VAC source as a steady ON, and read open as OFF.
5. Both relays click a real 24 VAC sprinkler valve; a pump runs on OUT1.
6. **Zero resets** through a 10-minute torture loop: Wi-Fi ping flood, both relays toggling at 1 Hz, pump on; buck and LDO temperatures recorded.
7. The demo take, one cut: 24 VAC transformer powers the board → float switch trips IN1 and its LED → relay clicks the valve open → pump runs on OUT1 → scope shots of 5 V ripple and the SW node → thermal check.

## 2. System Architecture — Sheet 01_System

The top sheet holds no components: one block per sub-sheet, connected by named nets. A net is simply a named wire; two points with the same net name are electrically the same wire, even across sheets.

### Two sides and a moat

The board has a **field side** and a **logic side** with a visible ≥ 2.5 mm copper-free moat between them, drawn on the silkscreen and labelled. Nothing crosses the moat except the four optocouplers (light crosses, copper does not) and the two relays (a magnetic field crosses; the coil pins sit on the logic side, the contact pins on the field side).

- **Field side:** the power-entry terminal and its rectifier, the four opto inputs, the two relay contact groups.
- **Logic side:** the DC bus after the rectifier, the buck converter, the USB-C block, the 3.3 V regulator, the ESP32-S3, the indicator LEDs, the relay coils and drivers, and the two MOSFET outputs.

One honest detail, stated the same way on the silkscreen: **the power input is not isolated from the logic ground.** The bridge rectifier's negative output *is* board ground. The opto inputs and the relay contacts are isolated; the MOSFET outputs are not. Section 17 spells out what that means for wiring.

### Power flow, in one paragraph

Field power (24 VAC or 10–36 V DC, either way round) enters at J201, passes a resettable fuse and a full bridge rectifier, and becomes the **DC bus**, net VBUS_DC, held up by a 470 µF electrolytic and clamped by a 43 V transient suppressor. The bus is anywhere from 7 V to 39 V. A synchronous buck converter (U301, LMR38020) turns the bus into **5V_BUCK**, a regulated 5.0 V rail that only exists when field power is present. 5V_BUCK feeds the two relay coils and, through a solder jumper, the VLOAD terminal for the MOSFET loads. 5V_BUCK also feeds, through a Schottky diode, the **logic rail 5V_SYS**; USB-C feeds the same 5V_SYS through its own Schottky diode. Whichever source is higher wins, neither can back-feed the other, and 5V_SYS sits at ≈ 4.6 V from either. 5V_SYS feeds the AP7361C regulator (1 A, SOT-223), whose 3.3 V output, **+3V3**, powers the ESP32-S3, the opto pull-ups, and every indicator LED on the logic side.

### The rails

| Net | What it is | Range |
|---|---|---|
| VBUS_DC | Rectified, fused, filtered field power. Buck input. | 7–39 V (24 VAC → 27–34 V with ripple; 36 V DC → 34.6 V; 28 VAC unloaded → 38.2 V) |
| 5V_BUCK | Buck output. Field-powered loads only: relay coils, VLOAD (jumpered), the FIELD PWR LED. | 5.02 V ± 3 % |
| 5V_SYS | Logic supply, OR'd from 5V_BUCK and USB through two SS14 Schottky diodes. | ≈ 4.4–4.85 V |
| USB_5V_PROT | USB VBUS after its fuse and TVS. | 4.75–5.25 V |
| +3V3 | AP7361C output. Everything that thinks or indicates. | 3.30 V |
| VLOAD | MOSFET load supply terminal. = 5V_BUCK with JP901 closed; external 8–12 V with JP901 cut. | 5 V or 8–12 V |
| GND | Logic ground = bridge negative = USB ground = MOSFET source. **Not** the field common of the inputs. | 0 V |
| FLD_COM | The shared common of the four opto inputs. Floats at whatever the field wiring puts on it. | field |

### Net name glossary

| Net | Meaning |
|---|---|
| FLD_PWR_A / FLD_PWR_B | The two power-terminal pins, before the fuse and bridge. Either may be positive, or they may be AC. |
| VBUS_DC | DC bus after the bridge. |
| VIN_SENSE | VBUS_DC ÷ 21, to an analogue input. |
| SW | The buck's switch node — the only fast, high-dV/dt net on the board. |
| BOOT | The buck's bootstrap capacitor node (not to be confused with the ESP32 BOOT button net, which is `IO0`). |
| FB / EN_BUCK / RT | Buck feedback, enable (UVLO divider) and frequency-set nodes. |
| 5V_BUCK · 5V_SYS · USB_5V_PROT · +3V3 · VLOAD | The rails, above. |
| USB_VBUS · USB_DP · USB_DN · USB_CONN_D* · USB_ESD_D* | The USB block, same names as Board 1. |
| EN · IO0 · TXD0 · RXD0 | ESP32-S3 reset, boot strap, recovery UART — same as Board 1. |
| IN1 … IN4 · FLD_COM | Field-side input terminals. |
| IN1_L … IN4_L | Logic-side opto outputs (collector nodes), active LOW. |
| RLY1 · RLY2 | GPIO drives to the relay transistors. K1_COIL / K2_COIL are the collector nodes. |
| K1_NO · K1_COM · K1_NC · K2_NO · K2_COM · K2_NC | Relay contact nets. Field side, never near logic. |
| OUT1 · OUT2 | GPIO drives to the MOSFET gates. OUT1_D / OUT2_D are the drains (terminal pins). |

### Current budget — the 5 V side, everything peaking at once

| Load | On which rail | Peak | Notes |
|---|---|---|---|
| ESP32-S3 Wi-Fi transmit peak, through the LDO | 5V_SYS | 360 mA | A linear regulator passes its output current straight through. |
| Two relay coils | 5V_BUCK | 159 mA | 70 Ω − 10 % = 63 Ω each at 5 V. |
| Two base drives | +3V3 → 5V_SYS | 8 mA | 3.75 mA each. |
| Indicator LEDs (up to 9 on) | +3V3 → 5V_SYS | 15 mA | 1.3 mA each. |
| Pump on VLOAD (jumpered to 5V_BUCK) | 5V_BUCK | 400 mA | The plan's allocation. |
| Opto pull-ups, dividers, LDO ground current | +3V3 → 5V_SYS | 10 mA | |
| **Total on the buck** | | **≈ 0.95 A (4.76 W)** | LMR38020 rated 2 A → **110 % margin**. |

On the field side the input current follows the bus voltage: 0.79 A at 9 V DC, 0.54 A at 12 V, 0.25 A at 24 V, 0.16 A at 36 V; on 24 VAC it is ≈ 0.18 A DC-equivalent but ≈ 0.40 A RMS through the fuse, bridge and bulk capacitor, because a capacitor-input rectifier draws its current in short pulses at the peaks.

### Power modes

- **Field power only** (the installed case): 5V_BUCK and 5V_SYS up, everything works, USB port idle.
- **USB only** (the bench): 5V_SYS ≈ 4.6 V from the laptop, the ESP32-S3 runs, flashes and logs; **5V_BUCK is dead, so the relays cannot click and VLOAD is 0 V.** This is enforced by the diode topology, not by firmware.
- **Both**: both Schottky diodes share 5V_SYS at ≈ 4.6 V; the field loads run from the buck. **Bench only, with a floating field supply** (the plug-in transformer, an unearthed bench supply) or a battery-powered laptop; the silkscreen says *DISCONNECT FIELD POWER BEFORE USB* because in the field the supply's return is usually earthed — see §17, ground loop.

### Isolation map

Three electrical domains, stated plainly: the **logic domain** (which includes the power entry, the buck, USB and the MOSFET outputs — all one ground), the **input domain** (IN1–IN4 and FLD_COM, floating), and the **relay-contact domains** (K1's contacts and K2's contacts, each floating on its own). The board is *opto-isolated inputs and isolated relay contacts on a non-isolated controller* — not a galvanically isolated controller.

| Boundary | Isolated? | By what | Withstand (as designed) |
|---|---|---|---|
| Inputs IN1–IN4/COM ↔ logic | **Yes** | EL817 optocoupler (5 kV RMS), ≥ 2.5 mm moat | functional isolation for ≤ 40 V field circuits — not a safety barrier |
| Relay contacts ↔ logic | **Yes** | relay (coil-to-contact), ≥ 2.5 mm moat | same |
| Power input ↔ logic | **No** | bridge rectifier (one diode drop) | — |
| MOSFET outputs ↔ logic | **No** | shared ground by design | — |
| USB ↔ logic | **No** | same ground | — |

## 3. Field Power Entry — Sheet 02_Field_Power_Entry

This sheet turns anything from 10 V DC to a 24 VAC transformer, wired either way round, into a fused, clamped, filtered DC bus. The published input is **12–36 V DC / 24 VAC (18–28 VAC)** — the two systems the board is for; the guaranteed floor behind the 12 V figure is 10 V (§4, UVLO). The AC ceiling stays at 28 VAC, not 30: a 30 VAC transformer peaks at 42 V and puts a 41 V bus within 2 V of the TVS standoff.

### J201 — power terminal (5.08 mm pitch, 2 positions)

A screw terminal accepting 0.5–2.5 mm² wire (26–12 AWG), the kind every furnace and irrigation controller uses. Pins are `FLD_PWR_A` and `FLD_PWR_B`. There is no polarity: the bridge behind it makes either order correct, and 24 VAC is simply both orders sixty times a second. Silkscreen: **PWR IN · 12–36V DC / 24V AC · ANY POLARITY**.

### F201 — resettable fuse (PPTC, 1.1 A hold, 60 V, radial)

PPTC = Polymeric Positive Temperature Coefficient device, a "polyfuse": too much current heats it, its resistance jumps and the current stops; it resets when it cools. F201 sits in series with `FLD_PWR_A` before the bridge, so it protects the bridge, the bulk capacitor and the field wiring against any downstream fault.

- **Part class:** Littelfuse **60R110** or Bourns **MF-RX110** — 1.1 A hold, 2.2 A trip, 60 V maximum, radial-leaded, hand-soldered. **Not** the Bourns MF-R110: that family is 30 V rated, and the bus reaches 39 V.
- **Why 1.1 A, not the plan's 0.5 A:** the full 5 V load is 4.76 W. At 9 V in the input current is 0.79 A; at 12 V, 0.54 A. A 0.5 A hold device would trip at the bottom of the DC range under full load, before any temperature derating. 1.1 A derates to ≈ 0.95 A at 60 °C — still above the worst case.
- **Resistance:** ≈ 0.1 Ω cold, ≈ 0.3 Ω warm — 0.2 V lost at the worst-case current. This is included in the UVLO arithmetic in §4.
- The 24 VAC inrush into the 470 µF bulk capacitor (≈ 15–20 A for well under a millisecond from a small transformer) is far below the family's 40 A maximum interrupt rating and the bridge's 120 A surge rating; no inrush limiter is needed.

### BR201 — bridge rectifier (KBP206, 2 A, 600 V, through-hole)

Four diodes in a bridge: whichever terminal pin is more positive at any instant feeds the bus, the other becomes the return. DC wired backwards therefore works; 24 VAC becomes 120 Hz pulses that the bulk capacitor smooths.

- **Why a bridge on everything:** reverse-wired DC becomes *impossible* rather than *protected against*, and 24 VAC needs it anyway. The price is two silicon diode drops in series with the supply: ≈ 1.4 V total at light load, ≈ 1.9 V at 0.8 A.
- **Ratings:** 2 A average (worst case here 0.79 A DC, ≈ 0.4 A RMS on AC), 600 V (each diode sees only the ≈ 40 V peak in reverse), IFSM 120 A. VF ≤ 1.0 V per element at 2 A. Dissipation ≈ 1.5 W at 9 V DC full load (the one place where low DC input costs), ≈ 0.3 W at 24 VAC.
- **Package:** KBP (through-hole, 4 in-line pins). Hand-soldered after reflow; it never sees the hot plate. LCSC C2494 (MDD) or any KBP206/KBP210.

### D201 — transient suppressor (SMBJ43A, unidirectional, 600 W, SMB)

TVS = Transient Voltage Suppressor: a diode that does nothing at normal voltage and clamps hard when a fast spike arrives. D201 sits across VBUS_DC to GND, right at the bridge output.

- **Sizing rule (from the plan, verified):** standoff must exceed the highest legitimate bus voltage. A 24 VAC class-2 transformer with nothing on it at high line reaches 28 VAC → 39.6 V peak → **38.2 V on the bus**. SMBJ43A: **standoff 43 V** (4.8 V of margin, < 1 µA leakage), breakdown ≥ 47.8 V, **clamp 69.4 V at 8.6 A**.
- **The check that chooses the buck:** the clamp voltage at full surge current must stay below the buck's absolute maximum. LMR38020: 85 V absolute maximum → **passes at full 600 W surge**. (Every 60 V-class buck fails it above ≈ 7 A of TVS current; the 470 µF bulk capacitor would rescue those parts in practice — it absorbs 8.6 A for 50 µs with a 1.3 V rise — but the 80 V part makes the argument unnecessary.)
- Placement: the TVS and the bulk capacitor sit within a few millimetres of the bridge output, TVS first in copper order.

### C201 — bulk electrolytic (470 µF, 63 V, 105 °C, low ESR, radial through-hole)

The reservoir between the rectifier's 120 Hz peaks. On 24 VAC the bus is refilled 120 times a second; between refills the buck draws from C201.

- **Ripple arithmetic (tolls format, from the plan):** ΔV = I × Δt / C. At the full-load 0.18 A DC-equivalent and a full 8.3 ms period, 330 µF sags 4.6 V; **470 µF sags 3.2 V**. The bus therefore rides between ≈ 30 V and ≈ 27 V at nominal 24 VAC, or ≈ 24 → 20 V at 18 VAC low line — never near the 6–7 V UVLO.
- **Ripple current:** a capacitor-input rectifier pulls ≈ 2.2× the DC current as RMS from the capacitor — ≈ 0.40 A RMS at 120 Hz. Specify ≥ 0.6 A ripple rating; electrolytic ripple ratings are quoted at 100 kHz and derate to ≈ 0.6× at 120 Hz, so a "1 A at 100 kHz" part is the right class. Nichicon UPW / Rubycon ZLH / Panasonic FR 470 µF 63 V (≈ 12.5 × 20 mm) or an equivalent 105 °C low-ESR part.
- **Voltage:** 63 V against a 39 V bus (62 % of rating). A 100 V part was suggested in the second review on the grounds that the TVS can clamp at 69 V; that confuses the TVS's rating with what the node does — the capacitor is in parallel with the TVS, and a 22 mJ solenoid kick (0.5 H at 0.3 A, the worst thing on a 24 VAC secondary) raises 470 µF from 34 V to 35.3 V. The node cannot reach the clamp voltage unless the capacitor has failed open, and then the 85 V buck survives on the TVS alone. 63 V stands; the footprint (Ø 12.5 mm, 5 mm pitch) is the common one. Never on the hot plate — through-hole, hand-soldered, big **+** on the silk.
- **C202 — 1 µF, 100 V, 1206 X7R** in parallel: takes the high-frequency part of the buck's input ripple that the electrolytic's ESL cannot, and gives the TVS a low-impedance partner for fast edges. (The buck's own ceramic input capacitors are on sheet 03, at its pins.)

### R201, R202, R203, C203 — input-voltage sense (2 × 100 kΩ 0805 in series / 10 kΩ 0603 / 100 nF)

A divider from VBUS_DC to GND; the midpoint, net `VIN_SENSE`, goes to **IO8 (ADC1_CH7)**. Ratio 10 / 210 = **1 / 21**: 9 V → 0.43 V, 24 V → 1.14 V, 39 V → 1.86 V, all inside the ADC's 0–2.9 V window (attenuation 3), 15 mV of bus per LSB. The ratio is set by the *fault* case, not the normal one: the ESP32-S3 has no clamp diodes to its supply and an absolute maximum of 3.6 V on any pin, so even a bus held at the TVS's 69 V clamp must map below that — 69 / 21 = 3.29 V (the first draft's 1:15.7 would have put 4.4 V on the pin). Two 100 kΩ in series split the voltage (≈ 19 V each, 0805 for the habit) and cost 186 µA at 39 V. C203 sits at the ESP32 pin, per the same ADC rule as Board 1 (the converter samples by charging a ≈ 10 pF internal capacitor; the 100 nF at the pin supplies that gulp); with the 200 kΩ source it also makes the node a 20 ms low-pass, which is what a supply-voltage reading wants. Firmware uses it for three things: "field power present" gating, input-voltage telemetry, and the low-input-voltage warning that turns "the board keeps resetting" into a number.

Nets leaving this sheet: VBUS_DC (to the buck), VIN_SENSE (to the core), GND.

## 4. 5 V Buck Converter — Sheet 03_Buck_5V

**The one new hard thing.** A buck converter chops the DC bus at 400 kHz and averages the chopped voltage through an inductor and capacitors into a steady 5 V. Everything on this sheet follows the datasheet's own 5 V design example; there are no creative substitutions on the first spin.

### U301 — LMR38020SDDAR (Texas Instruments, LCSC C3192337)

- **Why this part:** 4.2–80 V input (85 V absolute maximum — passes the TVS check above), 2 A (110 % margin over the 0.95 A worst case), **synchronous** (both switches inside; no external catch diode), **internally compensated** (no loop-design risk), precision enable for the UVLO divider, and an **HSOIC-8 PowerPAD** package — leaded, 1.27 mm pitch, every joint visible under the loupe. The plan's LMR36015 is a 2 × 3 mm leadless QFN that cannot be inspected once down; the plan's 100 V fallback, LM5164, is a 1 A part with 5 % margin. Both are retired.
- **Variant:** the **S** suffix = PFM at light load (efficient, slightly higher ripple when the load is tiny) with spread spectrum. FS (forced PWM + spread spectrum) is the drop-in alternative if light-load ripple ever matters; it does not here.
- **Pins:** 1 GND · 2 EN · 3 VIN · 4 RT/SYNC · 5 FB · 6 PG · 7 BOOT · 8 SW · exposed pad = GND (thermal).
- **Current limits:** high-side 2.6–3.8 A, low-side valley 1.8–2.8 A, with hiccup on a sustained short. Soft start 4 ms. Quiescent 40 µA.
- **Alternate (BOM, second source):** LMR16020PDDAR (LCSC C190006, 60 V, 2 A, same package) — non-synchronous, so it needs an SS36 catch diode, a 0.75 V feedback divider (RFBB 17.8 k) and its own RT resistor. Only if the LMR38020 is out of stock on freeze day.

### The datasheet design example, populated exactly

| Ref | Value | Package | Job |
|---|---|---|---|
| C301, C302 | 4.7 µF, 100 V, X7R | 1210 | Input ceramic capacitors (≥ 4.7 µF required; 100 V = 2.5× the bus). |
| C303 | 100 nF, 100 V, X7R | 0603 | High-frequency input bypass — **at pins 3 and 1**, closer than anything else. |
| C304 | 100 nF, 16 V, X7R | 0603 | Bootstrap capacitor, BOOT (pin 7) to SW (pin 8). |
| C305, C306, C307 | 22 µF, 25 V, X7R | 1210 | Output capacitors (datasheet: 3 × 22 µF for 5 V). 25 V X7R so the real capacitance at 5 V bias stays near 22 µF. |
| C308 | 22 pF — **DNP** | 0603 | Feed-forward across RFBT; footprint only. Internal compensation does not need it. |
| L301 | **15 µH ± 20 %**, shielded, Isat ≥ 3.8 A | 12 × 12 × 6 | Bourns **SRR1260-150M** (Isat 4.6 A, Irms 5.0 A, 27 mΩ, LCSC C2041333). |
| R301 | 64.9 kΩ, 1 % | 0603 | RT → **400 kHz** (datasheet Table 8-1; RT = 30970 × f^−1.027). Never open, never shorted. |
| R302 | 100 kΩ, 1 % | 0603 | RFBT, feedback top. |
| R303 | 24.9 kΩ, 1 % | 0603 | RFBB, feedback bottom → VOUT = 1.0 V × (1 + 100/24.9) = **5.016 V**. |
| R304 | 91 kΩ, 1 % | 0805 | RENT, UVLO divider top (sees up to 32 V). |
| R305 | 20 kΩ, 1 % | 0603 | RENB, UVLO divider bottom. |
| D301 | SS14 | SMA | OR diode, 5V_BUCK → 5V_SYS. |
| D302 + R306 | green LED + 1 kΩ | 0805 / 0603 | **FIELD PWR** indicator on 5V_BUCK, ≈ 3 mA. |

**Inductor arithmetic.** L = (VIN − VOUT) / (fSW × K × IOUT) × (VOUT / VIN) with K = 0.4 ripple ratio and IOUT = 2 A gives 14 µH at 48 V in; the datasheet rounds to 15 µH, and so does this board. At the 39 V bus maximum the ripple current is 0.73 A peak-to-peak, so the inductor peak is 1.31 A at the 0.95 A worst-case load and 2.36 A at 2 A. The saturation rule is the datasheet's, not the plan's "1.3× peak": **Isat ≥ the 3.8 A high-side current limit**, so the core cannot saturate even into a dead short. Minimum inductance against sub-harmonic oscillation is 0.25 × 5 / 400 kHz = 3.1 µH — comfortably below 15 µH.

**Output voltage tolerance.** Reference ± 1.5 % over temperature, 1 % resistors: worst case ± 2.7 %, inside the 5.00 V ± 3 % acceptance. Output ripple with 66 µF of ceramic: ΔV ≈ ΔIL / (8 × f × C) + ESR × ΔIL ≈ 3.5 mV + 4 mV ≈ **10 mV peak-to-peak**, against the 50 mV acceptance.

**Duty limits.** Minimum on-time 75 ns → minimum duty 3 % → the converter regulates 5 V from inputs up to ≈ 167 V without frequency foldback (irrelevant here). Minimum off-time 190 ns → maximum duty 92 % → regulation holds down to a ≈ 5.4 V bus before foldback stretches it further. The UVLO below shuts the converter off well before that.

### EN divider — the UVLO, and why it is 7.0 V not 7.5 V

UVLO = Under-Voltage Lock-Out: the buck stays off until its input is high enough to regulate cleanly, and shuts off cleanly when the input sags, so a brownout produces a clean stop and restart instead of a chattering 5 V rail. The EN pin has a precision threshold — **rising 1.25 V (1.10–1.40), falling 1.10 V (0.95–1.22)** — and a divider from VBUS_DC scales it: VON = VEN-H × (1 + RENT/RENB), VOFF = VEN-L × (1 + RENT/RENB).

- **RENB = 20 kΩ, RENT = 91 kΩ** (ratio 5.55): **turn-on 6.9 V typical (6.1–7.8), turn-off 6.1 V typical (5.3–6.8)** at the bus. Divider current 0.35 mA.
- **Why not the plan's 7.5 V:** at 9 V in, the bus sits at 6.9 V under full load (0.79 A through 0.3 Ω of PPTC and 1.9 V of bridge) and 7.6 V at light load. A 7.5 V turn-on would not start at 9 V in half the tolerance band, and its 6.6 V turn-off would drop the converter the moment the load arrived. That is the chatter the UVLO exists to prevent, built in.
- **What 7.0 V buys:** guaranteed start with a **10 V DC** terminal voltage even at the worst-case 7.8 V threshold (10 − 1.5 V of light-load drops = 8.5 V), typical start at ≈ 8.5 V, and a turn-off that always lands while the converter is still regulating (6.1 V typical, 5.3 V worst — both above the 5.4 V regulation floor plus margin, and the ESP32's 3.3 V rail never sags because the 5 V rail is still in regulation at the instant of shutdown).
- **Never** wire EN to the buck's own output — the unrecoverable latch from the client posting the plan mentions.

### The 5V_BUCK / 5V_SYS split (D301) — what changed from the plan and why

The plan had one 5 V node, with USB OR'd into it. On that node the relays would pull in from USB power alone (USB gives ≈ 4.6 V after a Schottky; the relay's must-operate voltage is 3.75 V), so "outputs stay off until field power is present" would have been a firmware promise. This board separates the rails:

- **5V_BUCK** (the buck's regulation point, 5.02 V) feeds: K1 and K2 coils, JP901 → VLOAD, D302 FIELD PWR LED.
- **5V_SYS** = 5V_BUCK through **D301 (SS14)**, or USB_5V_PROT through **D402 (SS14)** on sheet 04. Feeds the 3.3 V regulator (U501) and nothing else that matters.
- Consequences: USB alone → 5V_BUCK is dead → relays and VLOAD are dead, by physics. The buck can never push current into a laptop (D402 blocks it). USB can never feed a pump. The 3.3 V regulator sees ≈ 4.6 V instead of 5.0 V, so its worst-case dissipation drops from 0.64 W to 0.49 W. Cost: one SMA diode and 0.16 W in it at the 0.4 A logic load.

### Layout law for this sheet (mechanisms in `Hard_Rules_Layout_RevA.md`)

1. **The hot loop** on a synchronous buck is C303 ↔ VIN (pin 3) ↔ GND (pin 1) — both switches are inside the package, so the loop is just the input capacitor and two pins. C303 straddles pins 1 and 3 on the top layer, C301/C302 right behind it, all three grounded through vias at their pads. Nothing else is placed in that few square millimetres.
2. **SW node** (pin 8 → L301 → C305–C307): short and wide, no vias, no other nets alongside it. It is the only fast, high-dV/dt net on the board; the FB trace, the VIN_SENSE trace and the USB pair never run near it.
3. **BOOT capacitor** C304 across pins 7 and 8, short and wide.
4. **FB divider** at pin 5, ≤ 5 mm; the top of R302 taps the **output capacitor**, not the inductor pad.
5. **RT resistor** R301 at pin 4, grounded at the exposed pad, away from SW.
6. **Exposed pad**: 4–6 thermal vias (0.3 mm drill) to the bottom ground, solid-connected on top.
7. **Bottom copper unbroken under the whole converter.** No trace of any kind crosses beneath SW, the inductor or the input capacitors.
8. **≥ 15 mm from the antenna keep-out**, as far from the module as the board allows.
9. Test point **TP_SW** is a small pad at the inductor's SW end — probe ripple at the output capacitor, not at FB.
10. Watch Phil's Lab's buck-layout video once more before placing a single part. Board 1's rulebook did not cover a switcher; this list is the amendment.

Nets leaving this sheet: 5V_BUCK, 5V_SYS, GND.

## 5. USB-C Input — Sheet 04_USB_C_Input (copied from Board 1)

The Board 1 block, designator-shifted to 4xx, with one change: the outgoing rail is 5V_SYS through a Schottky instead of +5V_PROT directly.

- **J401** — TYPE-C-31-M-12 USB-C receptacle, USB 2.0 only (C165948). VBUS pads tied, D+ pairs and D− pairs tied at the connector, **GND pads A1/B1/A12/B12 tied to ground** (Board 1's blocking finding — do not repeat it), shield to ground, SBU unused. Overhangs the board edge by ≈ 1 mm per the HRO drawing.
- **R403, R404** — 5.1 kΩ, one per CC pin, never shared: the board announces itself as a 5 V sink.
- **D401** — SMF5.0A TVS on USB_VBUS at the connector (C2980403). **F401** — 1206L075/16WR PPTC, 0.75 A hold (C371166): USB carries only the logic load (≤ 0.4 A). **C404** — 10 µF 25 V 0805 bulk on USB_5V_PROT.
- **U401** — USBLC6-2SC6 data-line ESD array (C7519), flow-through, with **C401** 100 nF at its VBUS pin. **R401, R402** — 22 Ω series on D+/D− at the module end. **C402, C403** — reserved 100 nF footprints, **DNP** (if ever fitted, ≤ 47 pF).
- **D402** — SS14, USB_5V_PROT → 5V_SYS: the second half of the OR. On USB alone 5V_SYS ≈ 4.6 V.
- **Ground-loop rule (new on this board, §17):** USB is a bench port. With field power from an earthed supply connected, the USB cable's ground would bypass the bridge's return diode and carry the board's return current. Bench rule: floating supply (the plug-in 24 VAC transformer) or a battery-powered laptop, or no USB while field-powered.
- **Pair routing on 2 layers:** the pair cannot reach 90 Ω on 1.6 mm FR4 without absurd widths; it stays a short (< 20 mm), tightly coupled, via-free pair over unbroken bottom ground. USB Full Speed tolerates that, as §17 states openly.

Nets leaving this sheet: 5V_SYS, USB_DP, USB_DN, GND.

## 6. 3.3 V Regulator — Sheet 05_3V3_Power (Board 1's block, regulator upgraded)

- **U501 — AP7361C-33E-13** (Diodes Inc., **SOT-223**, LCSC C500795): 1 A low-dropout linear regulator, fixed 3.3 V, input 2.2–6.0 V, dropout 360 mV at 1 A (≈ 130 mV at this board's 0.37 A peak), 60 µA quiescent, 1.5 A current limit with a 400 mA short-circuit fold-back, thermal shutdown at 150 °C. The 3-pin SOT-223 has no enable pin — nothing to tie, nothing to forget. Pins: 1 IN, 2 GND (tab), 3 OUT.
- **Why not Board 1's AP2112K:** Board 1 spent its life asleep and its regulator saw 0.26 W in bursts. This board never sleeps — a connected ESP32-S3 draws 100–150 mA all day and 375 mA at every transmit — and it lives in a furnace closet. The same 0.19 W sustained / 0.49 W peak in a SOT-23-5 (≈ 150 °C/W on a pour) is a 29 °C / 73 °C rise; in a SOT-223 with its tab on a ground pour (110 °C/W on the datasheet board, ≈ 70 °C/W with a real pour) it is 14–21 °C / 34–54 °C. Same rail, same footprint class of effort, half the temperature — adopted from the second review. The AP2112K stays in the BOM as the alternate if the SOT-223 is out of stock.
- **C501** 1 µF at IN (datasheet: ≥ 1 µF ceramic), **C502** 4.7 µF at OUT (datasheet: ≥ 2.2 µF ceramic; 4.7 µF for load-step margin), **C503** 10 µF 25 V 0805 bulk on 5V_SYS beside it. Both regulator capacitors at the pins, tab on a copper pour stitched to the bottom ground.
- **D501 + R501** — yellow-green LED (C2289, Vf 2.0–2.2 V — the chemistry that lights from 3.3 V) with **1 kΩ** (≈ 1.3 mA). Board 1 used 10 kΩ for a sleep budget; this board never sleeps and the LED must read on camera.
- **Thermal:** (4.6 − 3.3) × 0.375 = 0.49 W at the Wi-Fi transmit peak, 0.19 W sustained at a typical 150 mA — record its temperature in the torture loop (step 7) anyway; the number belongs in the bring-up record.

## 7. ESP32-S3 Core — Sheet 06_ESP32S3_Core (copied from Board 1)

**U601** — ESP32-S3-WROOM-1-N8 (C2913198): the module with radio, antenna, 8 MB flash, no PSRAM. The block is Board 1's, with the pin map changed for this board's I/O.

- **Power:** 3V3 (pin 2) with **C601** 22 µF 0805 + **C602** 100 nF at the pin, smallest capacitor closest. GND pins 1, 40 and the exposed pad 41 to ground; pad vias into the bottom plane.
- **Reset:** EN (pin 3) with **R601** 10 kΩ to +3V3, **C603** 1 µF to ground, **SW602 = RESET** across the capacitor. **Boot:** IO0 (pin 27) with **R602** 10 kΩ to +3V3 and **SW601 = BOOT** to ground; no capacitor on IO0. Both switches are the TS-1187A (C318884) on **Board 1's renumbered 1/1/2/2 footprint** — the four-pad pairing trap is already solved in the copied library.
- **Strapping pins** IO3, IO45, IO46 unconnected. **IO1 and IO2 are left unconnected too**: the datasheet lists them (with IO0, IO43, IO44 and the flash pins) as pulled *up* at reset, which is exactly wrong for an output that must wake OFF.
- **USB:** IO19 = D− (`USB_DN`), IO20 = D+ (`USB_DP`), native USB-Serial/JTAG, no bridge chip.
- **Recovery UART:** TXD0 (IO43, pin 37) and RXD0 (IO44, pin 36) to through-hole test points with a through-hole GND beside them — Board 1's trio.
- **D602 + R603** — STATUS LED (yellow-green, 1 kΩ) on IO13: Wi-Fi state and heartbeat, so a board on a shelf shows it is alive and connected.
- **J601 — expansion header, DNP:** 1 × 6, 2.54 mm: 3V3 · GND · IO14 · IO16 · IO17 · IO18. Costs nothing, lets a DS18B20 or an I²C sensor join a deployment without a new board. Placed on the logic side, away from the antenna.
- **PG (buck power-good, pin 6 of U301)** is brought to test point TP14 only; it is open-drain and reads high through any pull-up when the buck is unpowered, so it cannot be the "field power present" signal — VIN_SENSE is.
- **Antenna:** nose overhanging the board edge, all-layer keep-out, stitching ring around (never inside) it, no off-board conductor within 15 mm — Board 1's rules 1–4 unchanged. On this board the additional rule is distance from the buck: **the module and the converter sit at opposite ends.**

### Complete pin map (every used module pin)

| Module pin | Pin name | Net | Role | Default pull at reset |
|---|---|---|---|---|
| 1, 40, 41 | GND / pad | GND | Ground and thermal pad | — |
| 2 | 3V3 | +3V3 | Power (C601 + C602 at the pin) | — |
| 3 | EN | EN | Reset network R601 / C603 / SW602 | — |
| 4 | IO4 | IN1_L | Opto input 1, active LOW | none |
| 5 | IO5 | IN2_L | Opto input 2, active LOW | none |
| 6 | IO6 | IN3_L | Opto input 3, active LOW | none |
| 7 | IO7 | IN4_L | Opto input 4, active LOW | none |
| 12 | IO8 | VIN_SENSE | DC-bus voltage, ADC1_CH7 | none |
| 13 | IO19 | USB_DN | Native USB D− | (USB) |
| 14 | IO20 | USB_DP | Native USB D+ | (USB) |
| 17 | IO9 | RLY1 | Relay 1 driver, active HIGH | none |
| 18 | IO10 | RLY2 | Relay 2 driver, active HIGH | none |
| 19 | IO11 | OUT1 | MOSFET 1 gate, active HIGH | none |
| 20 | IO12 | OUT2 | MOSFET 2 gate, active HIGH | none |
| 21 | IO13 | STATUS_LED | Wi-Fi / heartbeat LED (D602 + R603 1 kΩ) | none |
| 22, 9, 10, 11 | IO14, IO16, IO17, IO18 | EXP1–4 | J601 expansion header (DNP) | none |
| 27 | IO0 | IO0 | Boot strap, SW601 | pull-up |
| 36 | RXD0 (IO44) | RXD0 | Recovery UART, TP | pull-up |
| 37 | TXD0 (IO43) | TXD0 | Recovery UART, TP | pull-up |
| 15, 16, 26 | IO3, IO46, IO45 | — | Strapping pins, unconnected | (strap) |
| 38, 39 | IO2, IO1 | — | Unconnected (pulled up at reset) | pull-up |
| 8, 23–25, 28–35 | IO15, IO21, IO47, IO48, IO35–IO42 | — | Unconnected | none |

The five outputs (IO9–IO13) are on pins with **no default pull**, so the 10 kΩ pull-downs on sheets 08 and 09 hold every relay and MOSFET off from the first microsecond of power until firmware takes over. (The datasheet's Table 2-2 lists ≈ 60 µs power-up glitches on some pins; a 60 µs pulse cannot move a relay armature and would blink a pump for 60 µs — harmless, but check the table when the pins are final.) The four inputs and the ADC pin also have no default pull, so nothing biases the input filter or the sense divider before firmware runs.

ADC = Analogue-to-Digital Converter. VIN_SENSE uses ADC1 (usable while Wi-Fi is on; ADC2 is not), attenuation 3, 0–2.9 V, 100 nF at the pin.

## 8. Opto-Isolated Inputs ×4 — Sheet 07_Opto_Inputs (field side)

Each input answers one question — *is there 12–30 V between this wire and COM?* — and answers it across an isolation barrier, so the field wiring can sit at any potential, be AC or DC, and be wired either way round.

### J701 — input terminal (5.08 mm, 5 positions): IN1 · IN2 · IN3 · IN4 · COM

A shared common is how industrial I/O is actually wired: the thermostat's C wire to COM, the W/Y/G wires to IN1–IN3, the float switch between IN4 and COM. Silkscreen: **IN1 IN2 IN3 IN4 COM · 12–30V AC/DC · ISOLATED**.

### One channel (×4): U701 · R701 + R702 · D701 · D705 · R709 · C701

- **U701 — EL817S1(C)(TU)-F** (Everlight, LCSC C106900): a PC817-class optocoupler, **CTR rank C (200–400 % at 5 mA)**, in the surface-mount gull-wing DIP-4 package that goes on the hot plate with everything else. CTR = Current Transfer Ratio: how much transistor current you get per unit of LED current. Isolation 5 kV RMS; collector rated 80 V (it sees 3.3 V).
- **R701, R702 — 1.6 kΩ, 1206 anti-surge thick film, in series (3.2 kΩ total):** sets the LED current and takes the field voltage. Two parts spread the heat and double the voltage rating (2 × 200 V); the anti-surge class (Yageo PA/AC series, Panasonic ERJ-P08) survives the surge pulses a plain thick film cracks under. Current through the chain: **1.33 mA at 12 V, 2.27 mA at 15 V, 5.1 mA at 24 V, 6.95 mA at 30 V, 8.8 mA at 36 V**. Dissipation: 155 mW total at 30 V, **249 mW at 36 V — 125 mW per resistor, 50 % of the 1206 rating** (an 0805 would be at 100 %). The board's own power terminal hands out 36 V; the input must survive being wired to it.
- **D709 — BZT52C4V7 Zener (SOD-123), in series with the two LEDs — the threshold-setting part.** Below the Zener knee plus the two LED drops (≈ 7.75 V) no current flows at all; above it the resistors set the current. That turns the input into an **IEC 61131-2 Type 1 digital input**: OFF for anything ≤ 5 V (0 mA), ON from 15 V with 2.27 mA (the standard asks ≥ 2 mA), 6.95 mA at 30 V (the standard allows ≤ 15 mA). Without it (the first two drafts of this document) the threshold was ≈ 4 V and depended on the optocoupler's CTR — a number nobody could put on a datasheet. The Zener dissipates 41 mW at 36 V against a 500 mW rating. (Industry-standard audit, §2.1.)
- **D705 — red indicator LED (0805), in series with the opto's LED, on the field side.** It lights with the real field current (1.9–6.9 mA — a high-efficiency red is clearly visible), independent of firmware, and adds nothing to what the opto must sink. The plan put this LED on the logic side, where it would have loaded the opto's collector by another 1.3 mA — at 12 V in, more than the opto can give. Its ≈ 1.9 V forward drop adds to the opto LED's 1.15 V and the Zener's 4.7 V: the channel's threshold is **≈ 8–8.4 V** (the three drops plus the 0.2 mA the pull-up needs at the derated CTR). Anything below reads OFF — a power-stealing thermostat's 1–2 V of leakage, or a 5 V logic level, stays OFF; 12 V reads ON with margin, 15–30 V is squarely in the Type 1 ON band. At 12 V the indicator runs at 1.33 mA — dim but clearly visible on a high-efficiency red; at 24 V it is bright.
- **D701 — 1N4148W (SOD-123), anti-parallel across the (opto LED + indicator LED) pair:** for reverse-wired DC it carries the current harmlessly and clamps the reverse voltage across the two LEDs to under a volt; for AC it carries the negative half-cycle so the input reads 24 VAC as a half-wave signal. Rated 150 mA / 75 V; it carries ≤ 7 mA.
- **R709 — 47 kΩ pull-up to +3V3, C701 — 1 µF X7R 16 V 0603 (τ = 47 ms), on the collector node `IN1_L`.** The transistor pulls the node LOW when the LED is lit. Sink budget: the pull-up needs only **70 µA**; available collector current is **0.65 mA at 12 V** even with the CTR derated to 35 % (50 % minimum × 0.7 for low LED current) — **9× margin at the worst corner**, 28× at 30 V, and far more with the rank-C part actually specified. The first draft used 10 kΩ + 4.7 µF — the same 47 ms, but it asked the opto for 0.33 mA (2× margin at the worst corner) and needed a 4.7 µF 0805 that derates under bias. The second review's 47 kΩ + 1 µF is the same time constant with five times the sink margin, a plain 0603 capacitor, and headroom for the CTR to halve over the LED's life — adopted. The price is a lower input threshold (below), which the two LED drops keep at a useful level.
- **Why τ = 47 ms and not the plan's 10 ms — the AC arithmetic.** On 24 VAC the opto conducts only while the instantaneous voltage exceeds the ≈ 8.4 V threshold: from ≈ 14° to 166° of each positive half-cycle, **7.0 ms on, 9.7 ms off** per 16.7 ms cycle. During the off gap the capacitor charges through the pull-up toward 3.3 V: with the plan's 10 kΩ + 1 µF (τ = 10 ms) it reaches **≈ 2.0 V** — above the ESP32-S3's VIL of 0.825 V, into the undefined band; with **47 kΩ + 1 µF (τ = 47 ms) it reaches 0.61 V (0.75 V with 20 % capacitor derating — an X7R 16 V 0603 at 3.3 V actually derates ≈ 5 %)** — a steady LOW. If bring-up measures more than 0.7 V at the end of the gap, C701–C704 become 1.5 µF (τ = 70 ms, 0.42 V) — same footprint. Release after the signal stops: ≈ 3τ ≈ 140 ms. First-detect delay when a signal appears: the opto drags 1 µF from 3.3 V to 0.8 V with ≈ 0.6 mA net at 12 V in ≈ 4 ms — immediate.
- **Firmware belt to the hardware braces:** an input changes state only after 3 consecutive 10 ms samples agree (§14).

Field-side rules for this sheet: R701/R702, D701, D705 and the opto's LED pins are field copper — they sit on the field side of the moat with only local fills, no ground pour. The opto body straddles the moat. R709, C701 and the collector are logic copper.

Nets leaving this sheet: IN1_L … IN4_L (to the core).

## 9. Relay Outputs ×2 — Sheet 08_Relay_Outputs (field side, isolated contacts)

### K801, K802 — Hongfa HF3FF/005-1ZTF (LCSC C2764967), SPDT, through-hole

- **Why Hongfa and not the plan's Songle SRD-05VDC-SL-C:** same 19 × 15.2 mm "T73" outline, same coil, but an industrial part: **UL E134517, VDE R50148356, CQC**, **AgSnO₂ contacts** (the T suffix — the right material for inductive loads; Songle's AgCdO is the old one), **−40…85 °C** (the Songle is −25…70 °C, which a furnace closet or an attic exceeds), 1 × 10⁷ mechanical operations, 1500 VAC coil-to-contact. Hongfa is a top-three relay maker; the SRD is the clone. ≈ $0.80 against ≈ $0.25 — the most expensive upgrade on the board and the most obviously worth it. (Industry-standard audit, §1.)
- **Coil:** 5 V nominal, **70 Ω ± 10 % → 63–79 mA**, 0.36 W, pick-up ≤ 3.8 V, drop-out ≥ 0.5 V. On 5V_BUCK the coil sees 5.02 − 0.15 V (transistor saturation) = 4.87 V, 97 % of nominal.
- **Contacts:** one SPDT set (COM, NO = normally open, NC = normally closed), datasheet-rated 10 A at 250 VAC / 28 VDC. **This board rates them at ≤ 2 A, ≤ 30 V AC or DC** — set by the moat, the terminal, the trace width and the refusal of mains, not by the relay.
- **Why SPDT with all three contacts on terminals:** each deployment picks its own fail-safe direction. An overflow guard wired through **NC** keeps the air conditioner running even if this board loses power; a sprinkler valve wired through **NO** stays shut if the board dies. Kept verbatim in the README.
- Body 19.0 × 15.5 × 15.3 mm, the tallest part on the board. Through-hole, hand-soldered after reflow, thermal reliefs on its pads so the iron can wet them.

### Driver per relay: Q801 · R801 · R802 · D801 · D803 + R805

- **Q801 — MMBT2222A (NPN, SOT-23; onsemi MMBT2222ALT1G / Nexperia MMBT2222A,215 / Diodes MMBT2222A-7-F):** low-side switch for the coil — the 2N2222 in SOT-23, 600 mA, hFE ≥ 100 at 150 mA (≥ 90 at this coil's 79 mA), three tier-one sources. Replaces the plan's S8050, a commodity part with vague gain bins; BC817-40 is the equally standard alternate. Same network, same arithmetic.
- **R801 — 680 Ω base resistor** from the GPIO: (3.3 − 0.7) / 680 = **3.75 mA** of base current for a ≤ 79 mA coil → forced gain 21, against a minimum hFE of 85 — **4× overdrive, deep saturation**, VCE(sat) ≈ 0.15 V, 12 mW in the transistor.
- **R802 — 10 kΩ base pull-down:** the relay is OFF from the first microsecond of power, through reset, through the bootloader, until firmware says otherwise. Sized so that even a pin with a 45 kΩ internal pull-up would sit at 0.6 V at the base node — the plan's value would have been fine here, but 10 kΩ is used on every output on this board for one reason stated once (§10).
- **D801 — 1N4148W flyback across the coil** (cathode to 5V_BUCK): when the transistor opens, the coil's stored energy (≈ 0.2 mJ) circulates through the diode instead of spiking the collector. Release is slowed by ≈ L/R ≈ 1 ms — irrelevant for valves and fans.
- **D803 + R805 — red LED + 1 kΩ from the GPIO node to ground:** lights when the coil is driven (1.3 mA from the GPIO, which sources 5.1 mA in total — the ESP32-S3's default 20 mA drive is ample).

### J801, J802 — contact terminals (5.08 mm, 3 positions each): NO · COM · NC

Silkscreen: **K1: NO C NC** and **K2: NO C NC**, and beside both: **≤ 30V AC/DC · 2A MAX · NOT FOR MAINS**. Contact traces ≥ 1.5 mm wide (3.2 A at a 10 °C rise on 1 oz copper) and short; they never approach the logic side.

### Snubber and MOV footprints — fitted per deployment, DNP on the fab order

The flyback diode protects the *coil*; nothing protects the *contacts* from the arc an inductive **load** draws when they open. Most hobby relay boards omit this; the footprints are here and the README says which to fit:

- **R807 + C801 — RC snubber across COM–NO**, and **R808 + C802 across COM–NC**: 100 Ω 1206 + 100 nF 100 V X7R 1206. For a 24 VAC solenoid valve or contactor coil. Leakage through the snubber with the contact open: 100 nF at 60 Hz is 26.5 kΩ → 0.9 mA at 24 VAC — cannot hold a valve in.
- **RV801 — MOV across COM–NO**: 07D560K (7 mm disc, 35 V RMS / 45 V DC continuous, clamps ≈ 56 V). Alternative to the RC for AC loads.
- For **DC inductive loads** the right cure is a flyback diode across the load, at the load; the README says so.

Same set on K2: R809/C803, R810/C804, RV802.

Nets leaving this sheet: RLY1, RLY2 (from the core), 5V_BUCK, GND. The contact nets touch nothing else.

## 10. MOSFET Outputs ×2 — Sheet 09_MOSFET_Outputs (logic-side ground — not isolated)

Two low-side switches for loads that share the board's ground: a 5 V pump, a buzzer, an LED strip. "Low-side" means the switch is in the load's return path: the load connects between VLOAD and the OUTx terminal, and the MOSFET pulls OUTx to ground.

### Per channel: Q901 · R901 · R902 · D901 · D903 + R905

- **Q901 — AO3400A** (N-channel, SOT-23, C20917): 30 V, 5.7 A, **RDS(on) ≤ 48 mΩ at 2.5 V gate drive, ≈ 40 mΩ at 3.3 V** — a logic-level part that is fully on from a 3.3 V GPIO. 0.4 A → 6 mW; 1 A → 40 mW. Threshold 0.65–1.45 V.
- **R901 — 100 Ω gate resistor:** with ≈ 900 pF of gate capacitance that is a 90 ns edge — slow enough to be quiet, fast enough to be lossless at these switching rates (this output is on/off, not PWM by default; if firmware ever PWMs a pump, keep it ≤ 1 kHz).
- **R902 — 10 kΩ gate pull-down.** *The one rule for every output on this board:* the ESP32-S3 has pins that are pulled **up** at reset (IO0, IO1, IO2, IO3, IO43, IO44 and the flash pins). Against a ≈ 45 kΩ internal pull-up the plan's 100 kΩ pull-down would sit the gate at 2.3 V — above the 0.65 V minimum threshold, i.e. **ON at reset**. 10 kΩ gives 0.60 V even in that case, and the outputs are additionally assigned only to pins with no default pull. Same value on the relay bases for the same reason.
- **D901 — SS14 flyback**, anode at the drain, cathode at VLOAD: a pump motor is an inductor; when the MOSFET opens, its energy circulates through D901 instead of driving the drain above 30 V.
- **D903 + R905 — red LED + 1 kΩ on the GPIO side of R901.**

### J901 — output terminal (5.08 mm, 4 positions): VLOAD+ · GND · OUT1− · OUT2− — and JP901

- **Pin order** puts the supply pair (VLOAD+, GND) side by side and the two switched returns beside each other, so an external supply lands on two adjacent screws and a load's minus wire visibly goes to an OUT− pin (second review's suggestion — adopted, it is clearer than the first draft's VLOAD · OUT1 · OUT2 · GND).
- **JP901 — solder jumper, OPEN by default** (KiCad `SolderJumper_2_Open`). Closing it ties VLOAD to 5V_BUCK for the aquarium-pump case, up to the 400 mA allocation, no external supply. The first draft had it bridged by default; the second review's argument for open wins: with the jumper closed, an external 8–12 V supply wired to VLOAD would be driven straight into the buck's output and the two 5 V relay coils — a destructive mistake that an open jumper makes impossible until someone closes it on purpose. Closing a jumper is a five-second, deliberate act; the demo build does it once.
- **Leave JP901 open and feed 8–12 V into VLOAD+ / GND** for a bigger pump or a 12 V LED strip: the load supply's negative *must* land on the GND pin — these loads share board ground and are not isolated. AO3400A's 30 V rating is why VLOAD is specified ≤ 12 V. **An external VLOAD supply is not reverse-protected**: wired backwards it shorts through the MOSFET body diodes and D901/D902. Big **VLOAD +** on the silk, and a README rule: meter the pump supply before it meets J901.
- **C901 — 100 µF, 25 V electrolytic on VLOAD** at the terminal: a motor's 3–5× starting inrush comes out of this instead of dipping the buck's output. With the jumper open it sits on the external supply.
- Silkscreen: **VLOAD+ GND OUT1− OUT2− · NOT ISOLATED · CLOSE JP901 FOR 5V**.

Nets leaving this sheet: OUT1, OUT2 (from the core), 5V_BUCK, GND.

## 11. Mechanical, Moat, Silkscreen — Sheet 10_Mechanical

- **Board:** 2 layers, 1 oz outer copper, 1.6 mm FR4, lead-free HASL, green mask. **Outline from the enclosure, decided before layout** (`../mechanical/README.md`): a field controller lives on DIN rail, so the board is sized to a 6-module DIN enclosure's PCB drawing (reference class Camdenboss CNMB/6, 106 × 90 × 58 mm) with the terminals at its two windows — which is what the plan's "field terminals on at most two edges" was already asking for. Hard ceiling **100 × 100 mm** (JLC's cheapest 2-layer tier, stencil ships in the same box); 1–2 mm corner radius (Board 1's lesson: a radius forces tab-routing, which is fine at this size).
- **Fiducials:** FID1–FID3, 1 mm copper / 2 mm mask opening (KiCad `Fiducial_1mm_Mask2mm_SilkRing`), in three corners of the top side, ≥ 5 mm from the edge. They align the stencil on the bench and are mandatory the day a batch is assembled at JLC.
- **Layer plan:** every component on the top layer (single-sided reflow). Bottom copper = one unbroken ground beneath the logic side and the converter. The field side has **no ground pour at all** — its copper is local fills per net (the bridge output, the relay contact nets, the opto LED nets). The rectifier/bulk-capacitor return joins the logic ground at a **single star point at the buck's input capacitors**, so the rectifier's 120 Hz pulse current never flows through the ESP32's ground.
- **Moat:** ≥ 2.5 mm copper-free on both layers along the whole field/logic boundary, wider (≥ 4 mm) around the relay contact terminals. Silkscreen line plus **FIELD SIDE** / **LOGIC SIDE** text. Enforced by a DRC rule (netclass FIELD ↔ everything else ≥ 2.5 mm — `KiCad_Settings_RevA.md`).
- **Edges:** field terminals (J201, J701, J801, J802) on at most two edges; USB-C on the opposite edge; J901 (VLOAD, logic-referenced) on the logic side's edge next to nothing field-related. Antenna nose overhanging its edge, ≥ 15 mm from any terminal, screw, wire or the converter.
- **Mounting:** four M3 holes, Ø 6.5 mm screw-head keep-outs; none in the antenna region.
- **Silkscreen standard:** plain-English terminal labels as listed on each sheet; pin-1 and polarity marks (C201 +, C901 +, every diode's cathode, LED cathodes, opto pin 1, relay coil pins); BOOT / RESET; every test-point name; **NOT FOR MAINS · ≤30V · 2A**; **DISCONNECT FIELD POWER BEFORE USB** beside J401 (the ground-loop rule, §17, in four words); board name / Rev A / date / MuffinByteLabs.com / designer; the 2× logo from Board 1's `logos.pretty`; **a QR code to the repo** (KiCad's built-in QR footprint generator) — the standard the plan sets for Board 2; JLC's order-number token `JLCJLCJLCJLC` on the bottom silk.
- **Thermal reliefs** on every hand-soldered through-hole pad (relays, five terminals, bridge, electrolytics, PPTC); solid connections where current or heat demands it (buck exposed pad, input capacitor grounds).

## 12. Complete Bill of Materials — draft for LCSC ordering

Verified-in-stock LCSC numbers are given where confirmed on 2026-09-07; **(verify)** marks a number to confirm on the LCSC page at freeze. Library tier (Basic/Extended) no longer matters — nothing is assembled at JLC; buy everything from LCSC retail in the same checkout as the boards and stencil, and buy 6–7 sets of the cheap parts for five boards (placement losses).

### Semiconductors and modules

| Ref | What | Part | LCSC | Notes |
|---|---|---|---|---|
| U301 | Synchronous buck, 80 V / 2 A, HSOIC-8 | LMR38020SDDAR (TI) | C3192337 | Alternate: LMR16020PDDAR C190006 (non-sync — different passives, see §4) |
| U401 | USB ESD array | USBLC6-2SC6 | C7519 | Board 1 |
| U501 | 3.3 V LDO, 1 A, SOT-223 | AP7361C-33E-13 (Diodes) | C500795 | Alternate: Board 1's AP2112K-3.3TRG1 C51118 (SOT-23-5, runs hotter — §6) |
| U601 | Wi-Fi module | ESP32-S3-WROOM-1-N8 | C2913198 | Board 1 |
| U701–U704 | Optocoupler, CTR rank C, SMD gull-wing | EL817S1(C)(TU)-F (Everlight) | C106900 | PC817C-class equivalents acceptable if the same package |
| BR201 | Bridge rectifier 2 A / 600 V, KBP through-hole | KBP206 (MDD) | C2494 | any KBP206 / KBP210 |
| Q801, Q802 | NPN, SOT-23 | MMBT2222A (onsemi / Nexperia / Diodes) | (LCSC: pick a tier-one maker's listing) | hFE ≥ 100 at 150 mA; alt BC817-40 |
| Q901, Q902 | N-MOSFET 30 V logic-level, SOT-23 | AO3400A | C20917 | |
| D201 | TVS 43 V standoff, 600 W, SMB | SMBJ43A (Littelfuse) | C315993 | |
| D401 | TVS 5 V, SOD-123F | SMF5.0A | C2980403 | Board 1 |
| D301, D402, D901, D902 | Schottky 1 A / 40 V, SMA | SS14 | C2480 | OR diodes + MOSFET flybacks |
| D701–D704, D801, D802 | Switching diode, SOD-123 | 1N4148W | C81598 | opto anti-parallel, coil flyback |
| D709–D712 | Zener 4.7 V 500 mW, SOD-123 | BZT52C4V7-7-F (Diodes) | C260907 | input threshold — IEC 61131-2 Type 1 |
| D705–D708, D803, D804, D903, D904 | Red LED 0805 | (any high-efficiency red, Vf ≈ 1.9 V) | (verify) | 8 pcs |
| D501, D602 | Yellow-green LED 0603 | KT-0603YG / XL-0603QYGC | C2289 | Board 1's chemistry rule: ≈ 2 V Vf for a 3.3 V rail |
| D302 | Green LED 0805 | (any, on 5 V) | (verify) | FIELD PWR |

### Electromechanical, connectors, magnetics

| Ref | What | Part | LCSC | Notes |
|---|---|---|---|---|
| K801, K802 | Relay 5 V SPDT 10 A, THT, AgSnO₂, UL/VDE | HF3FF/005-1ZTF (Hongfa) | C2764967 | −40…85 °C; the Songle SRD-05VDC-SL-C (C35449) fits the footprint but is not the part |
| L301 | 15 µH shielded, Isat ≥ 3.8 A | SRR1260-150M (Bourns) | C2041333 | 12 × 12 × 6 mm; any equivalent ≥ 3.8 A Isat / ≤ 60 mΩ |
| F201 | PPTC 1.1 A hold / 60 V, radial | 60R110 (Littelfuse) or MF-RX110 (Bourns) | (verify; DigiKey fallback) | **not MF-R110 (30 V)** |
| F401 | PPTC 0.75 A / 16 V, 1206 | 1206L075/16WR | C371166 | Board 1 |
| J201 | Screw terminal, 2 pos, UL/VDE | Degson DG128-5.0-02P-14-00A(H) | C711349 | 5.0 mm pitch family (or Phoenix MKDS 1.5/2-5.08 from DigiKey); ≥ 10 A, 0.5–2.5 mm² wire; one family for all five |
| J701 | Screw terminal, 5 pos | Degson DG128-5.0-05P-14-00A(H) | (verify) | |
| J801, J802 | Screw terminal, 3 pos | Degson DG128-5.0-03P-14-00A(H) | C691861 | |
| J901 | Screw terminal, 4 pos | Degson DG128-5.0-04P-14-00A(H) | (verify) | |
| J401 | USB-C receptacle 16-pin | TYPE-C-31-M-12 | C165948 | Board 1 footprint |
| J601 | 1 × 6 header 2.54 mm — **DNP** | — | — | footprint only |
| SW601, SW602 | Tactile 5.1 mm | TS-1187A-B-A-B | C318884 | Board 1's 1/1/2/2 footprint |
| JP901 | Solder jumper, **open** | KiCad `SolderJumper_2_Open` | — | close for 5 V VLOAD |
| RV801, RV802 | MOV 7 mm disc — **DNP** | TDK/EPCOS S07K35 (B72207S0350K101) or 07D560K | (verify) | 35 V RMS / 45 V DC continuous |
| C201 | 470 µF 63 V 105 °C long-life low-ESR radial, ≥ 0.6 A ripple, ≥ 5,000 h | Nichicon UPW1J471MPD / Rubycon 63ZLH470MEFC12.5X20 / Panasonic EEU-FR1J471 | (verify) | 12.5 × 20 mm, 5 mm pitch; no no-name brands here |
| C901 | 100 µF 25 V electrolytic, 105 °C long-life | Nichicon UPW / Rubycon ZLH / Panasonic FR | (verify) | VLOAD bulk |
| FID1–FID3 | Fiducial 1 mm Cu / 2 mm mask | KiCad `Fiducial_1mm_Mask2mm_SilkRing` | — | three corners, top |

### Passives (0603 unless noted; all resistors 1 %)

| Ref | Value | Package | Purpose |
|---|---|---|---|
| R201, R202 | 100 kΩ | 0805 | VIN_SENSE top, two in series (≈ 19 V each) |
| R203 | 10 kΩ | 0603 | VIN_SENSE bottom → 1:21 |
| R301 | 64.9 kΩ | 0603 | RT → 400 kHz |
| R302 | 100 kΩ | 0603 | RFBT |
| R303 | 24.9 kΩ | 0603 | RFBB → 5.016 V |
| R304 | 91 kΩ | 0805 | RENT (UVLO top) |
| R305 | 20 kΩ | 0603 | RENB (UVLO bottom) |
| R306, R501, R603, R805, R806, R905, R906 | 1 kΩ | 0603 | LED limits, ≈ 1.3–3 mA |
| R401, R402 | 22 Ω | 0603 | USB series |
| R403, R404 | 5.1 kΩ | 0603 | USB-C CC pull-downs |
| R601, R602 | 10 kΩ | 0603 | EN / IO0 pull-ups |
| R701–R708 | 1.6 kΩ | **1206, anti-surge** (Yageo PA/AC, Panasonic ERJ-P08) | Opto series, two per channel |
| R709–R712 | 47 kΩ | 0603 | Opto collector pull-ups (τ = 47 ms with C701–C704) |
| R801, R803 | 680 Ω | 0603 | Relay base resistors |
| R802, R804, R902, R904 | 10 kΩ | 0603 | Base / gate pull-downs — OFF at boot |
| R901, R903 | 100 Ω | 0603 | Gate resistors |
| R807–R810 | 100 Ω — **DNP** | 1206 | Snubber resistors |
| C202 | 1 µF 100 V X7R | 1206 | Bus HF bypass |
| C203, C303*, C304*, C401, C602 | 100 nF | 0603 | *C303 = 100 V rated; C304 = 16 V |
| C301, C302 | 4.7 µF 100 V X7R | 1210 | Buck input |
| C305–C307 | 22 µF 25 V X7R | 1210 | Buck output |
| C308 | 22 pF — **DNP** | 0603 | CFF footprint |
| C402, C403 | 100 nF — **DNP** | 0603 | Reserved USB caps |
| C404, C503 | 10 µF 25 V | 0805 | USB_5V_PROT / 5V_SYS bulk |
| C501, C603 | 1 µF 16 V+ | 0603 | LDO in, EN delay |
| C502 | 4.7 µF 16 V X7R | 0603/0805 | LDO out (AP7361C wants ≥ 2.2 µF ceramic) |
| C601 | 22 µF 25 V | 0805 | Module bulk |
| C701–C704 | 1 µF 16 V X7R | 0603 | Opto input filters (τ = 47 ms with 47 kΩ) |
| C801–C804 | 100 nF 100 V X7R — **DNP** | 1206 | Snubber capacitors |

### Tally (the honest estimate)

≈ **116 placed components in ≈ 46 BOM lines** (105 reflowed on the plate, 11 through-hole by iron: K801, K802, F201, BR201, C201, C901 and the five terminals), plus 14 test points, 3 fiducials, 4 mounting holes, 1 logo, 1 QR, and 14 DNP footprints (J601, C308, C402, C403, R807–R810, C801–C804, RV801, RV802). The plan's "60–75 parts" was the count before the review added the second rail, the LED chain and the snubber footprints; the bench time it implies is ≈ 1.5–2.5 h of placement for the first article.

### Bought separately — bench and demo (plan §10)

24 VAC plug-in transformer · 24 VAC sprinkler solenoid valve · float switch · leak pads · 5 V pump + tubing · 12 V / 5 A bench adapter · wire, jug, spare 3 A fuses.

## 13. Test Points

TP = Test Point: a bare copper pad, named on the silkscreen, where a probe lands. Through-hole (THT) pads take a header pin.

| TP | Net | What is checked there |
|---|---|---|
| TP1 | VBUS_DC | Rectified bus: 7–39 V, 120 Hz ripple on AC |
| TP2 | 5V_BUCK | The acceptance number: 5.00 V ± 3 %, < 50 mVpp — probe here, at C305–C307 |
| TP3 | 5V_SYS | ≈ 4.6 V from either source |
| TP4 | +3V3 | 3.30 V |
| TP5 | GND | Scope ground, logic side |
| TP6 | GND (THT) | Header-pin ground for the recovery UART |
| TP7 | SW | **Small pad** at the inductor — switch-node shape only, never a ripple measurement |
| TP8 | EN | Reset line, reset button action |
| TP9 | IO0 | Boot strap, boot button action |
| TP10 | TXD0 (THT) | Recovery UART transmit |
| TP11 | RXD0 (THT) | Recovery UART receive |
| TP12 | VLOAD | 5 V jumpered, or the external supply |
| TP13 | VIN_SENSE | Divider output, 0.43–1.86 V (bus ÷ 21) |
| TP14 | PG | Buck power-good (open drain; add a 10 k pull-up on the probe if a level is wanted) |

None on the field side: probing IN1–IN4, COM or the contacts happens at the terminal screws.

## 14. Firmware Contract (summary — the full contract lives in `firmware/README.md`)

| Duty | Rule | Why |
|---|---|---|
| Outputs at boot | All five drive pins are inputs (high-impedance) until firmware deliberately configures them; hardware pull-downs hold everything OFF. Configure outputs *after* reading VIN_SENSE. | §9, §10 — no relay chatter, ever |
| Field-power gating | `V_bus = ADC volts × 21`; report "field power absent" and refuse output commands when V_bus < 7 V. | Relays cannot work without 5V_BUCK anyway; this makes the log say why |
| Input debounce | An input changes state only after 3 consecutive samples 10 ms apart agree. Works identically for AC and DC sources. | §8 — the 4.7 µF makes AC a steady LOW; the debounce makes the edge clean |
| Relay interlocks | Deployment config declares mutually exclusive relays (heat vs cool) and a minimum off-time (compressor short-cycle lockout, default 5 min). | Use cases 2–3 |
| Supervisory, not primary | The condensate use case adds a trip and an alert *in series with* the OEM float-switch interlock; firmware and documentation never describe this board as the safety device. | Second review, item 10 — NC wiring is fail-operational, not fail-safe |
| Safe state on link loss | Configurable per relay: hold / open / close after N minutes without the broker. Default hold. | An overflow guard must not stop guarding because Wi-Fi dropped |
| OTA | ArduinoOTA over Wi-Fi is the field update path; USB is a bench port. | §17 ground-loop rule |
| Watchdog | Hardware task watchdog enabled; reset-reason logged and published at boot. | Torture-loop acceptance |
| Telemetry | Publish VIN_SENSE (volts), input states, output states, reset reason, uptime; Home Assistant discovery payloads reused from Board 1's `net.cpp`. | |
| Pins | `PinMap_CheatSheet.md` is the source of truth; `Wire`/I²C not used unless J601 is populated. | |

## 15. Bring-Up Plan (staged; film the last step)

0. **Inspect before power** (×10 loupe): module castellations and alignment, every polarity mark (C201, C901, all diodes, LEDs, optos, relays, the buck's pin 1), bridges, tombstones, paste starvation. Fix with iron and wick now; the same fault at step 1 costs the debugging session.
1. **Bench supply, 12 V DC, 100 mA limit, unprogrammed board, no loads:** bridge orientation (TP1 ≈ 10.5 V), FIELD PWR LED, TP2 = 5.00 V ± 3 %, TP3 ≈ 4.6 V, TP4 = 3.30 V, first look at ripple on TP2 and the SW node shape on TP7. Then 24 V DC and 36 V DC: rails again, buck warmth by touch. **Raise the limit to 250–300 mA before any firmware that uses Wi-Fi runs** — a transmit peak needs ≈ 200 mA at the 12 V input, and a 100 mA limit would fake a brownout (second review, item 15).
2. **24 VAC wall transformer:** TP1 ripple on the scope (≈ 3 V sawtooth at 120 Hz under load), rails clean, bulk capacitor warmth.
3. **UVLO:** ramp the bench supply down from 12 V — the buck must stop cleanly at ≈ 7.6 V terminal (6.1 V bus) and restart at ≈ 8.5 V, no chatter. Record both numbers.
4. **USB only, no field power:** flash blink; TP3 ≈ 4.6 V; **TP2 = 0 V, relays cannot click** — the split rail proves itself.
5. **Inputs:** 24 V DC then 24 VAC through the resistor jig into each channel; field LED lights, firmware reads a steady ON, scope IN1_L to see the ≤ 0.7 V ripple during the AC gap.
6. **Relays:** click test, then the real sprinkler valve on K1 NO. **Pump on OUT1** with JP901 closed; note the inrush on TP2.
7. **Rail acceptance at 1.25 A** (4 Ω / 10 W across TP2–GND, on 12 V DC and on 24 VAC): 5.00 V ± 3 %, ripple < 50 mVpp, buck and bridge temperatures after five minutes. Then the **torture loop, 10 minutes:** Wi-Fi ping flood, both relays at 1 Hz, pump on; watch for resets (reset-reason in the log), record buck and LDO temperatures with the probe.
8. **The demo take.**

Full procedure, expected voltages and record sheet: `BringUp_Guide.md`.

## 16. Manufacturing & Assembly (bench, per plan §3.4)

- **JLCPCB order:** bare 2-layer PCB ×5 + **0.12 mm frameless stencil, top paste, ships in the same box**. No PCBA line, no part-tier fees. Order-number token on the bottom silk; "Remove Mark" if it is still free.
- **Paste layer before ordering the stencil:** the LMR38020 exposed pad and the ESP32 module's centre pad get **windowpaned apertures at ≈ 50–60 % coverage** (four squares each); everything else 1:1. Check the paste layer in the fab preview — a stencil is only as good as its apertures.
- **Parts:** LCSC, same checkout as the boards. Everything Sn63/Pb37-compatible (all standard). **MSL discipline (J-STD-033):** the ESP32-S3 module is MSL 3 — 168 h of floor life after the bag is opened; the buck and the optocouplers are typically MSL 3 too. Keep them sealed with their desiccant until assembly day, or bake (125 °C, 24 h for the module) before reflow. A "popcorned" module cracks under the pad nobody can see.
- **Bench:** ESD mat and wrist strap (ANSI/ESD S20.20 practice — the plan's silicone mat is not an ESD mat); inspection to **IPC-A-610 Class 2** criteria (`Assembly_and_Stencil_Plan.md` §6).
- **Reflow order on the plate:** all 0603/0805/1206 passives → SOD-123 / SMA / SOT-23 diodes and transistors → the four optos, USBLC6, the SOT-223 regulator → the buck IC → the 1210 capacitors → the shielded inductor → **the ESP32-S3 module last**. Single-sided, bottom heat, the paste manufacturer's profile, thermocouple on the board not the plate, board cools undisturbed.
- **Iron afterwards, never the plate:** K801, K802, J201, J701, J801, J802, J901, BR201, C201, C901, F201, TP6/TP10/TP11.
- **One first article, then the rest.** Inspect, bring up, let it say what went wrong, fix the technique, then build the other four.
- **RoHS statement:** boards assembled with Sn63/Pb37 are not RoHS-compliant and are not represented as such. Fume extraction on, hands washed, no food at the bench.

Detail and the stencil/aperture worksheet: `Assembly_and_Stencil_Plan.md`.

## 17. Known Limitations & Accepted Risks (stated openly)

- **The power input is not isolated from logic ground** — the bridge's negative is GND, one diode drop from the field return. Only the opto inputs and the relay contacts are galvanically isolated. The silkscreen says so.
- **Ground loop through USB.** If the field supply's negative or the 24 VAC common is earthed *and* the laptop is earthed, the USB cable's ground bypasses the bridge's return diode and carries the board's return current. Rule, printed on the silk beside the USB connector: **DISCONNECT FIELD POWER BEFORE USB.** The one exception is the bench, where the plug-in 24 VAC transformer and an unearthed bench supply are floating and a battery-powered laptop has no earth — bring-up steps 9–10 rely on that and say so. In the field, USB is never connected; updates are OTA. An isolated USB/debug port is a Rev B feature, not a Rev A promise.
- **External VLOAD is not reverse-protected.** Wired backwards it shorts through the MOSFET body diodes and the SS14 flybacks. Meter the supply first; big **+** on the silk.
- **Input range is 10–36 V DC guaranteed, ≈ 8.5 V typical.** "9 V" appears nowhere on the silk or in a proposal. At 9–12 V DC with the full 0.95 A load the bridge dissipates 1–1.5 W and runs warm; this is the price of "either polarity".
- **UVLO tolerance is ± 12 %** (the EN threshold spread) — start and stop voltages are recorded at bring-up per board, not promised to a tenth of a volt.
- **The isolation is functional, not a safety barrier.** 5 kV optos and a 2.5 mm moat make 30 V field circuits safe to share a board with the logic; nothing here is rated for mains, and mains is refused.
- **Relay contacts are rated by the board at 2 A / 30 V**, whatever the relay prints. Inductive loads need the snubber/MOV footprints fitted or a diode across the load.
- **USB pair impedance is uncontrolled on 2 layers** — short, coupled, via-free, over solid ground. Correct trade at USB Full Speed.
- **EMC immunity is not tested.** No IEC 61000-4-2/-4/-5 claim is made. The inputs have 3.2 kΩ of series resistance and diodes both ways; the power entry has the TVS and 470 µF. Bidirectional TVS per input and a power-entry choke are the Rev B footprints if a client requires the test (audit §4).
- **Not a listed product.** UL-recognised components throughout (relay, PPTC, terminals, optos, TVS); the board itself carries no UL/CE listing and the README does not claim one.
- **The 3.3 V regulator dissipates up to 0.49 W** during Wi-Fi transmit bursts; the SOT-223 AP7361C keeps that to a ≈ 35–55 °C rise. Measured in the torture loop.
- **The condensate use case is supervisory.** Wiring K2 through NC keeps cooling running if this board loses power — that is *fail-operational*, chosen for availability, not fail-safe. The OEM float-switch interlock stays in circuit; this board adds a second trip and a phone alert and is never the primary safety device.
- **Boards assembled with Sn63/Pb37 are not RoHS-compliant** and will not be represented as such.
- **PFM at light load** (the S variant) means a little more output ripple when the board is nearly idle; irrelevant to the LDO behind it. The FS variant is a drop-in if it ever matters.

## 18. Pre-Capture Checklist (what to have before the first schematic sheet)

- [ ] `hardware/` KiCad project created as `ESP32S3_FieldIO`, libraries from `hardware/libs/` (copied from Board 1 and renamed) in `fp-lib-table` / `sym-lib-table`.
- [ ] Per-sheet annotation set (200 / 300 / … per sheet) before the first component is placed.
- [ ] **Enclosure chosen and its PCB drawing in `mechanical/`** — the board outline and terminal positions come from it (`../mechanical/README.md`).
- [ ] LMR38020 symbol + HSOIC-8 (DDA) footprint, AP7361C SOT-223 (KiCad stock `SOT-223-3_TabPin2`), SRR1260 footprint, KBP footprint, HF3FF footprint (Hongfa drawing: coil pins 12.2 mm apart, contact pins on 3.4 mm ± 0.3 — the SRD "T73" pattern, but draw it from the Hongfa sheet), Degson DG128 terminal footprints, EL817S1 SMD-4 footprint, radial PPTC footprint, 12.5 mm electrolytic footprint, SOD-123 for the Zeners — each checked against its datasheet drawing (Board 1's `Footprint_Check` method).
- [ ] Netclasses FIELD / CONTACT / POWER / USB created and the moat DRC rule entered (`KiCad_Settings_RevA.md`).
- [ ] LCSC stock re-checked for U301, L301, F201, U701–U704, K801/K802 on the day the BOM is frozen; alternates recorded in the BOM.
- [ ] Datasheets for every new part in `references/datasheets/` (index in its README; the ones not yet fetched are listed there with links).

## Addendum A — What this document changes from Plan v7.3 §4, and why

Every change is a finding in [`reviews/Spec_Review_RevA_2026-09-07.md`](reviews/Spec_Review_RevA_2026-09-07.md); the finding numbers are in brackets.

| Plan v7.3 said | This document says | Because |
|---|---|---|
| LMR36015 / TPS54160, LM5164 at 100 V if needed | **LMR38020SDDAR**, 80 V, 2 A, HSOIC-8; LMR16020 as alternate | leadless QFN cannot be inspected; LM5164 is 1 A; the 80 V part passes the TVS check outright [4] |
| Opto RC = 10 k + 1 µF | **10 k + 4.7 µF** + 3-sample firmware debounce | 1 µF rises to 2 V during the 60 Hz gap [1] |
| UVLO ≈ 7.5 V; 9–36 V DC | **UVLO 7.0 / 6.1 V**; **10–36 V DC guaranteed**, ≈ 8.5 V typical | 7.5 V and 9 V contradict each other [2] |
| PPTC 0.5 A hold | **1.1 A hold, 60 V radial** (60R110 / MF-RX110) | 0.79 A input at 9 V full load [3] |
| One 5 V rail, USB OR'd in | **5V_BUCK** (relays, VLOAD) and **5V_SYS** (logic) split by SS14s | relays would click on USB power [6] |
| MOSFET gate pull-down 100 k | **10 k** on gates and bases; outputs on no-default-pull pins | pull-up-at-reset pins would turn the FET on [5] |
| Opto series 2 × 2.4 k 0805 | **2 × 2.4 k 1206** | 113 mW per 0805 at 36 V [8] |
| Input LED on the logic side | **In series with the opto LED, field side** | logic-side LED loads the opto's output [9] |
| 330–470 µF bulk | **470 µF 63 V, ≥ 0.6 A ripple-rated** | ripple current sized [16] |
| — | **VIN_SENSE** divider, FIELD PWR LED, expansion header, VLOAD bulk cap, PG test point | [11–13] |
| — | Ground-loop rule, reverse-VLOAD rule, OTA as the field update path | [7, 10, 22] |
| 60–75 parts | ≈ 112 placed components, ≈ 45 lines | tally [14] |
| Snubber/MOV "footprints" | RC 100 Ω + 100 nF 100 V; MOV 07D560K; across COM–NO and COM–NC | [15] |
| Power LED per Board 1 (10 k) | 1 kΩ | no sleep budget [19] |
| — | Per-sheet ×100 annotation; moat as a DRC rule; ≤ 100 × 100 mm; 0.12 mm stencil with windowpaned pads | [17, 18, 20, 21] |

### Adopted from the second-opinion review (same day) — [`reviews/Second_Opinion_Review_RevA_2026-09-07.md`](reviews/Second_Opinion_Review_RevA_2026-09-07.md)

| First draft of this document said | Now says | Because |
|---|---|---|
| U501 = AP2112K-3.3 (SOT-23-5), reused from Board 1 | **AP7361C-33E-13, 1 A, SOT-223** (C500795); AP2112K as alternate | this board never sleeps; SOT-223 halves the temperature rise [2nd-review 5] |
| Opto filter 10 kΩ + 4.7 µF | **47 kΩ + 1 µF** (same τ = 47 ms) | 5× the sink margin, 0603 cap, CTR-ageing headroom [2nd-review 6, the RC part of it] |
| VIN_SENSE 100 k / 6.8 k (1:15.7) | **2 × 100 k / 10 k (1:21)** | 69 V clamp must map below the ESP32's 3.6 V absolute maximum [2nd-review 12, ratio adjusted] |
| JP901 bridged by default; J901 = VLOAD · OUT1 · OUT2 · GND | **JP901 open by default; J901 = VLOAD+ · GND · OUT1− · OUT2−** | an external supply into a closed jumper would feed the buck output and the relay coils [2nd-review 11] |
| USB rule in prose only | **DISCONNECT FIELD POWER BEFORE USB on the silk**; bench exception spelled out | [2nd-review 8] |
| Published input 10–36 V DC | **12–36 V DC published, 10 V guaranteed floor** | the two real systems are 12 V and 24 V; the arithmetic still guarantees 10 V [2nd-review 1, lower bound only] |
| Rail acceptance at 0.8 A | **1.25 A test load, 1.1 A design point** | [2nd-review 13] |
| Bring-up limit 100 mA | 100 mA for the unprogrammed board, **250–300 mA once Wi-Fi runs** | [2nd-review 15] |
| "Condensate overflow guard" | "**supervisor**, in series with the OEM interlock" | NC is fail-operational, not fail-safe [2nd-review 10] |
| Isolation map | + the three-domain sentence | [2nd-review 7, already the design — wording made explicit] |

### Adopted from the industry-standard audit (same day) — [`reviews/Industry_Standard_Audit_RevA_2026-09-07.md`](reviews/Industry_Standard_Audit_RevA_2026-09-07.md)

| Was | Now | Because |
|---|---|---|
| Songle SRD-05VDC-SL-C relays | **Hongfa HF3FF/005-1ZTF** (C2764967) | UL/VDE, AgSnO₂, −40…85 °C, top-three maker; same outline and coil [audit §1] |
| S8050 relay transistors | **MMBT2222A** (BC817-40 alt) | three tier-one sources, specified gain; same network [audit §1] |
| Opto input: 2 × 2.4 kΩ, threshold ≈ 4 V by CTR | **BZT52C4V7 in series + 2 × 1.6 kΩ 1206 anti-surge** — **IEC 61131-2 Type 1** (OFF ≤ 5 V, ON ≥ 15 V at 2.27 mA) | a defined threshold is what a 24 V input is [audit §2.1] |
| generic KF128 screw terminals | **Degson DG128 (UL/VDE) or Phoenix MKDS** | recognised makers for anything touching field wiring [audit §1] |
| — | **FID1–FID3** fiducials | stencil alignment; JLC-ready [audit §2.13] |
| board size "≈ 100 × 70 mm" | **outline from a DIN-rail enclosure's PCB drawing**, chosen before layout | field controllers live on DIN rail [audit §2.12] |
| — | **MSL / J-STD-033 handling, IPC-A-610 Class 2 acceptance, ESD mat** in the assembly plan | [audit §2.5–2.8] |
| electrolytics "any 105 °C" | **named long-life series** (Nichicon UPW / Rubycon ZLH / Panasonic FR, ≥ 5,000 h) | always-on equipment [audit §1] |
| — | `mechanical/`, `CHANGELOG.md`, KiCad ERC/DRC CI | repository audit [audit §3] |

Recorded as optional or Rev B in the audit's §4: ISO1211/ISO1212 digital-input receivers, TPL7407L / TPS27S100 protected outputs, per-input TVS and a power-entry choke, pluggable terminal blocks, conformal coating, PlatformIO, TLS/signed OTA.

Not adopted from the second-opinion review, with the reasons in its file: LM5012 (COT + ripple injection + catch diode is more design risk than the synchronous, internally compensated LMR38020, whose 85 V absolute maximum already passes the TVS check), 100 V bulk capacitor (the node cannot reach the clamp voltage with 470 µF in parallel), LTV-814 AC-input optocouplers (20 % minimum CTR, and the series indicator LED needs the anti-parallel diode anyway), 100 kΩ pull-downs (reset-state pull-ups), 30 VAC upper limit (41 V bus against a 43 V standoff), SS14 for the relay flyback (1N4148W is rated 2× the coil current; optional).

### Companion documents

| Document | What it carries |
|---|---|
| [`PROJECT_STATUS.md`](PROJECT_STATUS.md) | The live hand-off: where the project stands, decisions, what is next |
| [`reviews/Spec_Review_RevA_2026-09-07.md`](reviews/Spec_Review_RevA_2026-09-07.md) | The findings behind Addendum A |
| [`calcs/board2_calcs.py`](calcs/board2_calcs.py) | Every number in this document, recomputed on demand |
| [`PinMap_CheatSheet.md`](PinMap_CheatSheet.md) | GPIO / net / terminal map |
| [`Hard_Rules_Layout_RevA.md`](Hard_Rules_Layout_RevA.md) | The graded rulebook, with the buck and moat amendments |
| [`KiCad_Settings_RevA.md`](KiCad_Settings_RevA.md) | Board setup, netclasses, the moat DRC rule |
| [`Assembly_and_Stencil_Plan.md`](Assembly_and_Stencil_Plan.md) | Stencil, paste apertures, placement order, first-article inspection |
| [`BringUp_Guide.md`](BringUp_Guide.md) | Staged first power, expected voltages, record sheet |
| [`../firmware/README.md`](../firmware/README.md) | The hardware → firmware contract in full |
| [`../references/datasheets/README.md`](../references/datasheets/README.md) | Datasheet index, fetched and to-fetch |
