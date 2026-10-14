# Stage 10 — Save-Data Tracing & PESDB Discovery

## Scope

Static, read-only analysis of `libUE4.so` (arm64, from
`PES-CLUB-MANAGER-v4-5-1.apk`) with capstone + pyelftools. No binary
executed, no server contacted, no artifacts modified.

**Headline: Stage 8's "not recoverable" conclusion is overturned.**
The player master database (`pesdb/Player.bin`) ships in the offline
containers — as binary `.bin` files inside the CRIWARE data CPK, not as
JSON. Stage 7's key-scan found nothing because it searched for JSON key
strings; the data is binary.

## 1. Save system (`sys::SaveData`)

| Item | Address (arm64) | Notes |
|---|---|---|
| `basic::FilePath::GetSaveDataPath()` | `0x4f09b00` | Returns `<app_files_dir>/SaveData/` |
| `sys::SaveFileRead(const char*, void*, size_t)` | `0x4e0f654` | Builds `SaveData/<name>`, then opens |
| `sys::SaveFileWrite(const char*, const void*, size_t)` | `0x4e0f9e8` | Same path construction |
| `sys::SaveData::LoadSystemData()` | `0x4db1508` | Reads `SystemData.dat` |
| `sys::SaveData::LoadUserInfoData()` / `SaveUserInfoData()` | `0x4db63a4` / `0x4db6608` | Reads/writes `UserInfoData.dat` |
| `sys::SaveData::LoadOnsysData()` | `0x4dbc064` | Reads `OnSysData.dat` |

Save files observed in `.rodata`: `SystemData.dat`, `UserInfoData.dat`,
`OnSysData.dat`, `receive.dat`, `user_news_info.dat`,
`EditInfo/EditDataList.dat`, `TopMenuData.dat`, `TopMenuDataSub.dat`,
`InterruptGameFile.dat`, `check.dat`.

Note: `tmpdb::InterruptGameInfo::SaveEncryptedGameFile()` /
`LoadEncryptedGameFile()` (`0x4e28140`) — some saves are encrypted;
scheme not yet recovered.

## 2. PESDB — player master database (new)

`pesdb::Manager::LoadData(uint)` (`0x59fb12c`) loads binary tables from
the CRIWARE virtual path `cpk_dat/common/etc/pesdb/`:

`Ball.bin`, `BallCondition.bin`, `Boots.bin`, `Coach.bin`,
`CoachDeleteList.bin`, `Competition.bin`, `CompetitionEntry.bin`,
`CompetitionKind.bin`, `CompetitionRegulation.bin`, `Country.bin`,
`Derby.bin`, `Glove.bin`, `MyclubCoach.bin`, `MyclubTactics.bin`,
`MyclubTacticsFormation.bin`, `Player.bin`, `PlayerAssignment.bin`

File format (`pesdb::Loader::SetData`, `0x59fb59c`): **flat array of
fixed-size records, no header** — `record_count = file_size /
record_size`.

Import chain:
`tmpdb::LinkPesdb::ImportPlayer()` (`0x4e49af8`)
→ `GetVectorOfPesdbPlayerData()` (`0x4e53bcc`, records are **0x138 =
312 bytes**)
→ per record: `SetPlayerData(tmpdb::Player*, pesdb::PlayerData*, idx)`
(`0x4e53fc8`) + `RangeCheckPlayerData()`.

`tmpdb::PlayerBase::SetWorkFromPesdb()` (`0x4e30398`, 6532 bytes)
converts each 312-byte `pesdb::PlayerData` into `tmpdb::Player`.
Field-by-field offset mapping is the next RE task (not yet extracted).

## 3. Container binding

- `cpk_dat/` is a CRIWARE binder alias. Bind config strings:
  `Def_DataBind_CpkPriorityLowest`, `cpk/`, `dt800` /
  `dt800_all.cpk`, `cpk_dat/xxx/`.
- The patch OBB (`patch.104050101...obb`, magic `CPK `) **is** the data
  CPK. Its file TOC is obfuscated/encrypted — the file list is not
  enumerable offline (confirms Stage 8's container observation).
- `Player.bin` / `pesdb` do not appear as plaintext in the main PAK or
  either raw OBB — consistent with an obfuscated CPK TOC.

## 4. What this unlocks

1. Deobfuscate the patch-OBB CPK TOC (find the key/algorithm in the
   `criFsBinder` code paths) → extract `Player.bin`.
2. Map the 312-byte `pesdb::PlayerData` layout via
   `SetWorkFromPesdb` → offline binary parser for the real master DB.
3. Cross-check against the Stage 6 JSON-key decoder schema.

## Tooling used

`scripts/s10_01_analyze_libue4.py` (new): ELF/dynsym enumeration,
aarch64 ADRP+ADD string-xref scanner, PLT→import resolver. Requires
`capstone` + `pyelftools` (`pip install --break-system-packages
capstone pyelftools`).
