# Design Reviews — ESP32-S3 Protected Field I/O Controller Rev A

Review records for Rev A, in order. Each one is a real record: what was examined, how, what was found, and what changed as a result. Board 1 had six; this board's list starts before capture.

| Date | Review | Method | Outcome |
|---|---|---|---|
| 2026-09-07 | [Specification review](Spec_Review_RevA_2026-09-07.md) | Every number in the frozen spec (plan v7.3 §4) re-derived from datasheets, in `../calcs/board2_calcs.py`, and checked against the plan's own claims | **4 blocking findings** — the opto input RC could not hold LOW through the 60 Hz gap, the 7.5 V UVLO contradicted the 9 V input claim, the 0.5 A PPTC tripped at the low end of the DC range, and the chosen buck was a leadless QFN — plus 6 risky, 12 improvements, 11 numbers confirmed. All resolved in the design document before capture |

## Planned gates (each gets a record here)

| Gate | Review | Method (inherited from Board 1) |
|---|---|---|
| After capture | Pre-layout design review | Netlist parsed from the `.kicad_sch` sources to pin level, cross-checked against every datasheet in `../../references/`; BOM regenerated and diffed against the design document |
| After placement | Placement review | Component-by-component against `../Hard_Rules_Layout_RevA.md`, annotated map |
| Before order | Finishing review + final layout audit | Scripted geometry pass; headless DRC with zone refill, schematic parity, the moat rule; paste-layer check |
| First article | First-article inspection + bring-up record | `../Assembly_and_Stencil_Plan.md` §6 and `../BringUp_Guide.md` §5 |

## The four blocking findings, 2026-09-07

Caught before any copper existed, so they cost nothing but an afternoon:

1. **The AC input filter would not have worked.** 10 kΩ + 1 µF rises to ≈ 2 V during the 9.5 ms gap between 60 Hz half-cycles — into the ESP32-S3's undefined input band. The HVAC use case reads 24 VAC thermostat wires. Fixed with 4.7 µF (τ = 47 ms, ≤ 0.74 V worst case) and a 3-sample debounce.
2. **UVLO 7.5 V and "9 V DC input" cannot both be true** once the bridge and PPTC drops are counted. Fixed with a 7.0 / 6.1 V UVLO and an honest 10–36 V DC guaranteed spec.
3. **The 0.5 A PPTC would trip** at 9–12 V DC under the full 5 V load (0.79 A input at 9 V). Fixed with a 1.1 A / 60 V radial part — and a note that the obvious MF-R110 is 30 V-rated.
4. **The LMR36015 is a 2 × 3 mm leadless package** on a board whose assembly method requires inspectable joints; the 100 V fallback had 5 % current margin. Fixed with the LMR38020 (80 V, 2 A, HSOIC-8), which also passes the TVS-clamp check outright.
