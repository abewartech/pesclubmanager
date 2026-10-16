# Stage 32 — Masterdata Serving in Stub Server

## Scope

Extend the stub server (Stage 24) to serve `/masterdata/` files from
the `analysis/masterdata_stub/templates/` directory.

## 1. Changes (`scripts/s24_01_stub_server.py`)

- `do_GET` now checks for `/masterdata/` in the path.
- Extracts the filename, looks for a matching template (with or
  without `.txt`).
- Returns the template content as `text/plain`, or 404 if missing.
- Request logging included (path + bytes served).

## 2. Templates (recreated)

`analysis/masterdata_stub/templates/`:
- `players.txt` — 3 sample players (flat KV).
- `teams.txt` — 2 sample teams.
- `leagues.txt` — 1 sample league.
- `mappings/masterdata_paths.json` — empty, fill from proxy observations.

## 3. Verified

- `py_compile` clean.
- Live test: `GET /asj/masterdata/players` returns the template;
  unknown path returns 404.

## 4. Next

Fill templates from real proxy observations (user's dynamic analysis).
