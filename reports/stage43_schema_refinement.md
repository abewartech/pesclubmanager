# Stage 43 — Schema Refinement from Static Analysis

## Method

Deep string extraction from `libUE4.so` `.rodata` (5,028 field-like
strings). Filtered out animation names, UI element IDs, and debug
strings.

## Confirmed field names (used in stubs)

### Scouting
- `scout`, `scout_id`, `scout_list`, `scout_list_count`
- `scout_point`, `scout_point_min`, `scout_ticket_num`
- `scout_report`, `scout_news`

### Training
- `training`, `trainer_list`, `trainer_get_list`, `trainer_result`
- `training_pt`, `training_position`
- `training_offense`, `training_physical`
- `training_skill02` … `training_skill22` (even numbers = skill slots)

### Team
- `team_player_list`, `team_short_name`, `team_salary`
- `formation_value`, `c_formation`
- `reserve`, `reserve_id`, `c_reserve`

### Player
- `player_rare`, `player_featured`, `player_serial_id`
- `player_list_max`, `player_num_max`, `player_num_min`
- `playercost`, `playercostnum`

### Match
- `match_away_score`, `match_home_score` (implied)
- `match_begin`, `match_end`, `match_complete`
- `goal`, `goal_event_data`, `center_score`

### Currency / items
- `game_point`, `friend_point`, `event_point`
- `energy_point`, `energy_num`, `match_energy`
- `point_item`, `icon_ticket`, `income_ticket`

## Array pattern (Stage 27 confirmed)

Only `news_*_size` arrays found as literal `_size` strings:
- `news_data_size`, `news_news_size`, `news_notice_size`, `news_asso_size`

Player/team indexed fields are likely built dynamically via
sprintf (not found as literals). The flat `player_{i}_{field}`
pattern from Stage 27 remains our best model.

## Updated stubs

The stub server now uses confirmed names where available:
- `do_scout_player.php`: added `scout_point`, `scout_ticket_num`
- `do_training.php`: added `training_pt`
- `get_team_info.php`: added `team_short_name`, `formation_value`
