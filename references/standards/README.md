# Standards and qualification references

This board is an indoor low-voltage prototype. No standard compliance or certification has been established. The [canonical plan](../../docs/STM32_Industrial_IO_Controller_RevA_Plan.md) defines the engineering tests to complete; the final product application determines which formal requirements apply.

Consult current primary publications and qualified test support when needed. Do not derive universal creepage, clearance, trace width, surge levels, or assembly acceptance from a copied quick-sheet.

| Reference family | Use during implementation |
| --- | --- |
| IPC-2221 and relevant sectional standards | General PCB design decisions, interpreted with the actual materials and application |
| IPC-2152 | Current-carrying conductor thermal design alongside actual stack-up and measurements |
| IPC-7351 or package-specific manufacturer land patterns | Surface-mount geometry; exact package drawings take priority in part verification |
| IPC-A-610 and J-STD-001 | Agreed assembly/workmanship criteria and process requirements |
| J-STD-020 and J-STD-033 | Part-specific reflow/moisture handling requirements |
| IEC 61131-2 | Reference for industrial-controller I/O behavior where applicable; isolated input IC ratings do not establish board compliance |
| Applicable IEC 61000-4 immunity methods | Define specific ESD/EFT/surge fixtures and acceptance criteria when relevant to the intended application |
| Applicable emissions regulations and test standards | Plan later EMC work for the actual equipment, cables, enclosure, and jurisdiction |

Useful primary entry points: [IPC standards](https://www.ipc.org/standards), [IEC publications](https://webstore.iec.ch/), and the [Modbus Organization specifications](https://www.modbus.org/modbus-specifications).

Maintain a dated test plan that identifies edition, setup, waveform, source impedance, coupling, cables, severity, monitoring, pass criteria, and results for each test. The analog ±30 V miswire goal is separate from an IEC surge/EFT claim. The CAN transceiver's grade does not establish automotive qualification.
