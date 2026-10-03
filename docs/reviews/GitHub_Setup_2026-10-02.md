# GitHub setup verification — October 2, 2026

[MuffinByteLabs/stm32-industrial-io](https://github.com/MuffinByteLabs/stm32-industrial-io) is the renamed public repository. Its original history was preserved, its default branch remains main, and the local remote points to its new SSH URL.

## Published configuration

- Description, website, and ten relevant project topics.
- Three implementation milestones, six roadmap issues, and phase/area labels.
- Engineering/problem issue forms, review template, project workflow guide, and MuffinByteLabs ownership.
- Portable documentation links and third-party KiCad library notices.
- Read-only document/planning and KiCad workflows; neither writes commits.

The [project guide](../GitHub_Project_Guide.md) links the live roadmap and describes checks and release gates.

## Attribution verified

The migration/setup commit and the CI correction were authored and committed as Ray with muffinbytelabs@gmail.com. GitHub resolves both author and committer to MuffinByteLabs. The repository contributors endpoint lists only MuffinByteLabs; the complete existing Git history uses the same identity and has no co-author trailers.

## Hosted validation

The following runs passed for [commit c4d84aa](https://github.com/MuffinByteLabs/stm32-industrial-io/commit/c4d84aa7d7aca694fb04b01300d58a6b267b73f1):

- [Project audit](https://github.com/MuffinByteLabs/stm32-industrial-io/actions/runs/37091803834): document links, PDF identities/hashes, local library paths, and planning calculations.
- [KiCad workflow](https://github.com/MuffinByteLabs/stm32-industrial-io/actions/runs/37091803782): workflow execution and explicit missing-design reporting. ERC and DRC were skipped because no native design exists.

The first hosted document audit exposed missing AES support for manufacturer PDFs. The pinned pypdf dependency now includes its crypto extra. The workflows also use the current official version 7 actions.

Both workflow files passed actionlint, all five GitHub YAML files parsed, and issue forms/embedded summary code were checked locally. The board remains in planning; these checks do not establish electrical performance or fabrication readiness.
