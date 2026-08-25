# Stage 5 Player JSON Normalizer

## Purpose

Stage 5 starts the offline player database path with a read-only JSON normalizer. The tool scans local JSON artifacts and emits canonical player-shaped records for review.

## Tool

- Script: `scripts/s5_01_normalize_player_json.py`
- Fixture: `analysis/stage5_player_json/fixtures/sample_players.json`
- Default output: `analysis/stage5_player_json/normalized_players.json`

## Safety Boundary

The script only reads local JSON input and writes analysis output. It does not patch game binaries, edit saves, repack APK/OBB/PAK/CPK containers, or contact online services.

## Initial Fixture Result

Verified with:

```text
python -m py_compile .\scripts\s5_01_normalize_player_json.py
python .\scripts\s5_01_normalize_player_json.py .\analysis\stage5_player_json\fixtures\sample_players.json --output .\analysis\stage5_player_json\normalized_players.json
```

Result:

```text
Scanned files: 1
Player records: 2
```

The first fixture record groups `param_speed` and `param_shot` under `abilities`, `skill_one_touch_shoot` under `skills`, `cf` under `positions`, `record_goal_total` under `records`, and `mystery_flag` under `raw_unmapped`.

## Next Validation Step

Run the normalizer against real offline JSON-like player records once they are identified from extracted assets or save/local data. Compare normalized keys with Stage 4 native evidence before designing any editor.
