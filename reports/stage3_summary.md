# Stage 3 Summary

## OBB

Two OBB files found. Both exist in `original/` (pristine copies) and `jp.konami.pesclubmanager/` (working copies).

| File | Size | Format | Role |
|------|------|--------|------|
| `main.104050101.jp.konami.pesclubmanager.obb` | 789,485,556 bytes (752.9 MB) | ZIP (PK\x03\x04) | Main game assets |
| `patch.104050101.jp.konami.pesclubmanager.obb` | 873,229,528 bytes (832.8 MB) | CRIWARE CPK | Animation/definition data |

OBB naming follows Android convention: `<type>.<versionCode>.<packageName>.obb`

---

## OBB Contents

### Main OBB

Contains exactly **one file**:
```
PesMobile/Content/Paks/PesMobile-Android_ETC1.pak  (789,485,288 bytes)
```

This is an Unreal Engine PAK file using ETC1 texture compression (Android-optimized).

### Patch OBB

CRIWARE CPK container. File listing not accessible — @UTF index tables are XOR-encrypted.
The TOC section is present at offset 0x800. Based on native library strings, the CPK contains
animation and game definition data under a virtual `cpk_dat/` path structure.

---

## Unreal PAK

| Property | Value |
|----------|-------|
| Version | 8 |
| Mount point | `../../../` |
| Index offset | 782,104,571 (0x2E9DF7FB) |
| Index size | 7,380,528 bytes (7.2 MB) |
| Index SHA1 | `ae77755a46d42f792ab89e700542437f068ffb8e` — VERIFIED |
| Total entries | 50,748 |
| Encryption | None detected |

---

## PAK Contents

50,748 assets parsed. Major categories:

| Extension | Approximate Count | Notes |
|-----------|------------------|-------|
| `.uasset` | ~25,000 | Unreal asset headers |
| `.uexp` | ~15,000 | Unreal export data |
| `.png` | ~5,000 | Textures |
| `.ubulk` | ~2,000 | Bulk binary data |
| `.ini` | ~100 | Configuration |
| `.bin` | 2 | Engine shader caches only |

**Notable:** No playerID, datatable, CPK-dat, formation, or ability definition files in the main PAK. It contains only engine/rendering assets and game visual content (characters, UI, stadiums, environments).

---

## CPK

| Property | Value |
|----------|-------|
| Magic | `CPK ` (0x43504B20) |
| SHA-256 | `e6b194d430b7b095e6179645714d5da429e6566205eb7ccde7ea6169505ff1db` |
| Size | 873,229,528 bytes (832.8 MB) |
| TOC offset | 0x0800 |
| ITOC offset | 0x07FF |
| @UTF encryption | YES — XOR with custom key |
| Key bytes (partial) | `5F CB A7 B3` (positions 0–3 of key stream) |
| Key derivation | Unknown — not standard CRIWARE LFSR |
| File listing | NOT ACCESSIBLE without decryption |

---

## PlayerID Tables

### Status: Located (in CPK) — Not Extractable

Evidence from native library (`libUE4.so` / `libafp-core.so`) string analysis confirms:

```
cpk_dat/common/anime/playerID/bin/Definedatatable.bin
cpk_dat/common/anime/playerID/bin/Derivationdatatable.bin
```

These are almost certainly inside `patch.104050101.jp.konami.pesclubmanager.obb` (the CRIWARE CPK),
under the virtual directory `cpk_dat/common/anime/playerID/bin/`.

Confirmed NOT present in the main Unreal PAK.

---

## Binary Format Findings

### Definedatatable.bin / Derivationdatatable.bin

Cannot be directly inspected. Based on:
- Name `Definedatatable` → likely a definition/record table (fixed-size structs)
- Name `Derivationdatatable` → likely a derivation/trait/inheritance table
- Used with `ParameterPlayerDefine` (C++ symbol from Stage 2)
- Path `playerID/bin/` → binary format, not text

**Hypothetical structure** (MEDIUM confidence):
- Binary struct array with header containing: magic, version, record_count, record_stride
- Records indexed by player ID
- Fields correlating with `ParameterPlayerDefine` offsets discovered in Stage 4 analysis

---

## Player Data Leads

```
CPK (patch OBB)
    ↓ cpk_dat/common/anime/playerID/bin/
        ↓ Definedatatable.bin  (player define records)
        ↓ Derivationdatatable.bin  (player derivation/trait records)
            ↓ loaded by libUE4.so
                ↓ tmpdb::Player
                    ↓ ParameterPlayerDefine
                        ↓ in-memory schema (Stage 4)
```

