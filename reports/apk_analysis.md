# APK / Package Analysis

Workspace: `C:\Users\rahma\Documents\projects\abe\reverse_engineering`

APK: `PES-CLUB-MANAGER-v4-5-1.apk`

Decoded output: `extracted/apktool/PES-CLUB-MANAGER-v4-5-1`

Tool used: `apktool_3.0.3.jar`

## Package Information

| Field | Value | Evidence | Confidence |
|---|---|---|---|
| Package name | `jp.konami.pesclubmanager` | `AndroidManifest.xml` | CONFIRMED |
| Version code | `104050101` | `apktool.yml`, `AndroidManifest.xml` | CONFIRMED |
| Version name | `4.5.1` | `apktool.yml`, `AndroidManifest.xml` | CONFIRMED |
| Min SDK | `21` | `apktool.yml` | CONFIRMED |
| Target SDK | `29` | `apktool.yml` | CONFIRMED |
| App label | `PESCM` | `res/values/strings.xml` | CONFIRMED |
| Install location | `internalOnly` | `AndroidManifest.xml` | CONFIRMED |
| Backup allowed | `false` | `AndroidManifest.xml` | CONFIRMED |

## Engine Metadata

| Field | Value | Confidence |
|---|---|---|
| Engine | Unreal Engine 4 | CONFIRMED |
| Engine version | `4.22.3` | CONFIRMED |
| Engine branch | `++UE4+Release-4.22` | CONFIRMED |
| Project name | `PesMobile` | CONFIRMED |
| Build configuration | `Shipping` | CONFIRMED |
| Cooked texture flavor | `ETC1` | CONFIRMED |
| OBB files enabled | `true` | CONFIRMED |
| Package data inside APK | `false` | CONFIRMED |
| Use external files dir | `true` | CONFIRMED |
| Verify OBB on startup | `false` | CONFIRMED |
| Vulkan support flag | `true` | CONFIRMED |

## Permissions

Declared permissions include:

| Permission | Likely purpose | Confidence |
|---|---|---|
| `android.permission.INTERNET` | Online services, downloads, SDK calls. | HIGH |
| `android.permission.ACCESS_NETWORK_STATE` | Network availability checks. | HIGH |
| `android.permission.ACCESS_WIFI_STATE` / `CHANGE_WIFI_*` | Network/download behavior and local connectivity features. | MEDIUM |
| `android.permission.BLUETOOTH` / `BLUETOOTH_ADMIN` | Konami peer/Bluetooth features. | MEDIUM |
| `android.permission.READ_EXTERNAL_STORAGE` / `WRITE_EXTERNAL_STORAGE` | OBB/assets/downloads/local files. | HIGH |
| `android.permission.WAKE_LOCK` | Keep device awake during game/download. | HIGH |
| `android.permission.VIBRATE` | Haptics/notifications. | MEDIUM |
| `com.android.vending.BILLING` | In-app billing. | HIGH |
| `com.android.vending.CHECK_LICENSE` | Google Play expansion/LVL flow. | HIGH |
| `com.google.android.c2dm.permission.RECEIVE` | Firebase/GCM push messaging. | HIGH |

## Components

### Main Activities

| Component | Role hypothesis | Confidence |
|---|---|---|
| `com.epicgames.ue4.SplashActivity` | Launcher splash activity. | HIGH |
| `com.epicgames.ue4.GameActivity` | Unreal Engine game activity, loads native `UE4` library. | CONFIRMED |
| `jp.konami.pesclubmanager.DownloaderActivity` | OBB downloader/checker. | HIGH |
| `jp.konami.ExpansionDownloader.DownloaderActivity` | Konami expansion downloader wrapper. | HIGH |

### Services / Receivers / Providers

