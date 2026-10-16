# Stage 25 — Server Selection Code & Patch Strategy

## Scope

User request: find the server-selection code to redirect the client
to localhost. Static RE, read-only.

## 1. Server config struct (`.data` @ `0x78352a0`)

Decoded layout:

```
0x78352a0: UI config keys (expand_R, expand_L, expand_none, ...)
0x78352d8: 0xffffffff (separator)
0x78352e0: "?uc="            (query prefix)
0x78352e8: "http://"
0x78352f0: "https://"
0x78352f8: [0]  asj.s.konaminet.jp/asj/      <- API prod (SSL)
0x7835300: [1]  asj.konaminet.jp/asj/        <- API prod
0x7835308: [2]  dev-asj001.s.konaminet.jp/asj/
0x7835310: [3]  dev-asj001.konaminet.jp/asj/
0x7835318: [4]  chk-asj001.s.konaminet.jp/asj/
0x7835320: [5]  asjrsc.konaminet.jp/asj/      <- resources
0x7835328: [6]  localhost/asj/trunk/         <- LOCAL OVERRIDE
0x7835330: [7]  asjmng01.konaminet.jp/asj/
0x7835338: [8]  graph.facebook.com/
0x7835340: [9]  chk-asj001.konaminet.jp/asj/
0x7835348: [10] stg-asj.s.konaminet.jp/asj/
0x7835350: [11] stg-asj.konaminet.jp/asj/
0x7835358: [12] stg-asj11.s.konaminet.jp/asj/
0x7835360: [13] stg-asj11.konaminet.jp/asj/
0x7835368: "release"                        <- build type
0x7835370: 0x5                              <- likely resource-server index
0x7835378: "data/resourcedata/"
0x7835380: "asj.konaminet.jp"               <- fallback domain
```

## 2. Selection code: NOT FOUND

- No `adrp` to the struct page (`0x7835000`) in `.text`.
- No `adrp` to the server-table page (`0x64dd000`) in `.text`.
- The struct is in writable `.data`; likely populated/read via a
  global accessor or JNI, not direct addressing.
- Code refs to the `release` string page lead to UE4 FString init,
  not selection logic.

## 3. Patch strategy (for APK build)

Since the struct is writable and the URL pointers are plain 8-byte
slots, the lowest-risk patch is **binary-level**:

- Option A: overwrite the pointer at `0x78352f8` (index 0, prod API)
  to point at a `localhost/...` string. Requires injecting a new
  string into the binary (or reusing the existing `localhost/asj/trunk/`
  at `0x64dd1ca`).
- Option B: find the index variable and change it to 6. The `0x5`
  at `0x7835370` is a candidate but unconfirmed as the API selector.

Both need validation on a real device/emulator: the client must
actually read the patched slot during boot.

## 4. APK build status

NOT BUILT. Remaining work:
1. Confirm which slot/index the API client reads (dynamic analysis
   or deeper static trace).
2. Handle HTTPS: client expects TLS; localhost needs a cert the
   client trusts (or patch scheme to http://).
3. Response schemas per endpoint (server dead since 2021).
4. Full game-logic emulation for playability.

The stub server (Stage 24) and this config map are the foundation.
The APK build is a multi-stage project, not a single step.
