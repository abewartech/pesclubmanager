# Stage 12 — pesdb::PlayerData Layout via SetWorkFromPesdb

## Scope

Static, read-only analysis of `tmpdb::PlayerBase::SetWorkFromPesdb`
(`0x4e30398`, 6532 bytes) — the function that imports pesdb records
into the management database. Goal: map the 312-byte record layout.

## 1. Function structure

- Signature: `SetWorkFromPesdb(const pesdb::PlayerData* x1, Kind x2)`, `this` in x0/x3.
- Kind-dispatched via `cbz`/`cmp w2`: targets `0x4e308d0` (Kind 0),
  `0x4e306e0` (Kind 1), `0x4e30b50` (Kind 2/default).
- Only **8 branches** in 6532 bytes — mostly long straight-line conversion code.

## 2. Key finding: only the first ~72 bytes are read

All direct reads from the pesdb pointer (x1):

| Kind | pesdb offsets read | Method |
|---|---|---|
| 0 | `+0x08` – `+0x48` | `LDP` pairs |
| 2 | `+0x20`, `+0x38`, `+0x40` | `LDP` |
| 1 | (none found) | — |

Total: ~72 bytes of the 312-byte record. The remaining **~240 bytes are
never read by this function**.

Only 2 functions in the entire binary take `pesdb::PlayerData*`:
`SetWorkFromPesdb` and `LinkPesdb::SetPlayerData` (which just calls the former).

## 3. Not a field mapper — a converter

- 409 `STR`s to stack temporaries vs 174 `LDR`s from stack.
- LDP-loaded values go to `[sp, ...]`, not directly to tmpdb fields.
- Only 1 `STR` to x3 (this) and 3 to x29 in the whole function.
- Conclusion: the function **computes** tmpdb values from pesdb inputs
  (with conversions, conditionals on Kind), it does not memcpy fields.
  A field-offset table cannot be extracted by simple LDR→STR pairing.

## 4. What this means

- The 312-byte `pesdb::PlayerData` layout is **not recoverable** from
  `SetWorkFromPesdb` alone. The unread ~240 bytes likely serve other
  consumers (match engine, other Kinds) or are padding.
- A complete offline parser requires either the actual `Player.bin`
  data (blocked by Stage 11 CPK encryption) or full decompilation-level
  understanding of the conversion logic.
- Partial result is honest: we know the import entry point, the Kind
  dispatch, and that management import uses only the record header.

## 5. Confirmed reusable facts

- `pesdb::PlayerData` record stride: `0x138` (312) — from
  `GetVectorOfPesdbPlayerData` (`0x4e53bcc`).
- Import chain: `LinkPesdb::ImportPlayer` → `GetVectorOfPesdbPlayerData`
  → `SetPlayerData` → `SetWorkFromPesdb` → `RangeCheckPlayerData`.
