# Engineering calculations

I use [controller_budget.py](controller_budget.py) to reproduce selected Rev A arithmetic: input-current margin, current-loop shunts, quantization versus accuracy targets, diode losses, AO loading, and resistive-load fixtures. My [architecture](../Architecture.md) and [validation plan](../Validation.md) define the associated engineering targets.

I run it with Python 3:

~~~text
python docs/calcs/controller_budget.py
python docs/calcs/controller_budget.py --service-w 5 --efficiency 0.85
~~~

My initial assumptions are 5 W delivered service power, 85% aggregate conversion efficiency, four 0.5 A loads, and a 3 A continuous input budget. At 9 V, the estimate is 2.654 A before extra protection losses, leaving approximately 0.346 A of budget.

This arithmetic does not prove regulator suitability, inrush/fault tolerance, transient protection, thermal limits, analog settling, stability, EMC, or fixture ratings. I will replace assumptions with verified worst-case values during schematic design and measurements during qualification.

At 30 V, four constant 0.5 A loads dissipate 60 W externally. Four fixed 48 Ω loads selected for 24 V instead draw 0.625 A/channel at 30 V. I will configure and thermally rate the fixture for each operating point.
