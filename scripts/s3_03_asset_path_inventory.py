"""
Stage 3 - Step 3: Read-only asset path inventory for main PAK and patch CPK.

This does not unpack or modify containers. It scans binary data for embedded
asset paths, then writes candidate lists for the offline player-data workflow.
"""
import collections
import os
import re
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
PAK_PATH = WORKSPACE / "extracted" / "obb_main" / "PesMobile" / "Content" / "Paks" / "PesMobile-Android_ETC1.pak"
CPK_PATH = WORKSPACE / "original" / "patch.104050101.jp.konami.pesclubmanager.obb"
OUT_DIR = WORKSPACE / "analysis" / "stage3_asset_paths"
REPORT = WORKSPACE / "reports" / "stage3_asset_path_inventory.md"

PATH_RE = re.compile(
    rb"(?:PesMobile/Content|cpk_dat/)[A-Za-z0-9_./+\- ]{4,260}"
)
KEYWORDS = (
    "player",
    "team",
    "parameter",
    "param",
    "define",
    "ability",
    "position",
    "contract",
    "salary",
    "save",
    "systemdata",
    "tmpdb",
    "database",
    "datatable",
    "master",
)


def scan_paths(path: Path):
    found = {}
    overlap = 512
    offset = 0
    carry = b""
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            data = carry + chunk
            base = offset - len(carry)
            for match in PATH_RE.finditer(data):
                raw = match.group(0).split(b"\x00", 1)[0]
                try:
                    text = raw.decode("utf-8")
                except UnicodeDecodeError:
                    text = raw.decode("latin-1", errors="ignore")
                text = text.strip("\x00\r\n\t ")
                if len(text) >= 8:
                    found.setdefault(text, base + match.start())
            carry = data[-overlap:]
            offset += len(chunk)
    return found


def extension_of(path: str):
    name = path.rsplit("/", 1)[-1]
    if "." not in name:
        return "[no extension]"
    return "." + name.rsplit(".", 1)[-1].lower()


def write_lines(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(row)
            f.write("\n")


def summarize(label, source_path, paths):
    sorted_paths = sorted(paths)
    candidates = [
        p for p in sorted_paths
        if any(keyword in p.lower() for keyword in KEYWORDS)
    ]
    ext_counts = collections.Counter(extension_of(p) for p in sorted_paths)
    top_dirs = collections.Counter("/".join(p.split("/")[:4]) for p in sorted_paths)
    return {
        "label": label,
        "source_path": source_path,
        "paths": sorted_paths,
        "candidates": candidates,
        "ext_counts": ext_counts,
        "top_dirs": top_dirs,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    inputs = [
        ("main_pak", PAK_PATH),
        ("patch_cpk", CPK_PATH),
    ]

    summaries = []
    for label, source_path in inputs:
        print(f"[*] Scanning {label}: {source_path}")
        if not source_path.exists():
            print(f"[!] Missing: {source_path}")
            summaries.append({
                "label": label,
                "source_path": source_path,
                "missing": True,
                "paths": [],
                "candidates": [],
                "ext_counts": collections.Counter(),
                "top_dirs": collections.Counter(),
            })
            continue
        paths = scan_paths(source_path)
        summary = summarize(label, source_path, paths)
        summaries.append(summary)
        write_lines(OUT_DIR / f"{label}_paths.txt", summary["paths"])
        write_lines(OUT_DIR / f"{label}_player_candidates.txt", summary["candidates"])
        print(f"[+] {label}: {len(summary['paths'])} unique paths, {len(summary['candidates'])} candidates")

    with REPORT.open("w", encoding="utf-8", newline="\n") as f:
        f.write("# Stage 3 Asset Path Inventory\n\n")
        f.write("Scope: read-only binary scan of embedded asset paths. No container extraction or patching was performed.\n\n")
        for summary in summaries:
            f.write(f"## {summary['label']}\n\n")
            f.write(f"**Source:** `{summary['source_path'].relative_to(WORKSPACE)}`\n\n")
            if summary.get("missing"):
                f.write("Missing source file.\n\n")
                continue
            f.write(f"**Unique paths:** {len(summary['paths']):,}\n\n")
            f.write(f"**Keyword candidates:** {len(summary['candidates']):,}\n\n")
            f.write("### Top Extensions\n\n")
            f.write("| Extension | Count |\n|---|---:|\n")
            for ext, count in summary["ext_counts"].most_common(20):
                f.write(f"| `{ext}` | {count:,} |\n")
            f.write("\n### Top Path Prefixes\n\n")
            f.write("| Prefix | Count |\n|---|---:|\n")
            for prefix, count in summary["top_dirs"].most_common(20):
                f.write(f"| `{prefix}` | {count:,} |\n")
            f.write("\n### Player/Data Candidates (first 80)\n\n")
            if summary["candidates"]:
                for path in summary["candidates"][:80]:
                    f.write(f"- `{path}`\n")
            else:
                f.write("No keyword candidates found.\n")
            f.write("\n")

        f.write("## Outputs\n\n")
        f.write(f"- `{OUT_DIR.relative_to(WORKSPACE)}/main_pak_paths.txt`\n")
        f.write(f"- `{OUT_DIR.relative_to(WORKSPACE)}/main_pak_player_candidates.txt`\n")
        f.write(f"- `{OUT_DIR.relative_to(WORKSPACE)}/patch_cpk_paths.txt`\n")
        f.write(f"- `{OUT_DIR.relative_to(WORKSPACE)}/patch_cpk_player_candidates.txt`\n")

    print(f"[+] Report written: {REPORT}")


if __name__ == "__main__":
    main()
