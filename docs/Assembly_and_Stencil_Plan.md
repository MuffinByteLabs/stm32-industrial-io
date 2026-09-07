# Assembly & Stencil Plan — Rev A (bench build, per plan §3.4 / §4.9)

*Written 2026-09-07. This board is the first stencil-and-hot-plate build; the plan's process is restated here with this board's specifics filled in. Update after the first article with what actually happened — that record is the deliverable the plan calls "assembly footage", in writing.*

## 1. What is ordered, and from where

| Item | Where | Spec | Notes |
|---|---|---|---|
| PCB × 5 | JLCPCB | 2-layer, 1.6 mm, 1 oz, green, lead-free HASL, ≤ 100 × 100 mm | Cheapest tier; tab-routed outline because of the corner radii; "Remove order number" if free, else the `JLCJLCJLCJLC` token on the bottom silk |
| Stencil | JLCPCB, same order | **Frameless, top paste only, 0.12 mm**, custom size = board + 20 mm margin | Ships in the same box when ≤ 280 × 280 mm; ≈ $3–8 |
| Parts | LCSC, same checkout | Quantities for **6–7 boards** of every cheap line; 5 of the expensive ones (U301, U601, L301, relays) + 1 spare U301 | LCSC and JLCPCB share a cart and a shipment |
| Solder paste | local / Amazon | Sn63/Pb37 no-clean, T3/T4 mesh, syringe or jar | Store per the manufacturer's instructions; bring to room temperature before opening |
| Hot plate, tweezers, squeegee, loupe, flux, wick, IPA, Kapton, thermocouple | plan §10 starter kit | | Bought once, before Board 2 |

## 2. Stencil thickness and apertures — the decision

- **0.12 mm** is the compromise this board's mix wants: the USB-C's 0.5 mm-pitch pins prefer 0.10–0.12, the 1210 ceramics and the inductor pads would take 0.15, 0603s are fine anywhere in that range. 0.12 keeps the USB-C from bridging without starving the big pads.
- **Two exposed pads get windowpaned apertures** in the footprint's paste layer before the gerbers are generated:
  - **U301 (LMR38020) thermal pad** — four squares, ≈ 50–60 % of the pad area. A full-area aperture floats the part on a paste cushion, tilts it, and pushes paste out into the pins as solder balls.
  - **U601 (ESP32-S3-WROOM-1) centre pad** — four windows, ≈ 50 %. The module's hidden ground pad cannot be inspected once the part is down; correct paste volume is the only way to manage its joint quality, and a functional test (Wi-Fi range, module temperature) confirms it afterwards.
- Every other aperture 1:1 with the pad. No aperture reduction on 0603s at 0.12 mm.
- **Check the paste layer twice:** in KiCad's 3D viewer with paste shown, and in the JLC fab preview's paste view, before the stencil is ordered.

## 3. Paste and place

1. Tape two spare boards (from the same order) flat as shims either side of the working board; tape the working board down; align the stencil on the fiducial-free board by eye against the pad pattern under the loupe (add two 1 mm fiducial dots on the silk if alignment is hard — free).
2. One squeegee pass at ≈ 45°, firm, then lift the stencil straight up. Inspect under the loupe: every pad printed, no smears between the USB-C pins. A bad print is wiped off with IPA and reprinted — cheaper than reworking a bridge.
3. **Place smallest and lowest first, tallest last** (tall parts block the tweezers for everything behind them):
   1. all 0603 resistors and capacitors
   2. 0805 / 1206 passives and LEDs
   3. SOD-123 (1N4148W, SMF5.0A), SMA (SS14 ×4), SOT-23 (S8050 ×2, AO3400A ×2)
   4. SOT-23-6 (USBLC6), SMB (SMBJ43A), SOT-223 (AP7361C — sits square, tab on its pour)
   5. the four EL817S1 optos
   6. **U301** — pin 1 dot under the loupe, sitting square on the windowpaned paste
   7. the 1210 ceramics (C301, C302, C305–C307)
   8. the SRR1260 inductor
   9. the USB-C receptacle — pegs into their holes, pins aligned under the loupe
   10. **the ESP32-S3 module last** — align the castellations to the silk outline
4. Polarity check of every polarised part against the assembly drawing before the plate: diodes, LEDs, optos, U301, U401, U501, U601, Q801/Q802, Q901/Q902.

## 4. Reflow

- Bottom heat only, single-sided, the paste manufacturer's profile (Sn63/Pb37: liquidus 183 °C; typical peak 210–220 °C, ≈ 30–60 s above liquidus).
- **Thermocouple on the board** (Kapton-taped near U601) — the plate's display reads the plate.
- Watch the paste: it turns from grey to bright as it reflows, and parts self-centre. End active heating once the *last* joints (the module and the inductor, highest thermal mass) have reflowed; move the board to a cool surface with a spatula, or switch the plate off and leave it undisturbed until below ≈ 100 °C. Never nudge a part while the solder is liquid.
- The ESP32-S3 module is the highest-thermal-mass part on the board and sets the minimum plate wattage (plan: 350–450 W, ≥ 100 × 100 mm heated area).

## 5. Through-hole, by iron, after the plate

In this order (short parts first): TP6/TP10/TP11 pins if fitted · F201 · C901 · BR201 · C201 (polarity!) · J201 · J701 · J801 · J802 · J901 · K801 · K802. Thermal reliefs on their pads are what lets a 60 W iron wet them without the ground pour sinking the heat.

## 6. First-article inspection (before power — this is BringUp step 0)

Under ×10, in this order, tick each:

- [ ] Module: all castellations wetted, no bridges, aligned to silk; no visible tilt
- [ ] U301: eight fillets visible, pin 1 correct, no solder balls at the pad edges
- [ ] USB-C: no bridges on the 0.5 mm pins; shell tabs wetted
- [ ] Every 0603/0805/1206: two fillets, no tombstones, no skew > 25 %
- [ ] Every diode band, LED cathode, opto dot, relay orientation, C201/C901 polarity
- [ ] No paste smears / solder balls between the opto field-side pads (they carry field voltage)
- [ ] All THT joints shiny cones, no cold joints on the relay and terminal pins

Fix with the iron first. A temperature-controlled hot-air station is bought only if the iron proves insufficient (plan §10) — decide after this board, not before.

## 7. What to write down (the assembly record)

Paste brand and lot · stencil thickness · plate set-point and measured board peak · time above liquidus · defects found and fixed · minutes per stage. That record goes into `docs/reviews/First_Article_RevA_<date>.md` and becomes the evidence behind the "JLCPCB-ready manufacturing packs" claim, and the input to the Board 3 assembly decision (plan §5.4).
