# Stage 5 Player JSON Normalizer Design

## Goal

Build a read-only offline parser that turns locally available player-shaped JSON into a canonical player database draft without modifying game files, save files, APK, OBB, PAK, CPK, or server state.

## Scope

The first Stage 5 tool accepts JSON files that already exist on disk. It does not extract CPK/PAK data, patch binaries, edit saves, or call online APIs. It normalizes evidence into a reviewable JSON output so later stages can validate real player records against native symbols and offsets.

## Inputs

- One JSON file or a directory containing JSON files.
- Optional output path.
- Existing Stage 4 evidence:
  - `analysis/stage4_player_schema/player_json_key_offset_map.json`
  - `analysis/stage4_player_schema/parameter_player_define_json_keys.json`
  - `analysis/stage4_player_schema/parameter_player_define_offsets.json`

## Detection

The tool recursively walks arrays and objects and treats an object as player-shaped when it contains at least two strong identity/profile keys such as `serial_id`, `master_id`, `name`, `rarity`, `salary`, `contract_period`, `original_team_id`, `position`, or `param_*`.

## Output Shape

Each normalized record contains:

- `identity`: `serial_id`, `master_id`, and other ID-like values when present.
- `profile`: `name`, `uniform_name`, `age`, `nationality`, `position`, `rarity`, and similar profile fields.
- `team`: team-related fields such as `original_team_id`.
- `contract`: salary, price, contract period, contract status, and related fields.
- `abilities`: `param_*` fields.
- `skills`: `skill_*` fields.
- `positions`: position aptitude keys such as `gk`, `cb`, `cmf`, `cf`.
- `records`: `record_*` fields and disciplinary counters.
- `raw_unmapped`: source keys not yet classified.
- `provenance`: source path and JSON pointer.

## Safety

The parser is read-only with respect to source data. It only writes analysis outputs under `analysis/stage5_player_json/` unless the caller passes another output path. It preserves unmapped fields instead of guessing destructive semantics.

## Testing

Create a tiny offline fixture with two player-like objects and one non-player object. Verify that only player-like objects are emitted, grouped fields land in the expected buckets, and unknown fields are preserved.
