# Stage 3 Evidence Report

## E001

**Finding:** Main OBB is a ZIP-compatible container

**Source:** Magic byte detection via Python `struct.unpack`

**File:** `original/main.104050101.jp.konami.pesclubmanager.obb`

**Offset:** 0x00 (file start)

**Evidence:** Bytes at offset 0: `50 4B 03 04` = `PK\x03\x04` — standard ZIP local file header signature

**Confidence:** HIGH — ZIP magic is unambiguous

---

## E002

**Finding:** Main OBB contains exactly one file: `PesMobile-Android_ETC1.pak`

**Source:** 7z extraction + directory walk

**File:** `extracted/obb_main/`

**Offset:** N/A

**Evidence:** 7z returned exit code 0. `os.walk` of `extracted/obb_main/` found exactly 1 file:
`PesMobile/Content/Paks/PesMobile-Android_ETC1.pak` (789,485,288 bytes)

**Confidence:** HIGH — extraction verified

---

## E003

**Finding:** `PesMobile-Android_ETC1.pak` is an Unreal Engine PAK v8

**Source:** Magic byte scan + footer parse (`scripts/s3_04_pak_reader_v2.py`)

**File:** `extracted/obb_main/PesMobile/Content/Paks/PesMobile-Android_ETC1.pak`

**Offset:** Bytes at offset `-172` from EOF

**Evidence:**
- Magic: `E1 12 6F 5A` (little-endian `0x5A6F12E1`) — Unreal PAK signature confirmed
- Version: `8`
- Index offset: `782,104,571`
- Index size: `7,380,528`
- Index SHA1 hash: `ae77755a46d42f792ab89e700542437f068ffb8e` — verified match

**Confidence:** HIGH — both magic and SHA1 index integrity confirmed

---

## E004

**Finding:** Main PAK contains 50,748 asset entries; no playerID/datatable/CPK paths

**Source:** Index parse (`scripts/s3_04_pak_reader_v2.py`)

**File:** `analysis/pak_listing/main_pak.txt`

**Offset:** PAK index at file offset 782,104,571

**Evidence:**
- 50,748 entries parsed with 0 errors
- Mount point: `../../../`
- Extension distribution: `.uasset` (dominant), `.uexp`, `.ubulk`, `.png`, `.ini`
- Search for: `DataTable`, `playerid`, `cpk_dat`, `Derivation`, `Define` → 0 hits
- Only `.bin` files: engine shader caches (`GlobalShaderCache-GLSL_ES2.bin`, `GlobalShaderCache-GLSL_ES3_1_ANDROID.bin`)

**Confidence:** HIGH — full index parsed and verified

---

## E005

**Finding:** Patch OBB is a CRIWARE CPK container

**Source:** Magic byte detection

**File:** `original/patch.104050101.jp.konami.pesclubmanager.obb`

**Offset:** 0x00

**Evidence:** Bytes at offset 0: `43 50 4B 20` = `CPK ` — CRIWARE CPK magic

**Confidence:** HIGH — CRIWARE CPK magic is unambiguous

---

## E006

**Finding:** CPK @UTF index tables are XOR-encrypted with a custom key

**Source:** Binary analysis (`scripts/s3_debug_cpk*.py`)

**File:** `original/patch.104050101.jp.konami.pesclubmanager.obb`

**Offset:** 0x10 (CPK header UTF), 0x810 (TOC UTF)

**Evidence:**
- Expected bytes at 0x10: `40 55 54 46` (`@UTF`)
- Actual bytes at 0x10: `1F 9E F3 F5`
- Recovered key bytes 0-3: `5F CB A7 B3` (via XOR of expected vs actual)
- Same key stream applies at 0x810 (TOC UTC table)
- Standard CRIWARE LFSR (`seed * 0x4E6F + 0x5D`) with all candidate seeds → no `@UTF` recovery
- Period-4 key produces `@UTF` magic but yields implausible header values
- Period-8 key: no plausible `@UTF` structure found

**Confidence:** HIGH (encryption confirmed) / LOW (key derivation algorithm unknown)

---

## E007

**Finding:** CPK structure has ITOC at 0x7FF, TOC at 0x800

**Source:** Magic scan

**File:** `original/patch.104050101.jp.konami.pesclubmanager.obb`

**Offset:** 0x7FF (`ITOC`), 0x800 (`TOC `)

**Evidence:**
```
0x07FF: 49 54 4F 43 = 'ITOC'
0x0800: 54 4F 43 20 = 'TOC '
0x0808: D0 04 00 00 00 00 00 00 = 1232 (TOC data size field)
```

**Confidence:** HIGH — exact magic byte match

---

## E008

**Finding:** `Definedatatable.bin` and `Derivationdatatable.bin` path strings present in native library

**Source:** Stage 2 `libUE4.so` / `libafp-core.so` string analysis

**File:** `extracted/apktool/PES-CLUB-MANAGER-v4-5-1/lib/arm64-v8a/libUE4.so`

**Offset:** Various (string table)

**Evidence:** Strings found in prior stage analysis:
- `Derivationdatatable.bin`
- `Definedatatable.bin`
- `cpk_dat/common/anime/playerID/bin/`

**Confidence:** HIGH (strings confirmed in binary) — location within patch CPK is HYPOTHESIS

---

## E009

**Finding:** SHA-256 fingerprints of both OBBs

**Source:** `scripts/s3_01_obb_inventory.py`

**File:** Both OBBs

**Offset:** Full file hash

**Evidence:**
- Main OBB SHA-256: *(computed during s3_01 run — see obb_inventory.md)*
- Patch OBB SHA-256: `e6b194d430b7b095e6179645714d5da429e6566205eb7ccde7ea6169505ff1db`

**Confidence:** HIGH — cryptographic hash

---

## E010

**Finding:** PAK mount point is `../../../` (Unreal Engine relative path convention)

**Source:** PAK index parse

**File:** PAK v8 index

**Offset:** First FString in index data (782,104,571 + 0)

**Evidence:** FString at index start = `../../../\x00` (length 10, UTF-8 with null terminator)

**Confidence:** HIGH — direct read from verified index
