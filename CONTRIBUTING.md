# Project workflow

I maintain this controller as Ray Malik / MuffinByteLabs. My [architecture](docs/Architecture.md), [design decisions](docs/Design_Decisions.md), [interfaces](docs/Interfaces.md), and [validation plan](docs/Validation.md) define the engineering baseline.

I use the [scope baseline](docs/Scope.md) and [implementation milestones](docs/Implementation_Plan.md) to order the work. I retain every selected feature and the complete architecture recorded in the [review disposition](docs/Architecture_Review.md). Any later controlled circuit change updates its dependent requirements and evidence together.

## Track a change

I use engineering tasks for design decisions, implementation milestones, and qualification tests. For a reproducible issue, I use a problem report with the affected revision, requirement, operating conditions, and evidence.

I keep changes focused enough to review. A requirement change includes the affected architecture, interface contract, implementation, and validation criteria. I save calculations and review evidence with the design so the decision can be reproduced.

The hardware side contains design requirements and candidate references; schematic, PCB, target firmware and bench implementation remain pending. Host diagnostic tools can be developed independently. I distinguish component ratings, engineering targets, host simulations and measured board results in the project records.

## Run repository checks

I run the repository tools with Python 3.12 and the pinned dependency in [requirements-dev.txt](requirements-dev.txt):

~~~text
python -m pip install -r requirements-dev.txt
python scripts/audit_project.py
python scripts/audit_component_selections.py
python scripts/audit_capture_readiness.py
python docs/calcs/controller_budget.py
python docs/calcs/support_checks.py
python docs/calcs/analog_checks.py
python docs/calcs/pwm_checks.py
python -m unittest discover -s tools/diagnostics/tests -v
python tools/diagnostics/fieldio_cli.py --simulate snapshot
~~~

The [diagnostic tools](tools/diagnostics/README.md) use the [protocol specification](firmware/Protocol.md). Their simulated records are marked `SIMULATED`; passing their tests does not close a hardware milestone. The optional live serial dependency is documented with the tool and is not required for its standard-library tests.

My [project audit](.github/workflows/project-audit.yml) checks local links, saved PDF identity and hashes, library paths, selected engineering arithmetic and host protocol behavior on pushes and pull requests. These checks do not validate electrical behavior.

My separate [KiCad workflow](.github/workflows/kicad-ci.yml) runs ERC and DRC when the native design files exist. Missing files produce an explicit report that those checks were not run. I also require schematic/layout review and the applicable simulation and bench evidence.

## Review hardware and release it

I identify the exact hardware and firmware revision in every review and test report. My [validation plan](docs/Validation.md) requires the setup, acceptance limits, observations, uncertainty, and unresolved concerns.

I use the [validation record template](docs/templates/Validation_Record.md) and [portfolio evidence guide](docs/Portfolio_Evidence.md). An M1/M2/M3 demonstration states its measured limits; it does not imply completion of M4 or authorize a full hardware release. Qualified capability records are separate from populated hardware and implemented protocol modes.

I reserve tags beginning with rev for complete hardware revisions. Before publishing one, I require the matching native design, review evidence, and manufacturing package to meet my [fabrication requirements](fabrication/README.md). These tags request the KiCad release checks and fabrication exports.

My automated workflows produce reports and artifacts without committing changes to design sources.
