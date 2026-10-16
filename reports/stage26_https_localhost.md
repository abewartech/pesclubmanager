# Stage 26 — HTTPS to Localhost

## Scope

User request: solve the HTTPS problem for redirecting the client to
a localhost stub server. Static RE, read-only.

## 1. Findings

### Certificate pinning: YES

`.rodata` @ `0x64a7eaf` contains:

```
"not match pinned public key. SSL server certificate status verification FAILED."
```

The client pins the server's public key. A MITM proxy with a
user-installed CA will NOT work — the client compares the cert's
public key against a pinned value and fails closed.

- The pinning check code was not located via static trace (no `adrp`
  refs to the string page; likely invoked through a function pointer
  or inlined in the curl SSL callback).
- The pinned key material itself was not found as a nearby base64
  blob; it may be raw DER bytes elsewhere.
- Java layer (`classes.dex`) has only stock `TrustManager` /
  `HostnameVerifier` references (jmdns, applilink SDK) — no custom
  Java pinning. Pinning is native.

### Scheme selection

Config struct (Stage 25) holds both schemes:

```
0x78352e8 -> "http://"
0x78352f0 -> "https://"
```

The client builds URLs as `<scheme><server>/asj/<endpoint>.php`.
Which slot is read per request was not traced.

## 2. Options to reach localhost

| # | Approach | Effort | Risk |
|---|----------|--------|------|
| A | Binary-patch `https://` → `http://` (overwrite the 8-byte pointer at `0x78352f0` to point at the `http://` string, or patch the string bytes in place with padding) | Low | Client may still try TLS on port 443; stub must serve plain HTTP on the expected port |
| B | Patch out the pinning check (NOP the verification callback) | Medium | Need to locate the check first |
| C | Extract the pinned public key, generate a cert with the same keypair | Impossible | We don't have Konami's private key |
| D | Use the `localhost/asj/trunk/` table entry via build config | Unknown | Selection mechanism not found |

**Recommended: Option A.** It sidesteps TLS entirely. The stub
server (Stage 24) already speaks plain HTTP. The remaining question
is which scheme slot the API client reads — that determines the
exact patch target.

## 3. Concrete patch (Option A, pending validation)

Target: `libUE4.so`, file offset of virtual `0x78352f0`.

```
# backup original
cp libUE4.so libUE4.so.bak
# overwrite the 8-byte LE pointer at file offset (0x78352f0 - .data vaddr + .data offset)
# new value: 0x64dd29b (address of "http://")
```

After patching, repack the APK (apktool), re-sign, and install.
The client will then issue plain-HTTP requests to whatever server
the table points at; combine with patching the server pointer
(Stage 25, Option A) to aim at `127.0.0.1`.

## 4. Not done

- Dynamic validation (needs emulator/device + patched APK).
- Locating the exact scheme/server slot read per API call.
- Response schemas (still the biggest blocker for playability).
