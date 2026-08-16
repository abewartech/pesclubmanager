# PlayerID Tables Analysis

## Summary

Search was performed for:
- `Derivationdatatable.bin`
- `Definedatatable.bin`
- Variants: `*Derivation*`, `*Define*`, `*datatable*`, `*playerID*`
- Directory paths: `cpk_dat/common/anime/playerID/bin/`

## Search Scope

| Container | Format | Searchable? | Result |
|-----------|--------|-------------|--------|
| main OBB | ZIP → Unreal PAK v8 | YES (50,748 entries indexed) | Not found |
| patch OBB | CRIWARE CPK | PARTIALLY (headers encrypted) | Cannot confirm |

## Main PAK Search Results

The Unreal PAK index was fully parsed (50,748 entries). The following searches returned no results:

- `Derivationdatatable` → 0 matches
- `Definedatatable` → 0 matches
- `datatable` → 0 matches (case-insensitive)
- `playerid` → 0 matches (case-insensitive)
- `cpk_dat` → 0 matches
- `*.bin` (game-specific) → Only 2 matches: engine shader caches
- `*.dat` → 0 matches

**Conclusion:** `Definedatatable.bin` and `Derivationdatatable.bin` are NOT in the main OBB/PAK.

## CPK Search Results

The CRIWARE CPK (patch OBB) contains encrypted @UTF index tables. The file listing
cannot be retrieved without the decryption key. However:

- String scanning of the raw CPK payload found **5,237** keyword matches
- All matches traced to **Adobe XMP metadata** embedded in PNG texture files
- No path strings like `cpk_dat/`, `playerID/`, `Definedatatable.bin` found as raw ASCII
- The actual file table (TOC) is encrypted

**Conclusion:** Cannot confirm or deny presence of datatable files in patch OBB without CPK decryption.

## Evidence from Native Symbol Analysis (Stage 2)

From prior Stage 2 native library analysis (`libUE4.so` / `libafp-core.so`), the following strings
were found:

```
Derivationdatatable.bin
Definedatatable.bin
cpk_dat/common/anime/playerID/bin/
```

This confirms these files **exist at runtime** and are loaded from the CPK. The most likely location is:

```
patch.104050101.jp.konami.pesclubmanager.obb
  └── CRIWARE CPK
        └── cpk_dat/common/anime/playerID/bin/
              ├── Definedatatable.bin
              └── Derivationdatatable.bin
```

## Binary Table Analysis

Since the files are inside the encrypted CPK and cannot be extracted read-only,
binary analysis of `Definedatatable.bin` and `Derivationdatatable.bin` was not possible
in this stage.

### Known from Native Symbol Context

From `libUE4.so` string analysis (Stage 2):

| Symbol | Context |
|--------|---------|
| `Definedatatable.bin` | Loaded by `tmpdb::Player` or `ParameterPlayerDefine` initializer |
| `Derivationdatatable.bin` | Loaded alongside define table; likely derivation/trait system |
| `cpk_dat/common/anime/playerID/bin/` | CPK virtual path prefix |

### Hypothetical Format

Based on native C++ symbols and PES series datatable conventions:

| Field | Hypothesis | Confidence |
|-------|-----------|------------|
| Format | Binary struct array | MEDIUM |
| Endianness | Little-endian (ARM Android) | HIGH |
| Header | Magic + version + count + stride | MEDIUM |
| Record fields | Player ID (uint32), Ability fields (uint16/uint8), Name offset (uint32 → string table) | MEDIUM |
| String table | Appended after record array | LOW |

These are hypotheses — no direct evidence until decryption succeeds.

## Next Steps

1. Decrypt CPK `@UTF` tables using key extracted from `libafp-core.so`
2. Extract `cpk_dat/common/anime/playerID/bin/` virtual directory
3. Run `python scripts/inspect_datatable.py Definedatatable.bin`
4. Cross-reference with Stage 4 player offset schema

## inspect_datatable.py

The read-only binary inspector is available:

```powershell
python scripts\inspect_datatable.py path\to\Definedatatable.bin
```

Outputs:
- File metadata (path, size, SHA-256)
- Magic bytes identification
- Hex dump (first 128 bytes)
- ASCII string scan
- UTF-16LE string scan
- Sequential integer array detection (candidate record IDs)
- Repeating-stride pattern analysis (candidate record size)
- Binary table header heuristics (count × stride ≈ file_size)
