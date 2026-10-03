# GitHub project guide

[Repository](https://github.com/MuffinByteLabs/stm32-industrial-io) · [Issues](https://github.com/MuffinByteLabs/stm32-industrial-io/issues) · [Actions](https://github.com/MuffinByteLabs/stm32-industrial-io/actions)

MuffinByteLabs owns and maintains this project. The repository was renamed from esp32s3-field-io while preserving its history. Rev A is in planning; no fabricated STM32 board or hardware release is claimed.

## Roadmap

| Milestone | Implementation issues |
| --- | --- |
| [Design freeze](https://github.com/MuffinByteLabs/stm32-industrial-io/milestone/1) | [Requirements and feasibility #1](https://github.com/MuffinByteLabs/stm32-industrial-io/issues/1), [schematic and MCU resources #2](https://github.com/MuffinByteLabs/stm32-industrial-io/issues/2), [four-layer PCB #3](https://github.com/MuffinByteLabs/stm32-industrial-io/issues/3) |
| [Working prototypes](https://github.com/MuffinByteLabs/stm32-industrial-io/milestone/2) | [First article and firmware #4](https://github.com/MuffinByteLabs/stm32-industrial-io/issues/4) |
| [Qualification and portfolio](https://github.com/MuffinByteLabs/stm32-industrial-io/milestone/3) | [Measured qualification #5](https://github.com/MuffinByteLabs/stm32-industrial-io/issues/5), [manufacturing handoff and portfolio #6](https://github.com/MuffinByteLabs/stm32-industrial-io/issues/6) |

The [canonical plan](STM32_Industrial_IO_Controller_RevA_Plan.md) owns the technical requirements. Close a roadmap issue only after its acceptance evidence exists. Use phase labels to identify design, prototype, and qualification work; area labels identify hardware, firmware, documentation, and manufacturing.

Issue forms request revision, requirements, test conditions, and evidence. The [project workflow](../CONTRIBUTING.md) explains how to keep changes reviewable. The [ownership file](../.github/CODEOWNERS) routes reviews to MuffinByteLabs.

## Checks and releases

- **Project audit** checks portable document links, saved PDF identities/hashes, library paths, and planning calculations on pushes, pull requests, and manual runs.
- **KiCad checks** report absent native files as not run. When implementation exists they enforce matching project settings, ERC, DRC, zone refill, and schematic parity.
- Hardware tags beginning with rev require complete native files and exactly four copper layers before exports. The [fabrication guide](../fabrication/README.md) defines the rest of the release package.

Successful document checks do not establish a working circuit or board. No hardware release tag is appropriate at the current stage.

Both workflows have read-only repository permissions and produce reports/artifacts. They do not author commits, update source, or publish hardware releases.

## Local checkout and commit identity

The remote for this checkout is:

~~~text
git@github.com:MuffinByteLabs/stm32-industrial-io.git
~~~

Commits use the maintainer's existing Git identity, Ray with muffinbytelabs@gmail.com, which GitHub associates with MuffinByteLabs. Repository-local identity settings leave other projects unchanged.

Run the checks listed in [CONTRIBUTING.md](../CONTRIBUTING.md) before publishing a change. Verify author and committer metadata before pushing. Preserve third-party notices independently of Git commit attribution; the [library guide](../hardware/libs/README.md) explains those notices.

The [migration record](reviews/Folder_Migration_2026-10-02.md) identifies the private recovery archive. Original supplied job dumps and that archive remain outside the public repository; only selected evidence excerpts and provenance hashes are included.
