# Dated procurement evidence

[2026-10-06_key_ic_stock.json](2026-10-06_key_ic_stock.json) records a bounded check of the six exact selected IC ordering codes questioned by the external pre-capture review. Current DigiKey US pages were read directly in Chrome on 6 October 2026. Manufacturer pages establish the distribution channels and the two TI carrier-only alternatives. The JSON was generated at 20:42:41 UTC; individual page-read times were not captured.

| Selected ordering code | Direct DigiKey observation | Packaging-only note |
| --- | --- | --- |
| TPS4H160BQPWPRQ1 | 5,799 in stock | Exact code available in cut tape |
| ISO1212DBQR | 11,539 in stock | Exact code available in cut tape |
| ISO1410DWR | 0; 20-week displayed lead time | ISO1410DW tube: 34 in stock |
| ISO1042DWVR | 0; 20-week displayed lead time | ISO1042DWV tube: 90 in stock |
| UCC33421QDHARQ1 | Available to order; not kept in stock; 26 weeks; full reel of 1,000 | No carrier-only alternative verified |
| STM32G474VET6 | 0; 52-week displayed lead time | STM32G474VET6TR: 0; 52 weeks |

The selected MCU's manufacturer eStore page also indicated out of stock. Regional cached search results disagreed, and a Mouser automated-access overlay limited its current-page verification; those results are not treated as established available inventory. The exact UCC part showed no numeric inventory quantity, so its JSON quantity is `null`, with its displayed availability status preserved.

[TI's authorized-distributor list](https://www.ti.com/ordering-resources/faqs/purchasing-online/authorized-distributors.html) names DigiKey and Mouser. [ST's contacts page](https://www.st.com/content/st_com/en/contact-us.html?sc=contact) names DigiKey, Farnell/Newark/element14 and Mouser as global e-commerce distributors and links its own store. Source URLs and selection-document locations are retained per part in the JSON.

The `AltMPN` entries record carrier changes only. TI identifies ISO1410DW and ISO1042DWV as the same respective devices and packages in tube carriers. ISO1042BDWVR is explicitly excluded because its basic-isolation variant changes the selected device's isolation classification. No active BOM, component choice, symbol, footprint or design contract was changed.

These observations refute a blanket claim that all five challenged ICs have zero authorized stock. They leave a real prototype sourcing constraint for the selected MCU and isolated power module. They do not establish global zero stock, reserve inventory, promise a delivery date or authorize an order. Recheck quantities, carrier requirements and delivery terms before purchase. No raw page archive or screenshot was captured; this record preserves the directly observed numbers, URLs, retrieval method and manufacturer authorization basis.
