# Stage 6 Player Cross-Reference

## Purpose

Stage 6 compares Stage 5 normalized player-shaped JSON with Stage 4 native key/offset evidence. This is a read-only validation step, not an editor or binary file parser.

## Summary

- Player records: 2
- Observed unique keys: 18
- Stage 4 mapped keys: 105
- Observed keys with offset evidence: 9
- Observed keys without offset evidence: 8
- Observed unmapped keys: 1
- Native mapped keys not observed in Stage 5 input: 88

## Outputs

- JSON: `C:\Users\rahma\Documents\projects\abe\reverse_engineering\analysis\stage6_player_cross_reference\player_field_coverage.json`
- CSV: `C:\Users\rahma\Documents\projects\abe\reverse_engineering\analysis\stage6_player_cross_reference\player_field_coverage.csv`

## Observed With Offset

| json_key | sections | occurrences | field_candidate | offsets | widths | confidence |
| --- | --- | --- | --- | --- | --- | --- |
| age | profile | 1 | Age | 0x18, 0x1c | u64, u8 | medium |
| contract_period | contract | 1 | ContractPeriod | 0x1e0 | u32 | medium |
| master_id | identity | 2 | MasterId | 0x1d0 | u64 | medium |
| name | profile | 2 | Name | 0x38 | pointer | medium |
| original_team_id | team | 1 | OriginalTeamId | 0xdc | u32 | medium |
| rarity | profile | 1 | Rarity | 0x1c0 | u32 | medium |
| record_goal_total | records | 1 | GoalSum | 0x170 | u32 | medium |
| salary | contract | 1 | Salary | 0x1e8 | u32 | medium |
| serial_id | identity | 2 | SerialId | 0x1c8 | u64 | medium |

## Observed Without Offset

| json_key | sections | occurrences | field_candidate | category | confidence | mapping_reason |
| --- | --- | --- | --- | --- | --- | --- |
| cf | positions | 1 | PositionAptitude | position_aptitude | medium | group: position aptitude bitfield/table |
| gk | positions | 1 | PositionAptitude | position_aptitude | medium | group: position aptitude bitfield/table |
| param_saving | abilities | 1 | AbilityParameter | ability_parameter | medium | group: ability parameter array |
| param_shot | abilities | 1 | AbilityParameter | ability_parameter | medium | group: ability parameter array |
| param_speed | abilities | 1 | AbilityParameter | ability_parameter | medium | group: ability parameter array |
| position | profile | 1 | RegisteredPosition | field | medium | direct synonym |
| skill_gk_long_throw | skills | 1 | SkillCard | skill_card | medium | group: skill-card flags/list |
| skill_one_touch_shoot | skills | 1 | SkillCard | skill_card | medium | group: skill-card flags/list |

## Observed Unmapped

| json_key | sections | occurrences |
| --- | --- | --- |
| mystery_flag | raw_unmapped | 1 |

## Interpretation

- `observed_with_offset` is the strongest current evidence path: the key exists in normalized records and has native offset support.
- `observed_without_offset` usually means grouped data such as ability, skill, or position arrays, or native strings whose storage still needs tracing.
- `observed_unmapped` must be preserved and reviewed; do not discard these fields.
- `native_unobserved` shows known Stage 4 fields that did not appear in the current Stage 5 input.

## Safety Boundary

This report is derived from local analysis artifacts only. It does not modify game data, containers, saves, binaries, or network state.
