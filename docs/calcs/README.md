# Planning calculations

[controller_budget.py](controller_budget.py) reproduces selected arithmetic from the [canonical plan](../STM32_Industrial_IO_Controller_RevA_Plan.md): input-current margin, current-loop shunts, quantization versus accuracy targets, diode losses, AO loading, and resistive-load fixtures.

Run with Python 3:

~~~text
python docs/calcs/controller_budget.py
python docs/calcs/controller_budget.py --service-w 5 --efficiency 0.85
~~~

The default assumes 5 W delivered service power, 85% aggregate conversion efficiency, four 0.5 A loads, and a 3 A continuous input budget. At 9 V this estimates 2.654 A before extra protection losses, leaving approximately 0.346 A of budget.

This is a planning calculation. It does not prove the chosen regulator network, inrush/fault tolerance, transient protection, component thermal limits, analog settling, stability, EMC, or test-fixture ratings. Replace assumptions with verified worst-case values during schematic design and actual measurements during qualification.

At 30 V, four constant 0.5 A loads dissipate 60 W externally. Four fixed 48 Ω loads selected for 24 V instead draw 0.625 A/channel at 30 V. Configure the load fixture for each actual operating point and provide thermal margin.
