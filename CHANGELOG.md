# Changelog

## Unreleased — STM32 Industrial I/O Controller Rev A

### October 2, 2026

- Replaced the previous project specification with a fresh four-layer STM32 controller plan based on the supplied conversation and relevant Upwork listings.
- Defined protected DC power, analog measurement, four group-isolated digital inputs, diagnosed high-side outputs, two relays, a voltage-source analog output, and separately isolated wired buses.
- Updated firmware, wiring, resource reservations, layout, KiCad, assembly, bring-up, mechanical, procurement, fabrication, and status documentation.
- Saved short job excerpts with source locations and hashes; documented strong and partial matches.
- Refreshed candidate-family manufacturer references and added repeatable reference identity/hash maintenance and planning calculations.
- Updated CI to report absent design files honestly and enforce native-design checks when implementation exists.
- Removed superseded design documents, sourcing drafts, review claims, unused legacy references, and empty old KiCad files. Retained useful generic assets under the new library name.
- Saved and verified an external recovery archive before migration. See the [migration review](docs/reviews/Folder_Migration_2026-10-02.md).
- Renamed the GitHub repository to stm32-industrial-io, preserved its history, and configured project topics, labels, three milestones, and six engineering roadmap issues.
- Added document/planning CI, engineering/problem issue forms, review template, ownership, pinned audit dependency, and portable publication links.
- Retained third-party KiCad library notices alongside the original project license. Automated workflows create reports rather than commits.

This entry records a documentation and project-structure migration. Schematic capture, PCB layout, firmware implementation, procurement, assembly, and measured qualification remain pending.

## Hardware releases

No STM32 hardware revision has been released or ordered. Add a dated entry here when an actual revision is frozen, with its design revision, firmware identifier, validation report, and fabrication package.
