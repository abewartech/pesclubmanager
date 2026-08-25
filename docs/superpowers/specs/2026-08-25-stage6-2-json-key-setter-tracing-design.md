# Stage 6.2 JSON Key-To-Setter Tracing Design

## Goal

Produce a read-only evidence report that correlates player JSON keys from `PrepareDataFromJson*` with known native field candidates, setter names, and recovered backing-struct offsets.

## Scope

This stage uses only existing static artifacts and optional radare2 disassembly outputs. It does not execute the game, hook runtime functions, patch binaries, call servers, or modify APK/OBB/PAK/CPK/save files.

## Inputs

- `analysis/stage4_player_schema/parameter_player_define_json_keys.json`
- `analysis/stage4_player_schema/player_json_key_offset_map.json`
- `analysis/stage4_player_schema/parameter_player_define_offsets.json`
- `analysis/libUE4_arm64_exports.json`

## Outputs

- `analysis/stage6/prepare_data_from_json_address.txt`
- `analysis/stage6/player_json_key_mapping.json`
- `analysis/stage6/mapping_confidence_report.csv`
- `analysis/stage6/new_fields_candidates.json`
- `reports/stage6_json_key_mapping_report.md`

## Confidence Model

- `HIGH`: JSON literal appears in `PrepareDataFromJson*`, maps to a field candidate, and that field has recovered offset evidence.
- `MEDIUM`: JSON literal appears and maps to a field/group, but direct offset evidence is missing or grouped.
- `LOW`: Native field has offset evidence, but no JSON key correlation was found.
- `UNKNOWN`: JSON-like field candidate exists with no usable native mapping yet.

## Honesty Rule

Do not label mappings as direct setter-call evidence unless the call target is actually observed in disassembly. If only a setter name is inferred from Stage 4 accessor metadata, record `setter_evidence` as `inferred_from_accessor_metadata`.
