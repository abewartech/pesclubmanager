# Stage 16 — Offline Save-File Parser

## Scope

First constructive deliverable from the save-format work (Stages
13–15): a read-only parser/validator for the three JSON save files.
No binary parsing is needed (Stage 14); this tool turns the mapped
schemas into something runnable.

Script: `scripts/s16_01_parse_saves.py`

## What it does

- Reads `SystemData.dat`, `UserInfoData.dat`, `OnSysData.dat` (files or
  a directory of `.dat` files).
- Validates each against the native loader schema:
  - `SystemData.dat`: `SystemDataVersion` int; `text_language` /
    `sound_language` int clamped 0–14 (Stage 14); `vibration` bool/int.
  - `UserInfoData.dat`: `auth_code`, `user_code`, `user_id` strings;
    `account_status` str/int (Stage 15).
  - `OnSysData.dat`: `multi_stats_wait_upload_flag` bool/int;
    `match_id`, `pid`, `peer_pid` str/int; `multi_stats_data`
    dict/list/str (Stage 15).
- Mirrors loader tolerance: unknown keys are reported, not rejected;
  missing keys report the loader default where documented.
- Exit code 0 = clean, 2 = warnings, 1 = no files / unreadable.

## Verification

Synthetic fixtures (no real save files exist to test against):

- Valid files for all three schemas → `OK: matches native schema`.
- Unknown key → `warn: unknown key ... (loader ignores it)`.
- Missing `account_status` → `warn: missing key ... (no documented default)`.
- `text_language: 99` → `warn: ... out of loader range 0-14`.
- Malformed JSON → `not valid JSON` error, keys `None`.

## Caveats

- Schemas rest on static analysis (Stages 14–15); unvalidated against
  real device saves.
- `account_status` read path was only partially traced; its schema entry
  is the most likely to need revision once a real file is seen.
- Interrupt saves (`InterruptGameFile.dat`, Blowfish) remain out of
  scope per Stage 13.
