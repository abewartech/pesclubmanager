# Stage 18 — Save (Write) Path Confirms JSON Round-Trip

## Scope

Closes the Stage 17 caveat ("write-path builders not traced; assumed
symmetric"). Traced the `sys::SaveData` write functions that persist the
three JSON save files. Static, read-only arm64 disassembly of
`libUE4.so`; strings via ADRP+ADD xref to `.rodata`.

## 1. Writes use the same keys as loads

| Function | VA | Writes to | JSON keys written |
|---|---|---|---|
| `SaveLanguage` | `0x4db2b4c` | `SystemData.dat` | `text_language`, `sound_language` (also refs `vibration` — whole-object rewrite) |
| `SaveVibration` | `0x4db2e78` | `SystemData.dat` | `vibration` |
| `SaveUserInfoData` | `0x4db63c0` | `UserInfoData.dat` | `auth_code`, `user_code`, `user_id` |
| `SaveMultiplayStats` | `0x4dbc564` | `OnSysData.dat` | `multi_stats_data` |

Every key the loaders read (Stages 14–15) is written by the matching
saver. Round-trip confirmed: no hidden keys, no binary side-channel.

## 2. Notes

- `SaveLanguage` references `vibration` too: the saver rewrites the
  whole `SystemData.dat` object, not just the changed key. The Stage 16
  parser's unknown-key tolerance matches this (extra keys survive).
- `SaveVibration` also references `first_notification_permission`
  (unrelated key handled in the same call flow; not traced further).
- `SaveMultiplayStats` validates its input against a `WESYS` marker:
  strncmp-like compare of 5 bytes at input+3 (`0x4dbc910`). Exact
  semantics not fully traced; likely a payload magic check.

## 3. Caveats

- Only key presence was verified on the write path, not value
  encoding or write ordering.
- `WESYS` marker semantics are inferred from the compare pattern,
  not fully traced.
