# Current-loop status receivers

I receive the two TPS26611 SGOOD signals with **two SN74AUP1T17DCKR** low-threshold Schmitt buffers and **one SN74LVC2G125DCUR** qualified output buffer. All three packages use controller `3V3_DIG` and `MAIN_GND`. This network completes the status connections to PD8 and PD9 in [Control and service](Control_Service.md); the current protectors themselves are specified in [Analog](Analog.md). My [component groups](../components/control_service.json) are capture selections, not a released assembly BOM.

## Input level, load and wiring

SGOOD is low when the protector reports a good signal and high when it reports a fault. With +Vs above 2.5 V, TI specifies a **2–3 V high**, rather than a 15 V logic output. Its low-state pull-down resistance is **6.3 kΩ typical**; the datasheet does not give a maximum resistance. I use a high-impedance receiver and do not put an LED, a 10 kΩ pullup, or a service-rail clamp on SGOOD. [TPS2661 Rev C, sections 7.5 and 8.3.7](https://www.ti.com/lit/ds/symlink/tps2661.pdf)

For each channel I connect `LOOPx_SGOOD_FIELD` through **100 Ω, ERJ-3EKF1000V**, to the Schmitt input. A **1.00 MΩ, ERJ-3EKF1004V**, input pulldown defines the input when the protector is unpowered; it does not feed a service supply into the field device. At a 3 V SGOOD high, the 1% pulldown corner and 0.5 µA receiver leakage draw less than **3.54 µA**. This is within the manufacturer's high-level output characterization load interval and far below the 200 µA SGOOD sink-current stress limit. The series resistor's maximum extra high-level drop from receiver leakage is less than 51 µV.

| SN74AUP1T17 DCK pin | Each channel connection |
| --- | --- |
| 1 NC | Explicit no-connect |
| 2 A | `LOOPx_STATUS_INPUT`, after the 100 Ω series resistor; 1 MΩ to MAIN_GND |
| 3 GND | MAIN_GND |
| 4 Y | `LOOPx_BAD_CONDITIONED`, directly to its qualified buffer input |
| 5 VCC | 3V3_DIG; 100 nF local X7R bypass |

At 3.0–3.6 V supply over −40 to +85 °C, the selected part's rising Schmitt threshold is at most **1.19 V** and its falling threshold is at least **0.50 V**. The 2 V minimum SGOOD high has about **0.81 V** of threshold margin. The input accepts slow transitions; I do not apply a non-Schmitt buffer's 20 ns/V requirement to the weak SGOOD output. Its input leakage and powered-off leakage are each bounded by **0.5 µA**, with signals up to 3.6 V. The 0–50 °C board envelope is inside this part's specified temperature range. [SN74AUP1T17 Rev A, sections 5, 6.3, 6.5 and 8](https://www.ti.com/lit/ds/symlink/sn74aup1t17.pdf)

The typical 6.3 kΩ low-state model produces only about 3.2 mV from 0.5 µA of unfavorable input leakage. I use that as a loading estimate, not a guaranteed maximum low voltage. I verify the actual SGOOD low remains below 0.50 V during the protector's good state. I keep the input trace short and fit no input filter capacitor; the protector already supplies its own status deglitching.

## Qualified output and fail defaults

I use one control-sheet inverter unit to make `HEALTH_READY_N = NOT HEALTH_READY; LOOP_STATUS_OE_N = HEALTH_READY_N`. This is one unit of the selected SN74LVC2G04DBVR in SOT-23-6; its other input is grounded and its unused output is no-connect. HEALTH_READY is independent analog/field power health and reset qualification. Neither SGOOD signal participates in generating this enable, so this status circuit creates no startup cycle.

| SN74LVC2G125 DCU pin | Connection |
| --- | --- |
| 1 1OE; 7 2OE | LOOP_STATUS_OE_N; shared 10 kΩ pullup to 3V3_DIG |
| 2 1A; 5 2A | LOOP1_BAD_CONDITIONED; LOOP2_BAD_CONDITIONED |
| 6 1Y | Through 100 Ω to `LOOP1_BAD_MCU`, PD8/package pin 55 |
| 3 2Y | Through 100 Ω to `LOOP2_BAD_MCU`, PD9/package pin 56 |
| 4 GND; 8 VCC | MAIN_GND; 3V3_DIG with 100 nF local bypass |

Each MCU-side status net has **100 kΩ, ERJ-3EKF1003V, to 3V3_DIG**. Disabled buffers therefore report **high/invalid**, including reset and lost analog health. The downstream buffer is powered from the same digital supply as the MCU and has powered-off protection. SGOOD never connects directly to the MCU rail or GPIO. The first-stage Schmitt outputs carry only the next buffer's input load; the 100 kΩ pulls are downstream of the qualified outputs. [SN74LVC2G125 pin functions and Ioff](https://www.ti.com/lit/ds/symlink/sn74lvc2g125.pdf)

| State | MCU status interpretation |
| --- | --- |
| HEALTH_READY low | High/invalid from output pullup; no usable loop status |
| Health valid, LOOP_ENABLE high, settled SGOOD low | Low/good |
| Health valid, settled SGOOD high | High/fault; invalidate the reading |
| Loop protection disabled or recovering | Invalid regardless of a low status level |

I name these GPIO nets `LOOP1_BAD_MCU` and `LOOP2_BAD_MCU` to preserve the physical high-is-fault polarity. A software `loop_good` value is true only when the status is low, LOOP_ENABLE is active, analog health and threshold settling are valid, and the status has settled after the protector's specified deglitch interval. I do not treat a disabled protector's low output as a valid current reading.

## Capture and qualification

I allocate three additional IC packages, three 100 nF capacitors, four 100 Ω resistors, two 1 MΩ pulldowns, two 100 kΩ pullups and one 10 kΩ OE pullup. One control-sheet inverter unit supplies the enable polarity; the other unit is grounded/no-connect. I keep both low-speed interstage traces short, and compare every physical pin with the datasheets and selected KiCad symbols before capture approval.

I qualify normal, overload, negative fault, reset, disabled receiver and external-supply removal states. I measure SGOOD low voltage, input loading, status transitions, qualified-output defaults and powered-off leakage. These are prototype checks; I have not yet measured this circuit. I reserve **0.50 mA from 3V3_DIG** for this receiver network in its stable state, including the two output pullups and the OE pullup's approximately 0.33 mA enabled-state current; brief switching and fault intervals remain in the measured controller-current budget.
