# Standards and qualification references

I am designing an indoor low-voltage prototype. I have not established standards compliance or certification. My [validation plan](../../docs/Validation.md) defines the engineering evidence I intend to collect; the final product application determines which formal requirements apply.

I will consult current primary publications and qualified test support for application-specific requirements. Creepage, clearance, trace width, surge severity, and assembly acceptance depend on the materials, installation, and agreed test conditions.

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

For each formal test, I will record the edition, setup, waveform, source impedance, coupling, cables, severity, monitoring, pass criteria, and results. My ±30 V analog miswire target is separate from an IEC surge/EFT claim. The CAN transceiver's grade does not establish automotive qualification for this board.
