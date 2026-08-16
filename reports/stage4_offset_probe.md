# Stage 4 Offset Probe

Scope: small read-only disassembly probe against `libUE4.so` arm64 exports. These are native in-memory `ParameterPlayerDefine` backing-data offsets, not yet offsets inside any extracted file format.

## Result

`onlinemode::ParameterPlayerDefine` stores or references backing player data through `[x0 + 0x28]`; the tiny accessors then read/write fields from that backing pointer.

| Field candidate | Getter/setter evidence | Backing-data offset | Access pattern | Confidence |
|---|---|---:|---|---|
| `PlayerId` | `GetPlayerId` / `SetPlayerId` | `0x2c` | `ldur/stur x?, [backing + 0x2c]` | High |
| `AppearanceId` | `GetAppearanceId` / `SetAppearanceId` | `0x1b0` | `ldr/str w?, [backing + 0x1b0]` | High |
| `Age` | `GetAge` / `SetAge` | bitfield at `0x1c`/word lane via `[backing + 0x18]` | getter masks `0x3f`; setter uses `bfi ..., 0x20, 6` | High, bitfield layout needs care |
| `Salary` | `GetSalary` / `SetSalary` | `0x1e8` | `ldr/str w?, [backing + 0x1e8]` | High |

## Disassembly Notes

```asm
GetPlayerId:
  ldr  x8, [x0, 0x28]
  ldur x0, [x8, 0x2c]
  ret

SetPlayerId:
  ldr  x8, [x0, 0x28]
  stur x1, [x8, 0x2c]
  ret

GetAge:
  ldr  x8, [x0, 0x28]
  ldrb w8, [x8, 0x1c]
  and  w0, w8, 0x3f
  ret

GetSalary:
  ldr w0, [backing + 0x1e8]
```

## Interpretation

This confirms Stage 4 should proceed by automatically disassembling small `ParameterPlayerDefine` getters/setters and extracting load/store offsets. The result should become a candidate in-memory schema first. Only after matching it against a real extracted/local record should it be treated as a file parser schema.

## Next

- Automate offset extraction for all small accessors in `analysis/stage4_player_schema/parameter_player_define_symbols.csv`.
- Disassemble `PrepareDataFromJson` and `PrepareDataFromJsonForScoutingList` to recover JSON key names and map server/local JSON fields to accessors.
- Keep editor work disabled until a read-only parser can round-trip known records to JSON without ambiguous fields.
