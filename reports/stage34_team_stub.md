# Stage 34 — Team Data Stub

## Scope

Add `GetTeamInfo` stub (first team-data operation after boot).

## 1. New endpoint

`get_team_info.php` returns:
- `team_id`, `team_name` ("Stub United"), `formation` ("4-4-2")
- 3 players (flat KV array pattern): id, name, position

## 2. Verified

- `py_compile` clean, live test returns 200 with expected JSON.

## 3. Next

`DoUpdateTeamInfo`, reserve team ops, then match setup.
