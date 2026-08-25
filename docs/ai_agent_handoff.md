# AI Agent Handoff: Offline Player Database Work

## What This Project Is

This repository is a local reverse-engineering workspace for PES Club Manager Android version `4.5.1` / version code `104050101`.

The current goal is not game patching. The goal is to recover enough offline player data structure to build a safe read-only database/parser first.

## Non-Negotiable Boundaries

Work offline. Do not touch production servers or online APIs. Do not bypass anti-cheat. Do not patch the game, OBBs, PAKs, CPKs, native libraries, or save files during the current stage.

Allowed outputs are derived analysis files:

- `analysis/`
- `reports/`
- `docs/`
- `scripts/`

Keep `original/` as pristine source material.

## Current Mental Model

The working pipeline is:

```text
OBB
  -> PAK
  -> CPK
  -> Player data
  -> Save/local data
  -> Recover Player structure
  -> Offline database/parser
  -> Offline viewer
  -> Offline editor
```

The project is currently at Stage 6:

```text
Read-only cross-reference between normalized player data and native evidence
```

Do not jump directly to an editor. The exact player field offsets/types and file format still need proof.

## Stage Summary

### Stage 3: Container And Asset Inventory

Confirmed:

- `main.104050101.jp.konami.pesclubmanager.obb` is a ZIP-like OBB that contains an Unreal `.pak`.
- The main PAK path is `extracted/obb_main/PesMobile/Content/Paks/PesMobile-Android_ETC1.pak`.
- `patch.104050101.jp.konami.pesclubmanager.obb` has CRIWARE CPK magic.
- Main PAK path scan found tens of thousands of asset paths.
- Patch CPK path scan found mostly animation/demo/fixdemo-like data, not a proven player master table.

Primary files:

- `reports/obb_inventory.md`
- `reports/obb_extraction.md`
- `reports/stage3_asset_path_inventory.md`
- `analysis/stage3_asset_paths/main_pak_paths.txt`
- `analysis/stage3_asset_paths/main_pak_player_candidates.txt`
- `analysis/stage3_asset_paths/patch_cpk_paths.txt`
- `analysis/stage3_asset_paths/patch_cpk_player_candidates.txt`

### Stage 4: Native Player Schema Recovery

Confirmed:

- `libUE4.so` is the main native target.
- The game uses Unreal Engine 4.22.3.
- Native exports include `tmpdb::Player`, `onlinemode::ParameterPlayerDefine`, `ParameterTeam`, `sys::SaveData`, and `systemdata::SystemData`.
- `ParameterPlayerDefine` methods load a backing player data pointer from `[x0 + 0x28]`.
- Getter/setter disassembly reveals many in-memory field offsets.
- JSON preparation functions reveal player key names such as `serial_id`, `master_id`, `name`, `salary`, `contract_period`, `param_speed`, `skill_*`, and position keys.

Primary files:

- `reports/native_analysis.md`
- `reports/stage4_offset_probe.md`
- `reports/stage4_player_symbol_schema.md`
- `reports/stage4_player_offset_schema.md`
- `reports/stage4_player_json_keys.md`
- `reports/stage4_player_key_offset_map.md`
- `analysis/stage4_player_schema/parameter_player_define_symbols.csv`
- `analysis/stage4_player_schema/parameter_player_define_offsets.json`
- `analysis/stage4_player_schema/parameter_player_define_json_keys.json`
- `analysis/stage4_player_schema/player_json_key_offset_map.json`

Important examples:

| Field | Evidence | Notes |
| --- | --- | --- |
| `PlayerId` / `Id` | backing offset `0x2c`, `u64` | From getter/setter accessors |
| `SerialId` | `0x1c8`, `u64` | JSON key `serial_id` |
| `MasterId` | `0x1d0`, `u64` | JSON key `master_id` |
| `Name` | `0x38`, pointer/address reference | JSON key `name` |
| `Age` | around `0x18` / `0x1c` | Bitfield behavior observed |
| `OriginalTeamId` | `0xdc`, `u32` | JSON key `original_team_id` |
| `Salary` | `0x1e8`, `u32` | JSON key `salary` |
| `ContractPeriod` | `0x1e0`, `u32` | JSON key `contract_period` |
| `Rarity` | `0x1c0`, `u32` | JSON key `rarity` |

### Stage 5: Read-Only JSON Normalizer

Implemented:

- `scripts/s5_01_normalize_player_json.py`
- `analysis/stage5_player_json/fixtures/sample_players.json`
- `analysis/stage5_player_json/normalized_players.json`
- `reports/stage5_player_json_normalizer.md`

