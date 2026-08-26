# Stage 7 Offline Player Viewer

## Purpose

Stage 7 renders the Stage 5 normalized offline player artifact through a read-only viewer. It does not edit, patch, or instrument any game data, containers, saves, or binaries. It combines the normalized player records with the Stage 6.2 JSON-key / native-field mapping evidence so each record carries a field-coverage summary.

## Pipeline Position

```text
OBB -> PAK -> CPK -> Player data -> Save/local data -> Player structure
    -> Stage 5 normalizer -> Stage 6 cross-reference -> Stage 6.2 setter tracing
    -> Stage 7 viewer (this stage)
```

## Tool

`scripts/s7_01_player_viewer.py`

- Loads a Stage 5 normalized player JSON (`players` list).
- Optionally loads a Stage 4/Stage 6.2 mapping artifact to annotate each player with field-coverage confidence (`HIGH` / `MEDIUM` / `UNKNOWN`).
- Renders a fixed-width terminal table.
- Can emit derived read-only exports:
  - `--csv-output PATH` — flat per-player table (`index`, `name`, `serial_id`, `master_id`, `position`, `original_team_id`, `salary`, `mapping_summary`).
  - `--json-output PATH` — full per-player `mapping_evidence` array with `field_candidate`, offsets, widths, setter/accessor functions.
- Refuses to overwrite any read-only source input (`assert_outputs_are_derived`).

## Usage

```powershell
python .\scripts\s7_01_player_viewer.py
python .\scripts\s7_01_player_viewer.py --mapping .\analysis\stage6\player_json_key_mapping.json
python .\scripts\s7_01_player_viewer.py --mapping .\analysis\stage6\player_json_key_mapping.json --csv-output .\analysis\stage7_player_view\players_view.csv --json-output .\analysis\stage7_player_view\players_view.json
```

## Current Output (fixture baseline)

```text
# | Name           | Serial ID | Master ID | Position | Team ID | Salary | Mapping
1 | Sample Forward | 101       | 9001      | cf       | 77      | 1200   | HIGH:8, MEDIUM:4, UNKNOWN:1
2 | Sample Keeper  | 102       | 9002      | gk       | -       | -      | HIGH:4, MEDIUM:4
Player records: 2
Read-only: source inputs were not modified
```

- Derived CSV: `analysis/stage7_player_view/players_view.csv`
- Derived JSON: `analysis/stage7_player_view/players_view.json`

## Offline Container Search (Recommended Work Item 1, partial)

A read-only byte scan of the pristine OBB containers (`original/main.*.obb`, `original/patch.*.obb`) was run for the 105 `PrepareDataFromJson` JSON-key literals recovered in Stage 4.

Result:

- High-signal player keys (`serial_id`, `master_id`, `param_shot`, `original_team_id`, `contract_period`, `rarity`) have **zero** raw occurrences in both OBBs.
- Common-word keys (`name` 6421x in patch, `position` 3x in patch) appear but are UI/asset noise, not player records.

Interpretation: player data is **not** stored as plain JSON keyed by these field names in the raw OBB stream. It is either nested inside a compressed `PAK`/`CPK` (not yet extracted offline) or serialized as a UE4 `UDataTable` / script-struct binary, consistent with the Stage 4 caveat that the exact on-disk player format is not yet proven.

Next sub-step to confirm: run the existing Stage 3 `PAK`/`CPK` extractors on the OBB read-only, then re-scan the extracted leaves for the same key markers.

## Safety Boundary

Offsets in the mapping evidence are candidate in-memory backing-data offsets from native accessors, not file offsets. The viewer only reads its inputs and writes derived artifacts under `analysis/`. It never modifies game containers, saves, or binaries.
