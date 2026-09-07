# KiCad Settings Log — ESP32-S3 Protected Field I/O Controller Rev A

*Every custom setting to configure before layout, with the reasoning. Written 2026-09-07 before the project exists in KiCad; tick items off as they are applied and add the date. KiCad 10, **2-layer**, JLCPCB bare board + stencil. Board 1's log (`ESP32S3_PlantMonitor_RevA/docs/KiCad_Settings_RevA.md`) is the parent; only differences are argued here.*

---

## 1. Project and libraries

- Create the project as `hardware/ESP32S3_FieldIO.kicad_pro` (File → New Project inside `hardware/`). The project-local `fp-lib-table` and `sym-lib-table` are already in `hardware/` and point at `${KIPRJMOD}/libs/` — keep `libs/` inside `hardware/`.
- `libs/FieldIO_JLC.pretty` / `.kicad_sym` / `.3dshapes` are **Board 1's verified footprints, renamed**: USB-C (HRO TYPE-C-31-M-12), the TS-1187A switch with its **1/1/2/2 pad renumbering**, D_SMA, D_SOD-123F, Fuse_1206, and the `logos` library. New footprints for this board go into the same library: LMR38020 HSOIC-8 (TI DDA0008B drawing), SRR1260 (12.4 × 12.4 mm pads per Bourns), KBP (4 × Ø 1.0 mm holes on 5.08 mm pitch), Hongfa HF3FF (Hongfa drawing: coil pins 12.2 mm apart, contact pins on 3.4 mm ± 0.3 — the T73 pattern), EL817S1 SMD-4 (2.54 mm pitch gull-wing, 7.62 mm row spacing), Degson DG128-5.0 terminals (5.0 mm pitch — or Phoenix MKDS at 5.08; one family), radial PPTC (5.08 mm), 12.5 mm radial electrolytic (5 mm pitch), 07D MOV disc (5 mm pitch). From KiCad's stock libraries: `SOT-223-3_TabPin2` for the AP7361C, `SolderJumper_2_Open` for JP901 (open by default — design doc §10), `TestPoint_Pad_D1.5mm` / `TestPoint_THTPad_D1.5mm_Drill0.7mm`, `Fiducial_1mm_Mask2mm_SilkRing` for FID1–FID3, `D_SOD-123` for the four Zeners. The board outline is imported from the enclosure's PCB drawing (`../mechanical/README.md`) — File → Import → Graphics onto Edge.Cuts — before the first footprint is placed.
- **Annotation: per sheet.** Schematic → Annotate → "Use first free number after" = 200 for sheet 02, 300 for sheet 03 … 1000 for sheet 10. Do this on each sheet before placing symbols, so the design document's designators are the schematic's.

## 2. Board Setup → Design Rules → Constraints

