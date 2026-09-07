# Layout Hard Rules — ESP32-S3 Protected Field I/O Controller Rev A

*Board 1's graded rulebook, carried over and amended for a 2-layer board with a switching converter and an isolation moat. "LAW" items are physics, safety or fabrication requirements — violating one produces a real defect. "STRONG PRACTICE" items are professional habits — deviate only with a reason. Written 2026-09-07 before layout; mechanisms that are new on this board are given inline, the rest are in Board 1's `Layout_Readiness_and_Placement_Guide_RevA.md`.*

---

## LAW — physics, safety, fabrication

### The moat (new)
1. **≥ 2.5 mm copper-free on both layers** between every field net and every non-field net, along the whole boundary; **≥ 4 mm** around the relay contact terminals. Field nets: FLD_PWR_A/B, IN1–IN4, FLD_COM, K1_NO/COM/NC, K2_NO/COM/NC. Enforced by the DRC rule in `KiCad_Settings_RevA.md` §4 — a moat violation is a DRC error, not an opinion.
2. **Nothing crosses the moat but light and magnetism**: the four optocoupler bodies and the two relay bodies straddle it; no trace, no pour, no via, no silk text.
3. **No ground pour on the field side.** Field copper is per-net local fills only. The rectifier's negative output (VBUS_DC return) is *logic* ground and joins the logic pour at **one star point at the buck's input capacitors** — the 120 Hz charging pulses of C201 must never flow through the ESP32's ground.
4. **Field terminals on at most two board edges; USB-C on the opposite edge; J901 (VLOAD, not isolated) on the logic side's edge.** Silkscreen line + FIELD SIDE / LOGIC SIDE text along the moat; **NOT FOR MAINS · ≤30V · 2A** beside the relay terminals.

### The buck (new)
5. **Hot loop = C303 (100 nF, 100 V) across VIN (pin 3) and GND (pin 1), on the top layer, first thing placed after U301.** C301/C302 (4.7 µF) directly behind it. Ground vias at every input-capacitor ground pad. (Mechanism: both switches are inside the package, so the loop carrying the 400 kHz pulsed current is pins 1–3 and this capacitor. Every millimetre of loop is ≈ 1 nH; V = L·ΔI/Δt with 2 A in ≈ 20 ns edges makes 1 nH ≈ 0.1 V of ringing per millimetre.)
6. **SW node short and wide, no vias, nothing alongside it** — pin 8 → L301 → the output capacitors. It is the only high-dV/dt net on the board. FB, VIN_SENSE, the USB pair and the input nets never run within 3 mm of it or under it.
7. **C304 (BOOT) across pins 7–8**, short and wide. **R301 (RT) at pin 4**, grounded at the exposed pad. **FB divider at pin 5, ≤ 5 mm**, R302 tapped at the **output capacitor** (C305–C307), not at the inductor pad.
8. **Bottom copper unbroken under the entire converter** — U301, L301, all its capacitors. No trace crosses beneath.
9. **Exposed pad: solid top connection + 4–6 thermal vias (0.3 mm drill) to the bottom ground.** It is the IC's only heatsink for ≈ 0.5 W.
10. **Converter and module at opposite ends of the board; ≥ 15 mm from the antenna keep-out to L301 and the SW copper.**
11. **Traces:** VBUS_DC and 5V_BUCK ≥ 0.8 mm (2 A at a 10 °C rise on 1 oz); VLOAD ≥ 0.8 mm; relay contact nets ≥ 1.5 mm (3.2 A at 10 °C); +3V3 and 5V_SYS ≥ 0.5 mm. IPC-2221 external, 1 oz: 0.5 mm → 1.4 A, 0.8 mm → 2.0 A, 1.0 mm → 2.4 A, 1.5 mm → 3.2 A, 2.0 mm → 3.9 A, all at a 10 °C rise.

### Radio (Board 1, unchanged)
12. Antenna keep-out absolute on both layers: no copper, traces, silk, pour or parts; overhang off the edge preferred. No metal in front of it; ≥ 15 mm to enclosure walls.
13. Ground stitching vias **around** the keep-out, never inside.
14. Off-board conductors — every terminal wire and the traces feeding them — stay ≥ 15 mm from the antenna zone; exits face away from it. (Conductors ≥ ~12 mm couple to the 2.4 GHz field; the field wiring is the biggest antenna in the system.)

### USB (Board 1, amended for 2 layers)
15. D+/D− as a glued pair: side by side, constant gap, matched length, **zero vias**, top layer only, **< 20 mm long**, over unbroken bottom ground. Impedance is not controlled on 2-layer 1.6 mm FR4 and is not claimed.
16. Copper order: J401 VBUS pads → D401 (TVS) within a few mm → F401 → C404 → D402. Data: J401 → U401 flow-through → R401/R402 at the module end → module pins.
17. R403/R404 (5.1 k) on CC1/CC2, one each. C402/C403 stay DNP. J401's shell nose overhangs the edge ≈ 1 mm per the HRO drawing.
18. J401's GND pads A1/B1/A12/B12 **connected** — Board 1's blocking finding.

### Power integrity
19. Every decoupler at its pin, millimetres not centimetres: C601/C602 @ module 3V3 · C501 (1 µF) @ LDO in · C502 (4.7 µF) @ LDO out · C401 @ U401 VBUS · R601/C603 @ EN · R602 @ IO0 · C203 @ IO8 · C701–C704 (1 µF) @ the opto collectors (logic side). Every decoupler's ground pad gets its own via.
20. **5V_SYS node** (D301 cathode + D402 cathode + C503 + LDO input) compact and fat.
21. **C901 (100 µF) at J901**, on the VLOAD pin; D901/D902 anodes at the MOSFET drains, cathodes at VLOAD, short.

