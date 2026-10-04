# Engineering calculations

I keep the design arithmetic reproducible and distinguish model results from measured performance. My [architecture](../Architecture.md) and [validation plan](../Validation.md) define the targets.

| Check | Scope |
| --- | --- |
| [controller_budget.py](controller_budget.py) | Input-current headroom, service reservations, current-loop burden/loading, quantization and output losses |
| [support_checks.py](support_checks.py) | Rail-monitor tolerance corners, retained auxiliary hold-up, USB VBUS detection and EEPROM timing |
| [analog_checks.py](analog_checks.py) | Input frontends, shunt/protection loading and receiving current-diagnostic network |
| [pwm_checks.py](pwm_checks.py) | DO3 period/on-window, finite edge/sense timing and illustrative switching-loss bounds |
| [spice_dc_check.py](spice_dc_check.py) / [dc_frontends.cir](dc_frontends.cir) | Bounded ideal DC model of active input and current-diagnostic paths |

~~~text
python docs/calcs/controller_budget.py
python docs/calcs/controller_budget.py --service-w 6 --efficiency 0.80
python docs/calcs/support_checks.py
python docs/calcs/analog_checks.py
python docs/calcs/pwm_checks.py
python docs/calcs/spice_dc_check.py --library "C:/Program Files/KiCad/10.0/bin/ngspice.dll"
~~~

I retain a 6 W delivered service ceiling and 5.75 W of conservative named reservations, including assumed downstream conversion losses. With four continuous 0.5 A loads, 9 V input and assumed 85% main-buck efficiency, the estimate is 2.784 A before extra protection losses and overhead; at 80% it is 2.833 A. I do not take credit for PWM duty when sizing the continuous fixture. PWM switching heat is evaluated separately; it redistributes delivered power and must not be added twice to the fixed-current supply model. The four pre-diode bleeders and a 20 mA engineering allowance for high-side operating current give approximately 2.808 A at 9 V/85% before protection losses. Actual operating current and thermal margins remain qualification requirements.

Four constant 0.5 A loads dissipate 60 W externally at 30 V. Fixed 48 Ω loads chosen for 24 V would draw 0.625 A/channel at 30 V, so I choose a separately rated fixture at each supply point.

I also evaluate the low-line contract at VFIELD=8.4 V after protection with assumed 80% buck efficiency. The full load/service demand, nominal bleeders and 20 mA operating allowance total about 2.916 A. The captured input path must limit its drop to 0.6 V at the 9 V connector fixture; tolerance, hot resistance and real conversion/operating consumption still need closure.

## Simulation and timing limits

The DC testbench uses equivalent input loading, resistances and ideal behavior. It does not simulate actual IC faults, converter startup, temperature, physical return paths or whole-board operation. I compare simulated operating points with independent equations and retain the simulator identity in the report.

PWM calculations use published TPS4H160 timing at the manufacturer's specified test conditions plus explicit engineering guards. I qualify actual edge timing and sense validity across the selected supply/control/limit conditions. A low-frequency target and calculated sampling window do not prove compatibility with arbitrary motors, solenoids or LED drivers.

## Capacitor evidence

I track the retained supply/reference banks in [capacitor_evidence.json](capacitor_evidence.json). Their effective-capacitance minima remain open until manufacturer bias/temperature evidence or documented measurement closes them. Nominal ratings do not prove regulator stability or protection shutdown hold-up.

The scripts and repository audits cover only their stated checks. Schematic/ERC, PCB/DRC, load/fault-energy review, thermal measurements and prototype qualification follow native implementation.
