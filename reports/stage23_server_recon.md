# Stage 23 — Server Infrastructure Reconnaissance

## Scope

First step toward the stub server (user request 2026-10-16): map the
game's server infrastructure from static strings. Read-only; no
packets captured, no servers contacted (all endpoints are dead since
2021-12-15).

## 1. Server table (`.rodata` @ `0x64dd123`)

```
?uc=
asj/
Def_Disuse_VersionFolder
%1d/
asj.s.konaminet.jp/asj/      <- production (SSL)
asj.konaminet.jp/asj/        <- production
dev-asj001.s.konaminet.jp/asj/
dev-asj001.konaminet.jp/asj/
chk-asj001.s.konaminet.jp/asj/
asjrsc.konaminet.jp/asj/     <- resources (CDN-ish)
localhost/asj/trunk/         <- local dev override!
asjmng01.konaminet.jp/asj/   <- management
chk-asj001.konaminet.jp/asj/
stg-asj.s.konaminet.jp/asj/
stg-asj.konaminet.jp/asj/
stg-asj11.s.konaminet.jp/asj/
stg-asj11.konaminet.jp/asj/
graph.facebook.com/          <- Facebook integration
```

URL shape: `https://<domain>/asj/<endpoint>.php?<params>&addParam=...`.
The `localhost/asj/trunk/` entry proves the client can be pointed at
a local server — the stub server strategy is viable.

## 2. API request format (`.rodata` @ `0x650487b`)

Base JSON template sent by the client:

```json
{"auth_code":"","ms_ver":0,"res_ver":0,"session_id":"","tutorial":0,"user_code":"","user_id":0}
```

- `auth_code`, `user_code`, `user_id`: from `UserInfoData.dat`
  (Stages 15–16) — the save file IS the client identity.
- `session_id`: empty on first boot, filled after login.
- `ms_ver` / `res_ver`: master-data and resource versions (update gating).
- `tutorial`: new-player tutorial flag.

## 3. Endpoint inventory (sample)

`top.php` (likely entry), `debug_login.php`, `loginBonus.php`,
`team.php`, `event.php`, `ranking_*`, `scout_*`, `campaign_*`,
plus `/resourcedata/`, `/masterdata/`, `/sounddata/` asset paths.

## 4. What's still unknown (stub-server blockers)

- Response format for each endpoint (JSON schema, binary parts).
- Session/auth handshake sequence.
- Request signing/encryption (if any) beyond the JSON body.
- Which endpoint is hit first on a fresh boot.
- The native code that selects the server row was not located
  (no `adrp` refs to the table page in `.text`; selection may be
  via JNI/config).

## 5. Next steps

1. Trace the HTTP request builder in native code (find `top.php`
   caller).
2. Capture the request/response schema per endpoint (needs dynamic
   analysis or deeper static tracing).
3. Build the minimal stub: DNS/hosts override to `localhost`, serve
   `top.php` with a canned session.
