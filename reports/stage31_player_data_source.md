# Stage 31 — Player/Team Data Source

## Scope

User request: check if player/team data is in the OBB or needs stubbing.

## 1. What's in the OBB (1.6 GB)

- **3D assets**: player models, textures, animations (`character/`).
- **Data tables**: `Definedatatable.bin`, `Derivationdatatable.bin`
  (player ID mappings, derivations).
- **Player schema**: Stages 4–8 mapped the in-memory player struct
  (`parameter_player_define_*`, `players_template.csv`).

## 2. What's NOT in the OBB

The **roster database** (player names, stats, teams, leagues) is NOT
in the OBB. Evidence:

- Server has a `/masterdata/` endpoint (Stage 23) — the client
  downloads master data at boot/update.
- `ms_ver` in the API request (Stage 23) gates master-data updates.
- Stage 8 produced only a `players_template.csv` (schema), not a
  populated roster.

## 3. Conclusion: NEEDS STUBBING

The stub server must provide player/team data via:

1. `/masterdata/` endpoint (bulk roster download), and/or
2. Per-operation responses (`Get*` ops returning player lists).

The 3D assets are local; only the **data** needs stubbing.

## 4. Next

- Trace the `/masterdata/` download format (likely a binary or
  JSON bundle).
- Build a minimal roster (even a few fake teams is enough to test
  match setup).
- The client-side match engine (Stage 28) will simulate with
  whatever roster the stub provides.
