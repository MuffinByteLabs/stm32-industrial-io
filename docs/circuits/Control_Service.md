# Controller, service, and hardware permission

I use this circuit specification with my [capture package](../Schematic_Capture.md). I power the complete controller from the external 9–30 V supply. USB carries data and provides VBUS detection; it does not supply the board. The values below are my Rev A capture selections. I verify resulting symbol pins, layout, firmware and measurements at the later gates.

## Controller and clock

I select STM32G474VET6, LQFP100. MAIN_GND is the common reference; VSSA has a quiet return to the same ground plane.

| MCU pins | Connection and local components |
| --- | --- |
| VDD 24, 49, 64, 75, 100 | 3V3_DIG; one 100 nF at each pair, plus 10 µF near the MCU |
| VSS 23, 48, 63, 74, 99 | MAIN_GND |
| VDDA 37 / VSSA 35 | 3V3_MCU_ANA / MAIN_GND; 100 nF and 1 µF at VDDA |
| VREF+ 36 | 3V3_MCU_ANA through 0 Ω, with its own 100 nF and 1 µF to VSSA; diagnostic ADC reference |
| VBAT 6 | 3V3_DIG with 100 nF; no backup battery |
| PG10–NRST 14 | RESET_OK, 10 kΩ to 3V3_DIG, 100 nF to MAIN_GND; reset button to ground |
| PB8–BOOT0 95 | 10 kΩ to MAIN_GND; test pad only |
| PF0–OSC_IN 12 | 8 MHz CMOS clock through 33 Ω at the oscillator |
| PF1–OSC_OUT 13 | No-connect in HSE bypass mode |

