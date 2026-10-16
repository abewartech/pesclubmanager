# Dynamic Analysis Plan: Server Slot Read Path

## Goal

Confirm at runtime which of the 14 `onlineapi::ServerData` URL slots is selected/read by the client, especially the observed value `0x5`.

## Static Evidence Already Confirmed

- URL table: `0x0078252f8`, 14 entries.
- Slot 5 = `asjrsc.konaminet.jp/asj/`.
- `Init()` reads `server_code`, normalizes it, and stores it into the `ServerData` singleton.
- `GetResourceUrl(..., SERVER_CODE)` reads the configured download slot when `SERVER_CODE == -1`.

## Offline-Only Setup

1. Use an Android emulator or test device, not production.
2. Map the host used by slot 5 to the local mock server in the device/emulator hosts file:

   ```text
   <host-lan-ip> asjrsc.konaminet.jp
   ```

3. Run the local mock server on the development machine.
4. Start Frida server on the emulator/device.
5. Launch PES Club Manager with the Frida script:

   ```sh
   frida -U -f jp.konami.pesclubmanager -l scripts/frida_onlineapi_server_slot.js
   ```

## Expected Evidence

- `ServerData::Init()` logs `GetAPIServer()`.
- `SetDownloadServer(slot=...)` logs the configured slot.
- `GetResourceUrl(...)` logs the requested slot argument and resulting host/path.
- `ChangeDownloadServer(...)` logs runtime slot changes.

If the runtime path reads slot 5, `GetResourceUrl` should resolve to `asjrsc.konaminet.jp/asj/...`.

## Safety

- No production servers are contacted.
- All traffic is redirected to the local mock server.
- Only static/dynamic analysis and logging are performed.
