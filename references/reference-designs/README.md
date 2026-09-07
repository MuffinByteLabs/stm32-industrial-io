# Reference designs

| Design | Used for | Where |
|---|---|---|
| Espressif ESP32-S3-DevKitC-1 schematic v1.1 | The core, reset and USB blocks (same as Board 1) | copy from `ESP32S3_PlantMonitor_RevA/references/reference-designs/` |
| TI LMR38020 EVM (LMR38020QEVM user guide, SNVU817) | The buck's reference layout: input-capacitor placement, SW copper, FB routing, thermal vias | [ti.com/lit/ug/snvu817](https://www.ti.com/lit/ug/snvu817/snvu817.pdf) — fetch before layout |
| Board 1 (ESP32S3_PlantMonitor_RevA) | The USB-C block, the 3.3 V stage, the module footprint, the switch footprint — copied, not redrawn | `../../../ESP32S3_PlantMonitor_RevA/hardware/` |
