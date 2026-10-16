# Stage 42 — Accurate Mock Client

## Scope

User request: more accurate mock client simulating the real client.

## 1. What it does (`scripts/s42_01_mock_client.py`)

Unlike the integration test (which just hits endpoints), the mock
client:
- Maintains session state (`auth_code`, `session_id`, `user_id`, `team_id`)
- Sends proper `param` JSON per Stage 23 format on every request
- Follows dependencies (scouted player → contract; team_id → match)
- Logs full request/response keys for schema analysis
- Simulates a complete session: boot → team → progression → match

## 2. Session flow

```
BOOT: auth_user → check_update → login → top
TEAM: get_team_info (captures team_id)
PROGRESSION: do_scout → do_contract → do_training
MATCH: get_match_info → [local sim] → submit_match_result
```

## 3. Verified

Full session runs clean against the stub server. Final state shows
proper state propagation (session, user, team IDs carried through).

## 4. Use

```bash
python3 scripts/s42_01_mock_client.py --port 8080 --log session.log
```

The log captures request/response keys — useful for refining stub
schemas without a real device.
