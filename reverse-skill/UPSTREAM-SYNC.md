# reverse-skill upstream sync

- **Upstream:** `zhaoxuya520/reverse-skill` @ `cab634bd` (main, 2026-09-22)
- **Synced:** 2026-10-16
- **Scope:** `reverse-skill/` vendored copy in `abewartech/pesclubmanager`

## What changed

- 76 files updated to upstream (routing benchmark 163→178 cases, new R41–R45
  routes, Binary Ninja skill, IDA supervisor/watchdog scripts, Codex adapter
  plugin, new docs: SECURITY.md, UV-AND-DOWNLOAD-SECURITY, QUICKSTART_zh,
  COMMUNITY-ISSUE-TRIAGE, SECURITY-REVIEW-2026-09-03, CI additions,
  macOS/BSD sed portability fixes, PS 5.1 BOM encoding fixes, etc.)
- 37 new files/dirs added from upstream (`plugins/`, `reports/`,
  `docs/superpowers/`, `docs/plans/`, `skills/binary-ninja-reverse/`,
  `skills/ctf-sandbox/`, `skills/threat-intelligence/`, new test scripts,
  `ucloud-astraflow.png` sponsor asset, …). No file over 5 MB.
- No upstream-deleted files needed handling (nothing was removed upstream
  that we carried).

## Local customizations preserved

- `README.md`: kept the afterglow.watch star-velocity badge and the
  QQ Group (942400892) / Discord contact lines. The old bottom sponsor
  block (Atlas Cloud + Kite AI, old layout) was dropped because upstream's
  new sponsor section covers the same sponsors (plus UCloud AstraFlow).
- `README_zh.md`: kept the local `docs/assets/star-history.svg` reference
  (upstream switched to a remote apivix chart). QQ 群 / Discord lines were
  already upstream; old bottom sponsor block dropped as superseded.
- `burp-mcp-full/bin/` (local build output, tracked): kept as-is.

## Caveats

- The project's own test suite is PowerShell-based (`test-routing.ps1`,
  `verify-routing-coherence.ps1`, …) and was not executed here (Linux,
  no PowerShell). CI on the PR will cover it.
- Sanity checks run: `bash -n` on changed shell scripts,
  `python3 -m py_compile` on changed Python files,
  `python3 -m json.tool` on changed JSON files.
