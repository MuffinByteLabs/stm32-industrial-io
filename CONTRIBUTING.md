# Project workflow

I maintain this controller as Ray Malik / MuffinByteLabs. My [architecture](docs/Architecture.md), [design decisions](docs/Design_Decisions.md), [interfaces](docs/Interfaces.md), and [validation plan](docs/Validation.md) define the engineering baseline.

## Track a change

I use engineering tasks for design decisions, implementation milestones, and qualification tests. For a reproducible issue, I use a problem report with the affected revision, requirement, operating conditions, and evidence.

I keep changes focused enough to review. A requirement change includes the affected architecture, interface contract, implementation, and validation criteria. I save calculations and review evidence with the design so the decision can be reproduced.

The current repository contains design requirements and candidate references; schematic, PCB, firmware, and bench implementation remain pending. I distinguish component ratings, engineering targets, simulations, and measured board results in the project records.

## Run repository checks

I run the repository tools with Python 3.12 and the pinned dependency in [requirements-dev.txt](requirements-dev.txt):

~~~text
python -m pip install -r requirements-dev.txt
python scripts/audit_project.py
python docs/calcs/controller_budget.py
~~~

My [project audit](.github/workflows/project-audit.yml) checks local links, saved PDF identity and hashes, library paths, and selected engineering arithmetic on pushes and pull requests. These checks do not validate electrical behavior.

My separate [KiCad workflow](.github/workflows/kicad-ci.yml) runs ERC and DRC when the native design files exist. Missing files produce an explicit report that those checks were not run. I also require schematic/layout review and the applicable simulation and bench evidence.

## Review hardware and release it

I identify the exact hardware and firmware revision in every review and test report. My [validation plan](docs/Validation.md) requires the setup, acceptance limits, observations, uncertainty, and unresolved concerns.

I reserve tags beginning with rev for complete hardware revisions. Before publishing one, I require the matching native design, review evidence, and manufacturing package to meet my [fabrication requirements](fabrication/README.md). These tags request the KiCad release checks and fabrication exports.

My automated workflows produce reports and artifacts without committing changes to design sources.
