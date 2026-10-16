# Stage 21 — sys::WesysData: multi_stats_data Payload Format

## Scope

Follows Stage 20: the `WESYS` validator is not a free function but
`sys::WesysData::IsValid`. This stage recovers the class interface
from `.dynsym` and decodes the payload layout from its accessors.
Static, read-only arm64 disassembly; tooling: capstone 5, pyelftools.

## 1. The class (from `.dynsym`)

| Symbol (demangled) | VA | Size |
|---|---|---|
| `sys::WesysData::WesysData(void*, char const*)` | `0x4dbc8e0` | 20 |
| `sys::WesysData::~WesysData()` | `0x4dbc8f4` / `0x4dbc8f8` | 4 |
| `sys::WesysData::IsValid(void*, unsigned long)` | `0x4dbc8fc` | 56 |
| `sys::WesysData::GetSize()` | `0x4dbc934` | 12 |
| `sys::WesysData::ReplaceEndian(unsigned int)` | `0x4dbc940` | 8 |
| `sys::WesysData::GetOrgSize()` | `0x4dbc948` | 12 |
| `sys::WesysData::GetData()` | `0x4dbc954` | 12 |
| `sys::WesysData::isXorShiftCrypt()` | `0x4dbc960` | 16 |
| `sys::WesysData::isZipCompress()` | `0x4dbc970` | 16 |
| vtable `sys::WesysData` | `0x7675508` | 32 |

## 2. Payload layout (decoded from accessors)

The object holds a buffer pointer at `[this+8]`; every accessor
dereferences it first. Header, 16 bytes:

```
offset  size  field
0       1     byte 0 (uninterpreted)
1       1     byte 1 (uninterpreted)
2       1     flags: bit0 = zip-compressed (isZipCompress:
              ldrb [buf+2], and #1)
              bit1 = xorshift-encrypted (isXorShiftCrypt:
              ldrb [buf+2], ubfx #1,#1)
3       5     magic "WESYS" (IsValid: memcmp 5 bytes at input+3)
8       4     uint32 LE stored size (GetSize: ldr w0, [buf+8])
12      4     uint32 LE original size (GetOrgSize: ldr w0, [buf+12])
16      …     payload (GetData: buf+0x10)
```

`IsValid`'s 16-byte minimum (Stage 20) is exactly this header size.
The payload may be zip-compressed and/or xorshift-encrypted per the
flag bits; `GetOrgSize` gives the post-decompression size.

## 3. Notes

- `ReplaceEndian` is a no-op stub (`mov w0, w1; ret`) in this build.
- The vtable at `0x7675508` (`.data.rel.ro`) reads zero in the file;
  entries are filled by `RELA` relocations at load time (normal for a
  PIC shared object), so virtual dispatch targets were not recovered
  statically.
- The constructor stores its `char const*` argument as the buffer
  pointer and installs the vtable pointer; destructors are trivial
  (`ret`-only thunks).
- Bytes 0–1 of the header remain uninterpreted; no accessor reads
  them.

## 4. What this unlocks

An offline parser for `multi_stats_data` can now: check the 16-byte
header, verify `"WESYS"`, read flags/size fields, and — given
implementations of the zip and xorshift steps — recover the original
payload. The decompression/decryption routines themselves were not
traced in this stage.
