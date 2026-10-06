# Retained architecture and verification record

**Disposition recorded October 4, 2026: retain the complete current architecture and every selected feature.** My [circuit specifications](Schematic_Capture.md#capture-references) and component selections remain the electrical baseline. This closes the scope choice; it does not close capacitor, package, native-connectivity or physical qualification gates.

## Why I retain the complete network

The selected local logic architecture has separate `3V3_DIG` and `3V3_FIELD_LOGIC` supplies in the same `MAIN_GND` domain. Independent startup/collapse drives receiving-domain buffers, enables and rail supervision. The control selection allocates 11 dual-AND packages, 10 dual receiving buffers including loop-status qualification, four dual Schmitt packages, six reset/window-monitor packages, an external watchdog and an ARM latch.

These circuits address the independent startup/collapse and powered-off pin conditions created by this supply choice. I retain their complete networks. Local supplies sharing MAIN_GND are not galvanic isolation; DI_COM, RS485_REF and CAN_REF remain actual isolated reference islands.

## Scope disposition

| Area | Retained baseline |
| --- | --- |
| Local supplies/crossings | Separate rails, receiving-domain buffers, qualified enables and supervision |
| Analog protection | Complete protection, threshold, hold-up and discharge networks |
| Actuation | Four diagnosed high-side channels including DO3 PWM capability, both relays and every hardware gate |
| Acquisition and communication | All selected inputs, both independent isolated bus supplies/ports, USB, debug and settings |

The +15 V, VFP11 and VFP6 rails remain essential to the current input protectors. Removing an analog output did not remove their purpose. I do not delete these rails or their health/discharge circuits merely to reduce part count.

The resulting design is substantial for a second board. I control that complexity through sheet-by-sheet capture and staged commissioning in the [implementation plan](Implementation_Plan.md). A shared-rail redesign or narrower variant is not the current implementation plan.

## Verification obligations that remain open

- [ ] The captured rail/domain drawing and complete pin/connection table match the retained specifications.
- [ ] MCU VDD/VDDA/VREF and ADC digital/analog supplies meet operating, absolute-limit and sequence constraints.
- [ ] Worst-case load, regulator stability, effective capacitance, switching noise and analog error budget are closed. Parent hold-up and the child-disable bound have evidence beyond nominal timing tables.
- [ ] Live external signals, USB-connected/unpowered operation, residual rail charge and power removal cannot inject illegal current/voltage into unpowered receivers.
- [ ] All four high-side commands and both relay drivers retain default inhibition and asynchronous ARM clearing; stale GPIO/timer states cannot restore drive.
- [ ] Watchdog enable/failure, reset, field/analog health, global driver fault and explicit disarm have a reviewed permission truth table with no startup deadlock.
- [ ] Analog input protection, permanent current shunts and output-current diagnostic isolation remain valid in their powered/unpowered states.
- [ ] DI and both bus reference islands retain their intentional galvanic boundaries and independent port supplies.
- [ ] Component selections, MCU resource tables, captured circuits, budgets, interfaces, validation and assembly variants agree.
- [ ] Required schematic/ERC, layout/DRC, applicable simulation and later physical sequence/fault tests are identified and completed at the proper stage.

## Disposition record

| Field | Current entry |
| --- | --- |
| Decision | Retain the complete documented architecture and all features |
| Affected documents/components | Scope, implementation plan, architecture, capture package, all circuit selections and validation |
| Evidence and open obligations | Document/datasheet review and bounded calculations; open requirements above and in the pre-schematic review |
| Disposition date | October 4, 2026 |
| Native implementation checks | Pending |
| Physical qualification | Pending |

I can begin hierarchy and library preparation now. I close each applicable electrical/library gate before freezing its sheet, then obtain the later native and physical evidence before claiming a qualified controller. The [pre-schematic review](Pre_Schematic_Review.md) records current findings and evidence limits; the [validation plan](Validation.md) defines physical acceptance.
