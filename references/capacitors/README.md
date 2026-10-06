# Murata capacitor characteristic exports

These six verified manufacturer CSVs are the canonical saved exports from the pre-schematic retrieval. Duplicate temporary copies and extracted text were removed after hash comparison. `manifest.json` records SHA-256, source URL, manufacturer headers, retrieval date, and curve/sample conditions.

Source: [Murata SimSurfing, exact GRM31CR71E106KA12L selection](https://ds.murata.com/simsurfing/mlcc.html?oripartnumbers=%5B%22GRM31CR71E106KA12L%22%5D&partnumbers=%5B%22GRM31CR71E106KA12%22%5D&rgear=zzo&rgearinfo=com). The requested full part has packing suffix **L**; the exported electrical model stem is **GRM31CR71E106KA12**. The viewer showed update 10/2/2026. Retrieval was 2026-10-04 local time; the CSV-generated date is 2026/10/05.

| CSV | Export condition |
| --- | --- |
| `GRM31CR71E106KA12_bias_25C_1Vrms.csv` | DC-bias percentage change at 25 °C / 1 Vrms |
| `GRM31CR71E106KA12_bias_0C_0p01Vrms.csv` | Absolute capacitance versus DC bias at 0 °C / 0.01 Vrms |
| `GRM31CR71E106KA12_bias_25C_0p01Vrms.csv` | Absolute capacitance versus DC bias at 25 °C / 0.01 Vrms |
| `GRM31CR71E106KA12_bias_50C_0p01Vrms.csv` | Absolute capacitance versus DC bias at 50 °C / 0.01 Vrms |
| `GRM31CR71E106KA12_temp_3p4V_0p01Vrms.csv` | Absolute capacitance versus temperature at 3.4 V DC / 0.01 Vrms |
| `GRM31CR71E106KA12_temp_5p25V_0p01Vrms.csv` | Absolute capacitance versus temperature at 5.25 V DC / 0.01 Vrms |

Each temperature export has 101 samples from 0–50 °C in 0.5 °C steps. Sampled typical ranges are **6.16848–7.55285 µF at 3.4 V** and **5.68285–6.66015 µF at 5.25 V**, with both minima at the 0 °C sample. This is useful screening evidence against the 2.2 µF LDO-output and 4.7 µF input requirements.

These are **typical characteristic/model data**, not approval-sheet guaranteed minima, production-lot bounds or hardware measurements. The exports do not establish aging, worst production tolerance, actual application ripple behavior or guaranteed behavior between model samples. No assumed 5% aging factor is treated as proof. All formal capacitor evidence gates remain OPEN. [Murata measurement conditions](https://ds.murata.com/simsurfing_data/pdf/en-us/mlcc/sim_mlcc_measuringcond_e.pdf) describe the measurement preparation; no local PDF was successfully archived in this pass.

Later exact-model graph/export attempts stalled. This archive makes no numeric retention claim for GRM32ER71E226KE15L, GRT31CR71H225KE13L, GRM32ER71H106KA12L or Würth 885382209002. No curve from another part was substituted.
