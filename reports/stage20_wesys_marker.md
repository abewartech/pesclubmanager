# Stage 20 — WESYS Marker Semantics in SaveMultiplayStats

## Scope

Closes the Stage 18 §2 caveat: the exact semantics of the `WESYS`
marker check referenced by `SaveMultiplayStats`. Static, read-only
arm64 disassembly of `libUE4.so`; strings via ADRP+ADD xref to
`.rodata`. Tooling: capstone 5, pyelftools (same as Stages 14–15).

## 1. The validator, fully traced (`0x4dbc8fc`–`0x4dbc930`)

```
0x4dbc8fc  cmp   x1, #0x10        ; len < 16 → return 0
0x4dbc900  b.hs  #0x4dbc90c
0x4dbc904  mov   w0, wzr
0x4dbc908  ret
0x4dbc90c  str   x30, [sp, #-0x10]!
0x4dbc910  adrp  x1, #0x6503000
0x4dbc914  add   x0, x0, #3       ; input+3
0x4dbc918  add   x1, x1, #0x91c   ; "WESYS"
0x4dbc91c  mov   w2, #5
0x4dbc920  bl    #0x19a1e28       ; memcmp-like
0x4dbc924  cmp   w0, #0
0x4dbc928  cset  w0, eq
0x4dbc92c  ldr   x30, [sp], #0x10
0x4dbc930  ret
```

Calling convention is `(ptr, len)`:
- Returns **false** if the input is shorter than **16 bytes**.
- Otherwise compares **5 bytes at input+3** against the rodata string
  `"WESYS"` (`0x650391c`) and returns **true iff equal**.

So `multi_stats_data` is a binary payload with a 5-byte magic
`"WESYS"` at offset 3, and a minimum length of 16 bytes. Bytes 0–2
(prefix) and bytes 8–15 (minimum tail) are not interpreted by this
check.

## 2. SaveMultiplayStats write path (`0x4dbc564`–`0x4dbc694`)

- References the `"multi_stats_data"` key (`0x650390b`) and the
  `"OnSysData.dat"` filename (`0x65038d3`), then calls the JSON file
  writer at `0x4db2494`.
- The `WESYS` validator itself was **not** observed on this write
  path; no direct `bl` to `0x4dbc8fc` was found in `.text`, and no
  `adrp` references its page. It is most plausibly invoked from the
  load/parse side (validating untrusted file content before use),
  but the caller was not traced — treat that as inference.

## 3. Rodata adjacency note

In `.rodata`, `"WESYS"` sits immediately after `"multi_stats_data\0"`
(`...multi_stats_data\0WESYS\0DeathList\0...`). This is string-table
packing, not a structural relationship; the validator references
`WESYS` by its own address (`0x650391c`), not relative to the key
name.

## 4. Caveats

- The validator's caller is untraced; "load-side validation" is
  inference from the check's shape (length + magic on an input
  buffer), not from an observed call.
- Bytes 0–2 and the payload beyond offset 8 are not interpreted here;
  full `multi_stats_data` encoding remains unmapped.
- The memcmp-like target at `0x19a1e28` (relative `bl`) was not
  resolved to a PLT symbol in this pass; the 5-byte compare semantics
  are read from the argument setup (`x0`=input+3, `x1`="WESYS",
  `w2`=5) and the `cset w0, eq` result handling.