### Thermal
22. LDO U501 (AP7361C, SOT-223): the tab (pin 2, GND) on a copper pour ≥ 1 cm², stitched to the bottom plane with 4+ vias — ≈ 0.49 W peaks, 0.19 W sustained; the SOT-223 was chosen for exactly this pour.
23. Bridge BR201: 1.5 W at 9 V DC full load — through-hole pins into generous copper on both layers; not next to C201 or the optos.
24. Relay coils are 0.36 W each, continuous when on — nothing temperature-sensitive touching them (nothing on this board is).

### Analogue
25. VIN_SENSE: R201/R202 (the two 100 kΩ) at the bus, R203 and C203 **at the module pin**; the trace runs on the logic side, never alongside SW or the USB pair.
26. Opto collector nodes IN1_L–IN4_L: short runs from U70x to the module; C70x at the module end of each. 47 kΩ + 1 µF makes them slow, high-impedance nets — keep them off the SW node's side of the board and away from the relay coil drivers; otherwise "not under the inductor" is the only rule.

### Ground
27. Bottom layer = one continuous logic-side ground. No trenches, especially under the converter, the USB pair and the module.
28. Stitch top pour to bottom ground every ~5 mm and at every decoupler; extra ring around the antenna keep-out and around the converter.
29. GND is never a long skinny trace — pour + vias. Module centre pad into the plane through its via array.

### Assembly & fabrication (bench process — new)
30. **Every reflowed part on the top layer.** Nothing on the bottom but copper and silk.
31. **Through-hole for anything with a screw, a coil or a can**: K801, K802, J201, J701, J801, J802, J901, BR201, C201, C901, F201. Their pads get **thermal reliefs** so the iron can wet them after reflow. The through-hole test points TP6/TP10/TP11 likewise.
32. **No leadless packages** (no QFN, no DFN, no BGA) — every joint inspectable under ×10. Finest pitch on the board is the USB-C's 0.5 mm; the buck is 1.27 mm HSOIC.
33. **Paste layer:** U301's exposed pad and U601's centre pad windowpaned to ≈ 50–60 % coverage; all other apertures 1:1. Checked on the fab's paste preview before the stencil is ordered.
34. Passives ≥ 0603; opto series resistors and the bus HF cap 1206; buck ceramics 1210. Part orientation consistent (all 0603 values readable from one direction) — it halves the tweezers time.
35. Copper ≥ 0.5 mm from the board edge; courtyards clear; DRC 0 / unconnected 0 / parity 0 before any order.
36. Connector openings face off-board; M3 heads Ø 6.5 mm part-free; no hole or standoff in the antenna region.
37. **Safety silk:** terminal labels in plain English per `PinMap_CheatSheet.md`; **+** at C201, C901 and VLOAD+; every diode's cathode and LED cathode; opto and relay pin 1; BOOT/RESET; TP names; NOT FOR MAINS; NOT ISOLATED at J901; ISOLATED at J701/J801/J802; **DISCONNECT FIELD POWER BEFORE USB** beside J401; **CLOSE JP901 FOR 5V** beside the jumper.

### Process, before ordering
38. ERC and DRC clean with board↔schematic parity; the moat rule passing; the paste preview inspected.
39. DNP parts excluded from BOM and placement files (J601, C308, C402, C403, R807–R810, C801–C804, RV801, RV802).
40. LCSC stock re-verified for U301, L301, F201, U701–U704, K801/K802 at freeze; alternates in the BOM.
41. Fab files frozen into `fabrication/revA/` from a tagged commit; committed and pushed.

---

## STRONG PRACTICE — do unless there's a reason

42. Smallest capacitor closest to the pin (C602 before C601; C303 before C301/C302); supply traces flow past the caps into the pin.
43. Draw the moat outline and the bottom ground zone **before** placing anything else; place the edge-committed parts (J401, U601, the five terminals, the relays) next and lock them; then the buck cluster; then everything else.
44. Opto bodies in a row along the moat; series resistors and LEDs on the field side of each; pull-up and capacitor on the logic side of each — the schematic's left-right order becomes the board's.
45. Relays with coil pins toward the logic side, contacts toward the field terminals — the relay's own pinout draws the moat for you.
46. 45° corners; parts at 0°/90°; doubled vias where real current changes layers (5V_BUCK, VLOAD, VBUS_DC return).
47. Keep the board ≤ 100 × 100 mm; aim for ≈ 100 × 70. The stencil ships in the same box, and the PCB price stays in the lowest tier.
48. Silk: name / Rev A / date / MuffinByteLabs.com / designer, the 2× logo, and a **QR to the repo** — the standard the plan sets from Board 2 on.

## Pocket numbers

- Trace ≈ 6 nH/cm, ≈ 10 mΩ/cm at 0.5 mm width (1 oz) · via ≈ 0.5–1 nH · cap ESL ≈ 0.5–1 nH · loose wire ≈ 10 nH/cm.
- **V = L·(ΔI/Δt)**: nH × (A ÷ ns) = V. The buck's 2 A / 20 ns edge across 5 nH of hot loop = 0.5 V of ringing. Keep the loop under a few nH.
- ΔV = I·Δt/C (tank sag) — C201: 0.18 A × 8.3 ms / 470 µF = 3.2 V · τ = R·C — opto filter 10 k × 4.7 µF = 47 ms.
- IPC-2221 external 1 oz: I = 0.048 × ΔT^0.44 × A^0.725 (A in mil²).
- 2.4 GHz: λ ≈ 12.5 cm; conductors ≥ ~12 mm start coupling to the antenna.
- IPC-2221 clearance, uncoated external, ≤ 100 V: 0.6 mm. The moat is 4× that.
