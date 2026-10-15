# Stage 13 — Save-File Encryption Scheme

## Scope

Static, read-only analysis. Goal: determine which save files are encrypted
and how, to assess offline save-parsing feasibility.

## 1. Blowfish encryption (InterruptGameInfo only)

`tmpdb::InterruptGameInfo::SaveEncryptedGameFile` (`0x4e28140`, 1040 bytes)
and `LoadEncryptedGameFile` (`0x4e28550`, 1272 bytes) use:

- `blowfish::CBlowFish::Initialize(uint8_t*)` (`0x4e282e4`)
- `blowfish::CBlowFish::Encode(uint8_t*, uint8_t*, uint)` (`0x4e28324`)
- `md5_append` / `md5_finish` (integrity / key-derivation input)

Key findings:

- **Cipher: Blowfish** (not AES, not XOR). Well-understood; decryptable
  if the key is recovered.
- **Key is derived, not hardcoded**: 16 bytes built on the stack as
  `[x8 (8B) | 0x3b9aca00 (4B) | w22 (4B)]`, where `x8` comes from an
  `madd` over MD5-context data and `w22` is a length field from the
  object. The key is per-file, derived from the content being saved.
- File is written via `fopen`/`fwrite`/`fclose` (standard C I/O).

## 2. SystemData.dat is NOT encrypted

`sys::SaveData::LoadSystemData` (`0x4db1508`, 1456 bytes) contains **zero**
calls to blowfish/md5/crypto routines. It uses plain file I/O.

Implication: `SystemData.dat`, `UserInfoData.dat`, `OnSysData.dat` (all
handled by `sys::SaveData`) are stored **unencrypted**. Only the interrupt
save (`InterruptGameFile.dat` via `tmpdb::InterruptGameInfo`) uses Blowfish.

## 3. What this means for offline parsing

- System/user save files: parseable with plain binary parsing once the
  format is mapped. No crypto barrier.
- Interrupt save: Blowfish with per-file derived key. Decryption requires
  fully reversing the key-derivation arithmetic (MD5 input selection +
  `madd` chain). Feasible but non-trivial; deprioritized since interrupt
  saves are transient match-state, not player-database data.

## 4. Reusable facts

| Function | Address | Crypto |
|---|---|---|
| `SaveEncryptedGameFile` | `0x4e28140` | Blowfish + MD5 |
| `LoadEncryptedGameFile` | `0x4e28550` | Blowfish + MD5 |
| `sys::SaveData::LoadSystemData` | `0x4db1508` | none (plain) |
| `blowfish::CBlowFish::Initialize` | (via `0x4e282e4`) | — |
| `blowfish::CBlowFish::Encode` | (via `0x4e28324`) | — |
