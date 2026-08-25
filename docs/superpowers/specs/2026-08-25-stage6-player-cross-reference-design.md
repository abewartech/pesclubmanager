# Stage 6 Player Cross-Reference Design

## Goal

Build a read-only validator that compares Stage 5 normalized player records against Stage 4 native evidence and produces a field coverage report.

## Scope

Stage 6 does not parse binary player files, patch game data, or contact online services. It measures how much of the current normalized player shape is supported by known JSON keys, native field candidates, and recovered offsets.

## Inputs

- `analysis/stage5_player_json/normalized_players.json`
- `analysis/stage4_player_schema/player_json_key_offset_map.json`
- `analysis/stage4_player_schema/parameter_player_define_offsets.json`

## Outputs

- `analysis/stage6_player_cross_reference/player_field_coverage.json`
- `analysis/stage6_player_cross_reference/player_field_coverage.csv`
- `reports/stage6_player_cross_reference.md`

## Coverage Buckets

- `observed_with_offset`: key appears in normalized records and has native offset evidence.
- `observed_without_offset`: key appears in normalized records and maps to a native field/group but has no recovered offset.
- `observed_unmapped`: key appears in normalized records but has no Stage 4 mapping.
- `native_unobserved`: Stage 4 mapped key exists but does not appear in normalized records.

## Safety

The script reads analysis artifacts and writes derived reports only. It never modifies source JSON, game files, containers, binaries, saves, or network state.
