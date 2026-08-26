# Save Data Structure: Current Static Evidence

## Scope

This document records only the save-data evidence currently available from static native analysis. It is not a save format specification, parser, editor, or recovery guide.

Sources:

- `reports/native_analysis.md`
- `reports/reverse_engineering.md`

## Confirmed Leads

| Lead | Static evidence | What it supports | Confidence |
|---|---|---|---|
| `sys::SaveData` | Exported native symbols include `sys::SaveData::GetFrameSkipSetting` and `sys::SaveData::GetMatchWinCountForReview`. | A native local save/settings layer exists and exposes settings and review-related state. | HIGH for the namespace; MEDIUM for the review-count interpretation. |
| `systemdata::SystemData` | Exported native symbols include `systemdata::SystemData::SaveTutorialState`. | Tutorial state is persisted by a native system-data layer. | HIGH |
| Migration state | `systemdata::SystemData::SaveDataMigrationServerTime` and `SaveEncourageDataMigrationTime` are static native leads. | Migration-related timestamps or prompt state are persisted locally or in a synced-state model. | MEDIUM |
| Unreal save capability | `Saved/`, `SaveToUserDir`, and `CPF_SaveGame` strings appear in the native analysis. | Unreal save/config facilities are available in the binary. | MEDIUM |

## Structure That Can Be Stated Safely

The available evidence supports a layered model, not a byte layout:

```text
native sys::SaveData / systemdata::SystemData APIs
        -> local settings, tutorial, and migration-state leads
        -> Unreal save/config capability strings
        -> actual PESCM save path and format remain unconfirmed
```

`sys::SaveData` and `systemdata::SystemData` are useful static call-chain targets. The Unreal strings establish engine capability only; they do not prove that a particular PESCM save uses an Unreal `SaveGame` object or any particular directory.

## Unknowns

The following have not been recovered and must not be inferred from the current reports:

- Actual save file path, filename, or Android storage location.
- Save file format, record boundaries, field order, field widths, versioning, checksums, compression, or serialization layout.
- Whether player data is stored in a save, referenced from a save, loaded from a container, or synchronized separately.
- Encryption presence, algorithm, key, IV, nonce, derivation scheme, or integrity mechanism.
- A correspondence between `ParameterPlayerDefine` in-memory offsets and any on-disk save offsets.

The OpenSSL-style symbols and `EAUDP_ENCRYPT` indicator in the native analysis are not evidence of save-data encryption. The reports identify no confirmed save-data key, IV, or algorithm.

## Strict Read-Only Boundary

This workspace remains static and offline:

- Do not install hooks, attach runtime instrumentation, execute a game binary, or probe services.
- Do not patch APK, OBB, PAK, CPK, native libraries, save files, or files under `original/`.
- Do not authenticate, scrape, fuzz, or make endpoint calls.
- Keep derived tooling and evidence under `scripts/`, `analysis/`, `reports/`, or `docs/`.

Future work may only refine this document after additional static, read-only evidence demonstrates a concrete path or format. Until then, all save-layout claims remain unproven.
