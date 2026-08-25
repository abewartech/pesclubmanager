# Stage 5 Player JSON Normalizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a read-only Stage 5 utility that normalizes offline player-shaped JSON into reviewable canonical player records.

**Architecture:** Add one focused Python CLI script under `scripts/` and a tiny fixture under `analysis/stage5_player_json/fixtures/`. The script recursively scans JSON values, classifies player-like objects with conservative heuristics, groups known keys into canonical sections, preserves unknowns, and writes an analysis JSON artifact.

**Tech Stack:** Python standard library only: `argparse`, `json`, `pathlib`, and recursive object walking.

---

### File Structure

- Create: `scripts/s5_01_normalize_player_json.py`
  - CLI entrypoint and normalizer logic.
  - Reads files/directories.
  - Writes normalized JSON.
- Create: `analysis/stage5_player_json/fixtures/sample_players.json`
  - Minimal offline fixture containing two player-like objects and one ignored non-player object.
- Create: `reports/stage5_player_json_normalizer.md`
  - Run summary and safety notes.

### Task 1: Fixture And Classifier

**Files:**
- Create: `analysis/stage5_player_json/fixtures/sample_players.json`
- Create: `scripts/s5_01_normalize_player_json.py`

- [ ] **Step 1: Add a fixture with two player-like objects and one non-player object**

```json
{
  "players": [
    {
      "serial_id": 101,
      "master_id": 9001,
      "name": "Sample Forward",
      "age": 24,
      "original_team_id": 77,
      "salary": 1200,
      "contract_period": 12,
      "param_speed": 81,
      "param_shot": 79,
      "skill_one_touch_shoot": 1,
      "cf": 3,
      "record_goal_total": 18,
      "mystery_flag": 5
    },
    {
      "serial_id": 102,
      "master_id": 9002,
      "name": "Sample Keeper",
      "rarity": 4,
      "position": "gk",
      "param_saving": 83,
      "skill_gk_long_throw": 1,
      "gk": 3
    }
  ],
  "metadata": {
    "name": "not a player because it has only one weak key"
  }
}
```

- [ ] **Step 2: Implement `is_player_candidate(record)`**

```python
STRONG_KEYS = {
    "serial_id",
    "master_id",
    "original_team_id",
    "salary",
    "contract_period",
    "rarity",
    "position",
}

def is_player_candidate(value):
    if not isinstance(value, dict):
        return False
    keys = set(value)
    score = sum(1 for key in STRONG_KEYS if key in keys)
    score += sum(1 for key in keys if key.startswith("param_"))
    score += sum(1 for key in keys if key.startswith("skill_"))
    if "name" in keys and ({"serial_id", "master_id"} & keys):
        score += 1
    return score >= 2
```

- [ ] **Step 3: Run fixture scan**

Run: `python .\scripts\s5_01_normalize_player_json.py .\analysis\stage5_player_json\fixtures\sample_players.json`

Expected: output JSON contains exactly two normalized records.

### Task 2: Canonical Normalization

**Files:**
- Modify: `scripts/s5_01_normalize_player_json.py`

- [ ] **Step 1: Add key groups**

```python
IDENTITY_KEYS = {"id", "player_id", "serial_id", "master_id"}
PROFILE_KEYS = {
    "name",
    "uniform_name",
    "age",
    "nationality",
    "position",
    "rarity",
    "playstyle",
    "stronger_foot",
    "height",
    "weight",
}
TEAM_KEYS = {"original_team_id", "team_id"}
CONTRACT_KEYS = {
    "salary",
    "next_salary",
    "salary_list",
    "price",
    "sell_price",
    "contract_period",
    "contract_period_max",
    "contract_period_request",
    "contract_status",
}
RECORD_KEYS = {
    "camulative_yellow_cards",
    "record_match_total",
    "record_goal_total",
    "record_assist_total",
    "record_point_total",
    "record_yellow_card_total",
    "record_red_card_total",
}
POSITION_KEYS = {"gk", "cb", "rsb", "lsb", "dmf", "cmf", "rmf", "lmf", "omf", "rwg", "lwg", "st", "cf"}
```

- [ ] **Step 2: Add `normalize_player(record, source, pointer)`**

```python
def normalize_player(record, source, pointer):
    normalized = {
        "identity": {},
        "profile": {},
        "team": {},
        "contract": {},
        "abilities": {},
        "skills": {},
        "positions": {},
        "records": {},
        "raw_unmapped": {},
        "provenance": {"source": source, "json_pointer": pointer},
    }
    for key, value in record.items():
        if key in IDENTITY_KEYS:
            normalized["identity"][key] = value
        elif key in PROFILE_KEYS:
            normalized["profile"][key] = value
        elif key in TEAM_KEYS:
            normalized["team"][key] = value
        elif key in CONTRACT_KEYS:
            normalized["contract"][key] = value
        elif key.startswith("param_"):
            normalized["abilities"][key] = value
        elif key.startswith("skill_"):
            normalized["skills"][key] = value
        elif key in POSITION_KEYS:
            normalized["positions"][key] = value
        elif key in RECORD_KEYS or key.startswith("record_"):
            normalized["records"][key] = value
        else:
            normalized["raw_unmapped"][key] = value
    return normalized
```

- [ ] **Step 3: Verify grouped fields**

Run: `python .\scripts\s5_01_normalize_player_json.py .\analysis\stage5_player_json\fixtures\sample_players.json --output .\analysis\stage5_player_json\normalized_players.json`

Expected: first record has `param_speed` under `abilities`, `skill_one_touch_shoot` under `skills`, `cf` under `positions`, and `mystery_flag` under `raw_unmapped`.

### Task 3: Reporting And Verification

**Files:**
- Create: `reports/stage5_player_json_normalizer.md`

- [ ] **Step 1: Compile the script**

Run: `python -m py_compile .\scripts\s5_01_normalize_player_json.py`

Expected: command exits with status 0.

- [ ] **Step 2: Run the fixture command**

Run: `python .\scripts\s5_01_normalize_player_json.py .\analysis\stage5_player_json\fixtures\sample_players.json --output .\analysis\stage5_player_json\normalized_players.json`

Expected: report line says `Player records: 2`.

- [ ] **Step 3: Write the Stage 5 report**

The report records the input fixture path, output path, detected record count, read-only safety boundary, and next recommended validation step.

### Self-Review

- Spec coverage: the plan covers read-only input, conservative detection, canonical grouping, preservation of unmapped keys, fixture verification, and report output.
- Placeholder scan: no unresolved placeholder tasks are present.
- Type consistency: function names and output section names are consistent across tasks.
