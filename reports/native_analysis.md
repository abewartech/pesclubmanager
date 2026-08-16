# Native Library Analysis

Workspace: `C:\Users\rahma\Documents\projects\abe\reverse_engineering`

Decoded APK libraries: `extracted/apktool/PES-CLUB-MANAGER-v4-5-1/lib`

Tool used: `radare2/bin/rabin2.exe`

## Scope

This is an initial static native pass. No binary patching, execution, server access, or anti-cheat bypass work was performed.

## Libraries

| ABI | Library | ELF class | Machine | Language | Stripped | Notable properties | Confidence |
|---|---|---|---|---|---|---|---|
| `arm64-v8a` | `libUE4.so` | ELF64 | ARM aarch64 | C++ | true | NX, PIC, full RELRO, stack canary, Android clang 7.0.2 | CONFIRMED |
| `arm64-v8a` | `libafp-core.so` | ELF64 | ARM aarch64 | C | true | NX, PIC, full RELRO, GCC/clang 3.5-era toolchain | CONFIRMED |
| `arm64-v8a` | `libavs2-core.so` | ELF64 | ARM aarch64 | C | true | NX, PIC, full RELRO, clang 3.7.1-era toolchain | CONFIRMED |
| `armeabi-v7a` | `libUE4.so` | ELF32 | ARM EABI5 | C++ | true | NX, PIC, full RELRO, stack canary, Android clang 7.0.2 | CONFIRMED |
| `armeabi-v7a` | `libafp-core.so` | ELF32 | ARM EABI5 | C | true | NX, PIC, full RELRO | CONFIRMED |
| `armeabi-v7a` | `libavs2-core.so` | ELF32 | ARM EABI5 | C | true | NX, PIC, full RELRO | CONFIRMED |

## Native Library Roles

| Library | Role hypothesis | Evidence | Confidence |
|---|---|---|---|
| `libUE4.so` | Main Unreal Engine runtime plus PESCM gameplay/application code. | Manifest loads `UE4`; exports include Unreal, `PesMobile`, `match`, `menu`, `onlineapi`, `tmpdb`, `systemdata` symbols. | HIGH |
| `libafp-core.so` | UI/animation/script runtime component, likely proprietary middleware. | Strings include `afp-*`, `afp_data`, `afp-motion`, `afp-render`, `afp_abc_*`. | MEDIUM |
| `libavs2-core.so` | AVS2 system/network/filesystem/JSON helper middleware. | Strings include `avs_net_*`, `AVS_DTYPE_SOCKET`, `PROP_JSON_*`, `/env/avs2/*`, `EAUDP_ENCRYPT`. | MEDIUM |

## Imported Symbols of Interest

From `libUE4.so` arm64:

| Symbol | Category | Hypothesis | Confidence |
|---|---|---|---|
| `socket`, `connect`, `send`, `sendto`, `recv`, `recvfrom` | Network | Native code can open sockets directly or via bundled networking libraries. | HIGH |
| `AAssetManager_fromJava`, `AAssetManager_open`, `AAsset_getBuffer`, `AAsset_getLength` | Android assets | Native code reads APK assets. | HIGH |
| `dlopen`, `dlsym`, `dlclose` | Dynamic loading | Runtime loads/resolves native symbols dynamically. | HIGH |
| `fopen`, `fdopen`, `read`, `write`, `open`, `close` | Filesystem | Native code reads/writes local files. | HIGH |
| OpenSSL-style symbols such as `RSA_up_ref`, `EVP_CIPHER_CTX_set_flags`, `NCONF_dump_fp` | Crypto/TLS support | `libUE4.so` includes or links OpenSSL-like code. Not evidence of save-data encryption by itself. | MEDIUM |
| libcurl strings and HTTP transfer errors | HTTP stack | Unreal/native HTTP uses libcurl. | HIGH |

## Exported Symbols / Namespaces

Although `libUE4.so` is marked stripped, many exported C++ symbols remain demangleable. This is a major source of structure discovery.

