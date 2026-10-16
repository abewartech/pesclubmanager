# Stage 30 — Patched APK Build

## Scope

User request: build the patched APK with `https://` → `http://` and
server → localhost. First patched build.

## 1. Binary patches (libUE4.so)

| VA | Old | New |
|----|-----|-----|
| `0x78352f0` | `0x64dd2a3` ("https://") | `0x64dd29b` ("http://") |
| `0x78352f8` | `0x64dd128` ("asj.s.konaminet.jp/asj/") | `0x64dd1ca` ("localhost/asj/trunk/") |

Both patches verified by re-reading the patched binary.

**Effect**: the client now builds API URLs as
`http://localhost/asj/trunk/<endpoint>.php` instead of
`https://asj.s.konaminet.jp/asj/<endpoint>.php`.

This sidesteps both TLS and certificate pinning (Stage 26).

## 2. APK repack

- Method: direct `.so` replacement in the APK zip (no manifest/resource
  changes, so apktool not needed).
- Verified: no duplicate zip entries.
- Signed with a fresh self-signed key (`patch.keystore`, RSA-2048).
- `apksigner verify` passes (warnings about unprotected META-INF
  version files only — harmless).

## 3. Artifact

`builds/pescm-patched-v1.apk` (84 MB, signed).

**Not for distribution** — research build for dynamic analysis only.
Install on a test device/emulator with the stub server
(`scripts/s24_01_stub_server.py`) running on the device's localhost.

## 4. Not tested

- No emulator available in this environment (no KVM, 1 GB RAM).
- Client boot against the stub has not been observed yet.
- The 168 `onlineapi::` operations are not yet stubbed (only the
  generic canned responses).

## 5. Next

1. Install on a real device/emulator.
2. Run the stub server on-device (or port-forward).
3. Observe the boot sequence; stub `AuthUser`/`CheckUpdate`/`Login`.
