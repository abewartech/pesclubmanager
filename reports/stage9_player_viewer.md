# Stage 9 — Offline Player DB Viewer + Save-Data Tracing Plan

## Scope

Read-only, offline. No binary executed, no server contacted, no artifacts
patched. All outputs under `analysis/` and `scripts/`.

## 1. HTML player DB viewer (delivered)

`scripts/s9_01_html_viewer.py` generates a single self-contained HTML file
(no CDN, no server, no build step) from the Stage 5 normalized players and
the Stage 6 decoder schema:

```powershell
python .\scripts\s9_01_html_viewer.py
python .\scripts\s9_01_html_viewer.py --players <players.json> --mapping <mapping.json> --out <viewer.html>
```

Output: `analysis/stage9_player_view/player_db_viewer.html`

Features:

- **Players tab** — searchable table (name / serial_id / master_id);
  click a row for the full record, grouped by section
  (identity, profile, team, contract, abilities, skills, positions,
  records), each field annotated with its native-evidence badge
  (HIGH / MEDIUM / UNKNOWN / LOW), field candidate, and offsets.
  `raw_unmapped` fields are shown verbatim, never reinterpreted.
- **Schema mapping tab** — all 105 JSON keys with field candidate,
  confidence, offsets, and setter functions; filterable by confidence.
- **Unknown keys tab** — the 8 unmapped keys (`LeftRight`, `durability`,
  `e_09`, `energy`, `er_home_10`, `height`, `stability`, `weight`) with
  their `PrepareDataFromJson` instruction/literal addresses, preserved
  as-is per the workspace rule against inventing semantics.

Verified: generator runs clean, emitted HTML embeds both fixture players,
`node --check` passes on the inline script.

## 2. Save-data tracing plan (for a machine with the game binary)

Static leads are exhausted at the symbol-name level (`sys::SaveData`,
`systemdata::SystemData`, Unreal `Saved/` strings — see
`docs/save_data_structure.md`). The next concrete step needs
`libUE4.so` + a disassembler and cannot run in this offline workspace:

1. Locate `sys::SaveData` / `systemdata::SystemData` method bodies via
   the export map (`analysis/libUE4_arm64_exports.json`).
2. Trace callees for file I/O: `fopen`/`open` with string refs under
   `/data/data/jp.konami.pesclubmanager/`, `Saved/`, `.sav`, plus
   `CHttpAsyncRequest::SetSaveFilePath` call sites.
3. Record concrete save paths and the serialization calls (memcpy widths,
   struct sizes) without executing anything.
4. Only if a save file with player-shaped records is obtained: run the
   Stage 5 normalizer, then Stage 6/6.2, and compare coverage against the
   fixture baseline (`Player records: 2, Observed keys: 18`).

Do **not** invent a save format from strings alone; every layout claim
needs disassembly evidence first.

## Status

- Viewer: done, verified.
- Save-data tracing: planned, blocked on binary access (not available in
  this environment).
- The 8 unknown JSON keys and 60 native-only offset fields remain the
  open research surface; both are now browsable in the viewer.
