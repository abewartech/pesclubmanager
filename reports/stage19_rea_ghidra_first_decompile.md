# Stage 19 — REA/Ghidra Toolchain Operational, First Decompilation

## Scope

Per user request: put the `morluto/rea` tool to real use, then document
the follow-up. This stage brings up REA's native-analysis backend
(Ghidra) and produces the first Ghidra decompilation in this project:
`PrepareDataFromJson` (`0x04b2ae68`), the player JSON preparation
function from Stage 6.2.

## 1. Toolchain (durable installs)

| Component | Location | Notes |
|---|---|---|
| REA CLI | `~/workspace/rea-cli` (`npm install rea-agents`) | run via `node .../scripts/rea.mjs`; global npm is wiped on VM redeploy |
| Ghidra 12.1.2 | `~/workspace/ghidra/ghidra_12.1.2_PUBLIC` | set `GHIDRA_INSTALL_DIR` |
| JDK 21 (Temurin) | `~/workspace/.jdk21` | Ghidra 12.1.x requires JDK 21+; set `JAVA_HOME` |
| Decompile script | `scripts/s19_01_ghidra_decompile_one.java` | single-function headless decompile |

Required env for every run:

```bash
export GHIDRA_INSTALL_DIR=$HOME/workspace/ghidra/ghidra_12.1.2_PUBLIC
export JAVA_HOME=$HOME/workspace/.jdk21
export TMPDIR=$HOME/workspace/rea-tmp   # /tmp is a 512MB tmpfs, too small
export PATH=$HOME/workspace/.jdk21/bin:$PATH
```

## 2. REA limitations found (honest)

- `rea function … --provider ghidra` on the 121MB `libUE4.so` hits
  `provider_timeout`: Ghidra's import + full auto-analysis needs more
  than 30 minutes (`REA_GHIDRA_STARTUP_TIMEOUT_MS=1800000` was still hit).
  Full-binary REA analysis is impractical here.
- `/tmp` (512MB tmpfs) overflows on Ghidra's project DB; `TMPDIR` must
  point at workspace storage.
- Workaround that works: Ghidra `analyzeHeadless` directly with
  `-noanalysis` + a postScript that recursive-disassembles one function
  and decompiles it. ~90 seconds per function, no full-binary analysis.

Usage:

```bash
analyzeHeadless <projdir> PESCM -import <binary> -noanalysis \
  -scriptPath <dir> -postScript DecompileOne.java 0x<addr> -deleteProject
```

## 3. First decompilation: PrepareDataFromJson (0x04b2ae68)

- Artifact: `analysis/stage19/prepare_data_from_json_decompiled.c`
- 294 instructions disassembled, 1176-byte function body.
- Capstone cross-check confirms the target: prologue `sub sp, sp, #0x180`
  and JSON key string refs (`'name'`, `'1'`, `'2'`).

### Quality caveat (important)

The decompiler output is **preliminary**: it shows a heavily repetitive
ushort bitfield pattern (`& 0xfe00 | & 0xff | & 0x100`) repeated ~15×,
which reads like a loop the decompiler failed to structure (or an
artifact of disassembling without full program analysis). Do not treat
the C listing as authoritative control flow. What it reliably shows:

- the function manipulates packed 9-bit-ish `ushort` fields in a tight
  repetitive sequence (consistent with writing an ability/parameter
  array — the MEDIUM-confidence group from Stage 6.2);
- it calls three small helpers repeatedly (`FUN_01aebd38`,
  `FUN_01aebd18`, `FUN_01aebd28` — unresolved without full analysis).

Raising this to HIGH confidence needs either full Ghidra auto-analysis
(impractical per §2) or targeted manual review of the 294-instruction
disassembly against the Stage 6.2 key map.

## 4. What this unlocks

- Any native function in `libUE4.so` can now be decompiled in ~90s via
  `scripts/s19_01_ghidra_decompile_one.java`.
- Next candidates: the `Save*` writers (Stage 18) for exact value
  encoding, and the `WESYS` check site (`0x4dbc910`).
