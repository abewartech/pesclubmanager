# Stage 33 — Boot Sequence Stubs

## Scope

Add `AuthUser`, `CheckUpdate`, and `Login` stubs to the stub server
(boot sequence per Stage 29).

## 1. New endpoints (`scripts/s24_01_stub_server.py`)

| Endpoint | Response |
|----------|----------|
| `auth_user.php` | `result=0`, session, auth_code, user_code, user_id |
| `check_update.php` | `result=0`, `update_required=0`, latest versions |
| `login.php` | `result=0`, session, `tutorial=0` |

All return `result: 0` (success) with minimal fields. Schemas are
best-guess from naming patterns; refine from proxy observations.

## 2. Verified

- `py_compile` clean.
- Live test: all three endpoints return 200 with expected JSON.

## 3. Next

Observe the actual boot sequence from the patched APK; adjust field
names/values based on what the client actually parses.
