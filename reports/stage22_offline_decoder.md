# Stage 22 — Offline WesysData Decoder

## Scope

"Offline mode" milestone: turn the Stage 21 format recovery into a
working offline decoder for `multi_stats_data`. Script:
`scripts/s22_01_decode_wesysdata.py`. Read-only; tested against
synthetic payloads (raw, zip, xorshift-flagged).

## 1. What the decoder does

- Accepts raw binary, hex, or base64 input, or extracts
  `multi_stats_data` directly from an `OnSysData.dat` JSON file
  (`--from-json`).
- Validates the 16-byte header: `"WESYS"` magic at offset 3 (mirrors
  `sys::WesysData::IsValid`'s length + magic gate).
- Parses flags (byte 2: bit0 = zip, bit1 = xorshift), stored size,
  original size.
- Decompresses zlib payloads (tries zlib wrapper, falls back to raw
  deflate) and checks the output length against the header's
  original size.

## 2. Verified behavior

| Input | Result |
|---|---|
| Raw payload (flags=0) | Decoded, byte-exact; rc=0 |
| Zip-compressed (flags=1) | Decompressed via zlib; length matches header; rc=0 |
| Xorshift-flagged (flags=2) | Header parsed; payload returned as-is with warning; rc=2 |

## 3. Known gap

The xorshift decryption routine was not recovered from the binary
(no xorshift32 instruction pattern found; no direct callers of the
`WesysData` methods via `bl`). Payloads with the xorshift flag set
cannot be decrypted offline yet. The decoder reports them honestly
instead of guessing.

## 4. Offline-mode status

- ✅ Parse the three JSON save files (Stage 16).
- ✅ Validate + decode WesysData header (Stages 20–22).
- ✅ Decompress zip payloads (Stage 22).
- ❌ Decrypt xorshift payloads (routine untraced).
- ❌ Real-device save files not yet tested (no samples available
  offline).

The remaining work is tracing the xorshift routine (likely near the
`WesysData` vtable users or the `.bin` write path) and testing
against real save data.
