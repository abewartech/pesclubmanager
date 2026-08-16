# PES Club Manager Reverse Engineering

Workspace: `C:\Users\rahma\Documents\projects\abe\reverse_engineering`

Status: Work in progress. Current checkpoint covers inventory, engine identification, APK/package analysis, and initial native analysis. No game files were modified.

## 1. Game Information

| Field | Value | Confidence |
|---|---|---|
| Package | `jp.konami.pesclubmanager` | CONFIRMED |
| Version | `4.5.1` | CONFIRMED |
| Version code | `104050101` | CONFIRMED |
| App label | `PESCM` | CONFIRMED |
| Project name | `PesMobile` | CONFIRMED |

## 2. File Inventory

Full report: `reports/inventory.md`

Key artifacts:

| Artifact | SHA-256 | Notes |
|---|---|---|
| `PES-CLUB-MANAGER-v4-5-1.apk` | `27113d1114bf9668ed9afa3831bbccda1ac3dcb271deec1c10cad163132a353e` | Primary APK. |
| `main.104050101.jp.konami.pesclubmanager.obb` | `705eb0cc1024ae9c459fd3e719e1744ed34b36e1082a2765b0d399e1140fbe86` | ZIP-style OBB containing Unreal `.pak`. |
| `patch.104050101.jp.konami.pesclubmanager.obb` | `e6b194d430b7b095e6179645714d5da429e6566205eb7ccde7ea6169505ff1db` | CPK-like OBB. |

Preserved copies are in `original/`.

## 3. Engine

Full report: `reports/engine.md`

Engine: Unreal Engine 4.22.3

Confidence: CONFIRMED

Evidence:

| Evidence | Confidence |
|---|---|
| Manifest metadata `com.epicgames.ue4.GameActivity.EngineVersion=4.22.3`. | CONFIRMED |
| Native library `libUE4.so` exists for `arm64-v8a` and `armeabi-v7a`. | CONFIRMED |
| Main OBB contains `PesMobile/Content/Paks/PesMobile-Android_ETC1.pak`. | HIGH |

## 4. APK Structure

Full report: `reports/apk_analysis.md`

Decoded APK path: `extracted/apktool/PES-CLUB-MANAGER-v4-5-1`

Important APK findings:

| Area | Finding | Confidence |
|---|---|---|
| Manifest | Launcher is `com.epicgames.ue4.SplashActivity`; game activity is `com.epicgames.ue4.GameActivity`. | CONFIRMED |
| Native libs | `libUE4.so`, `libafp-core.so`, `libavs2-core.so` for ARM64 and ARMv7. | CONFIRMED |
| OBB | App expects main and patch OBB version `104050101`. | CONFIRMED |
| SDKs | Firebase, Facebook, Google Play Games/Services, IronSource, Twitter4J, Konami Applilink, billing/downloader libraries. | HIGH |
| Java layer | Mostly Android wrappers, SDK glue, downloader, billing, native bridge. | HIGH |

## 5. Native Libraries

Full report: `reports/native_analysis.md`

Important native finding:

`libUE4.so` is the primary analysis target. It contains demangleable symbols for gameplay/data areas such as `match`, `menu`, `onlineapi`, `onlinemode`, `tmpdb`, `sys::SaveData`, and `systemdata`.

## 6. Managed Code

No Unity Mono/IL2CPP managed gameplay assembly was found. APK Java/Smali code exists, but current evidence indicates gameplay/data logic is mainly native Unreal code.

Confidence: HIGH

## 7. Assets

Known:

| Artifact | Finding | Confidence |
|---|---|---|
| Main OBB | Contains `PesMobile/Content/Paks/PesMobile-Android_ETC1.pak`. | HIGH |
| Patch OBB | Header starts with `CPK`. | HIGH |

Detailed asset extraction/listing is pending.

## 8. Database

Pending. No standalone `.db`/`.sqlite` game database has been confirmed yet.

## 9. Player Data

Confirmed leads:

| Lead | Evidence | Confidence |
|---|---|---|
| `tmpdb::Player` native model | `libUE4.so` exported symbols. | HIGH |
| `onlinemode::ParameterPlayerDefine` | Ability accessor references `tmpdb::Player::Ability`. | HIGH |
| `ParameterTeam::GetPlayerBySerialIdConst` | Native exported symbol. | HIGH |
| CPK path `cpk_dat/common/anime/playerID/bin/Definedatatable.bin` | Native string. | HIGH |

Exact field offsets/types are not known yet.

## 10. Team Data

Confirmed leads:

| Lead | Evidence | Confidence |
|---|---|---|
| `onlinemode::ParameterTeam` | Native symbols. | HIGH |
| `TEAMID_*` constants | Native strings. | HIGH |
| League constants such as `LEAGUE_ENG1`, `LEAGUE_JPN1`, `LEAGUE_KONAMI` | Native strings. | HIGH |

## 11. Save Data

Confirmed leads:

