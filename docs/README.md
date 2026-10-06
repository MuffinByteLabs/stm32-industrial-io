# Engineering documentation

I document the controller from requirements through validation, with enough detail to explain why I chose each interface and how I intend to verify it.

| Document | My focus |
| --- | --- |
| [Scope](Scope.md) | Frozen major functions and boundaries of each operating milestone |
| [External-review verification](External_Review_Verification.md) | October 6 corrections, independently checked suggestions, sourcing and remaining gates |
| [Deep pre-schematic review](Pre_Schematic_Review.md) | October 4 historical corrections and retained capture gates |
| [Library preflight](Library_Preflight.md) | Exact missing-asset work list and pin/pad approval procedure |
| [Implementation plan](Implementation_Plan.md) | M0 capture gates through M4 full physical qualification |
| [Architecture review](Architecture_Review.md) | Full architecture retained, with electrical verification obligations recorded |
| [Portfolio evidence](Portfolio_Evidence.md) | Cohesive demonstration, measurements and release presentation |
| [Validation record template](templates/Validation_Record.md) | Repeatable setup, build identity, uncertainty and results |
| [Market alignment](Market_Alignment.md) | Supplied-job evidence and the reasons for the chosen scope |
| [Protocol](../firmware/Protocol.md) | Exact measurement and guarded command contracts |
| [Engineering review](Engineering_Review.md) | Current component status, compatibility, corrections, and review scope |
| [Schematic capture](Schematic_Capture.md) | Complete circuit/support-component reference set, physical-pin allocation, sequencing and capture order |
| [Architecture](Architecture.md) | Power, signal paths, component candidates, and isolation |
| [Design decisions](Design_Decisions.md) | Protection, measurement, output behavior, and layout tradeoffs |
| [Interfaces](Interfaces.md) | Electrical contracts, wiring, and communication behavior |
| [Validation](Validation.md) | Test conditions, acceptance limits, and traceable evidence |
| [Calculations](calcs/README.md) | Reproducible power, measurement, and loading analysis |

My scope retains external power, four precision inputs, both isolated buses and a later bounded PWM mode, with the same hardware shutdown requirements throughout. I finish static Modbus control first and keep qualification status explicit.

The architecture and requirements baseline is documented and reviewed. I close the remaining evidence gates as I capture the schematic, then add PCB, target firmware and measured evidence as I implement Rev A. Until then, I treat the electrical specifications as design targets.

I keep exact support values and ordering codes in my [component selection index](components/README.md), with detailed circuit instructions linked from the [capture package](Schematic_Capture.md).
