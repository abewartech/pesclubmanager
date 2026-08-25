# Stage 4 Player JSON Key Inventory

Scope: read-only extraction of string literals referenced by `ParameterPlayerDefine` JSON preparation methods. These are candidate JSON keys or enum/string constants and require cross-checking.

**Functions scanned:** 5

**Literal references:** 261

**Meaningful non-numeric literals:** 109

## By Function

| Function | Literal refs | Example literals |
|---|---:|---|
| `PrepareDataFromJson` | 230 | `name, EMouseCursor::TextEditBeam, ursor::TextEditBeam, LeftRight, uniform_name, original_team_id, licence, stronger_foot, next_salary, condition_status, camulative_yellow_cards, record_match_total` |
| `PrepareDataFromJsonForScoutingList` | 28 | `24, 25, 26, 27, 20, 21, 22, 23, 13, 14, 15, 16` |
| `SetMilestoneListFromJson` | 3 | `` |

## Candidate Keys

- `EMouseCursor::TextEditBeam`
- `LeftRight`
- `age`
- `camulative_yellow_cards`
- `cb`
- `cf`
- `cmf`
- `condition_status`
- `contract_period`
- `contract_period_max`
- `contract_period_request`
- `contract_status`
- `deleted`
- `dmf`
- `durability`
- `e_09`
- `energy`
- `er_home_10`
- `gk`
- `height`
- `injury`
- `legend_status`
- `licence`
- `lmf`
- `lsb`
- `lwg`
- `master_id`
- `motivation`
- `name`
- `nationality`
- `next_salary`
- `omf`
- `original_team_id`
- `param_agility`
- `param_ball_spin_control`
- `param_body_balance`
- `param_defense_decision`
- `param_dribble`
- `param_gk_decision`
- `param_heading`
- `param_intercept`
- `param_jump`
- `param_kick_power`
- `param_long_pass`
- `param_offense_decision`
- `param_place_kicking`
- `param_r_foot_acc`
- `param_r_foot_frequency`
- `param_saving`
- `param_short_pass`
- `param_shot`
- `param_speed`
- `param_stamina`
- `param_teamwork`
- `param_trap`
- `playstyle`
- `position`
- `price`
- `rarity`
- `record_assist_season`
- `record_assist_total`
- `record_average_rating_season`
- `record_average_rating_total`
- `record_goal_season`
- `record_goal_total`
- `record_match_season`
- `record_match_total`
- `record_red_card_season`
- `record_red_card_total`
- `record_yellow_card_season`
- `record_yellow_card_total`
- `rmf`
- `rsb`
- `rwg`
- `salary`
- `salary_list`
- `sell_price`
- `serial_id`
- `skill_acrobatic_shoot`
- `skill_back_spin_lob`
- `skill_captaincy`
- `skill_chasing`
- `skill_combative_spirit`
- `skill_control_curve`
- `skill_flip_flap`
- `skill_gk_long_throw`
- `skill_knuckle_shoot`
- `skill_long_throw`
- `skill_low_pant_kick`
- `skill_man_mark`
- `skill_one_touch_pass`
- `skill_one_touch_shoot`
- `skill_out_spin_kick`
- `skill_pin_point_cross`
- `skill_pivot_foot_touch`
- `skill_quick_touch`
- `skill_roulette`
- `skill_scissors`
- `skill_sombrero`
- `skill_super_sub`
- `st`
- `stability`
- `stronger_foot`
- `uniform_name`
- `uniform_number`
- `ure`
- `ursor::TextEditBeam`
- `vvx`
- `weight`

## Outputs

- `analysis\stage4_player_schema\parameter_player_define_json_keys.csv`
- `analysis\stage4_player_schema\parameter_player_define_json_keys.json`
- `analysis\stage4_player_schema\player_json_key_probe_disasm.txt`

## Next

- Correlate key order with nearby setter calls in `PrepareDataFromJson`.
- Build a conservative read-only JSON normalizer for any captured/local JSON records.
- Keep binary editor disabled until file/local record layout is confirmed.
