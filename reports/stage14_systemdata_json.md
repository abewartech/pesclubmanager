# Stage 14 — SystemData.dat Is JSON: Schema from LoadSystemData

## Scope

Static, read-only disassembly of `sys::SaveData::LoadSystemData`
(`0x4db1508`, 1456 bytes / 364 instructions, arm64) in `libUE4.so`.
Goal, per Stage 13 §3: map the unencrypted system save format so it can
be parsed offline.

Tooling: capstone 5 (arm64), pyelftools; PLT resolved via
`R_AARCH64_JUMP_SLOT` relocations; rodata strings via ADRP+ADD xref.

## 1. Headline finding: SystemData.dat is JSON, not binary

Stage 13 §3 said the unencrypted saves are "parseable with plain binary
parsing once the format is mapped". The loader proves otherwise:
`LoadSystemData` never calls `fread`/`fscanf`. It calls:

- `sys::SaveData::ConvertFormat()` (format migration entry point)
- `Json::Value::resolveReference(key, false)` — 8 calls, 4 distinct keys
- `Json::Value` copy-ctor / dtor (jsoncpp value lifetime management)

The file is parsed as **jsoncpp JSON**. No binary record layout exists to
map; the "format" is a JSON object schema.

## 2. Schema (verified keys)

| Key | Reads | Value handling |
|---|---|---|
| `SystemDataVersion` | 2× `resolveReference` | version gate (int; details below) |
| `text_language` | 2× `resolveReference` | int enum, clamped 0–14 |
| `sound_language` | 2× `resolveReference` | same int-enum pattern as `text_language` |
| `vibration` | 2× `resolveReference` | same two-pass pattern (bool/int, not fully traced) |

Filename referenced directly in the loader: `"SystemData.dat"`.

Each key is resolved twice. First pass: if the value is a Json object
(type 7) or array (type 6), the code walks it (legacy-format probe —
likely handles an older schema where the setting was nested); scalar
values fall through to the second pass. Second pass coerces scalars:

- `text_language` second pass (`0x4db16d8`): `type-1 <= 4` dispatch —
  int (`ldr w8,[x0]`, clamp `> 14` → default), double (`fcvtzu`,
  clamp `<= 14`), string (first byte → lookup table at rodata-derived
  base — maps a language-name string to the enum id), anything else →
  default 0. Out-of-range int path loads constant `0x19` (25).
- Interpretation: language is an enum with valid values **0–14**;
  missing/invalid values default to 0. String and double forms are
  accepted for backward compatibility.

## 3. What this means for offline parsing

- `SystemData.dat` needs **no binary parser**: read it as JSON, read the
  four keys above. Unknown future keys are safely ignored (loader only
  resolves these four).
- `SystemDataVersion` is read first and gates the rest — a version bump
  in a future game update may add keys; the loader pattern (resolve +
  type-check + default) is forward-tolerant.
- Per Stage 13, `UserInfoData.dat` / `OnSysData.dat` go through the same
  `sys::SaveData` layer and are likewise unencrypted; their loaders were
  not traced in this stage.
- Interrupt saves stay out of scope (Stage 13: Blowfish, deprioritized).

## 4. Reusable facts

| Symbol | Address | Notes |
|---|---|---|
| `sys::SaveData::LoadSystemData` | `0x4db1508` | 1456 B; JSON loader |
| `sys::SaveData::ConvertFormat` | (called) | migration entry, runs before key reads |
| `Json::Value::resolveReference` | PLT `0x19ebd18` | key lookup helper |
| jsoncpp type enum (from `ldrb [x0,#8]`) | — | 0 null, 1 int, 2 uint, 3 real, 4 string, 5 bool, 6 array, 7 object |

## 5. Caveats / not proven

- Exact semantics of the first-pass object/array probe per key (which
  legacy schema it migrates) were not fully reversed.
- `sound_language` / `vibration` second-pass coercion assumed identical
  to `text_language` from the shared code shape — spot-check, not a
  full trace.
- On-device path of `SystemData.dat` (built in local `0x4db1ab8`) not
  reversed; no real save file was available to validate against.
- Claims rest on static disassembly only.
