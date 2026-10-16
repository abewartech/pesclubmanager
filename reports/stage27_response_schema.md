# Stage 27 — Response Schema per Endpoint

## Scope

User request: map response schemas. Static RE only; server dead since
2021-12-15. Schemas inferred from client-side key strings in `.rodata`.

## 1. Serialization format

The API does NOT use nested JSON for responses. It uses a **flat
key-value** encoding:

```
<key>=<value>&<key>=<value>&...
```

Arrays use a count + indexed-prefix pattern:

```
news_notice_size=2
news_notice_0_isRead=1
news_notice_0_time_recv=1699999999
news_notice_1_isRead=0
news_notice_1_time_recv=1699999998
```

Evidence: adjacent key strings `news_notice_size`, `news_notice_`,
`_isRead`, `_time_recv` at `0x65048c4`.

## 2. `top.php` response keys (inferred)

From `.rodata` @ `0x6504700`:

| Key | Type | Notes |
|-----|------|-------|
| `ms_ver` | int | master-data version |
| `res_ver` | int | resource version |
| `session_id` | string | (in request; echoed/renewed) |
| `user_system_` | prefix | per-user system flags |
| `root_dir` | string | |
| `first_dialog` | int | show first-run dialog |
| `use_facebook` | int | FB integration enabled |
| `trunk` / `stage` / `local` / `mgcheck` | strings | environment markers |
| `asso_approval_check_time` | int | timestamp |
| `asso_new_user_check_time` | int | timestamp |
| `online_cup_count` | int | |
| `contract_quality_player` | int | |
| `isShownRankingPointTutorial` | int | bool |
| `is_show_invitation_code` | int | bool |
| `data_migration_servertime` | int | timestamp |
| `purchase_check` | int | |
| `banner_data_length` | int | |
| `download3DData` | int | bool |
| `_match_status` | int | |

### News arrays

| Array | Count key | Item fields |
|-------|-----------|-------------|
| admin news | `news_admin` | `read` |
| notices | `news_notice_size` | `_isRead`, `_time_recv` |
| news | `news_news_size` | `_time_expire`, `_type`, `_titleParam_size`, `_numParam_size`, `_titleParam`, `_strParam_size`, `_numParam`, `_strParam` |
| friend requests | `news_friendReq_size` | (prefix `news_friendReq_`) |
| friend gifts | `news_friendGift_size` | (prefix `news_friendGift_`) |
| association | `news_asso_size` | `_body`, `_asso_id` |
| (generic) | `news_data_size` | |

## 3. Other endpoints (keys found, schema TBD)

- `team.php`, `event.php`, `loginBonus.php`, `ranking_*`, `scout_*`,
  `campaign_*` — endpoint names confirmed (Stage 23); per-endpoint
  response keys not yet mapped.
- `EditInfo/EditDataList.dat`, `TopMenuData.dat`, `user_news_info.dat`
  — local files the client reads/writes alongside API data.

## 4. Confidence

- **High**: flatKV + `_size` array pattern (multiple corroborating key
  clusters).
- **Medium**: `top.php` key list (keys are real; assignment to
  `top.php` vs other endpoints is inferred from proximity to the
  request template).
- **Low**: exact types, required vs optional, value ranges.

## 5. Next

Dynamic analysis (patched client + stub) is the only way to confirm
schemas. The stub server (Stage 24) should be extended with these
`top.php` keys as the next iteration.
