# Stage 14 — Save Files Are JSON, Not Binary

## Scope

Static, read-only analysis of `sys::SaveData::LoadSystemData` (`0x4db1508`,
1456 bytes) to determine the on-disk format of save files.

## 1. Key finding: the ".dat" files are JSON

`LoadSystemData` makes **16 calls** to `Json::Value` methods
(`resolveReference`, constructors, destructors) and **zero** binary-parse
calls. The file is parsed as JSON text.

JSON keys referenced in `LoadSystemData`:

- `SystemDataVersion`
- `text_language`
- `sound_language`
- `vibration`

(The function also calls `ConvertFormat` for version migration of language
settings — `ConvertFormatSoundLang`, `ConvertFormatTextLang`.)

## 2. All three save files share one loader

`sys::SaveData::LoadUserInfoData` (`0x4db63a4`, 28 bytes) and
`sys::SaveData::LoadOnsysData` (`0x4dbc064`, 28 bytes) are **thunks**:
they load filename strings (`UserInfoData.dat`, `OnSysData.dat`) and
branch directly to `LoadSystemData` (`0x4db1508`).

Therefore:

| File | Loader | Format |
|---|---|---|
| `SystemData.dat` | `LoadSystemData` | JSON |
| `UserInfoData.dat` | `LoadSystemData` (via thunk) | JSON |
| `OnSysData.dat` | `LoadSystemData` (via thunk) | JSON |

## 3. What this means

- **No binary format to reverse** for system/user saves. They are
  human-readable JSON — trivially parseable offline with any JSON parser.
- Combined with Stage 13 (no encryption on these files), the entire
  system-save layer is **fully accessible** to offline tooling.
- The remaining unknown is only the *schema* (which keys each file uses),
  recoverable from a real save file or by enumerating `resolveReference`
  key strings per thunk path.

## 4. Correction to earlier assumptions

Stage 10 listed these as save-data files by extension without asserting a binary format. They
are JSON text files with a `.dat` extension. The binary-format work in
Stage 12 (pesdb records) is unaffected — that concerns CPK game data,
not saves.
