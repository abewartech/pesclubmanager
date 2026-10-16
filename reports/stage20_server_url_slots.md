# Stage 20: Server URL Slot Confirmation

## Summary

Static extraction of `libUE4.so` (`onlineapi::ServerData`) confirms the 14-entry URL server table used by the PES Club Manager client.

The table starts at virtual address `0x0078252f8` and contains 14 consecutive qword pointers. Each entry maps directly to one of the server strings recovered from `.rodata`:

| Slot | Host/path |
|---:|---|
| 0 | `asj.s.konaminet.jp/asj/` (production API) |
| 1 | `asj.konaminet.jp/asj/` |
| 2 | `dev-asj001.s.konaminet.jp/asj/` |
| 3 | `dev-asj001.konaminet.jp/asj/` |
| 4 | `chk-asj001.s.konaminet.jp/asj/` |
| 5 | `asjrsc.konaminet.jp/asj/` |
| 6 | `localhost/asj/trunk/` |
| 7 | `asjmng01.konaminet.jp/asj/` |
| 8 | `graph.facebook.com/` |
| 9 | `chk-asj001.konaminet.jp/asj/` |
| 10 | `stg-asj.s.konaminet.jp/asj/` |
| 11 | `stg-asj.konaminet.jp/asj/` |
| 12 | `stg-asj11.s.konaminet.jp/asj/` |
| 13 | `stg-asj11.konaminet.jp/asj/` |

## Value `0x5`

The observed value `0x5` maps to slot **5**:

```text
asjrsc.konaminet.jp/asj/
```

This is consistent with resource/download-server selection:

- `onlineapi::ServerData::GetResourceUrl(..., SERVER_CODE)` loads the configured download server slot before building the resource URL.
- `onlineapi::ServerData::SetDownloadServer(SERVER_CODE)` writes that active slot.
- `onlineapi::ServerData::Init()` reads the `server_code` config value and clamps it against the available table range, then stores it into the `ServerData` singleton.

## Caveat

This is static evidence only. It confirms the table layout and the slot that index 5 points to, but dynamic analysis on a running client is still required to prove the live read path and any runtime/config override behavior.

Machine-readable output:

- `analysis/stage20_server_url_slots/server_url_slots.json`
