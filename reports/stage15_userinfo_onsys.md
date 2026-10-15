# Stage 15 — UserInfoData.dat & OnSysData.dat Schemas

## Scope

Same method as Stage 14, applied to the remaining `sys::SaveData`
loaders named in Stage 13 §3: `LoadUserInfoData` (`0x4db63a4`) and
`LoadOnsysData` (`0x4dbc064`). Static, read-only arm64 disassembly of
`libUE4.so`; PLT resolved via `R_AARCH64_JUMP_SLOT`; strings via
ADRP+ADD xref to `.rodata`.

## 1. Both files are JSON too

Both loaders call `Json::Value::resolveReference(key, false)` — the same
jsoncpp pattern as `LoadSystemData` (Stage 14). No `fread`-style binary
parsing. All three `sys::SaveData` files are JSON objects.

## 2. UserInfoData.dat — identity schema

Loader: `sys::SaveData::LoadUserInfoData` (`0x4db63a4`).

| Key | Reads |
|---|---|
| `auth_code` | 2× `resolveReference` |
| `user_code` | 3× `resolveReference` |
| `user_id` | 3× `resolveReference` |
| `account_status` | referenced (Json::Value key construction at `0x4db6a10`; full read path not traced) |

Interpretation: local identity/auth cache — the codes the client presents
at sign-in (`GetAuthCode` / `GetUserId` / `GetUserCode` accessors exist in
the same namespace). String-valued; exact types/defaults not traced.

## 3. OnSysData.dat — multiplayer stats upload queue

Loader: `sys::SaveData::LoadOnsysData` (`0x4dbc064`).

| Key | Reads |
|---|---|
| `multi_stats_wait_upload_flag` | 2× `resolveReference` |
| `match_id` | 2× `resolveReference` |
| `pid` | 2× `resolveReference` |
| `peer_pid` | 2× `resolveReference` |
| `multi_stats_data` | 3× `resolveReference` |

Interpretation: pending multiplayer-stats upload — a flag plus one match
record (`match_id`, local/peer player ids, stats payload). Consistent
with the `SaveMultiplayStats` / `GetMultiplayStatsWaitUploadFlag`
accessors in `sys::SaveData`. The "upload later" design explains why
this file exists separately from the online API structs.

## 4. Consolidated save-file map (Stages 13–15)

| File | Loader | Format | Keys |
|---|---|---|---|
| `SystemData.dat` | `LoadSystemData` `0x4db1508` | JSON | `SystemDataVersion`, `text_language`, `sound_language`, `vibration` |
| `UserInfoData.dat` | `LoadUserInfoData` `0x4db63a4` | JSON | `auth_code`, `user_code`, `user_id`, (`account_status`) |
| `OnSysData.dat` | `LoadOnsysData` `0x4dbc064` | JSON | `multi_stats_wait_upload_flag`, `match_id`, `pid`, `peer_pid`, `multi_stats_data` |
| `InterruptGameFile.dat` | `tmpdb::InterruptGameInfo` | Blowfish+MD5 | (Stage 13; deprioritized) |

## 5. Caveats

- Per-key value types, defaults, and version gating were traced in full
  only for `SystemData.dat` (Stage 14); here only key presence and read
  counts are verified.
- `account_status`'s read path is partially traced (key materialized as
  a `Json::Value` at `0x4db6a10`, consumer not identified).
- No real save files available to validate against; claims rest on
  static disassembly only.