| Component | Role hypothesis | Confidence |
|---|---|---|
| `jp.konami.pesclubmanager.OBBDownloaderService` | OBB download service. | HIGH |
| `jp.konami.ExpansionDownloader.DownloaderServiceSub` | Expansion download service. | HIGH |
| `jp.konami.android.common.FirebaseMessagingServiceDerived` | Push messaging. | HIGH |
| `jp.konami.android.common.FirebaseInstanceIdServiceDerived` | Firebase instance/token handling. | HIGH |
| `com.facebook.FacebookContentProvider` | Facebook SDK integration. | HIGH |
| `com.google.firebase.provider.FirebaseInitProvider` | Firebase initialization. | HIGH |

## Deep Links

| Scheme / host | Source | Purpose hypothesis | Confidence |
|---|---|---|---|
| `pesclubmanager://` | `GameActivity` intent filter | App-specific deep link. | HIGH |
| `pesclubmanager://konaminet.jp` | `GameActivity` intent filter and `twitter_callback_url` resource | Login/social callback or campaign callback. | MEDIUM |
| `pescmgetparam://konaminet.jp` | `GameActivity` intent filter | Parameter handoff callback. | MEDIUM |
| `fbconnect://cct.jp.konami.pesclubmanager` | Facebook `CustomTabActivity` intent filter | Facebook custom tab login callback. | HIGH |

## Native Libraries

| ABI | Library | Size | Purpose hypothesis | Confidence |
|---|---|---:|---|---|
| `arm64-v8a` | `libUE4.so` | 120.34 MB | Unreal native runtime/game code. | CONFIRMED |
| `arm64-v8a` | `libafp-core.so` | 1.34 MB | Third-party/native SDK component; exact role unknown. | LOW |
| `arm64-v8a` | `libavs2-core.so` | 0.47 MB | Third-party/native SDK component; exact role unknown. | LOW |
| `armeabi-v7a` | `libUE4.so` | 99.31 MB | Unreal native runtime/game code. | CONFIRMED |
| `armeabi-v7a` | `libafp-core.so` | 1.13 MB | Third-party/native SDK component; exact role unknown. | LOW |
| `armeabi-v7a` | `libavs2-core.so` | 0.37 MB | Third-party/native SDK component; exact role unknown. | LOW |

## Bytecode / Smali

| Item | Value | Confidence |
|---|---:|---|
| Dex files in APK | `classes.dex`, `classes2.dex` | CONFIRMED |
| Smali files decoded | 8,919 | CONFIRMED |

Interesting decoded packages/classes:

| Package/class | Observed role | Confidence |
|---|---|---|
| `com.epicgames.ue4.*` | Unreal Android bootstrap/runtime bridge. | HIGH |
| `jp.konami.pesclubmanager.*` | PESCM package-specific Android wrapper/downloader classes. | HIGH |
| `jp.konami.pescm.NativeLibLoader` | Native bridge/helper class. | HIGH |
| `jp.konami.ExpansionDownloader.*` | OBB expansion download/check logic. | HIGH |
| `jp.konami.android.inappbilling.*` and `jp.konami.android.common.iab.*` | In-app billing wrappers. | HIGH |
| `jp.konami.android.common.*` | Shared Konami Android utility/network/social classes. | HIGH |
| `jp.applilink.sdk.*` | Konami Applilink SDK integration. | MEDIUM |
| `com.facebook.*`, `com.google.firebase.*`, `com.ironsource.*`, `twitter4j.*` | Third-party social, ads, messaging, and sharing SDKs. | HIGH |

## Assets / Resources

APK assets are minimal:

| Asset | Purpose hypothesis | Confidence |
|---|---|---|
| `assets/link_file_000.html` | Static SDK/app web content or legal/link page. | MEDIUM |
| `assets/open_source_license.html` | Open source license disclosure. | HIGH |

Most game content is expected in OBB/Pak/CPK containers, not in APK resources.

Confidence: HIGH

## OBB Metadata

