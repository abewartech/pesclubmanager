# Stage 17 — On-Device Save-File Paths

## Scope

Closes the Stage 14 §5 caveat: the on-device path of the `.dat` files,
built by the local path-builder at `0x4db1ab8`. Static, read-only arm64
disassembly of `libUE4.so`; strings via ADRP+ADD xref to `.rodata`.

## 1. Save files live under `<app-files>/SaveData/`

`sub_4db1ab8` (called by `LoadSystemData`, `LoadUserInfoData`,
`LoadOnsysData`) builds:

```
<base>/SaveData/<filename>      opened with "rb"
```

- The `SaveData/` component is the rodata string at `0x6509ac8`.
- The filename (`SystemData.dat`, `UserInfoData.dat`, `OnSysData.dat`)
  is passed in by the caller.
- `<base>` is a runtime-resolved global (loaded from `0x7e93880`-region
  state), not a static string: no hardcoded `/data/data/...` path
  exists in the binary. It is UE4's sandboxed files directory for the
  app, resolved at startup from the Android context.

## 2. Sibling data directories

Adjacent rodata strings reveal the app's data-dir layout:

| Directory | VA |
|---|---|
| `Download/` | `0x6509abe` |
| `SaveData/` | `0x6509ac8` |
| `TempData/` | `0x6509ad2` |
| `SettingInfo/` | `0x6509adc` |
| `DebugOutput/` | `0x6509ae9` |

All are `<base>/`-relative, built by the same path-builder family.

## 3. What this means for offline parsing

- To parse real saves offline, pull `<app-files>/SaveData/*.dat` from a
  rooted device or backup (`adb pull` needs the app debuggable or root;
  the dir is inside the app sandbox, not on shared storage). The files
  are plain JSON objects (Stages 14–15).
- No path surprises: the three JSON files from Stages 14–15 are exactly
  the files this builder opens.

## 4. Caveats

- `<base>` value confirmed only as runtime-resolved; the typical
  `/data/data/<pkg>/files` shape is inferred from Android convention,
  not from the binary (the extracted tree has no manifest to confirm
  the package id).
- Write-path (`Save*`) builders were not traced; assumed symmetric.
