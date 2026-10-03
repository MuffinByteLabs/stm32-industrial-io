# Engineering calculations

I use [controller_budget.py](controller_budget.py) to reproduce selected Rev A arithmetic: input-current margin, current-loop shunts, quantization versus accuracy targets, diode losses, AO loading, and resistive-load fixtures. My [architecture](../Architecture.md) and [validation plan](../Validation.md) define the associated engineering targets.

I run it with Python 3:

~~~text
python docs/calcs/controller_budget.py
python docs/calcs/controller_budget.py --service-w 6 --efficiency 0.80
~~~

My corrected assumptions are 6 W delivered service power, 85% field-buck conversion efficiency, four 0.5 A loads, and a 3 A continuous input budget. Named service reservations total 5.75 W, including downstream conversion losses, leaving 0.25 W inside that ceiling. At 9 V, the estimate is 2.784 A before extra input-protection losses and overhead, leaving approximately 0.216 A. At assumed 80% efficiency it becomes 2.833 A. These efficiencies and reservations need circuit and measured closure.

This arithmetic does not prove regulator suitability, inrush/fault tolerance, transient protection, thermal limits, analog settling, stability, EMC, or fixture ratings. I will replace assumptions with verified worst-case values during schematic design and measurements during qualification.

At 30 V, four constant 0.5 A loads dissipate 60 W externally. Four fixed 48 Ω loads selected for 24 V instead draw 0.625 A/channel at 30 V. I will configure and thermally rate the fixture for each operating point.

## Limited DC frontend simulation

I also provide [dc_frontends.cir](dc_frontends.cir) and [spice_dc_check.py](spice_dc_check.py). I ran this operating-point model on October 3, 2026 using the ngspice shared library bundled with KiCad 10. The amplifiers are ideal high-gain sources and the switches are resistors; this model does not simulate actual IC faults, enable transitions, temperature, amplifier stability, or converter behavior.

~~~text
python docs/calcs/spice_dc_check.py --library "C:/Program Files/KiCad/10.0/bin/ngspice.dll"
~~~

I assumed 12.5 Ω main-switch resistance, 100 Ω additional series resistance, 8.6 kΩ total feedback-path resistance, a 10 kΩ external load, and a 100 kΩ terminal pulldown. These are model inputs, not guaranteed limits at my selected +15 V operating point. The terminal-feedback topology produces 9.99995 V from a nominal 10 V command. The same resistive output path without terminal feedback gives 9.87772 V. I keep the gain divider local to the first amplifier so the feedback-switch resistance does not change the gain.

For a 20 mA receiver with a 200 Ω shunt, 8.3 Ω sense-path resistance, and the ADC's 0.85 MΩ/2.5 V equivalent input model, I obtain 3.999647 V at the shunt and 3.999633 V at the ADC sense node. The script checks this against an independent loading equation. This verifies connectivity and the static compensation principle; The separate typical amplifier model and [analog calculation report](ao_model_results.json) cover the selected compensation with finite cable loads; I qualify measured accuracy after schematic capture.

## Capture support bounds

I use [support_checks.py](support_checks.py) for resistor/temperature/input-bias corners of the rail monitors, USB fault-limiter bounds and EEPROM rise time. It bounds field-UV release below 9 V and field-OV recovery above 30 V and keeps the negative-bias loss threshold below −0.15 V. My [analog specification](../circuits/Analog.md) records further calculation and manufacturer-model evidence.

## Capacitor evidence

I record exact nominal evidence, operating-bias requirements and finite closure criteria in [capacitor_evidence.json](capacitor_evidence.json). Fourteen supply/reference banks still require effective-capacitance evidence. The report does not mark an unavailable curve or a nominal rating as a passed stability or shutdown bound.