| Metadata | Value | Confidence |
|---|---|---|
| `VersionObb0` / `ExpVersionMain` | `104050101` | CONFIRMED |
| `VersionObb1` | `104050101` | CONFIRMED |
| `FileSizeObb0` / `ExpFileSizeMain` | `789485556` | CONFIRMED |
| `FileSizeObb1` | `873229528` | CONFIRMED |
| `FileHashObb0` / `ExpFileHash` | `8678ef9e8bdd078a58f23cb5a6d115c3` | CONFIRMED |
| `FileHashObb1` | `16ab5526bd221eca09aec3d421e41195` | CONFIRMED |

Note: These manifest hashes appear to be app-defined hashes for OBB validation, not SHA-256. The SHA-256 hashes are recorded in `reports/inventory.md`.

## Static Network Seeds

No network requests were made. These are strings found statically.

| String/domain | Source | Purpose hypothesis | Confidence |
|---|---|---|---|
| `https://asj.s.konaminet.jp/asj/facebook/share/images/share_` | `jp.konami.android.common.TwitterLink`, `SnsLauncher`, `Facebook$4` | Social sharing image URL prefix. | HIGH |
| `http://www.konami.jp/pescm` | `TwitterLink`, `SnsLauncher` | Public PESCM URL. | HIGH |
| `https://www.konami.com/wepes/mobile/pescm` | `TwitterLink`, `SnsLauncher`, `Facebook$4` | Public PESCM URL. | HIGH |
| `http://www.konami.jp` | `KWebDialog` | Default web dialog URL. | MEDIUM |
| `lnk-stg.pvt.mo.konami.net` | `jp.applilink.sdk.common.ApplilinkConsts$Environment` | Staging Applilink host. | MEDIUM |
| `lnk-dev.pvt.mo.konami.net` | `jp.applilink.sdk.common.ApplilinkConsts$Environment` | Development Applilink host. | MEDIUM |
| `ObbDownload.url` | `jp.konami.ExpansionDownloader.DownloaderManager` | Asset key or config filename for OBB download URL. | HIGH |

## Local Storage Seeds

| String/class | Source | Purpose hypothesis | Confidence |
|---|---|---|---|
| `/Android/obb/` | `com.android.vending.expansion.zipfile.APKExpansionSupport` | Standard Android OBB path. | HIGH |
| `main.` / `patch.` / `.obb` | Expansion helper classes | OBB filename construction. | HIGH |
| `download.dat` | `jp.konami.android.common.HttpRequest` | Download state/temp metadata. | MEDIUM |
| `.downloadtmp` | `jp.konami.android.common.HttpDownloadImpl` | Temporary download suffix. | HIGH |
| `DownloadColumns` | Google expansion downloader `DownloadsDB` | Downloader SQLite table. | HIGH |

## Encryption / Serialization Seeds

| String/class | Source | Purpose hypothesis | Confidence |
|---|---|---|---|
| `RSA` | `jp.konami.android.inappbilling.Security`, `jp.konami.android.common.iab.util.Security` | Google Play billing signature verification. | HIGH |
| `AES` | `jp.applilink.sdk.common.util.EncryptionUtils` | Applilink SDK encryption helper. | MEDIUM |

These are SDK-level indicators. They do not yet prove encryption of player/save data.

## Initial Interpretation

The APK is mainly an Android/Unreal launcher and SDK wrapper. The game logic and data are likely concentrated in:

1. `libUE4.so`
2. `main.104050101.jp.konami.pesclubmanager.obb` -> `PesMobile/Content/Paks/PesMobile-Android_ETC1.pak`
3. `patch.104050101.jp.konami.pesclubmanager.obb` -> likely CPK container

## Unknowns / Next Experiments

| Unknown | Next experiment |
|---|---|
| Exact contents of Unreal `.pak` | Extract/list OBB into `extracted/obb_main/`, then inspect `.pak` header/index read-only. |
| Exact contents of CPK patch OBB | Identify a local CPK-capable tool or write a read-only header parser. |
| Native JNI exports and game strings | Run native library analysis against extracted `libUE4.so`, `libafp-core.so`, and `libavs2-core.so`. |
| Player/team database location | Search extracted PAK/CPK and native strings for player/team/schema terms. |
