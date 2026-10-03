# Project workflow

MuffinByteLabs maintains this controller project. The [board plan](docs/STM32_Industrial_IO_Controller_RevA_Plan.md) defines the architecture and acceptance targets; [project status](docs/PROJECT_STATUS.md) records implementation progress. Start engineering work from the [open items](docs/Open_Engineering_Items.md).

## Track a change

Use an engineering task for a design decision, implementation milestone, or qualification test. Use a problem report for a reproducible issue. Include the affected revision, requirement, operating conditions, and evidence needed to close the work.

Keep a change focused enough to review. When a requirement changes, update the board plan, affected interface or implementation guides, and status together. Store calculations and review evidence with the design so the decision can be reproduced.

The current repository contains planning material and candidate references. Do not describe a circuit, board, or firmware feature as implemented until its source exists. Distinguish manufacturer component ratings, design targets, simulations, and measured board results.

## Run repository checks

Use Python 3.12 and the pinned development dependency in [requirements-dev.txt](requirements-dev.txt):

~~~text
python -m pip install -r requirements-dev.txt
python scripts/audit_project.py
python docs/calcs/controller_budget.py
~~~

The [project audit](.github/workflows/project-audit.yml) runs these document and planning checks on pushes and pull requests. It checks local links, saved PDF identity and hashes, library paths, and selected planning arithmetic. It does not validate electrical behavior.

The separate [KiCad workflow](.github/workflows/kicad-ci.yml) runs ERC and DRC when the new native design files exist. Missing files produce an explicit report that those checks were not run. A successful document check does not replace schematic review, layout review, simulation, or bench testing.

## Review hardware and release it

Use the [layout rules](docs/Hard_Rules_Layout_RevA.md), [assembly plan](docs/Assembly_and_Stencil_Plan.md), and [bring-up guide](docs/BringUp_Guide.md) at the appropriate stage. Identify the exact board and firmware revision in every test report. Save the test setup, acceptance limit, observations, and unresolved concerns.

Publish a hardware release only after the matching native design, review evidence, and manufacturing package meet the [fabrication requirements](fabrication/README.md). Tags beginning with rev request the KiCad release checks and fabrication exports; they are reserved for complete hardware revisions.

Automated workflows produce reports and artifacts. They do not commit changes or update design sources.
