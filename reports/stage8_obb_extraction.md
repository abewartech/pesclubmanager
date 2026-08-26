# Stage 8 — OBB / PAK / CPK Extraction & Player-Data Locating

## Scope

Read-only offline extraction and inventory of the two game containers, followed by a
scan for the 105 `PrepareDataFromJson` player JSON-key markers. No binary was
executed, no server contacted, and `original/` remains pristine.

## Container format (verified)

| File | Magic | Format | Status |
|---|---|---|---|
| `main.104050101...obb` | `PK\x03\x04` | ZIP with **one** stored entry | Extracted |
| `patch.104050101...obb` | `CPK ` (0x43504B20) | CRIWARE CPK | Header TOC obfuscated |

### main OBB (ZIP → UE4 PAK)
The ZIP holds a single, uncompressed entry:

```
PesMobile/Content/Paks/PesMobile-Android_ETC1.pak   789,485,288 bytes
```

Extracted read-only to `extracted/obb_main/...`. The PAK is **unencrypted**
(earlier Stage 3 analysis: "Encryption: None detected").

Parsed via `scripts/s3_04_pak_reader_v2.py`:
- **50,748 entries** (mount point `../../../`), 0 parse errors.
- 49,554 entries live under `PesMobile/Content`.
- Extension mix: 21,355 `.uexp`, 21,345 `.uasset`, 7,232 `.ubulk`, 487 `.res`, 224 `.png`, plus engine/config/audio.

### patch OBB (CRIWARE CPK)
The `@UTF` TOC table is **not** at the standard `0x10` offset — the header is
obfuscated/encrypted, so the file list cannot be enumerated offline.

Scanning the whole file for `@UTF` tables reveals only **CRIWARE ADX2 (ACB/AWB)
audio headers** (table `Header` with `FileIdentifier`, `BusTable`,
`CueLimitWorkTable`, …). The patch CPK is therefore **primarily a sound-bank
container**, not a player-data store. The "49,556 CPK paths" noted in the brief
correspond to this CPK's encrypted file list, which is not recoverable offline
without the obfuscation key.

## Player-record search

1. **Raw OBB byte scan** (earlier Stage 7): 0 occurrences of distinctive keys
   (`serial_id`, `master_id`, `param_shot`, `contract_period`, `rarity`, …) in
   either raw OBB.
2. **PAK asset-name search**: 0 entries named with `parameter` / `define` /
   `datatable` / `tmpdb`. The 70 `player`-named assets are all character
   **visual** assets (`BP_DummyPlayer`, `RealFace/100117_*`, hair/face tables)
   and debug blueprints — not the numeric DB.
3. **Full PAK content scan** — `scripts/s7_03_scan_pak_for_player_keys.py`:
   - 50,708 / 50,748 entries decompressed and scanned for all 105 JSON keys.
   - **0 entries** contained a *distinctive* player key.
   - 25,139 entries matched only *common-word* keys (`age` 21,660, `st` 15,560,
     `name` 9,036, position codes `gk`/`cb`/`cf`…) — substring noise inside UE4
     asset strings.

## Conclusion (preservation-critical)

**The numeric player database (`ParameterPlayerDefine`, 73+ fields) is NOT stored
as static assets inside the shipped offline containers.** The PAK carries engine,
character-visual, and audio assets; the patch CPK carries CRIWARE audio.

The player records are populated at runtime via `PrepareDataFromJson` from a
**JSON source that was server-provided (now dead) or held in local save data not
present in these containers.** This is the key preservation finding: the game's
player data was server-authoritative and is not recoverable from the OBB/PAK/CPK
alone.

The 105-key → field-offset mapping (`analysis/stage6/player_json_key_mapping.json`)
remains the authoritative offline *decoder schema* for player records **once they
are obtained** from a save dump, a server-capture, or memory inspection. It is not
a container format and does not imply on-disk layout.

## Deliverables

| Type | Path |
|---|---|
| Container inventory (PAK) | `analysis/pak_listing/main_pak.txt`, `main_pak_relevant.txt` |
| PAK meta reports | `reports/obb_contents.md`, `reports/pak_inventory.md` |
| Player-key scan script | `scripts/s7_03_scan_pak_for_player_keys.py` |
| Player-key scan result | `analysis/stage7_scan/pak_player_key_hits.json` |
| Player-key scan report | `reports/stage7_pak_player_key_scan.md` |
| Record parser / viewer (for obtained records) | `scripts/s5_01_normalize_player_json.py`, `scripts/s7_01_player_viewer.py` |
| Field-offset schema | `analysis/stage4_player_schema/parameter_player_define_offsets.json` |

## Next read-only steps (if real records are found)

1. Obtain player records from a local save dump or server capture (outside scope here).
2. Run `s5_01` normalizer → `s7_01` viewer, mapping each record to the 105-key schema.
3. Cross-reference against `parameter_player_define_offsets.json` for the in-memory layout.
