# Offline Mode — Status & Handoff

## Completed (2026-10-16)

### Reverse Engineering (Stages 20–37)
- WesysData format + offline decoder
- Server infrastructure (domains, API format, endpoints)
- Certificate pinning analysis
- Response schema (flat KV format)
- Game logic architecture (client-side match sim)
- 120 onlineapi:: operations inventoried

### Stub Server
- 14 endpoints: auth, update check, login, top, team, match,
  training, scouting, contract, items, facility, post-match, masterdata
- Integration test: 9/9 passing

### Patched APK
- `builds/pescm-patched-v1.apk` (84 MB, signed, gitignored)
- Patches: https→http, server→localhost

### Docs
- `docs/OFFLINE_MODE.md` — full user guide

## Remaining (needs device testing)

1. Install patched APK on device/emulator
2. Run stub server, observe actual client requests
3. Refine schemas from observations
4. Stub remaining operations as needed

The foundation is complete. The next phase is driven by real
client observations, not static analysis.
