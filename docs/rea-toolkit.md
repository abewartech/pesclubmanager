# REA Toolkit

[REA](https://github.com/morluto/rea) (`rea-agents` on npm) is an agentic
reverse-engineering framework used for deeper analysis in this project:
cross-referencing the native binary, decompiling functions, and tracing
app features down to native code. It complements the hand-rolled Python
scripts under `scripts/` — use those for quick targeted scans, REA for
deeper work.

## Install

One-off use without installing:

```bash
npx -y rea-agents@latest <command> --json
```

Regular use:

```bash
npm install --global rea-agents
rea --help
```

Native binary analysis (Ghidra / Hopper / IDA bridges) needs a provider
configured first; see REA's `docs/cli.md` for provider selection.

## Use on this project

Point REA at the extracted binary (never the pristine `original/`
artifacts — copy first if you need to experiment):

```
original/extracted/apk/lib/arm64-v8a/libUE4.so
```

Write findings under `reports/` or `analysis/`, following the existing
stage numbering.

## Rules

- Analysis is read-only and offline. Never patch the APK, OBB, native
  libraries, or save files, and never contact game servers.
- The full REA source is intentionally not vendored here (68 MB+);
  install it from npm or clone upstream when needed.
