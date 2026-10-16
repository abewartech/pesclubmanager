# Stage 24 — Request Format & Minimal Stub Server

## Scope

Continues the stub-server track (Stage 23): pin down the HTTP request
format and ship a minimal working stub. Read-only RE + a new
research tool. The game is discontinued (2021-12-15); this is
preservation work.

## 1. Request format (verified from `.rodata`)

- Method: `POST` (libcurl; `Content-Type: application/x-www-form-urlencoded`)
- URL: `https://<domain>/asj/<endpoint>.php`
- Body: `param=<json>&addParam=...`
- The JSON body is the Stage 23 template:
  `{"auth_code":"","ms_ver":0,"res_ver":0,"session_id":"","tutorial":0,"user_code":"","user_id":0}`

## 2. Stub server (`scripts/s24_01_stub_server.py`)

- Plain-Python `http.server` on localhost (default `:8080`).
- Handles `POST /asj/*.php`: parses form body, pretty-prints params,
  extracts `param` JSON keys, returns canned JSON per endpoint.
- Canned: `top.php` → session + server_time + maintenance flag;
  `debug_login.php` → debug session; everything else → `{"result":0}`.
- Purpose is **observation**: run it, point the client at it, and log
  which endpoints the client actually hits during boot. It does not
  emulate game logic.

## 3. Verified

- `py_compile` clean.
- Live test: `POST /asj/top.php` with a sample `param` JSON returns
  the canned session response; request params and JSON keys are
  logged.

## 4. Blockers for a real device test

- The client speaks **HTTPS**. Testing on device needs either a
  user-installed CA + MITM proxy, or a client patch to plain HTTP.
- Response schemas per endpoint are still unknown (server is dead;
  schemas must be inferred from client parsing code).
- The `localhost/asj/trunk/` table entry suggests the client can be
  switched without patching, but the selection code path was not
  located.

## 5. Next

Trace the boot sequence: which endpoint is hit first, and what the
client does with the response. That determines the minimum viable
stub responses.
