# Engineering documentation

I document the controller from requirements through validation, with enough detail to explain why I chose each interface and how I intend to verify it.

| Document | My focus |
| --- | --- |
| [Engineering review](Engineering_Review.md) | Current component status, compatibility, corrections, and review scope |
| [Schematic capture](Schematic_Capture.md) | Complete circuit/support-component reference set, physical-pin allocation, sequencing and capture order |
| [Architecture](Architecture.md) | Power, signal paths, component candidates, and isolation |
| [Design decisions](Design_Decisions.md) | Protection, measurement, output behavior, and layout tradeoffs |
| [Interfaces](Interfaces.md) | Electrical contracts, wiring, and communication behavior |
| [Validation](Validation.md) | Test conditions, acceptance limits, and traceable evidence |
| [Calculations](calcs/README.md) | Reproducible power, measurement, and loading analysis |

My revised scope includes external power, four precision inputs, both isolated buses and one bounded PWM load channel, with the same hardware shutdown requirements throughout the documents.

I have completed the architecture and requirements documentation. I’ll add schematic, PCB, firmware, and measured evidence as I implement Rev A. Until then, I treat the electrical specifications as design targets.

I keep exact support values and ordering codes in my [component selection index](components/README.md), with detailed circuit instructions linked from the [capture package](Schematic_Capture.md).
