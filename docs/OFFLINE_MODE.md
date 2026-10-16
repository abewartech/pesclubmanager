# Offline Mode Guide — PES Club Manager (Preservation)

> The game was discontinued by Konami on 2021-12-15. This guide
> documents how to run it against a local stub server for
> preservation/research purposes.

## Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Patched APK | `builds/pescm-patched-v1.apk` | Client with `https://`→`http://` and server→localhost patches |
| Stub server | `scripts/s24_01_stub_server.py` | Serves API endpoints + masterdata |
| Integration test | `scripts/s36_01_integration_test.py` | Validates the stub (7/7) |
| Masterdata templates | `analysis/masterdata_stub/templates/` | Sample roster data |

## Patches applied (Stage 30)

`libUE4.so`:
- `0x78352f0`: `https://` → `http://` (bypass TLS + cert pinning)
- `0x78352f8`: `asj.s.konaminet.jp` → `localhost/asj/trunk/`

## Running the stub server

```bash
# On the machine reachable as 'localhost' from the device:
python3 scripts/s24_01_stub_server.py --port 8080

# If the device is an emulator, use adb reverse:
adb reverse tcp:8080 tcp:8080
```

## Stubbed endpoints

| Endpoint | Stage | Notes |
|----------|-------|-------|
| `auth_user.php` | 33 | Boot: returns session |
| `check_update.php` | 33 | Boot: no update required |
| `login.php` | 33 | Boot: login success |
| `top.php` | 27 | Top menu data |
| `get_team_info.php` | 34 | Sample squad |
| `get_match_info.php` | 35 | Opponent data |
| `/masterdata/*` | 32 | Roster templates |

## Testing

```bash
python3 scripts/s36_01_integration_test.py --port 8080
# Expected: 7/7 passed
```

## Limitations

- Schemas are inferred from static analysis, not observed traffic.
- Only ~8 of 168 `onlineapi::` operations are stubbed.
- Match simulation is client-side (no server work needed).
- 3D assets come from the local OBB; only data is stubbed.

## Next steps

1. Install the patched APK on a device/emulator.
2. Run the stub server, observe actual client requests.
3. Refine schemas from observations; stub more operations.