| Namespace / prefix | Examples | Interpretation | Confidence |
|---|---|---|---|
| `match::*` | `match::player::ActionSpaceRun`, `match::registry::PlayerInfo`, `match::TeamFormation`, `match::AnimePlayer` | Match simulation, AI, player animation, registry state. | HIGH |
| `menu::*` | `MarketScoutPoolList`, `ClubDataRecordPlayerStats`, `TeamEditTop`, `CommonPlayerParameter` | UI/menu systems around scouting, club data, team edit, player parameters. | HIGH |
| `onlineapi::*` | `Serialize(Json::Value&)`, `Deserialize(Json::Value const&)`, `GetScoutPlayerList`, `GetScoutPlayerDetail`, `SaveCupTeam` | Native online API request/response models using JSON. | HIGH |
| `onlinemode::*` | `ParameterPlayerDefine`, `ParameterTeam`, `ParameterTown`, `ParameterRankMatchSeason` | Higher-level game state/online-mode parameter models. | HIGH |
| `tmpdb::*` | `tmpdb::Player`, `tmpdb::util`, `tmpdb::Match`, `tmpdb::Competition` | Temporary/local database or loaded game data models. | HIGH |
| `sys::SaveData` / `systemdata::*` | `SaveTutorialState`, `GetFrameSkipSetting`, `SaveDataMigrationServerTime` | Local/system save or settings layer. | HIGH |
| `Cri*` / `cri*` | `criAtomEx*`, `CriMana*` | CRIWARE audio/video middleware. | HIGH |
| `Json::*` | `Json::Value`, `Json::StyledStreamWriter` | JSON serialization/parsing present in native code. | HIGH |

## Data / Player / Team Leads

These are leads, not confirmed field layouts.

| String/symbol | Address / source | Context | Hypothesis | Confidence |
|---|---|---|---|---|
| `tmpdb::Player` | Exported symbols such as `tmpdb::Match::CopyMatchPlayer(tmpdb::Player*, ...)` | Native symbol names. | A native `Player` structure/class exists under `tmpdb`. | HIGH |
| `onlinemode::ParameterPlayerDefine::GetAbilityParameter(tmpdb::Player::Ability)` | `libUE4.so` export | Function name and type reference. | Player ability enum/field accessor exists. | HIGH |
| `match::input::Parameter::SetPlayerParameter(HomeAway, uint, PlayerParameter const&)` | `libUE4.so` export | Match input parameter setup. | Match player parameter structure is passed into match runtime. | HIGH |
| `menu::CommonPlayerParameter` / `menu::MarketPlayerListDetail` | `libUE4.so` exports | UI layers. | Player stats are rendered through menu layer; useful call-chain target. | HIGH |
| `onlinemode::ParameterTeam::GetPlayerBySerialIdConst(unsigned long)` | `libUE4.so` export | Team model accessor. | Team owns or indexes players by serial id. | HIGH |
| `TEAMID_*`, `LEAGUE_*`, `CUP*`, `GROUP_LEAGUE` | `libUE4.so` strings around `0x064aef00+` | ASCII constants. | League/team/competition enum names are embedded. | HIGH |
| `annualSalary_valueText`, `on_notContractMark`, `transfersScout`, `transfersMarket` | `libUE4.so` strings around `0x064b970b+` | UI/data strings. | Contract/salary/transfer UI elements exist. | MEDIUM |
| `cpk_dat/common/anime/playerID/bin/Derivationdatatable.bin` | `libUE4.so` string at `0x064b0048` | CPK data path. | Patch CPK likely contains playerID animation data tables. | HIGH |
| `cpk_dat/common/anime/playerID/bin/Definedatatable.bin` | `libUE4.so` string at `0x064b0082` | CPK data path. | Patch CPK likely contains playerID definition data table. | HIGH |

## Save / Local Data Leads

