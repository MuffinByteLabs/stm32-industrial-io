# Controller, service, and hardware permission

I use this circuit specification with my [capture package](../Schematic_Capture.md). The values below are my Rev A capture selections. I verify the resulting symbol pins, layout, firmware, and measurements at the later gates; I do not treat this document as an assembled-board rating.

## Controller and clock

I select STM32G474VET6, LQFP100, and use the following power connections. MAIN_GND is the common electrical reference; VSSA has a quiet return to the same ground plane.

| MCU pins | Connection and local components |
| --- | --- |
| VDD 24, 49, 64, 75, 100 | 3V3_DIG; one 100 nF X7R at each pair, plus one 10 µF bulk capacitor near the MCU |
| VSS 23, 48, 63, 74, 99 | MAIN_GND |
| VDDA 37 / VSSA 35 | 3V3_MCU_ANA / MAIN_GND; 100 nF and 1 µF at VDDA |
| VREF+ 36 | 3V3_MCU_ANA through 0 Ω; separate 100 nF and 1 µF to VSSA. This is the MCU diagnostic ADC reference, not the external ADC reference |
| VBAT 6 | 3V3_DIG, with 100 nF local bypass; no backup battery in Rev A |
| PG10–NRST 14 | RESET_OK open-drain reset net, 10 kΩ to 3V3_DIG, 100 nF to MAIN_GND; reset button pulls to ground |
| PB8–BOOT0 95 | 10 kΩ to MAIN_GND; test pad only, no field function |
| PF0–OSC_IN 12 | 8 MHz CMOS clock through 33 Ω close to the oscillator |
| PF1–OSC_OUT 13 | Unconnected with a no-connect flag; HSE bypass mode |

