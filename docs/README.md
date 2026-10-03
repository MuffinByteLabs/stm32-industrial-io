# Engineering documentation

I document the controller from requirements through validation, with enough detail to explain why I chose each interface and how I intend to verify it.

| Document | My focus |
| --- | --- |
| [Engineering review](Engineering_Review.md) | Current component status, compatibility, corrections, and review scope |
| [Schematic capture](Schematic_Capture.md) | Pin/clock allocation, supervision, sequencing, and capture checks |
| [Architecture](Architecture.md) | Power, signal paths, component candidates, and isolation |
| [Design decisions](Design_Decisions.md) | Protection, measurement, output behavior, and layout tradeoffs |
| [Interfaces](Interfaces.md) | Electrical contracts, wiring, and communication behavior |
| [Validation](Validation.md) | Test conditions, acceptance limits, and traceable evidence |
| [Calculations](calcs/README.md) | Reproducible power, measurement, and loading analysis |

I have completed the architecture and requirements documentation. I’ll add schematic, PCB, firmware, and measured evidence as I implement Rev A. Until then, I treat the electrical specifications as design targets.
