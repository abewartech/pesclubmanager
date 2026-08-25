# Stage 4 Player Key/Offset Map

Scope: conservative correlation of extracted JSON-key literals with candidate native `ParameterPlayerDefine` backing-data offsets. This is not yet a file-format parser.

**Unique useful JSON keys:** 105

**Mapped keys:** 97

## Core Field Map

| JSON key | Field candidate | Native offset(s) | Widths | Confidence |
|---|---|---:|---|---|
| `age` | `Age` | `0x18, 0x1c` | `u64, u8` | medium |
| `camulative_yellow_cards` | `SumYellow` | `0x18c` | `u32` | medium |
| `condition_status` | `Condition` | `0xf4, 0xf7` | `u64, u8` | medium |
| `contract_period` | `ContractPeriod` | `0x1e0` | `u32` | medium |
| `contract_period_max` | `ContractPeriodMax` | `0x1dc` | `u32` | medium |
| `contract_period_request` | `ContractPeriodRequest` | `0x1e4` | `u32` | medium |
| `contract_status` | `ContractStatus` | `0x210` | `u32` | medium |
| `deleted` | `DeleteType` | `0x214` | `u32` | medium |
| `injury` | `InjuryLength` | `0xf4, 0xf8` | `u64, u8` | medium |
| `legend_status` | `LegendStatus` | `0x1bc` | `u32` | medium |
| `licence` | `License` | `0x204` | `u32` | medium |
| `master_id` | `MasterId` | `0x1d0` | `u64` | medium |
| `motivation` | `MotivationValue` | `0x20c` | `u8` | medium |
| `name` | `Name` | `0x38` | `pointer` | medium |
| `nationality` | `Nationality` | `0xf4` | `u64` | medium |
| `next_salary` | `NextSalary` | `0x1ec` | `u32` | medium |
| `original_team_id` | `OriginalTeamId` | `0xdc` | `u32` | medium |
| `playstyle` | `PlayStyle` | `0x18` | `u64` | medium |
| `position` | `RegisteredPosition` | `?` | `?` | medium |
| `price` | `MarketValue` | `0x1a0` | `u64` | medium |
| `rarity` | `Rarity` | `0x1c0` | `u32` | medium |
| `salary` | `Salary` | `0x1e8` | `u32` | medium |
| `salary_list` | `ContractSalary` | `0x1f0` | `u32` | medium |
| `sell_price` | `SellPrice` | `0x1a8` | `u32` | medium |
| `serial_id` | `SerialId` | `0x1c8` | `u64` | medium |
| `stronger_foot` | `StrongerFoot` | `?` | `?` | medium |
| `uniform_name` | `NamePrint` | `0x75, 0xf7` | `pointer, u8` | medium |
| `uniform_number` | `UniformNumber` | `0x1ac` | `u32` | medium |
| `record_assist_season` | `AssistSeason` | `0x174` | `u32` | medium |
| `record_assist_total` | `AssistSum` | `0x178` | `u32` | medium |
| `record_average_rating_season` | `PointSeason` | `0x17c` | `u32` | medium |
| `record_average_rating_total` | `PointSum` | `0x180` | `u32` | medium |
| `record_goal_season` | `GoalSeason` | `0x16c` | `u32` | medium |
| `record_goal_total` | `GoalSum` | `0x170` | `u32` | medium |
| `record_match_season` | `GameSeason` | `0x164` | `u32` | medium |
| `record_match_total` | `GameSum` | `0x168` | `u32` | medium |
| `record_red_card_season` | `RedSeason` | `0x194` | `u32` | medium |
| `record_red_card_total` | `RedSum` | `0x198` | `u32` | medium |
| `record_yellow_card_season` | `YellowSeason` | `0x184` | `u32` | medium |
| `record_yellow_card_total` | `YellowSum` | `0x188` | `u32` | medium |

## Grouped Keys

### ability_parameter

`param_agility`, `param_ball_spin_control`, `param_body_balance`, `param_defense_decision`, `param_dribble`, `param_gk_decision`, `param_heading`, `param_intercept`, `param_jump`, `param_kick_power`, `param_long_pass`, `param_offense_decision`, `param_place_kicking`, `param_r_foot_acc`, `param_r_foot_frequency`, `param_saving`, `param_short_pass`, `param_shot`, `param_speed`, `param_stamina`, `param_teamwork`, `param_trap`

### skill_card

`skill_acrobatic_shoot`, `skill_back_spin_lob`, `skill_captaincy`, `skill_chasing`, `skill_combative_spirit`, `skill_control_curve`, `skill_flip_flap`, `skill_gk_long_throw`, `skill_knuckle_shoot`, `skill_long_throw`, `skill_low_pant_kick`, `skill_man_mark`, `skill_one_touch_pass`, `skill_one_touch_shoot`, `skill_out_spin_kick`, `skill_pin_point_cross`, `skill_pivot_foot_touch`, `skill_quick_touch`, `skill_roulette`, `skill_scissors`, `skill_sombrero`, `skill_super_sub`

### position_aptitude

`cb`, `cf`, `cmf`, `dmf`, `gk`, `lmf`, `lsb`, `lwg`, `omf`, `rmf`, `rsb`, `rwg`, `st`

### field

`LeftRight`, `age`, `camulative_yellow_cards`, `condition_status`, `contract_period`, `contract_period_max`, `contract_period_request`, `contract_status`, `deleted`, `durability`, `e_09`, `energy`, `er_home_10`, `height`, `injury`, `legend_status`, `licence`, `master_id`, `motivation`, `name`, `nationality`, `next_salary`, `original_team_id`, `playstyle`, `position`, `price`, `rarity`, `salary`, `salary_list`, `sell_price`, `serial_id`, `stability`, `stronger_foot`, `uniform_name`, `uniform_number`, `weight`

## Unmapped Field-like Keys

- `LeftRight`
- `durability`
- `e_09`
- `energy`
- `er_home_10`
- `height`
- `stability`
- `weight`

## Outputs

- `analysis\stage4_player_schema\player_json_key_offset_map.csv`
- `analysis\stage4_player_schema\player_json_key_offset_map.json`

## Next

- Trace nearby setter calls for each JSON key to raise confidence from medium to high.
- Use this map as the schema for a read-only JSON player normalizer/viewer.
- Keep binary editing out of scope until a real local file layout is proven.
