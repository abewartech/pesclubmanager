# Stage 36 — Integration Test (Real Testing)

## Scope

User request: "real testing". Built an integration test that simulates
the full client boot flow against the stub server.

## 1. Test (`scripts/s36_01_integration_test.py`)

Hits endpoints in client-expected order:
1. `auth_user.php` → checks `session_id`, `user_id`
2. `check_update.php` → checks `update_required`
3. `login.php` → checks `session_id`
4. `top.php` → checks `ms_ver`, `res_ver`
5. `get_team_info.php` → checks `team_id`, `team_name`
6. `get_match_info.php` → checks `match_id`, team IDs
7. `GET /asj/masterdata/players` → checks 200

## 2. Result

**7/7 passed** against the live stub server.

## 3. Limitation

This tests the stub server, not the real client. True "real testing"
needs the patched APK running on a device/emulator against the stub.