| String/symbol | Context | Hypothesis | Confidence |
|---|---|---|---|
| `sys::SaveData::GetFrameSkipSetting` | Exported native symbol. | Local settings are exposed through native `sys::SaveData`. | HIGH |
| `sys::SaveData::GetMatchWinCountForReview` | Exported native symbol. | Local save tracks review-related match win count. | MEDIUM |
| `systemdata::SystemData::SaveTutorialState` | Exported native symbol. | Tutorial completion is persisted. | HIGH |
| `systemdata::SystemData::SaveDataMigrationServerTime` | Exported native symbol. | Migration timestamp/server time stored locally or in synced state. | MEDIUM |
| `SaveEncourageDataMigrationTime` | Exported native symbol. | Migration prompt timing is persisted. | MEDIUM |
| Unreal strings `Saved/`, `SaveToUserDir`, `CPF_SaveGame` | Engine strings. | Unreal save/config system is available. Not yet evidence of PESCM-specific save format. | MEDIUM |

## Network / API Leads

| Symbol/string | Context | Hypothesis | Confidence |
|---|---|---|---|
| `onlineapi::*Request::CreateData(Json::Value&, ...)` | Many exported symbols. | Request payloads are built in native code as JSON. | HIGH |
| `onlineapi::*Response::Deserialize(Json::Value const&)` | Many exported symbols. | Response payloads are parsed in native code as JSON. | HIGH |
| `onlineapi::ServerData::SetDownloadServer(SERVER_CODE)` | Exported symbol. | Download server selection exists in native layer. | MEDIUM |
| `CHttpAsyncRequest::SetSaveFilePath(char const*)` | Exported symbol. | Native HTTP supports saving payloads to local files. | HIGH |
| `libUE4.so` imports `socket/connect/send/recv` | Imports. | Native network capability exists. | HIGH |
| `libUE4.so` libcurl error strings | Strings. | HTTP transfers likely use libcurl through Unreal/native code. | HIGH |

No live endpoint probing was performed.

## Encryption / Serialization Leads

| Indicator | Source | Interpretation | Confidence |
|---|---|---|---|
| `Json::Value`, `Serialize`, `Deserialize` | `libUE4.so` exports | Many API models serialize/deserialize JSON. | HIGH |
| `EVP_*`, `RSA_*`, OpenSSL-style symbols | `libUE4.so` exports/imports/strings | Crypto/TLS implementation present. | MEDIUM |
| `EAUDP_ENCRYPT` | `libavs2-core.so` string | AVS2 has encrypted UDP/network mode support. | MEDIUM |
| `PROP_JSON_*` | `libavs2-core.so` strings | AVS2 includes JSON/parser configuration. | MEDIUM |

No confirmed save-data encryption key, IV, or algorithm was identified in this pass.

## High-Value Next Targets

| Target | Why |
|---|---|
| `tmpdb::Player` symbols and nearby xrefs | Best lead for player data structure. |
| `onlinemode::ParameterPlayerDefine` | Likely accessor layer for player ability/identity fields. |
| `onlinemode::ParameterTeam` | Team-to-player relationship lead. |
| `onlineapi::*Serialize/Deserialize` | JSON field names and API schema can be recovered from call chains/strings. |
| `sys::SaveData` / `systemdata::SystemData` | Local save/config persistence lead. |
| `cpk_dat/common/anime/playerID/bin/*.bin` | Concrete asset/data paths likely in CPK patch container. |

## Unknowns

| Unknown | Next experiment |
|---|---|
| Exact player field offsets and primitive types | Analyze `tmpdb::Player` methods and `ParameterPlayerDefine::GetAbilityParameter` in Ghidra/radare2. |
| Whether player/team master data is in `.pak`, CPK, or native binary tables | Extract/list OBB containers and search for matching data files. |
| CPK table of contents | Use a read-only CPK parser/tool or write `scripts/inspect_cpk.py`. |
| Native API endpoint base URLs | Continue string extraction with better UTF-16/ASCII filtering and inspect `onlineapi::ServerData`. |
| Save file path and format | Follow `sys::SaveData` and Android external files dir paths after OBB analysis. |