| Field | Value | Why |
|---|---|---|
| Minimum clearance | **0.2 mm** | JLC 2-layer can do 0.127; 0.2 is a 1.5× cushion. The moat has its own rule (§4). |
| Minimum track width | **0.2 mm** | Signals route at 0.25–0.3; power at 0.8–1.5. |
| Minimum connection width | **0.2 mm** | Catches necked zone connections. |
| Minimum annular width | **0.15 mm** | JLC minimum; the 0.6/0.3 via has exactly 0.15. |
| Minimum via diameter | **0.5 mm** | Working via 0.6/0.3; stitching 0.8/0.4; thermal vias 0.6/0.3. |
| Copper to hole clearance | **0.3 mm** | JLC PTH hole-to-track 0.28 min / 0.35 recommended. |
| Copper to edge clearance | **0.5 mm** | Routed edge wander ±0.2. |
| Minimum drill size | **0.3 mm** | No module thermal-via trick needed this time — nothing below 0.3 (the ESP32 footprint's 0.2 mm centre-pad vias from Board 1 are the one exception; keep them at 0.6 pad so they stay surcharge-free). |
| Hole to hole clearance | **0.5 mm** | |
| Silk min text height / thickness | **1.0 / 0.15 mm** | JLC legibility floor. |

## 3. Pre-defined sizes

- Tracks: **0.25 / 0.3 / 0.5 / 0.8 / 1.0 / 1.5 / 2.0 mm**
- Vias: **0.6/0.3** (signal, thermal) · **0.8/0.4** (power, stitching)

## 4. Net classes and the moat rule

| Class | Clearance | Track | Via | Nets (patterns) |
|---|---|---|---|---|
| Default | 0.2 | 0.25 | 0.6/0.3 | everything else |
| **POWER** | 0.2 | **0.8** | 0.8/0.4 | `VBUS_DC` · `5V_BUCK` · `5V_SYS` · `VLOAD` · `*USB_5V_PROT` · `*USB_VBUS` |
| **LOGIC3V3** | 0.2 | 0.5 | 0.6/0.3 | `+3V3` |
| **SW** | 0.3 | **1.0** | — (no vias allowed by rule) | `*SW` (buck switch node) |
| **USB** | 0.2 | 0.25 | 0.6/0.3 | `USB_DP` · `USB_DN` · `*USB_CONN_D*` · `*USB_ESD_D*` |
| **FIELD** | **1.0** | 0.5 | 0.8/0.4 | `*FLD_PWR_*` · `*IN1` … `*IN4` · `*FLD_COM` · `*K1_*` · `*K2_*` |
| **CONTACT** | 1.0 | **1.5** | 0.8/0.4 | `*K1_NO` · `*K1_COM` · `*K1_NC` · `*K2_NO` · `*K2_COM` · `*K2_NC` (assign these after FIELD so the wider track wins) |

The `*` prefixes exist because local labels carry a sheet prefix in the full net name (Board 1's lesson); check the "Nets matching" preview in Board Setup after capture and fix any pattern that matches nothing.

**Custom rules** (Board Setup → Custom Rules), the thing Board 1 did not have:

```
(version 1)

(rule "moat: field nets keep 2.5 mm from everything else"
  (condition "A.NetClass == 'FIELD' && B.NetClass != 'FIELD' && B.NetClass != 'CONTACT'")
  (constraint clearance (min 2.5mm)))

(rule "moat: contact nets keep 2.5 mm from everything else"
  (condition "A.NetClass == 'CONTACT' && B.NetClass != 'FIELD' && B.NetClass != 'CONTACT'")
  (constraint clearance (min 2.5mm)))

(rule "relay contacts: 4 mm from logic at the terminals"
  (condition "A.NetClass == 'CONTACT' && B.NetClass != 'FIELD' && B.NetClass != 'CONTACT' && A.insideArea('RelayTerminalZone')")
  (constraint clearance (min 4.0mm)))

(rule "SW node: no vias"
  (condition "A.NetClass == 'SW'")
  (constraint via_count (max 0)))

(rule "field side: no copper pour"
  (condition "A.insideArea('FieldSide') && A.Type == 'Zone' && A.NetName == 'GND'")
  (constraint disallow zone))
```

`RelayTerminalZone` and `FieldSide` are rule areas drawn on `User.1` with those names (Rule Area → name field). The last rule is the belt to rule 3's braces: if a GND zone ever leaks onto the field side, DRC says so. Syntax is per the KiCad 10 custom-rules reference; test each rule with a deliberate violation once before trusting it.

## 5. Other Board Setup pages

- **Physical Stackup: 2 copper layers, 1.6 mm**, 1 oz outer (JLC's standard 2-layer: 0.035 / 1.51 core Er 4.5 / 0.035). Fill in the Er even though nothing is impedance-controlled — the length-tuning tools read it.
- **Layer plan:** F.Cu = every part + all fast or sensitive nets (SW, the buck cluster, the USB pair, VIN_SENSE, the relay drivers); B.Cu = one GND zone across the logic side and under the converter, plus slow crossings (LED and pull-down returns, the recovery UART, opto collector nets if they must cross). **No GND zone on the field side** (rule above).
- **Antenna keep-out:** Rule Area with "keep out copper pours", "keep out tracks", "keep out vias" on F.Cu and B.Cu — this board has a real on-board region beside the module (unlike Board 1 where the whole keep-out overhung the edge), so the rule area is needed.
- **Text & Graphics defaults:** silk 1.0 mm / 0.15 mm. **Solder mask/paste expansion:** zero — JLC applies its own mask expansion; paste apertures are edited per footprint (the two exposed pads), not globally.
- **Zone defaults:** clearance 0.3 / min width 0.25 / thermal reliefs for through-hole pads, spoke 0.5 / solid for the buck exposed pad and the input-capacitor grounds / remove islands.

## 6. Interactive router, grids, annotation colour

As Board 1: **Shove** mode; grids **0.5 mm** (Alt+1) and **0.25 mm** (Alt+2); floorplan boxes on `User.Comments` in spring green `#00FF7F` — one box per sheet territory: 02 Field power · 03 Buck · 04 USB · 05 3V3 · 06 Core · 07 Optos · 08 Relays · 09 MOSFETs · 10 Mech — plus the moat line drawn first on `User.Comments` and later copied to `F.Silkscreen`.

## 7. Paste layer edits (before the stencil is ordered)

- **U301 exposed pad:** replace the footprint's single paste aperture with four squares covering ≈ 50–60 % of the pad area (edit the footprint: pad → Clearance Overrides → solder paste ratio, or draw four paste rectangles on F.Paste and set the pad's paste to none).
- **U601 centre pad:** same, ≈ 50 % in four windows — Board 1's footprint was assembled by JLC with their own paste; the bench needs less.
- Everything else 1:1. Check `F.Paste` in the fab preview and in the gerber viewer before ordering.

## 8. Related files

- `docs/Hard_Rules_Layout_RevA.md` — the rulebook these settings enforce
- `docs/Assembly_and_Stencil_Plan.md` — why the paste layer is edited
- `references/JLCPCB_Capabilities_2026-08.md` — fab limits (Board 1's capture; the 2-layer columns apply)
- `docs/PROJECT_STATUS.md` — overall project state