Purpose:

The script reads local JSON input and emits canonical player records. It does not edit source data.

Canonical output sections:

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

Run:

```powershell
python .\scripts\s5_01_normalize_player_json.py .\analysis\stage5_player_json\fixtures\sample_players.json --output .\analysis\stage5_player_json\normalized_players.json
```

Expected:

```text
Scanned files: 1
Player records: 2
```

### Stage 6: Player Cross-Reference

Implemented:

- `scripts/s6_01_cross_reference_player_schema.py`
- `tests/stage6_cross_reference_assert.py`
- `analysis/stage6_player_cross_reference/player_field_coverage.json`
- `analysis/stage6_player_cross_reference/player_field_coverage.csv`
- `reports/stage6_player_cross_reference.md`

Purpose:

The script compares Stage 5 normalized records with Stage 4 native key/offset evidence. It classifies observed fields into:

- `observed_with_offset`
- `observed_without_offset`
- `observed_unmapped`
- `native_unobserved`

Run:

```powershell
python .\scripts\s6_01_cross_reference_player_schema.py
```

Fixture-baseline result:

```text
Player records: 2
Observed keys: 18
Observed with offsets: 9
Observed without offsets: 8
Observed unmapped: 1
Native unobserved: 88
```

## How To Continue Safely

### Good Next Step

Find real offline JSON-like player records in extracted or local data, then run:

```powershell
python .\scripts\s5_01_normalize_player_json.py <json-file-or-directory> --output .\analysis\stage5_player_json\normalized_players_real.json
```

Then inspect:

- `meta.player_record_count`
- `players[*].raw_unmapped`
- `players[*].native_evidence`
- whether IDs, names, abilities, positions, and contracts group cleanly

After normalizing real records, run Stage 6 again and inspect:

- `coverage.observed_with_offset`
- `coverage.observed_without_offset`
- `coverage.observed_unmapped`
- `coverage.native_unobserved`

### Next Analysis Step

Improve key-to-field confidence by tracing `PrepareDataFromJson` more deeply:

- key literal address
- surrounding call sequence
- target setter/accessor
- final field candidate and offset

This should reduce medium-confidence mappings like `uniform_name`, `position`, `stronger_foot`, `height`, `weight`, `durability`, `stability`, and `energy`.

### Do Not Do Yet

- Do not build a save editor.
- Do not write modified player records back to game files.
- Do not repack APK/OBB/PAK/CPK.
- Do not assume in-memory offsets equal file offsets.
- Do not assume every JSON key is proven just because it has a native string.

## Useful Commands

Compile Stage 5:

```powershell
python -m py_compile .\scripts\s5_01_normalize_player_json.py
```

Compile Stage 6:

```powershell
python -m py_compile .\scripts\s6_01_cross_reference_player_schema.py .\tests\stage6_cross_reference_assert.py
```

Run Stage 5 fixture:

```powershell
python .\scripts\s5_01_normalize_player_json.py .\analysis\stage5_player_json\fixtures\sample_players.json --output .\analysis\stage5_player_json\normalized_players.json
```

Run all Stage 4/5 compile checks:

```powershell
python -m py_compile .\scripts\s4_01_player_symbol_schema.py .\scripts\s4_02_extract_player_offsets.py .\scripts\s4_03_extract_player_json_keys.py .\scripts\s4_04_correlate_json_keys_offsets.py .\scripts\s5_01_normalize_player_json.py .\scripts\s6_01_cross_reference_player_schema.py
```

Run Stage 6 assertions:

```powershell
python .\tests\stage6_cross_reference_assert.py
```

## Git Note

This workspace may produce:

```text
fatal: detected dubious ownership in repository
```

Do not run global git config changes unless the user approves. The suggested command from git is:

```powershell
git config --global --add safe.directory C:/Users/rahma/Documents/projects/abe/reverse_engineering
```

## Handoff Checklist For The Next Agent

Before making changes:

1. Read `AGENTS.md`.
2. Read `reports/stage5_player_json_normalizer.md`.
3. Read `reports/stage6_player_cross_reference.md`.
4. Read `reports/stage4_player_key_offset_map.md`.
5. Confirm the requested work stays offline/read-only unless the user explicitly changes stage.
6. Run the Stage 5 fixture command before modifying parser behavior.
7. Run the Stage 6 assertion command before modifying cross-reference behavior.
8. Preserve `raw_unmapped` fields when extending normalization.
