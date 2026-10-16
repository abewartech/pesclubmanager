# Rizin Toolkit

[Rizin](https://rizin.re/) (v0.9.1) is a command-line reverse-engineering
framework, the maintained successor of radare2 (which Stage 4 used).
It complements the REA/Ghidra setup: Ghidra is for deep decompilation,
Rizin is for fast targeted disassembly and scripted byte-level work
with no 30-minute analysis phase. (radare2, Rizin's predecessor, was used in Stage 2 via `rabin2` for
export dumping and in Stage 4 for scripted disassembly.)

## Install

Static x86_64 build, no dependencies, kept durable under
`~/workspace/rizin/` (global installs are wiped on VM redeploy):

- `rizin-bin` — main interactive/headless binary (named `-bin` because
  the tarball's `rizin/` data directory collides with the binary name)
- `rz-asm`, `rz-bin`, `rz-find`, `rz-hash`, … — single-purpose tools

Upstream: https://github.com/rizinorg/rizin/releases (v0.9.1,
`rizin-v0.9.1-static-x86_64.tar.xz`, 137,626,404 bytes).

## Tested (2026-10-16)

1. `rz-asm -a arm -b 64 -o 0x4db1508 -B -l 32 -f <bytes> -D`
   disassembles ARM64 correctly: output for `LoadSystemData`
   (`adrp x0, 0x6503000` / `add x0, x0, 0xaa`) matches the Stage 14
   capstone ground truth exactly. Runs in milliseconds.
2. `rz-bin`, `rz-asm`, `rz-find`, `rz-hash` all report v0.9.1 and run.
3. `rz-find -s <string>` works but a full 121MB scan takes minutes;
   slice the binary first for interactive use.

## Use on this project

- Fast check of a few instructions: extract bytes with Python
  (`elftools`, see Stage 14 scripts) and pipe through `rz-asm`.
- Scripted scans: prefer the existing Python/capstone scripts under
  `scripts/` for anything non-trivial; reach for Rizin when you want
  its disassembler, IL, or binary-format parsing without writing code.
- Full interactive `rizin-bin` sessions on the 121MB `libUE4.so` are
  slow to start; keep them for small regions, not whole-binary
  auto-analysis.

## Rules

- Read-only, offline. Same rules as `docs/rea-toolkit.md`: never patch
  the APK/OBB/native libraries/save files, never contact game servers.
- The 137MB tarball is not vendored here; reinstall from upstream
  releases when needed.
