# Standards & reference texts

These are **deliberately not in the repository** — they are copyrighted works that cannot be
redistributed. They are listed here so the sources behind this board's rules are on the record, and
kept locally outside the repo tree (`PCB_Design/references_local/`).

| Work | What this project uses it for |
|---|---|
| **IPC-2221** — Generic Standard on Printed Board Design | Conductor sizing (the 2 A relay-contact paths at ≥ 1.5 mm, the 0.8 mm power traces) and the clearance figure the ≥ 2.5 mm moat is measured against (0.6 mm for uncoated external conductors ≤ 100 V) |
| **Ritchey, *Right the First Time*, Vol. 1** (Speeding Edge) | Return-current reasoning behind "bottom copper unbroken under the converter" and the single star point for the rectifier return |
| **TI SNVA021 / buck-layout application notes; Phil's Lab buck-converter layout video** | The hot-loop, SW-node and FB-routing rules in `docs/Hard_Rules_Layout_RevA.md` §5–§9 |

Vendor datasheets, which *are* freely redistributable, live in
[`../datasheets/`](../datasheets/) and are indexed there.