I select **SiT8008BI-22-33S-8.000000E**, an 8 MHz, 3.3 V, ±25 ppm, industrial-temperature oscillator in 3.2 × 2.5 mm. The code specifies standby, default drive, and 1,000-piece tape packaging; prototype cut tape must contain the same programmed configuration. Pin 4 is 3V3_DIG, pin 2 is ground, pin 3 is OUT, and pin 1 is ST. I fit 100 nF at pin 4 and a 10 kΩ pullup on ST. PC4 drives ST low only after switching to an internal clock for USB-only suspend. I do not substitute the OE variant: OE does not give the same low standby current. I verify the land pattern against the manufacturer drawing. [SiT8008 datasheet](https://www.sitime.com/datasheet/SiT8008), [production status](https://www.sitime.com/products/mhz-oscillators/lvcmos-oscillators/sit8008)

I use HSE bypass with PLLM=2, PLLN=72, PLLR=2 and PLLQ=6: 144 MHz core and 48 MHz USB/FDCAN. I start SPI1 at 1.125 MHz, and I2C3 at 100 kHz. I retain SWD and SWO, disable unused JTAG functions, and disable UCPD dead-battery pull resistors since CC uses discrete resistors. I keep PG10 configured as NRST. I use normal application boot from flash; SWD is the initial recovery/programming path. ROM DFU is not a dependency of Rev A. [STM32G474 datasheet](https://www.st.com/resource/en/datasheet/stm32g474ve.pdf), [hardware guide](https://www.st.com/resource/en/application_note/an5093-getting-started-with-stm32g4-series--hardware-development-boards-stmicroelectronics.pdf), [RM0440](https://www.st.com/resource/en/reference_manual/rm0440-stm32g4-series-advanced-armbased-32bit-mcus-stmicroelectronics.pdf)

## Complete MCU signal allocation

I assign every required peripheral, command, health input and diagnostic signal before capture. The numbers below are physical LQFP100 pins from DS12288 Table 12. I compare this table with the selected symbol and generated CubeMX configuration before approving the schematic.

| Signal | MCU pin / package pin | Configuration / external default |
| --- | --- | --- |
| ADC_CS / DAC_CS | PE2 / 1; PE3 / 2 | GPIO outputs; receiving field pullups 10 kΩ |
| ARM_CLK | PE4 / 3 | GPIO; 10 kΩ pulldown; fresh pulse ≥10 µs |
| DISARM_N | PE5 / 4 | GPIO; 10 kΩ pulldown, low asynchronously clears ARM |
| AO_CMD | PE6 / 5 | GPIO; 10 kΩ pulldown |
| DI2 / DI3 / DI4 | PC0 / 15; PC1 / 16; PC2 / 17 | Buffered inputs; 10 kΩ pulldowns at receiver |
| FIELD_OK | PC3 / 18 | Conditioned service-domain health input |
| DI1_TIMER | PA0 / 20 | TIM2_CH1 AF1, timer capture/counting; 10 kΩ pulldown |
| FIELD3V3_OK / ADC5_OK | PA1 / 21; PA2 / 22 | Conditioned health inputs |
| ANA15_OK / VNEG_OK | PA3 / 25; PA4 / 26 | Conditioned health inputs |
| SPI_SCK / MISO / MOSI | PA5 / 27; PA6 / 28; PA7 / 29 | SPI1 AF5; SCK/MOSI receiving pulldowns; MISO pulldown |
| HSE_ST / REF_OK | PC4 / 30; PC5 / 31 | Oscillator standby output / health input |
| AO_READBACK / DO_CS_ADC | PB0 / 32; PB1 / 33 | ADC1_IN15 / ADC1_IN12, per analog circuit |
| WATCHDOG_OK | PB2 / 34 | Conditioned hardware watchdog status |
| DO1_CMD … DO4_CMD | PE7 / 38; PE8 / 39; PE9 / 40; PE10 / 41 | GPIO; each 10 kΩ pulldown before receiving command gate |
| RELAY1_CMD / RELAY2_CMD | PE11 / 42; PE12 / 43 | GPIO; 10 kΩ pulldowns |
| DO_CS_SEL_L / DO_CS_SEL_H / DO_DIAG_EN | PE13 / 44; PE14 / 45; PE15 / 46 | Buffered GPIO; receiving defaults low |
| DO_FAULT_N | PB10 / 47 | Buffered field status; mark invalid when field power is absent |
| WD_EN / WDI | PB11 / 50; PB12 / 51 | GPIO, 10 kΩ pulldowns; enable only after initialization |
| AO_FAULT_N / VOLTAGE_MUX_FAULT_N / CURRENT_MUX_FAULT_N | PB13 / 52; PB14 / 53; PB15 / 54 | Conditioned/buffered status inputs; analog validity required |
| LOOP1_BAD_MCU / LOOP2_BAD_MCU | PD8 / 55; PD9 / 56 | Qualified Schmitt status; high is fault/invalid, low is good only when enabled and settled; per [loop status](Loop_Status.md) |
| INPUT_FAULT_N / USB_FAULT_N / POWER_SOURCE_STATUS | PD10 / 57; PD11 / 58; PD12 / 59 | Level-shifted or buffered status as required by each power circuit |
| STATUS_LED / FAULT_LED | PD13 / 60; PD14 / 61 | 1 kΩ series, green/red LEDs to ground; low turns off |
| EEPROM_WP | PD15 / 62 | 10 kΩ pullup; high write-protects |
| ARM_STATE / VBUS_PRESENT_N | PC6 / 65; PC7 / 66 | ARM latch Q feedback / transistor collector sense |
| EEPROM_SCL / SDA | PC8 / 67; PC9 / 68 | I2C3 AF8; each 4.7 kΩ to 3V3_DIG |
| SERVICE_BUTTON_N | PA8 / 69 | GPIO input, 10 kΩ pullup and 100 nF; button to ground |
| USB D− / D+ | PA11 / 72; PA12 / 73 | USB full speed; 22 Ω series at MCU |
| SWDIO / SWCLK | PA13 / 76; PA14 / 77 | SWD, retain debug |
| ADC_RESET_N_CMD | PC10 / 79 | GPIO, 10 kΩ pulldown; tenth outgoing buffer to ADC_RST_N_FIELD |
| ACQ_ENABLE_CMD | PA15 / 78 | GPIO, 10 kΩ pulldown; disables/restarts both loop protectors through hardware-qualified gate |
| CAN_RX / CAN_TX | PD0 / 82; PD1 / 83 | FDCAN1 AF9; receiving TX default high |
| RS485_DE_CMD / TX / RX | PD4 / 86; PD5 / 87; PD6 / 88 | USART2 AF7; DE hardware gated, TX idle high |
| SWO | PB3 / 90 | Trace output to debug header |

I leave the other GPIOs unconnected and set no-connect flags. Firmware sets unused pins to an appropriate low-consumption state, preserving boot/debug pins. I keep PC13–PC15 unused. I do not route signals to supply pins or reuse the clock/boot/reset pins.

## USB-C service and storage

I retain the TYPE-C-31-M-12 USB 2.0 receptacle and its project-local verified drawing. I join A6/B6 for D+ and A7/B7 for D−. I join all VBUS pins to USB5_RAW and all GND pins to MAIN_GND. CC1 and CC2 each receive **5.1 kΩ, 1% to ground**; I leave SBU1/SBU2 unconnected. I fit TPD2E2U06DBZR on CC1/CC2 and USBLC6-2SC6 on the data pair, with its VBUS clamp tied to USB5_RAW. I connect the shield directly to MAIN_GND through a fitted 0 Ω link for the initial plastic-enclosure fixture. A future chassis bonding arrangement requires its own review. [USBLC6](https://www.st.com/resource/en/datasheet/usblc6-2.pdf), [CC ESD part](https://www.ti.com/lit/ds/symlink/tpd2e2u06.pdf)

I use TPS2553DBVR before the power mux: IN=USB5_RAW, OUT=USB5_LIMIT, GND=MAIN_GND, EN=USB5_RAW through 10 kΩ, ILIM=61.9 kΩ 1% to ground. I fit 100 nF and 1 µF on IN and 1 µF on OUT. FAULT has a 10 kΩ service pullup and uses the twelfth service-receiving buffer channel. At resistor tolerance corners, the datasheet limit equations give about **378–480 mA**, before the separately specified transient response. I do not use this fault limiter as the USB current permission mechanism. Firmware must draw ≤100 mA before configuration; the USB configuration declares 500 mA, and normal USB-only service is budgeted below 150 mA. Startup uses a reduced core clock with LEDs off. I qualify inrush, cable drop, enumeration and removal against the implemented circuit. [TPS2553](https://www.ti.com/lit/ds/symlink/tps2553.pdf)

I sense VBUS without applying 5 V to an MCU pin: USB5_RAW →100 kΩ→MMBT3904 base; 100 kΩ base to emitter; emitter at ground; collector PC7 with 100 kΩ service pullup. VBUS_PRESENT_N is active low. USB attachment requires valid VBUS and USB clocks before enabling the internal D+ pullup.

I power ISO1212 logic, both bus VCC1 pins, ADC/DAC digital supplies, and all field receiving command gates from **3V3_FIELD_LOGIC**. Those interfaces are off during USB-only service. USB suspend while field power is absent disarms outputs, drives WD_EN low, turns LEDs off, puts EEPROM in standby, stops the external oscillator using ST, and enters the documented MCU USB-wake low-power mode. I require measured VBUS current ≤2.5 mA in that state before claiming USB suspend compliance. With field power present the mux prefers field power. I do not claim USB compliance from the component list alone.

I select 24LC64-I/SN, SOIC8. VCC=3V3_DIG, VSS/A0/A1/A2=ground, address 0x50, 100 nF bypass, 4.7 kΩ SCL/SDA pullups, WP=PD15 with 10 kΩ pullup. I start at 100 kHz and limit bus capacitance to 200 pF (nominal 0.8473RC rise ≈796 ns). Configuration/calibration uses two versioned CRC records; writes are explicit and rate-limited. [24LC64 datasheet](https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/24AA64-24FC64-24LC64-64-Kbit-I2C-Serial-EEPROM-DS20001189.pdf)

I use a keyed 2×5, 1.27 mm SWD header, Samtec FTSH-105-01-L-DV-K. Pins 1–10: VTREF, SWDIO, GND, SWCLK, GND, SWO, key/no pin, reserved/no-connect, GND, NRST. VTREF senses 3V3_DIG and does not power the board. I fit reset and service buttons (TS-1187A), with 10 kΩ service pullup and 100 nF on the service button at PA8/pin69. I fit LTST-C190KGKT and LTST-C190KRKT status LEDs with 1 kΩ resistors.

## Supervisors and tolerance-bounded rail health

I select three TPS3808G33DBVR supervisors, all powered from service 3V3_DIG: one SENSE monitors 3V3_DIG, one monitors 3V3_FIELD_LOGIC, and one monitors 3V3_MCU_ANA. The analog and digital supervisors share the open-drain RESET_OK net, holding MCU reset and removing HEALTH_READY whenever either MCU supply is invalid. I power the diagnostic readback TMUX1511 from its receiving 3V3_MCU_ANA rail and qualify its controls with HEALTH_READY; a valid digital rail alone cannot enable acquisition into a missing analog rail. CT is open, each VDD gets 100 nF, and MR has a 10 kΩ service pullup. Service RESET also receives the reset button and MCU NRST. I feed watchdog WDO to service MR so the supervisor stretches reset release by its 12–28 ms specified delay. The second RESET has a service 10 kΩ pullup and directly supplies FIELD3V3_OK. Powering this monitor from service lets it actively report an absent field rail and avoids an enable/status dependency through a disabled crossing buffer. [TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf)

I power three TPS3700DDCR and one TPS3702CX50DDCR from service 3.3 V, each with 100 nF. TPS3700 INA monitors UV and INB monitors OV; I join OUTA/OUTB only for the corresponding positive-rail window, with 10 kΩ service pullups. The VNEG monitor's OUTA/OUTB remain separate for REF_OK and VNEG_OK. All divider resistors are 0.1%, ≤25 ppm/°C, and 0603; high-side divider voltage is distributed where the selected resistor working voltage requires it. I fit 1 nF C0G at each TPS3700 sense node for RF filtering, and use the Schmitt outputs for digital gates.

| Health | Frozen network | Nominal transition |
| --- | --- | --- |
| FIELD_OK UV | INA: series 200 kΩ+10 kΩ to VFIELD /10 kΩ to ground | Healthy release 8.800 V; falling assert 8.679 V |
| FIELD_OK OV | INB: series 750 kΩ+20 kΩ to VFIELD /10 kΩ to ground | Rising assert 31.200 V; falling clear 30.771 V |
| ANA15_OK UV | INA: series 300 kΩ+20 kΩ to 15V_ANA /10 kΩ | Release 13.200 V; assert 13.019 V |
| ANA15_OK OV | INB: series 390 kΩ+10 kΩ to 15V_ANA /10 kΩ | Assert 16.400 V; clear 16.175 V |
| ADC5_OK | TPS3702CX50 SENSE=ADC_AVDD, SET=3V3_DIG | Nominal UV/OV trips 4.80/5.20 V; specified tolerance and hysteresis remain in the acceptance bounds |
| REF_OK | VNEG-monitor INA: series 49.9 kΩ+100 Ω to REF2V5 /10 kΩ to ground | Reference release 2.400 V; assert 2.367 V |
| VNEG_OK | VNEG-monitor INB: 68.1 kΩ to REF2V5, series 18.2 kΩ+300 Ω to VNEG | Bias-loss assert −0.170 V; recovery −0.177 V |

I select REF3325AIDBZR for REF2V5: VIN=3V3_DIG, GND=MAIN_GND, 1 µF at input/output. The negative monitor node is `(18.5×VREF+68.1×VNEG)/86.6`; it remains above −0.3 V when the reference is absent and normal negative bias is present. REF_OK prevents an absent reference from qualifying the analog domain. The reproduced bounds include comparator threshold limits, input bias, ±0.1% resistors, ±25 ppm/°C drift over 0–50 °C, reference ±0.15% and 30 ppm/°C drift. I publish those results in [support calculations](../calcs/support_checks.py). These are guard bands around 9–30 V, rather than precision cutoffs. [TPS3700](https://www.ti.com/lit/ds/symlink/tps3700.pdf), [TPS3702](https://www.ti.com/lit/ds/symlink/tps3702.pdf), [REF33](https://www.ti.com/lit/ds/symlink/ref33.pdf)

## Watchdog, ARM latch, and explicit logic

I use TPS3431SDRBR, VDD=3V3_DIG, GND=MAIN_GND, 100 nF local bypass. SET1=VDD and CWD=10 kΩ to VDD select a **170–230 ms** timeout. WDI receives a falling edge every 50 ms only after application health checks. WD_EN has a 10 kΩ pulldown and is set high after initialization; pulling it low immediately removes output permission through ENOUT. ENOUT has its own 10 kΩ pullup to 3V3_DIG. WDO has a separate 10 kΩ pullup and drives service-supervisor MR. I keep WDO separate from ENOUT to avoid holding the MCU in reset whenever watchdog enable is low. WATCHDOG_OK is the AND of conditioned WDO and ENOUT; disabling the watchdog cannot leave outputs permitted. I measure reset/enable timing before validation. [TPS3431](https://www.ti.com/lit/ds/symlink/tps3431.pdf)

I use SN74LVC1G74DCUR for ARM: VCC=3V3_DIG, GND=MAIN_GND, D and PRE_N tied high, CLK=ARM_CLK with 10 kΩ pulldown, CLR_N from the hardware combination below, Q=ARM_STATE, Q_N unused. I fit 100 nF at every logic IC. I use SN74LVC2G17DBVR for nine raw health signals and SN74LVC2G08DCUR for the following service combinations. I ground unused gate inputs and leave their outputs unconnected.

~~~text
A = FIELD_OK AND ADC5_OK  (FIELD5V_VALID)
B = ANA15_OK AND VNEG_OK
C = REF_OK AND FIELD3V3_OK
D = A AND B
ANALOG_VALID = D AND C
HEALTH_READY = ANALOG_VALID AND RESET_OK
WATCHDOG_OK = WDO_HIGH AND ENOUT_HIGH
CLR_BASE = HEALTH_READY AND WATCHDOG_OK
CLR_N = CLR_BASE AND DISARM_N
PERMISSION = CLR_N AND ARM_STATE
FIELD_IO_OK = FIELD_OK AND FIELD3V3_OK
CROSS_OK = FIELD_IO_OK AND RESET_OK
~~~

I allocate six dual AND packages to these twelve service gates, five dual Schmitt packages to the nine health signals, and one SN74LVC2G04DCUR dual inverter for CROSS_OE_N and HEALTH_READY_N. LOOP_STATUS_OE_N is the same net as HEALTH_READY_N. READBACK_ENABLE is HEALTH_READY; both inverter units are used. I do not insert firmware in the asynchronous fault-clear path.

I allocate five dual AND packages powered by 3V3_FIELD_LOGIC: four DO gates, two relay gates, one AO gate, one RS485_DE gate qualified by CROSS_OK, and one acquisition-enable gate (ANALOG_VALID AND ACQ_ENABLE_CMD), and one threshold-supply gate VFP_ENABLE = ANALOG_VALID AND FIELD3V3_OK. RS485_DE_GATED = RS485_DE_CMD AND CROSS_OK; bus direction stays available while actuator ARM is clear. The other seven actuator gates use PERMISSION. Every command input and final actuator-enable output has a 10 kΩ pulldown. PERMISSION, CROSS_OK and ANALOG_VALID each have a field-side 10 kΩ pulldown so a missing service rail cannot leave a receiving gate input floating. CAN transmit is an interface signal with idle-high default, not an actuator ARM command. The logic families' Ioff capability is required on receiving gates.

| Condition | ARM and resulting permission |
| --- | --- |
| Reset, USB-only, missing field/analog rail, watchdog disabled/failed, or DISARM_N low | CLR_N low, ARM=0, output gates low |
| All health returns with no fresh ARM_CLK edge | ARM remains 0 |
| All health valid, DISARM_N high, fresh arm pulse and watchdog healthy | ARM=1; commands can pass |
| Any required health lost while armed | Asynchronous ARM clear; stale commands do not restore permission |

I set ACQ_ENABLE_CMD high only after analog health is valid. A latched loop fault requires an explicit recovery with ARM clear and ACQ_ENABLE_CMD low for at least 10 ms before re-enabling both receivers. I clear firmware commands before raising DISARM_N and pulsing ARM. I wait at least 50 ms after VFP_ENABLE rises for the threshold supplies to settle, then delay the arm pulse at least 1 ms after hardware health stabilizes. The system has one command owner and a 1 s lease; traffic without a valid owner command does not renew it. Ownership changes and recovery always disarm.

## Domain crossings and defaults

I use SN74LVC2G125DCUR buffers powered from the **receiving** rail. Field-interface OE pins use CROSS_OE_N; each also has a 10 kΩ receiving-rail pullup. The USB_FAULT_N receiving channel has OE tied low so its fault remains observable in USB-only service, independently of field health. Ioff covers a live input with an absent receiving supply, with finite datasheet leakage. I fit 33 Ω at transmitting outputs on SPI and the short MCU-side bus signals. I group the following channels into eleven dual packages; unused inputs are grounded and unused outputs have no-connect flags.

| Direction | Channels | Destination defaults |
| --- | --- | --- |
| Service → field, five dual packages | SCK, MOSI, ADC_CS, DAC_CS, diagnostic select low/high, diagnostic enable, RS485_TX, CAN_TX, ADC_RST_N_FIELD | CS/TX high; clock/data/selection/enable low |
| Field → service, six dual packages | ADC_SDO, DI1–DI4, RS485_RX, CAN_RX, DO_FAULT_N, AO_FAULT_N, two TMUX fault flags, USB_FAULT_N | Serial idle-high where required; acquisition/default GPIO low; field-dependent status invalid when CROSS_OK is low |

I do not drive OE from a field-powered status gate that disappears before the service supply. Service hardware produces the enable and clears it on reset/field undervoltage. I receive the weak 2–3 V loop SGOOD outputs through the separately specified [loop-status receivers](Loop_Status.md). Their additional SN74LVC2G125 package brings the project total to twelve dual crossing/status buffers; the eleven packages above and this extra package have distinct component rows. Input eFuse fault/status follows the power specification. I keep the independent analog readback clamp/isolation network specified in [Analog](Analog.md). [SN74LVC2G125](https://www.ti.com/lit/ds/symlink/sn74lvc2g125.pdf), [SN74LVC2G08](https://www.ti.com/lit/ds/symlink/sn74lvc2g08.pdf), [SN74LVC2G17](https://www.ti.com/lit/ds/symlink/sn74lvc2g17.pdf)

## Capture and measurement gates

I include labeled test points for every rail, each raw/conditioned health net, CLR_N, ARM_STATE, PERMISSION, CROSS_OK, WDI/WDO/ENOUT, reset, boot, and USB limiter output. I use 1.5 mm plated test pads with 0.8 mm drills for accessible low-speed nodes; SPI/clock scope points are small pads with adjacent ground access. I verify each supervisor polarity and the complete gate truth table in the captured netlist, including simultaneous rail ramps. The TPS3808 SENSE-to-reset timing is a typical value, not a guaranteed maximum for my 100 nF reset network. During source removal and transfer I measure 3V3_MCU_ANA/VDDA/VREF+, RESET_OK, READBACK_ENABLE and both MCU ADC nodes. I require no positive ADC injection and valid inputs between ground and VREF+ while converting; I do not assume a generic clamp-current allowance. I check STM32 supply ramp limits and stop conversions before analog supply loss. I record REV_ID and review the [current errata](https://www.st.com/resource/en/errata_sheet/es0430-stm32g471xx473xx474xx483xx484xx-device-errata-stmicroelectronics.pdf) before firmware release.

I must still verify physical symbols/footprints, generated MCU timing, USB suspend/inrush, rail-ramp timing, power-off leakage, and actual fault response using the completed schematic and prototype. These are implementation/qualification gates, not missing feature or component selections.
