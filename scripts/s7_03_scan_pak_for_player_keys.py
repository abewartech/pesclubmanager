"""
Stage 7.3 - Read-only scan of the unpacked UE4 PAK for the 105 PrepareDataFromJson
player JSON-key markers.

This does NOT modify any source. It reads the extracted PAK (produced by the
Stage 3 extraction), decompresses each entry in memory, and reports which
entries (if any) contain player JSON keys. It is a discovery/coverage tool,
not a parser or editor.

Usage:
    python scripts/s7_03_scan_pak_for_player_keys.py
"""
import json
import os
import struct
import zlib
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
PAK_PATH = WORKSPACE / "extracted" / "obb_main" / "PesMobile" / "Content" / "Paks" / "PesMobile-Android_ETC1.pak"
IDX_OFFSET = 782104571
IDX_SIZE = 7380528
MAPPING_PATH = WORKSPACE / "analysis" / "stage6" / "player_json_key_mapping.json"
REPORT = WORKSPACE / "reports" / "stage7_pak_player_key_scan.md"
OUT_JSON = WORKSPACE / "analysis" / "stage7_scan" / "pak_player_key_hits.json"

# Keys that are distinctive enough to be strong positive evidence.
DISTINCTIVE = {
    "serial_id", "master_id", "param_shot", "original_team_id",
    "contract_period", "rarity", "market_value", "sell_price",
    "uniform_number", "motivation_value", "record_goal_total",
}


def read_fstring(data, offset):
    if offset + 4 > len(data):
        return None, offset
    length = struct.unpack_from('<i', data, offset)[0]
    offset += 4
    if length == 0:
        return "", offset
    if length < 0:
        byte_count = (-length) * 2
        if offset + byte_count > len(data):
            return None, offset
        s = data[offset:offset + byte_count].decode('utf-16-le', errors='replace').rstrip('\x00')
        return s, offset + byte_count
    if offset + length > len(data):
        return None, offset
    s = data[offset:offset + length].decode('utf-8', errors='replace').rstrip('\x00')
    return s, offset + length


def parse_index():
    data = PAK_PATH.read_bytes()[IDX_OFFSET:IDX_OFFSET + IDX_SIZE]
    pos = 0
    mount_point, pos = read_fstring(data, pos)
    entry_count = struct.unpack_from('<i', data, pos)[0]
    pos += 4
    entries = []
    for _ in range(entry_count):
        filename, pos = read_fstring(data, pos)
        if filename is None:
            break
        offset = struct.unpack_from('<q', data, pos)[0]; pos += 8
        comp_sz = struct.unpack_from('<q', data, pos)[0]; pos += 8
        uncomp_sz = struct.unpack_from('<q', data, pos)[0]; pos += 8
        comp_meth = data[pos]; pos += 1
        pos += 20  # sha1
        blocks = None
        if comp_meth != 0:
            block_count = struct.unpack_from('<I', data, pos)[0]; pos += 4
            blocks = []
            for _ in range(block_count):
                b_start = struct.unpack_from('<q', data, pos)[0]; pos += 8
                b_end = struct.unpack_from('<q', data, pos)[0]; pos += 8
                blocks.append((b_start, b_end))
        pos += 1 + 4  # flags + compression_block_size
        entries.append({
            "path": (mount_point or "") + filename,
            "offset": offset,
            "comp_sz": comp_sz,
            "uncomp_sz": uncomp_sz,
            "method": comp_meth,
            "blocks": blocks,
        })
    return entries


def load_keys():
    payload = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
    items = payload if isinstance(payload, list) else payload.get("mappings", [])
    return [i["json_key"] for i in items if i.get("json_key")]


def decompress_entry(pak, entry):
    pak.seek(entry["offset"])
    raw = pak.read(entry["comp_sz"])
    if entry["method"] == 0:
        return raw
    blocks = entry.get("blocks")
    if blocks:
        # UE4 PAK: each block is an independent zlib stream.
        out = bytearray()
        for b_start, b_end in blocks:
            chunk = raw[b_start:b_end]
            try:
                out += zlib.decompress(chunk)
            except zlib.error:
                try:
                    out += zlib.decompressobj().decompress(chunk)
                except zlib.error:
                    pass
        return bytes(out)
    try:
        return zlib.decompress(raw)
    except zlib.error:
        return b""


def main():
    keys = load_keys()
    key_bytes = [k.encode("utf-8") for k in keys]
    entries = parse_index()
    print(f"[*] PAK entries: {len(entries):,}")
    print(f"[*] JSON keys to scan: {len(keys)}")

    hits = []
    distinct_total = {k: 0 for k in keys}
    scanned = 0
    with PAK_PATH.open("rb") as pak:
        for entry in entries:
            data = decompress_entry(pak, entry)
            if not data:
                continue
            found = [k for k, kb in zip(keys, key_bytes) if kb in data]
            if found:
                hits.append({"path": entry["path"], "keys": found})
                for k in found:
                    distinct_total[k] += 1
            scanned += 1

    print(f"[*] Entries scanned (decompressed): {scanned:,}")
    print(f"[*] Entries containing >=1 player JSON key: {len(hits)}")
    strong = [h for h in hits if DISTINCTIVE.intersection(h["keys"])]
    print(f"[*] Entries with DISTINCTIVE keys: {len(strong)}")

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({
        "scanned": scanned,
        "hit_entries": len(hits),
        "strong_hit_entries": len(strong),
        "distinct_key_counts": distinct_total,
        "hits": hits[:200],
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    with REPORT.open("w", encoding="utf-8") as f:
        f.write("# Stage 7.3 PAK Player-Key Scan\n\n")
        f.write(f"**PAK:** `{PAK_PATH.relative_to(WORKSPACE)}`\n\n")
        f.write(f"**Entries parsed:** {len(entries):,}\n\n")
        f.write(f"**Entries scanned (decompressed):** {scanned:,}\n\n")
        f.write(f"**Entries with >=1 player JSON key:** {len(hits)}\n\n")
        f.write(f"**Entries with DISTINCTIVE keys:** {len(strong)}\n\n")
        f.write("## Distinctive-key occurrence tally\n\n")
        f.write("| key | occurrences |\n|---|---:|\n")
        for k in sorted(DISTINCTIVE):
            f.write(f"| `{k}` | {distinct_total.get(k, 0)} |\n")
        f.write("\n## Interpretation\n\n")
        if not strong:
            f.write("- No entry contained a distinctive player JSON key "
                    "(`serial_id`, `master_id`, `param_shot`, etc.).\n")
            f.write("- The numeric player DB (`ParameterPlayerDefine`) is **not** "
                    "stored as static JSON assets in this PAK.\n")
            f.write("- Player records are populated at runtime via "
                    "`PrepareDataFromJson`, sourced from the (now dead) server "
                    "or local save data not present in the offline containers.\n")
        else:
            f.write("See `analysis/stage7_scan/pak_player_key_hits.json` for matches.\n")

    print(f"[+] Report: {REPORT}")
    print(f"[+] Hits JSON: {OUT_JSON}")


if __name__ == "__main__":
    main()