| Lead | Evidence | Confidence |
|---|---|---|
| `sys::SaveData` | Native exported symbols. | HIGH |
| `systemdata::SystemData::SaveTutorialState` | Native exported symbol. | HIGH |
| Unreal `Saved/` and `CPF_SaveGame` strings | Native strings. | MEDIUM |

Actual save file path/format is pending.

## 12. Serialization

Confirmed:

| Serialization | Evidence | Confidence |
|---|---|---|
| JSON | `onlineapi::*Serialize(Json::Value&)` and `Deserialize(Json::Value const&)` symbols. | HIGH |
| Unreal object/package serialization | Unreal engine strings. | HIGH |

## 13. Encryption

Current indicators:

| Indicator | Evidence | Confidence |
|---|---|---|
| OpenSSL-style crypto symbols | `libUE4.so`. | MEDIUM |
| `RSA` billing verification | Smali billing classes. | HIGH |
| `AES` Applilink helper | Smali Applilink SDK. | MEDIUM |
| `EAUDP_ENCRYPT` | `libavs2-core.so`. | MEDIUM |

No confirmed save-data encryption key or algorithm yet.

## 14. Network Endpoints

Static-only seeds found so far:

| Domain / URL | Context | Confidence |
|---|---|---|
| `https://asj.s.konaminet.jp/asj/facebook/share/images/share_` | Social sharing image prefix. | HIGH |
| `http://www.konami.jp/pescm` | Public PESCM URL. | HIGH |
| `https://www.konami.com/wepes/mobile/pescm` | Public PESCM URL. | HIGH |
| `lnk-stg.pvt.mo.konami.net` | Applilink staging host. | MEDIUM |
| `lnk-dev.pvt.mo.konami.net` | Applilink development host. | MEDIUM |

No network requests were made.

## 15. Important Classes

| Class/namespace | Why it matters | Confidence |
|---|---|---|
| `com.epicgames.ue4.GameActivity` | Android entry into Unreal native runtime. | HIGH |
| `jp.konami.pescm.NativeLibLoader` | Native bridge/helper. | HIGH |
| `jp.konami.pesclubmanager.OBBData` | OBB metadata wrapper. | HIGH |
| `tmpdb::Player` | Player data lead. | HIGH |
| `onlinemode::ParameterPlayerDefine` | Player parameter/ability accessor lead. | HIGH |
| `onlineapi::*` | Native API request/response models. | HIGH |

## 16. Important Functions

| Function/symbol | Why it matters | Confidence |
|---|---|---|
| `onlinemode::ParameterPlayerDefine::GetAbilityParameter(tmpdb::Player::Ability)` | Player ability field access lead. | HIGH |
| `tmpdb::Match::CopyMatchPlayer(tmpdb::Player*, ...)` | Player record movement/copy lead. | HIGH |
| `onlinemode::ParameterTeam::GetPlayerBySerialIdConst(unsigned long)` | Team/player relationship lead. | HIGH |
| `CHttpAsyncRequest::SetSaveFilePath(char const*)` | Download-to-file path lead. | HIGH |
| `onlineapi::*::Serialize/Deserialize` | API JSON schema lead. | HIGH |

## 17. Data Structures

Pending. Do not infer binary structs yet.

## 18. Findings

1. APK/game is Unreal Engine 4.22.3, not Unity.
2. Gameplay/data logic is likely in `libUE4.so` and OBB containers.
3. `libUE4.so` retains many useful demangleable C++ names.
4. Main OBB contains Unreal `.pak`; patch OBB appears CPK-like.
5. Player/team/save leads exist but field layouts are not yet confirmed.

## 19. Hypotheses

| Hypothesis | Evidence | Confidence | Next experiment |
|---|---|---|---|
| Player master/local structures can be recovered via `tmpdb::Player` and `ParameterPlayerDefine`. | Native symbols. | HIGH | Disassemble these functions and inspect struct offsets. |
| Main game assets are in Unreal `.pak`; some patch/playerID data is in CPK. | OBB listing and native CPK path strings. | HIGH | Read-only list/extract containers into `extracted/`. |
| API schemas are JSON and recoverable from native symbols/string refs. | `onlineapi::*Serialize/Deserialize`. | HIGH | Analyze specific request/response functions. |

## 20. Unknowns

| Unknown | Next step |
|---|---|
| Exact player/team field layout | Native disassembly and data file extraction. |
| Exact save file path/format | Follow `sys::SaveData` and inspect runtime file path strings. |
| CPK contents | Build or use read-only CPK listing. |
| Unreal `.pak` encryption/compression status | Inspect `.pak` header/index after extracting main OBB. |

## 21. Next Steps

1. Extract/list main OBB ZIP into `extracted/obb_main/`.
2. Inspect `PesMobile-Android_ETC1.pak` header/index read-only.
3. Identify/list patch OBB CPK contents.
4. Generate focused string/symbol reports for `tmpdb`, `ParameterPlayerDefine`, `ParameterTeam`, `SaveData`, and `onlineapi`.
5. Only after data formats are understood, consider offline/local-only modification possibilities.
