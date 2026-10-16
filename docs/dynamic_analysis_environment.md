# Dynamic Analysis Environment — PES Club Manager (offline)

Dokumen ini merangkum environment dynamic analysis yang dipakai untuk memverifikasi server slot (termasuk value `0x5`) dan menyiapkan stub masterdata `/data/masterdata/`.

## Safety

- Semua pengujian dilakukan offline/local.
- Tidak ada probing/fuzz ke server production.
- Traffic diarahkan ke proxy/mock lokal.

## Komponen yang disiapkan

### Emulator

- AVD: `Small_Phone` (Android 37)
- Aplikasi: `jp.konami.pesclubmanager` 4.5.1 terinstall
- Emulator dijalankan tanpa window:

```sh
/Users/it-admiinistrator/Library/Android/sdk/emulator/emulator \
  -avd Small_Phone \
  -no-window -no-audio -no-boot-anim
```

### Proxy logging

- `mitmdump` berjalan di `10.0.2.2:8080`
- Addon: `scripts/mitm_log_responses.py`
- Output:
  - `analysis/dynamic_mock_responses/*.txt` (request + response)
  - `analysis/dynamic_mock_responses/*.json` (response JSON jika content-type JSON)

Menjalankan proxy:

```sh
cd /Users/it-admiinistrator/Documents/apps/web-sos-indonesia/others/pesclubmanager
nohup mitmdump -p 8080 -s scripts/mitm_log_responses.py \
  > /tmp/mitmdump.log 2>&1 &
```

Proxy sistem emulator:

```sh
adb shell settings put global http_proxy 10.0.2.2:8080
adb shell settings get global http_proxy
```

### Frida script

Script yang disiapkan:

- `scripts/frida_onlineapi_server_slot.js`

Hook utama:

- `onlineapi::ServerData::Init()`
- `onlineapi::ServerData::SetDownloadServer(SERVER_CODE)`
- `onlineapi::ServerData::GetResourceUrl(path, SERVER_CODE)`
- `onlineapi::ServerData::ChangeDownloadServer(...)`

Tujuan:

- Membuktikan slot yang benar-benar dibaca client saat runtime, khususnya value `0x5`.

## Hasil statis yang akan diverifikasi runtime

Tabel server URL mulai di `0x0078252f8` dengan 14 entri:

| Slot | Host/Path |
|---:|---|
| 0 | `asj.s.konaminet.jp/asj/` (production API) |
| 5 | `asjrsc.konaminet.jp/asj/` |
| 6 | `localhost/asj/trunk/` |
| 13 | `stg-asj11.konaminet.jp/asj/` |

Claim working: value `0x5` mengarah ke slot 5 (`asjrsc.konaminet.jp/asj/`). Klaim final baru valid bila Frida log runtime menunjukkan `slotArg=5` atau host `asjrsc.konaminet.jp`.

## Roster / Masterdata

- Roster tidak tersedia di OBB.
- Data pemain/tim/liga di-download dari server melalui path `/data/masterdata/...`.
- Asset 3D/tekstur/animasi tetap lokal dari OBB.
- Stub server hanya perlu melayani data masterdata sesuai shape response observasi.

## Langkah operasi

1. Jalankan emulator + proxy.
2. Launch app PES CM.
3. Trigger flow startup/masterdata.
4. Kumpulkan file di `analysis/dynamic_mock_responses/`.
5. Analisis schema request/response dari capture.
6. Update stub `/data/masterdata/` berdasarkan observasi, bukan tebakan statis.
7. Setelah slot terbukti lewat Frida, finalkan mapping slot 5.

## Catatan keterbatasan

Beberapa image Android yang tersedia tidak root/debuggable, nên Frida gadget mungkin dibutuhkan untuk instrumentasi penuh. Demikian pula HTTPS dapat memerlukan CA trust setup tambahan. Untuk evidence slot level, log hal-hal yang dinyatakan di Frida script tetap menjadi target utama.
