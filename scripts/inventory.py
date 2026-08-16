#!/usr/bin/env python3
"""Generate a static inventory report for reverse engineering artifacts."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path


IMPORTANT_EXTENSIONS = {
    ".apk",
    ".xapk",
    ".apks",
    ".zip",
    ".obb",
    ".so",
    ".dex",
    ".odex",
    ".vdex",
    ".dat",
    ".bin",
    ".bytes",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".json",
    ".xml",
    ".csv",
    ".txt",
    ".jar",
}

TEXT_EXTENSIONS = {".json", ".xml", ".csv", ".txt", ".properties", ".ini", ".cfg", ".conf"}
ARCHIVE_EXTENSIONS = {".apk", ".xapk", ".apks", ".zip", ".jar", ".obb"}
DATABASE_EXTENSIONS = {".db", ".sqlite", ".sqlite3"}
NATIVE_EXTENSIONS = {".so"}
DEX_EXTENSIONS = {".dex", ".odex", ".vdex"}
DATA_EXTENSIONS = {".dat", ".bin", ".bytes"}

SKIP_DIRS = {"reports", "analysis", "modified", "backups"}


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def human_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{size} B"
        value /= 1024
    return f"{size} B"


def classify(path: Path) -> tuple[str, str, str]:
    suffix = path.suffix.lower()
    name = path.name.lower()
    parts = {part.lower() for part in path.parts}

    if suffix in ARCHIVE_EXTENSIONS:
        if suffix == ".apk":
            return "Android APK archive", "Primary install package or nested split APK", "yes"
        if suffix == ".obb":
            return "Android OBB expansion archive", "Large game asset container", "yes"
        return "Archive", "Container for APK/assets/tools", "yes"
    if suffix in NATIVE_EXTENSIONS:
        return "Native shared library", "Android native code, engine, JNI, or vendor SDK", "yes"
    if suffix in DEX_EXTENSIONS:
        return "Dalvik bytecode", "Android Java/Kotlin bytecode or optimized bytecode", "yes"
    if suffix in DATABASE_EXTENSIONS:
        return "SQLite database", "Structured game, app, or save data", "yes"
    if suffix in DATA_EXTENSIONS:
        if "assets" in parts or "files" in parts:
            return "Binary data", "Asset, metadata, serialized data, or save/config payload", "yes"
        return "Binary data", "Potential data blob or tool artifact", "maybe"
    if suffix in TEXT_EXTENSIONS:
        if "manifest" in name:
            return "XML manifest/config", "Android package metadata or app configuration", "yes"
        return "Text/config data", "Readable config, resource, metadata, or notes", "maybe"
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        return "Image asset", "Game/UI visual asset", "maybe"
    if suffix in {".wav", ".mp3", ".ogg"}:
        return "Audio asset", "Game audio asset", "maybe"
    if suffix in {".ttf", ".otf"}:
        return "Font asset", "Game/UI font", "maybe"
    if suffix in {".dll"}:
        return "Managed/native library", "Potential Mono/.NET assembly or Windows tool library", "maybe"
    if suffix in {".exe"}:
        return "Executable", "Local analysis tool or bundled binary", "maybe"
    if "shared_prefs" in parts:
        return "Android preferences", "Local app configuration", "yes"
    return "Unknown/other", "Unclassified file", "no"


def should_hash(path: Path, size: int) -> bool:
    suffix = path.suffix.lower()
    if suffix in IMPORTANT_EXTENSIONS:
        return True
    if any(part.lower() in {"assets", "lib", "shared_prefs", "databases", "files"} for part in path.parts):
        return size <= 100 * 1024 * 1024
    return False


def iter_files(root: Path):
    for current_root, dirs, files in os.walk(root):
        current_path = Path(current_root)
        rel_parts = current_path.relative_to(root).parts if current_path != root else ()
        if rel_parts and rel_parts[0] in SKIP_DIRS:
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d not in {".git"}]
        for file_name in files:
            yield current_path / file_name


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="Workspace root")
    parser.add_argument("--output", default="reports/inventory.md", help="Markdown report path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = (root / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    counts: dict[str, int] = {}
    total_size = 0
    for path in sorted(iter_files(root), key=lambda p: str(p).lower()):
        try:
            stat = path.stat()
        except OSError:
            continue
        if not path.is_file():
            continue
        file_type, purpose, interesting = classify(path)
        total_size += stat.st_size
        counts[file_type] = counts.get(file_type, 0) + 1
        digest = sha256_file(path) if should_hash(path, stat.st_size) else ""
        rows.append(
            {
                "file": path.relative_to(root).as_posix(),
                "size": human_size(stat.st_size),
                "type": file_type,
                "hash": digest,
                "purpose": purpose,
                "interesting": interesting,
            }
        )

    lines = [
        "# Inventory",
        "",
        f"Workspace: `{root}`",
        "",
        f"Total files scanned: {len(rows)}",
        f"Total file size: {human_size(total_size)}",
        "",
        "## Summary",
        "",
        "| Type | Count |",
        "|---|---:|",
    ]
    for file_type, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {file_type} | {count} |")

    lines.extend(
        [
            "",
            "## Files",
            "",
            "| File | Size | Type | SHA-256 | Likely purpose | Interesting? |",
            "|---|---:|---|---|---|---|",
        ]
    )
    for row in rows:
        digest = row["hash"] or "-"
        lines.append(
            f"| `{row['file']}` | {row['size']} | {row['type']} | `{digest}` | "
            f"{row['purpose']} | {row['interesting']} |"
        )

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output}")
    print(f"Scanned {len(rows)} files ({human_size(total_size)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
