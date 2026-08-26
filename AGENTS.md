# AI Agent Handoff

This workspace is for offline, read-only reverse engineering of PES Club Manager Android assets and native symbols.

## Safety Rules

- Do not contact, probe, fuzz, scrape, authenticate to, or test production servers.
- Do not patch APK, OBB, PAK, CPK, native libraries, or save files unless the user explicitly starts a later editor/patching stage.
- Treat current work as static/offline analysis only.
- Keep source artifacts under `original/` pristine.
- Write derived data only under `analysis/`, `reports/`, `docs/`, or new purpose-specific tooling under `scripts/`.
- Preserve unknown fields instead of inventing semantics.

## Current Goal

Recover enough offline player data structure to build a read-only player database/parser first. Editing comes only after the format is proven.

Target pipeline:

```text
OBB -> PAK -> CPK -> Player data -> Save/local data -> Player structure -> Offline parser -> Viewer -> Editor
```

Current stage:

```text
Stage 6: read-only cross-reference between normalized player data and native evidence
```

## Important Findings

- Main binary target: `libUE4.so`.
- Engine: Unreal Engine 4.22.3.
- Strong native model lead: `tmpdb::Player`.
- Main player accessor lead: `onlinemode::ParameterPlayerDefine`.
- Team relation lead: `ParameterTeam`.
- Local/save leads: `sys::SaveData` and `systemdata::SystemData`.
- Native strings mention CPK paths around `playerID`, but those player table files have not yet been confirmed in extracted containers.

## Key Evidence Files

- `reports/native_analysis.md`
- `reports/stage3_asset_path_inventory.md`
- `reports/stage4_player_symbol_schema.md`
- `reports/stage4_player_offset_schema.md`
- `reports/stage4_player_json_keys.md`
- `reports/stage4_player_key_offset_map.md`
- `reports/stage5_player_json_normalizer.md`
- `reports/stage6_player_cross_reference.md`
- `analysis/stage4_player_schema/player_json_key_offset_map.json`
- `analysis/stage5_player_json/normalized_players.json`
- `analysis/stage6_player_cross_reference/player_field_coverage.json`

## Main Scripts

- `scripts/s3_03_asset_path_inventory.py`
  - Scans PAK/CPK binaries for embedded asset paths.
- `scripts/s4_01_player_symbol_schema.py`
  - Extracts player-related native symbol candidates from `libUE4` exports.
- `scripts/s4_02_extract_player_offsets.py`
  - Uses radare2 disassembly to recover `ParameterPlayerDefine` backing-struct field offsets.
- `scripts/s4_03_extract_player_json_keys.py`
  - Extracts JSON key string literals from player JSON preparation functions.
- `scripts/s4_04_correlate_json_keys_offsets.py`
  - Maps JSON keys to native field candidates and offsets.
- `scripts/s5_01_normalize_player_json.py`
  - Read-only normalizer for local player-shaped JSON.
- `scripts/s6_01_cross_reference_player_schema.py`
  - Read-only cross-reference validator for normalized player fields and native key/offset evidence.

## Stage 5 Usage

Run the fixture:

```powershell
python .\scripts\s5_01_normalize_player_json.py .\analysis\stage5_player_json\fixtures\sample_players.json --output .\analysis\stage5_player_json\normalized_players.json
```

Expected output:

```text
Scanned files: 1
Player records: 2
```

Run on a directory of offline JSON files:

```powershell
python .\scripts\s5_01_normalize_player_json.py .\path\to\offline_json_dir --output .\analysis\stage5_player_json\normalized_players.json
```

The normalizer emits:

- `identity`
- `profile`
- `team`
- `contract`
- `abilities`
- `skills`
- `positions`
- `records`
- `raw_unmapped`
- `native_evidence`
- `provenance`

## Stage 6 Usage

Run the cross-reference validator:

```powershell
python .\scripts\s6_01_cross_reference_player_schema.py
```

Expected fixture-baseline output:

```text
Player records: 2
Observed keys: 18
Observed with offsets: 9
Observed without offsets: 8
Observed unmapped: 1
Native unobserved: 88
```

The main output buckets are:

- `observed_with_offset`
- `observed_without_offset`
- `observed_unmapped`
- `native_unobserved`

## High-Confidence Native Offsets

Examples from Stage 4:

- `PlayerId` / `Id`: `0x2c`, `u64`
- `SerialId`: `0x1c8`, `u64`
- `MasterId`: `0x1d0`, `u64`
- `Name`: `0x38`, pointer/address reference
- `Age`: bitfield around `0x18` / `0x1c`
- `OriginalTeamId`: `0xdc`, `u32`
- `MarketValue`: `0x1a0`, `u64`
- `SellPrice`: `0x1a8`, `u32`
- `Salary`: `0x1e8`, `u32`
- `NextSalary`: `0x1ec`, `u32`
- `ContractPeriodMax`: `0x1dc`, `u32`
- `ContractPeriod`: `0x1e0`, `u32`
- `ContractPeriodRequest`: `0x1e4`, `u32`
- `ContractSalary`: `0x1f0`, `u32`
- `ContractStatus`: `0x210`, `u32`
- `Rarity`: `0x1c0`, `u32`
- `UniformNumber`: `0x1ac`, `u32`
- `MotivationValue`: `0x20c`, `u32`

Always check `reports/stage4_player_offset_schema.md` and `analysis/stage4_player_schema/parameter_player_define_offsets.json` before relying on an offset.

## Known Caveats

- Exact player file format in OBB/PAK/CPK is not proven yet.
- `ParameterPlayerDefine` offsets are in-memory backing-struct offsets, not automatically file offsets.
- Some mappings are medium confidence and need validation through call tracing or real offline data.
- Stage 5 currently normalizes JSON-like records only. It is not a binary CPK/PAK table parser.
- Git may fail with `dubious ownership` in this workspace. Do not change global git config without user approval.

## Stage 6.2 Usage

Static JSON-key -> native-field setter/accessor correlation (read-only).

```powershell
python .\scripts\s6_02_trace_json_key_setters.py
```

Outputs under `analysis/stage6/`:
- `player_json_key_mapping.json` (105 keys; 97 with candidates)
- `mapping_confidence_report.csv`
- `new_fields_candidates.json` (native-only field candidates)
- `prepare_data_from_json_address.txt`
- `reports/stage6_json_key_mapping_report.md`

## Stage 7 Usage

Read-only offline viewer over Stage 5 normalized players.

```powershell
python .\scripts\s7_01_player_viewer.py
python .\scripts\s7_01_player_viewer.py --mapping .\analysis\stage6\player_json_key_mapping.json
python .\scripts\s7_01_player_viewer.py --mapping .\analysis\stage6\player_json_key_mapping.json --csv-output .\analysis\stage7_player_view\players_view.csv --json-output .\analysis\stage7_player_view\players_view.json
```

See `reports/stage7_player_viewer.md`.

## Recommended Next Work

1. Extract the OBB read-only via the Stage 3 `PAK`/`CPK` extractors, then re-scan leaves for the 105 `PrepareDataFromJson` key markers (raw OBB scan found zero occurrences of high-signal keys, so player data is nested/compressed or UE4 `UDataTable`-serialized — see `reports/stage7_player_viewer.md`).
2. Once real player-shaped records are located, run Stage 5 normalizer then Stage 6/6.2 and compare coverage against the fixture baseline.
3. Raise confidence on `MEDIUM` grouped fields (ability parameter array, skill-card list, position-aptitude table) by tracing `PrepareDataFromJson` array/buffer stores.
4. Editor design (Stage 8) stays blocked until read-only parsing is proven against multiple real samples.