The connection from CPK files to in-memory C++ objects is HYPOTHESIS based on:
1. String evidence from native library (HIGH confidence)
2. C++ symbol naming conventions (MEDIUM confidence)
3. No direct runtime trace (cannot confirm without dynamic analysis)

---

## Important Files

| File | Role | Status |
|------|------|--------|
| `original/main.104050101.jp.konami.pesclubmanager.obb` | Main OBB (ZIP) | Extracted |
| `extracted/obb_main/PesMobile/Content/Paks/PesMobile-Android_ETC1.pak` | Unreal PAK v8 | Index parsed |
| `original/patch.104050101.jp.konami.pesclubmanager.obb` | Patch OBB (CRIWARE CPK) | Header analyzed, content encrypted |
| `analysis/pak_listing/main_pak.txt` | Full PAK file listing (50,748 entries) | Complete |
| `analysis/cpk_listing/patch_cpk_strings.txt` | CPK raw ASCII string scan | Complete |

---

## Important Offsets

| File | Offset | Value |
|------|--------|-------|
| Main OBB PAK | -172 from EOF | Unreal PAK magic `0x5A6F12E1` |
| Main OBB PAK | 782,104,571 | PAK index start |
| Patch OBB | 0x00 | CPK magic `CPK ` |
| Patch OBB | 0x08 | UTF block size field: 832 |
| Patch OBB | 0x10 | Encrypted @UTF (key[0:4]=5F CB A7 B3) |
| Patch OBB | 0x7FF | ITOC section magic |
| Patch OBB | 0x800 | TOC section magic + size 1232 |

---

## Confirmed Findings

1. Main OBB = ZIP → single Unreal PAK v8 containing engine/visual assets only
2. Patch OBB = CRIWARE CPK containing animation/definition data (encrypted headers)
3. Unreal PAK v8 format successfully parsed — 50,748 entries, 0 errors
4. No playerID/datatable files in main PAK
5. CPK @UTF tables are XOR-encrypted; partial key recovered (`5F CB A7 B3`)
6. CPK has TOC at 0x800 and ITOC at 0x7FF
7. `Definedatatable.bin` and `Derivationdatatable.bin` exist in native lib strings pointing to CPK path

---

## Hypotheses

- `Definedatatable.bin` and `Derivationdatatable.bin` are inside `patch.104050101.jp.konami.pesclubmanager.obb` at virtual path `cpk_dat/common/anime/playerID/bin/` (HIGH confidence)
- CPK XOR key is derived from a game-specific key embedded in `libafp-core.so` (MEDIUM confidence)
- Standard CRIWARE CPK decryption tools will not work without the game-specific key (MEDIUM confidence)
- The player data tables use fixed-stride binary struct format (MEDIUM confidence)

---

## Unknowns

- Full CPK XOR key derivation algorithm
- Exact virtual path structure inside patch CPK
- Number of player entries in Definedatatable.bin
- Record stride of player data tables
- Whether ETOC/GTOC sections contain filename information
- Whether `libafp-core.so` initialization code contains the CPK key

---

## Recommended Stage 4

### Priority 1: CPK Decryption Key Recovery

Disassemble `libafp-core.so` (CRIWARE ACE/CRI Ware library) to find the CPK XOR key setup:
- Search for constant `5F CB A7 B3` in binary
- Look for CRIWARE CPK key initialization function (usually named `CriFsServer::Initialize` or similar)
- The key may be hardcoded as a 16-byte or 32-byte array

```powershell
radare2\bin\rabin2.exe -z extracted\apktool\PES-CLUB-MANAGER-v4-5-1\lib\arm64-v8a\libafp-core.so | findstr /I "5fcba7b3"
```

### Priority 2: Alternate Access via Memory

If key extraction fails:
- Use Stage 2 Frida instrumentation to hook CPK open/read calls and dump decrypted file list
- This is dynamic analysis — only possible at runtime

### Priority 3: In-Memory Schema Cross-Reference

Continue Stage 4 work to correlate:
- `ParameterPlayerDefine` field offsets → binary table field mapping
- Player ability codes → CPK table entries
- `tmpdb::Player` struct → CPK player record layout

### Scripts Available

| Script | Purpose |
|--------|---------|
| `scripts/s3_04_pak_reader_v2.py` | Unreal PAK v8 index reader |
| `scripts/s3_05_cpk_inspect.py` | CRIWARE CPK structure parser |
| `scripts/s3_06_cpk_strings.py` | CPK raw string scanner |
| `scripts/inspect_datatable.py` | Binary table read-only inspector |
