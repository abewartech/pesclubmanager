# Stage 11 — CPK TOC Deobfuscation Attempt

## Scope

Static, read-only analysis. Goal: extract `cpk_dat/common/etc/pesdb/Player.bin`
from the patch OBB to feed the Stage 10 parser plan. No binary executed.

## 1. CPK structure (patch OBB)

| Offset | Content |
|---|---|
| `0x00` | `CPK ` magic |
| `0x08` | `0x340` — TOC offset |
| `0x340` | TOC, high-entropy (encrypted/obfuscated, not `@UTF`) |

The file list is not enumerable offline. This confirms the Stage 8
container observation with a precise offset.

## 2. Bind chain (how the game opens it)

- `sys::FileBinder::AttachDpDlcCpk()` (`0x4dd0bdc`) → `BindDpDlcCpk()` (`0x4dcfb5c`)
  → `criFsBinder_BindCpk()` (statically linked CRIWARE) with binder name
  `Def_DataBind_CpkPriorityLowest`, CPK `cpk/dt800_all.cpk`.
- `sys::FileBinder::BindExpansionCpk()` (`0x4dcf0b0`) binds `ExpansionCpk.cpk`.
- `pesdb::Manager::LoadData` then reads via `sys::File::Create("cpk_dat/...")`
  → CRIWARE virtual path. No decryption-key API is called on the bind path;
  TOC decryption (if keyed) happens inside CRIWARE.

## 3. Deobfuscation attempts (all failed = honest negative results)

1. **Simple XOR**: assumed TOC starts `@UTF`, derived 4-byte key
   `73fe7779` — decrypts to garbage after the magic. Not simple XOR.
2. **Known-plaintext attack**: searched 1 MB of TOC for a repeating
   4/8/16/32-byte XOR key yielding `Player.bin`. Only coincidental
   10-byte self-consistent hits (expected false positives). Not XOR.
3. **Content fingerprint**: scanned the full 873 MB for 312-byte
   records with sequential u32 IDs at offset 8 (from
   `GetVectorOfPesdbPlayerData` behavior). Zero hits — file data is not
   plaintext with that layout, or is also encrypted.

## 4. Conclusion

The pesdb data is present in the patch OBB (the game demonstrably reads
`cpk_dat/common/etc/pesdb/Player.bin` through the bound CPK), but both
the TOC **and likely the file data** are encrypted with a non-trivial
scheme. Extracting `Player.bin` requires either:

1. Recovering the CRIWARE content key from the binary (deeper RE of
   `cpkCore_ExecuteServer` / the CPK analyze path), or
2. Runtime extraction on a rooted device (outside this workspace's
   static-only boundary).

This is a hard cryptographic barrier, not a parsing problem. The Stage 10
findings (save system, pesdb format, 312-byte records, import chain)
remain valid and are the foundation for whenever `Player.bin` is obtained.