I select **SiT8008BI-22-33S-8.000000E**, an 8 MHz, 3.3 V, ±25 ppm industrial oscillator in 3.2 × 2.5 mm. Pin 4 is 3V3_DIG with 100 nF, pin 2 ground, pin 3 OUT and pin 1 ST with 10 kΩ to 3V3_DIG. ST stays high; no MCU standby command is required. Prototype cut tape must contain the same programmed standby configuration. I compare the land pattern with the manufacturer drawing. [SiT8008 datasheet](https://www.sitime.com/datasheet/SiT8008), [production status](https://www.sitime.com/products/mhz-oscillators/lvcmos-oscillators/sit8008)

I use HSE bypass with PLLM=2, PLLN=72, PLLR=2 and PLLQ=6: 144 MHz core and 48 MHz USB/FDCAN. I start SPI1 at 1.125 MHz and I2C3 at 100 kHz. I retain SWD/SWO, disable unused JTAG and UCPD dead-battery pulls, and retain PG10 as NRST. Normal boot is from flash; SWD is the initial programming/recovery path. [STM32G474 datasheet](https://www.st.com/resource/en/datasheet/stm32g474ve.pdf), [hardware guide](https://www.st.com/resource/en/application_note/an5093-getting-started-with-stm32g4-series--hardware-development-boards-stmicroelectronics.pdf), [RM0440](https://www.st.com/resource/en/reference_manual/rm0440-stm32g4-series-advanced-armbased-32bit-mcus-stmicroelectronics.pdf)

## Complete MCU signal allocation

I compare these physical LQFP100 pins with DS12288 Table 12, the selected symbol and generated CubeMX configuration before approving capture. The field side owns local output defaults; controller-side source pullups join only 3V3_DIG.

| Signal | MCU pin / package pin | Configuration / default |
| --- | --- | --- |
| ADC_CS | PE2 / 1 | GPIO; source 10 kΩ to 3V3_DIG, buffered field output 10 kΩ to field logic |
| ARM_CLK | PE4 / 3 | GPIO, 10 kΩ pulldown; fresh pulse ≥10 µs |
| DISARM_N | PE5 / 4 | GPIO, 10 kΩ pulldown; low asynchronously clears ARM |
| DI2 / DI3 / DI4 | PC0 / 15; PC1 / 16; PC2 / 17 | Buffered inputs with service 10 kΩ pulldowns |
| FIELD_OK | PC3 / 18 | Conditioned input-power health |
| DI1_TIMER | PA0 / 20 | TIM2_CH1 AF1; 10 kΩ pulldown |
| FIELD3V3_OK / ADC5_OK | PA1 / 21; PA2 / 22 | Conditioned rail health |
| ANA15_OK | PA3 / 25 | Conditioned +15 V window health |
| SPI_SCK / SPI_MISO / SPI_MOSI | PA5 / 27; PA6 / 28; PA7 / 29 | SPI1 AF5; SCK/MOSI source and field-output defaults low, MISO service default low |
| DO_CS_ADC | PB1 / 33 | ADC1_IN12; protected current-diagnostic path |
| WATCHDOG_OK | PB2 / 34 | Conditioned watchdog permission |
| DO1_CMD / DO2_CMD / DO4_CMD | PE7 / 38; PE8 / 39; PE10 / 41 | GPIO; receiving command gates have 10 kΩ pulldowns |
| DO3_CMD | PE9 / 40 | TIM1_CH1 AF2 for qualified PWM, otherwise GPIO; 10 kΩ pulldown before hardware permission gate |
| RELAY1_CMD / RELAY2_CMD | PE11 / 42; PE12 / 43 | GPIO; 10 kΩ pulldowns |
| DO_CS_SEL_L_CMD / DO_CS_SEL_H_CMD | PE13 / 44; PE14 / 45 | Buffered GPIO; source and receiving defaults low |
| DO_FAULT_N_MCU | PB10 / 47 | Buffered active-low field fault, also conditioned into asynchronous ARM clear |
| WD_EN / WDI | PB11 / 50; PB12 / 51 | GPIO; WD_EN 10 kΩ pulldown |
| VOLTAGE_MUX_FAULT_N / CURRENT_MUX_FAULT_N | PB14 / 53; PB15 / 54 | Buffered status; analog validity required |
| LOOP1_BAD_MCU / LOOP2_BAD_MCU | PD8 / 55; PD9 / 56 | High is fault/invalid, low is good only while enabled and settled; [loop status](Loop_Status.md) |
| INPUT_FAULT_N | PD10 / 57 | Input eFuse open-drain fault; power sheet owns its service pullup |
| STATUS_LED / FAULT_LED | PD13 / 60; PD14 / 61 | Green/red LEDs with 1 kΩ; low turns off |
| EEPROM_WP | PD15 / 62 | 10 kΩ pullup; high write-protects |
| ARM_STATE / VBUS_PRESENT_N | PC6 / 65; PC7 / 66 | ARM latch Q / transistor collector sense |
| EEPROM_SCL / SDA | PC8 / 67; PC9 / 68 | I2C3 AF8 with 4.7 kΩ pulls to 3V3_DIG |
| SERVICE_BUTTON_N | PA8 / 69 | GPIO, 10 kΩ pullup and 100 nF; button to ground |
| USB D− / D+ | PA11 / 72; PA12 / 73 | USB full speed, 22 Ω series at MCU |
| SWDIO / SWCLK | PA13 / 76; PA14 / 77 | Retain SWD |
| ACQ_ENABLE_CMD / ADC_RESET_N_CMD | PA15 / 78; PC10 / 79 | GPIO, 10 kΩ pulldowns; reset command uses outgoing buffer |
| CAN_RX / CAN_TX | PD0 / 82; PD1 / 83 | FDCAN1 AF9; TX source and receiving defaults high |
| RS485_DE_CMD / TX / RX | PD4 / 86; PD5 / 87; PD6 / 88 | USART2 AF7; direction default low, TX source/receiving defaults high |
| SWO | PB3 / 90 | Trace output to debug header |

I leave other GPIOs unconnected with no-connect flags, including PE3, PE6, PA4, PC4, PC5, PB0, PB13, PE15, PD11 and PD12. I preserve boot/debug pins and set other unused pins to suitable low-consumption states. TIM1 is reserved for DO3; DI1 uses TIM2 independently.

For DO3 I use APB2 prescaler 1, TIM1 clock 144 MHz, PSC=143 and ARR=9999 for 100 Hz. PWM mode 1 is active high; CCR1=1000–9000 selects 10–90%. I preload duty updates for a period boundary. The 0%/100% endpoints use a disabled timer and explicit GPIO low/high, behind the same PERMISSION gate. I clear timer enable, compare values and command mode on disarm before accepting a fresh command and ARM edge. The initial load/frequency/diagnostic qualifications are in [Field I/O](Field_IO.md); this is not a motor or proportional-valve specification.

## USB-C data, programming and storage

I use TYPE-C-31-M-12 as a USB 2.0 data receptacle. I join A6/B6 for D+, A7/B7 for D−, all GND pins to MAIN_GND, and all VBUS pins only to USB_VBUS_SENSE. VBUS has 100 nF local bypass and no connection to a regulator input or board power rail. CC1/CC2 each have 5.1 kΩ, 1% to ground and TPD2E2U06DBZR ESD protection. USBLC6-2SC6 protects the data pair with its VBUS clamp at USB_VBUS_SENSE; SBU1/SBU2 are no-connect. The shield uses a fitted 0 Ω MAIN_GND link for the initial plastic enclosure. [USBLC6](https://www.st.com/resource/en/datasheet/usblc6-2.pdf), [CC protection](https://www.ti.com/lit/ds/symlink/tpd2e2u06.pdf)

I detect VBUS through MMBT3904: pin 1 base receives USB_VBUS_SENSE through 100 kΩ and has 100 kΩ to emitter; pin 2 emitter joins MAIN_GND; pin 3 collector is VBUS_PRESENT_N/PC7 with 100 kΩ to 3V3_DIG. The high-value sense path and ESD leakage are the only intended VBUS current. I declare a self-powered USB device and set descriptor power information from the measured host-current bound. Firmware enables the internal D+ pullup only with external power, valid MCU supplies/clocks and detected VBUS; it detaches on VBUS loss. I qualify host attach/removal and power-off data-line leakage. Connecting USB alone leaves the controller unpowered.

I select 24LC64-I/SN: VCC=3V3_DIG, VSS/A0/A1/A2=ground, address 0x50, 100 nF local bypass, 4.7 kΩ SCL/SDA pullups, WP=PD15 with 10 kΩ pullup. At 100 kHz and ≤200 pF, nominal 0.8473RC rise is about 796 ns. I store two versioned CRC configuration/calibration records; writes are explicit and rate-limited. [24LC64](https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/24AA64-24FC64-24LC64-64-Kbit-I2C-Serial-EEPROM-DS20001189.pdf)

My keyed Samtec FTSH-105-01-L-DV-K SWD header pins 1–10 are VTREF, SWDIO, GND, SWCLK, GND, SWO, key/no pin, reserved/no-connect, GND, NRST. VTREF senses 3V3_DIG and does not power the board. I select two TS-1187A reset/service buttons, LTST-C190KGKT and LTST-C190KRKT LEDs, and 1 kΩ LED resistors.

## Supervisors and rail health

I retain three TPS3808G33DBVR supervisors powered from 3V3_DIG: digital and MCU-analog SENSE share RESET_OK; field-logic SENSE produces FIELD3V3_OK. Each has 100 nF, open CT, and MR with 10 kΩ to 3V3_DIG. RESET_OK has the MCU's shared 10 kΩ pullup; FIELD3V3_OK has a separate 10 kΩ pullup. The current-diagnostic TMUX1511 uses receiving 3V3_MCU_ANA and **DO_CS_ENABLE=HEALTH_READY**, so absent analog supply cannot qualify acquisition. Watchdog WDO drives the digital supervisor MR; reset release is stretched by the specified 12–28 ms delay. [TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf)

I use two TPS3700DDCR windows and one TPS3702CX50DDCR, powered from 3V3_DIG with 100 nF each. For each TPS3700 window I join OUTA/OUTB with one service 10 kΩ pullup and fit 1 nF C0G at each sense node. ADC5_OK also has a 10 kΩ service pullup. Dividers use 0.1%, ≤25 ppm/°C 0603 resistors, with high-side voltage distributed across the stated series parts.

| Health | Frozen network | Nominal transition |
| --- | --- | --- |
| FIELD_OK UV | INA: 180 kΩ+10 kΩ from VFIELD /10 kΩ ground | Healthy release 8.000 V; falling assert 7.890 V |
| FIELD_OK OV | INB: 750 kΩ+20 kΩ from VFIELD /10 kΩ ground | Rising assert 31.200 V; falling clear 30.771 V |
| ANA15_OK UV | INA: 300 kΩ+20 kΩ from 15V_ANA /10 kΩ ground | Release 13.200 V; assert 13.019 V |
| ANA15_OK OV | INB: 390 kΩ+10 kΩ from 15V_ANA /10 kΩ ground | Assert 16.400 V; clear 16.175 V |
| ADC5_OK | TPS3702CX50 SENSE=ADC_AVDD, SET=3V3_DIG | Nominal UV/OV 4.80/5.20 V; retain tolerance/hysteresis bounds |

My [support calculations](../calcs/support_checks.py) include comparator threshold/bias limits and resistor tolerance plus 25 ppm/°C drift over 0–50 °C. They give a **12.72283 V minimum falling +15 V threshold**, used in the VFP shutdown proof. I require VFIELD ≥8.4 V at a measured 9 V connector input and full load, limiting the total hot input-path drop to 0.6 V. FIELD_OK release is 7.890844–8.109745 V and falling assertion is 7.711399–8.029498 V, leaving margin under that protected-rail bound. I start unloaded and qualify the eFuse UVLO and hot loaded path separately. These are bounded rail-health decisions rather than exact 9.000/30.000 V cutoffs. [TPS3700](https://www.ti.com/lit/ds/symlink/tps3700.pdf), [TPS3702](https://www.ti.com/lit/ds/symlink/tps3702.pdf)

## Watchdog, ARM latch and explicit logic

I use TPS3431SDRBR with VDD=3V3_DIG, 100 nF, SET1 high and CWD through 10 kΩ to VDD for a 170–230 ms timeout. WDI falls every 50 ms only after application health checks. WD_EN has 10 kΩ to ground and goes high after initialization. ENOUT and WDO have separate 10 kΩ service pullups. WDO drives digital-supervisor MR; ENOUT is combined with WDO for permission rather than joined to MR, avoiding a reset lock when watchdog enable is low. [TPS3431](https://www.ti.com/lit/ds/symlink/tps3431.pdf)

SN74LVC1G74DCUR stores ARM: VCC=3V3_DIG, D/PRE_N high, CLK=ARM_CLK, CLR_N from hardware below, Q=ARM_STATE and Q_N no-connect. I use four SN74LVC2G17DBVR dual Schmitt packages for FIELD_OK, ADC5_OK, ANA15_OK, FIELD3V3_OK, RESET_OK, WDO, ENOUT and buffered DO_FAULT_N_MCU. The last conditioned signal is DO_FAULT_OK, high only while the field fault line is inactive. Each logic IC has 100 nF.

~~~text
FIELD5V_VALID = FIELD_OK AND ADC5_OK
ANALOG_A = FIELD5V_VALID AND ANA15_OK
ANALOG_VALID = ANALOG_A AND FIELD3V3_OK
HEALTH_READY = ANALOG_VALID AND RESET_OK
WATCHDOG_OK = WDO_HIGH AND ENOUT_HIGH
CLR_HEALTH = HEALTH_READY AND WATCHDOG_OK
CLR_FAULT = CLR_HEALTH AND DO_FAULT_OK
CLR_N = CLR_FAULT AND DISARM_N
PERMISSION = CLR_N AND ARM_STATE
FIELD_IO_OK = FIELD_OK AND FIELD3V3_OK
CROSS_OK = FIELD_IO_OK AND RESET_OK
~~~

I allocate six service-powered SN74LVC2G08DCUR packages for eleven gates and one grounded-input spare. Five field-powered dual packages provide ten gates: four DO and two relay commands AND PERMISSION, RS485_DIR_GATED=RS485_DE_CMD AND CROSS_OK, ACQ_ENABLE_CMD AND ANALOG_VALID, VFP_ENABLE=ANALOG_VALID AND FIELD3V3_OK, and DO_DIAG_EN=FIELD5V_VALID AND FIELD3V3_OK. DO_DIAG_EN is hardware-held high whenever those two rails are valid; firmware has no disable path. FIELD5V_VALID and FIELD3V3_OK each have a shared field-side 10 kΩ pulldown at these gate inputs. Every command and each DO/relay final-enable output has a 10 kΩ pulldown. PERMISSION, CROSS_OK and ANALOG_VALID each have a field-side 10 kΩ pulldown; only ground pulls are placed directly on MCU commands that reach field gates. VFP/loop EN local pulldowns belong to the analog sheet. CAN TX has its separate buffered idle-high default.

I use one SN74LVC2G04DCUR unit for HEALTH_READY_N/LOOP_STATUS_OE_N; I ground the spare unit's input and leave its output unconnected. DO_CS_ENABLE remains active high and needs no inverter.

| Condition | ARM and output permission |
| --- | --- |
| Reset, missing required rail, watchdog disabled/failed, asserted DO fault, or DISARM_N low | CLR_N low; ARM=0; output commands blocked |
| Health/fault recovers without a fresh ARM_CLK edge | ARM remains zero |
| Valid health and watchdog, inactive DO fault, DISARM_N high, fresh ARM edge | ARM=1; commands can pass |
| DO3 timer still running when a fault occurs | Hardware PERMISSION blocks it and ARM clears; timer state is discarded before recovery |

The DO fault participates in asynchronous ARM clear because PWM input transitions can reset the load switch's internal thermal latch. I qualify diagnostic enable and all intended PWM/load transitions against false faults, without masking real short/thermal faults. I clear commands and timer state, verify recovery and pulse ARM only after a fresh valid command. My field-I/O specification records the switch's fault behavior and test sequence.

ACQ_ENABLE_CMD rises only after valid analog health. A latched loop fault is recovered with ARM clear and acquisition enable low for ≥10 ms before re-enable. I wait ≥50 ms after VFP_ENABLE rises for threshold settling, then ≥1 ms of stable hardware health before arming. One selected command owner has a 1 s lease; read-only or invalid traffic does not renew it. Owner changes and recovery disarm.

## Domain crossings and default-off enables

I retain receiving-powered SN74LVC2G125DCUR buffers for unequal derived-rail ramps and collapse. I group eight outgoing channels into four packages and ten incoming channels into five packages. Source pulls on MCU signals use 3V3_DIG; field-output pulls are after the buffer and use 3V3_FIELD_LOGIC. This prevents an idle-high pullup from feeding an unpowered MCU pin. I fit 33 Ω on the clock, SPI SCK/MOSI/MISO and short MCU-side bus TX/RX paths.

| Direction | Channels | Buffered output defaults |
| --- | --- | --- |
| Controller → field | SPI_SCK → ADC_SCLK_FIELD; SPI_MOSI → ADC_MOSI_FIELD; ADC_CS → ADC_CS_FIELD; DO_CS_SEL_L_CMD/H_CMD → DO_CS_SEL_L/H; RS485_TX → RS485_TX_FIELD; CAN_TX → CAN_TX_FIELD; ADC_RESET_N_CMD → ADC_RST_N_FIELD | CS/TX high; clock/data/selection/reset low |
| Field → controller | ADC_MISO_FIELD → SPI_MISO; DI1_FIELD → DI1_TIMER and DI2_FIELD/DI3_FIELD/DI4_FIELD → DI2/DI3/DI4; RS485_RX_FIELD → RS485_RX; CAN_RX_FIELD → CAN_RX; DO_FAULT_N_FIELD → DO_FAULT_N_MCU; AI_V_FAULT_N_FIELD → VOLTAGE_MUX_FAULT_N; AI_I_FAULT_N_FIELD → CURRENT_MUX_FAULT_N | Serial/status high where appropriate; DI/MISO low; field status invalid unless health is valid |

I keep **CROSS_OE_N_FIELD** and **CROSS_OE_N_DIG** separate. Each receives one 10 kΩ pullup only to its own receiving rail. A separate MMBT3904 sinks each OE net: collector pin 3 at OE, emitter pin 2 at MAIN_GND, base pin 1 through 10 kΩ from CROSS_OK with 100 kΩ base-emitter pulldown. The two bases share a command, not their receiving-rail pullups. No OE net links the two rails through resistors. At approximately 0.33 mA collector load and about 0.25 mA base drive, I retain ample forced-base-current margin and qualify saturation and release timing. The transistor collector has no connection to a controller supply clamp.

| CROSS_OK / power | OE and buffer behavior |
| --- | --- |
| CROSS_OK high with valid supplies | Both transistors on, OE low, crossings enabled |
| CROSS_OK low or controller supply absent | Bases discharged; each available receiving rail pulls its OE high, crossings disabled |
| Receiving rail absent | Ioff protects live inputs; no pullup feeds that absent rail from another supply |

I tie unused buffer inputs to ground, disable unused outputs and mark them no-connect. The separately specified loop-status receiver adds one dual buffer, for ten SN74LVC2G125 packages total. Its OE uses HEALTH_READY_N entirely within 3V3_DIG. The analog current diagnostic uses its own DO_CS_ENABLE, divider/clamps and receiving-domain protection. [SN74LVC2G125](https://www.ti.com/lit/ds/symlink/sn74lvc2g125.pdf), [SN74LVC2G08](https://www.ti.com/lit/ds/symlink/sn74lvc2g08.pdf), [SN74LVC2G17](https://www.ti.com/lit/ds/symlink/sn74lvc2g17.pdf)

## Capture and measurement gates

I label test points for every rail, raw/conditioned health, DO_FAULT_OK, CLR_N, ARM_STATE, PERMISSION, CROSS_OK, both crossing OE nets, WDI/WDO/ENOUT, reset, boot and VBUS sense. Low-speed points use accessible plated pads; scope points have adjacent ground access. I compare the captured netlist with these tables, inspect supervisor polarities and the whole permission truth table, and measure simultaneous rail ramps, fault propagation and crossing-transistor release.

During external supply removal I measure VDDA/VREF+, RESET_OK, DO_CS_ENABLE and DO_CS_ADC; conversions stop before analog-supply loss. I require valid conversion inputs between ground and VREF+ and no positive ADC injection. I qualify the STM32 supply-ramp limits and review its silicon REV_ID and [current errata](https://www.st.com/resource/en/errata_sheet/es0430-stm32g471xx473xx474xx483xx484xx-device-errata-stmicroelectronics.pdf). Native capture/ERC and prototype qualification remain pending.
