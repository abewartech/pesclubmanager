# Stage 7.3 PAK Player-Key Scan

**PAK:** `extracted/obb_main/PesMobile/Content/Paks/PesMobile-Android_ETC1.pak`

**Entries parsed:** 50,748

**Entries scanned (decompressed):** 50,708

**Entries with >=1 player JSON key:** 25139

**Entries with DISTINCTIVE keys:** 0

## Distinctive-key occurrence tally

| key | occurrences |
|---|---:|
| `contract_period` | 0 |
| `market_value` | 0 |
| `master_id` | 0 |
| `motivation_value` | 0 |
| `original_team_id` | 0 |
| `param_shot` | 0 |
| `rarity` | 0 |
| `record_goal_total` | 0 |
| `sell_price` | 0 |
| `serial_id` | 0 |
| `uniform_number` | 0 |

## Interpretation

- No entry contained a distinctive player JSON key (`serial_id`, `master_id`, `param_shot`, etc.).
- The numeric player DB (`ParameterPlayerDefine`) is **not** stored as static JSON assets in this PAK.
- Player records are populated at runtime via `PrepareDataFromJson`, sourced from the (now dead) server or local save data not present in the offline containers.
