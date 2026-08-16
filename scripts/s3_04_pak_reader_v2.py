"""
Stage 3 - PAK v8 corrected parser
Actual entry layout (observed from hex dump):
  FString filename
  int64  offset
  int64  compressed_size
  int64  uncompressed_size
  uint8  compression_method  (1 byte, not 4!)
  bytes[20] sha1_hash
  if compression_method != 0:
      uint32 block_count
      for each block: int64 start + int64 end
  uint8  flags
  uint32 compression_block_size
"""
import os, struct, sys, hashlib

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAK_PATH  = os.path.join(WORKSPACE, "extracted", "obb_main", "PesMobile", "Content", "Paks", "PesMobile-Android_ETC1.pak")
IDX_OFFSET = 782104571
IDX_SIZE   = 7380528

HIGH_KW   = ['playerid','datatable','definedatatable','derivationdatatable','cpk_dat','cpk','derivation','define']
MEDIUM_KW = ['player','team','club','formation','ability','parameter','common','anime','database','table']

def read_fstring(data, offset):
    if offset + 4 > len(data):
        return None, offset
    length = struct.unpack_from('<i', data, offset)[0]
    offset += 4
    if length == 0:
        return '', offset
    if length < 0:
        byte_count = (-length) * 2
        if offset + byte_count > len(data):
            return None, offset
        s = data[offset:offset+byte_count].decode('utf-16-le', errors='replace').rstrip('\x00')
        return s, offset + byte_count
    else:
        if offset + length > len(data):
            return None, offset
        s = data[offset:offset+length].decode('utf-8', errors='replace').rstrip('\x00')
        return s, offset + length

def score_path(path):
    pl = path.lower()
    for kw in HIGH_KW:
        if kw in pl:
            return 'HIGH'
    for kw in MEDIUM_KW:
        if kw in pl:
            return 'MEDIUM'
    ext = os.path.splitext(pl)[1]
    if ext in ('.bin','.dat','.uasset','.uexp','.ubulk'):
        return 'LOW'
    return 'LOW'

def parse_index():
    with open(PAK_PATH, 'rb') as f:
        f.seek(IDX_OFFSET)
        idx = f.read(IDX_SIZE)

    print(f"[*] Index size: {len(idx):,}")

    pos = 0
    mount_point, pos = read_fstring(idx, pos)
    print(f"[*] Mount point: {mount_point!r}")

    entry_count = struct.unpack_from('<i', idx, pos)[0]; pos += 4
    print(f"[*] Entry count: {entry_count:,}")

    entries = []
    errors  = 0

    for i in range(entry_count):
        start_pos = pos
        filename, pos = read_fstring(idx, pos)
        if filename is None:
            print(f"[!] FString read failed at entry {i}, byte offset {start_pos}")
            errors += 1
            break

        if pos + 8+8+8+1+20 > len(idx):
            print(f"[!] Truncated at entry {i}")
            break

        offset    = struct.unpack_from('<q', idx, pos)[0]; pos += 8
        comp_sz   = struct.unpack_from('<q', idx, pos)[0]; pos += 8
        uncomp_sz = struct.unpack_from('<q', idx, pos)[0]; pos += 8
        comp_meth = struct.unpack_from('<B', idx, pos)[0]; pos += 1   # 1 byte!
        sha1      = idx[pos:pos+20].hex(); pos += 20

        # compression blocks
        if comp_meth != 0:
            if pos + 4 > len(idx):
                break
            block_count = struct.unpack_from('<I', idx, pos)[0]; pos += 4
            pos += block_count * 16   # each block: int64 + int64

        # flags(1) + comp_block_size(4)
        if pos + 5 > len(idx):
            break
        flags    = struct.unpack_from('<B', idx, pos)[0]; pos += 1
        cb_size  = struct.unpack_from('<I', idx, pos)[0]; pos += 4

        full_path = (mount_point or '') + filename
        entries.append({
            'path': full_path,
            'filename': filename,
            'offset': offset,
            'compressed_size': comp_sz,
            'uncompressed_size': uncomp_sz,
            'compression_method': comp_meth,
            'sha1': sha1,
            'flags': flags,
            'relevance': score_path(full_path),
        })

        if (i+1) % 10000 == 0:
            print(f"  ... {i+1:,} entries")

    print(f"[+] Parsed {len(entries):,} entries  ({errors} errors)")
    return mount_point, entries

def write_listing(entries):
    out = os.path.join(WORKSPACE, 'analysis', 'pak_listing', 'main_pak.txt')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(f"# Unreal PAK Listing  — {len(entries):,} entries\n")
        f.write("# RELEVANCE | OFFSET | COMP_SIZE | UNCOMP_SIZE | METHOD | PATH\n#\n")
        for e in entries:
            cm = {0:'None',1:'Zlib',2:'Gzip',4:'LZ4'}.get(e['compression_method'], str(e['compression_method']))
            f.write(f"{e['relevance']:6} | {e['offset']:>12} | {e['compressed_size']:>12} | {e['uncompressed_size']:>12} | {cm:4} | {e['path']}\n")
    print(f"[+] Listing: {out}")

    # Also write a HIGH+MEDIUM only file
    out2 = os.path.join(WORKSPACE, 'analysis', 'pak_listing', 'main_pak_relevant.txt')
    rel_entries = [e for e in entries if e['relevance'] in ('HIGH','MEDIUM')]
    with open(out2, 'w', encoding='utf-8') as f:
        f.write(f"# PAK Relevant Entries ({len(rel_entries):,})\n#\n")
        for e in rel_entries:
            cm = {0:'None',1:'Zlib',2:'Gzip',4:'LZ4'}.get(e['compression_method'], str(e['compression_method']))
            f.write(f"{e['relevance']:6} | {e['offset']:>12} | {e['compressed_size']:>12} | {e['uncompressed_size']:>12} | {cm:4} | {e['path']}\n")
    print(f"[+] Relevant listing: {out2}")

def write_reports(mount_point, entries):
    total = len(entries)
    high  = [e for e in entries if e['relevance'] == 'HIGH']
    med   = [e for e in entries if e['relevance'] == 'MEDIUM']
    low   = [e for e in entries if e['relevance'] == 'LOW']

    # extensions
    exts = {}
    for e in entries:
        ext = os.path.splitext(e['path'])[1].lower()
        exts[ext] = exts.get(ext, 0) + 1

    # unique top-level dirs
    top_dirs = set()
    for e in entries:
        parts = e['path'].replace('\\','/').split('/')
        if len(parts) >= 2:
            top_dirs.add(parts[0]+'/'+parts[1])

    # --- obb_contents.md ---
    p = os.path.join(WORKSPACE, 'reports', 'obb_contents.md')
    with open(p, 'w', encoding='utf-8') as f:
        f.write("# OBB Contents Inventory\n\n")
        f.write("## Summary\n\n")
        f.write(f"Main OBB contains a single Unreal PAK file with **{total:,} entries**.\n\n")
        f.write(f"- PAK version: 8\n- Mount point: `{mount_point}`\n\n")
        f.write("## File Extensions\n\n| Extension | Count |\n|-----------|-------|\n")
        for ext, cnt in sorted(exts.items(), key=lambda x: -x[1])[:30]:
            f.write(f"| `{ext or '(none)'}` | {cnt:,} |\n")
        f.write("\n## Top-Level Directories (sample)\n\n")
        for d in sorted(top_dirs)[:40]:
            f.write(f"- `{d}`\n")
        f.write("\n## HIGH Relevance Files\n\n")
        if high:
            for e in high:
                f.write(f"- `{e['path']}` ({e['uncompressed_size']:,} bytes, method={e['compression_method']})\n")
        else:
            f.write("None detected at HIGH relevance.\n")
        f.write(f"\n## MEDIUM Relevance Files ({len(med):,} total, first 100)\n\n")
        for e in med[:100]:
            f.write(f"- `{e['path']}`\n")
    print(f"[+] OBB contents: {p}")

    # --- pak_inventory.md ---
    pak_size = os.path.getsize(PAK_PATH)
    rel_pak  = os.path.relpath(PAK_PATH, WORKSPACE)
    p2 = os.path.join(WORKSPACE, 'reports', 'pak_inventory.md')
    with open(p2, 'w', encoding='utf-8') as f:
        f.write("# Unreal PAK Inventory\n\n")
        f.write("## Detected PAK Files\n\n")
        f.write(f"| # | Path | Size (MB) | Version | Magic | Entries |\n|---|------|-----------|---------|-------|---------|\n")
        f.write(f"| 1 | `{rel_pak}` | {pak_size/1024/1024:.2f} | v8 | 0x5A6F12E1 ✓ | {total:,} |\n\n")
        f.write("## PAK #1 Details\n\n")
        f.write(f"**Path:** `{rel_pak}`\n\n")
        f.write(f"**Size:** {pak_size:,} bytes ({pak_size/1024/1024:.2f} MB)\n\n")
        f.write(f"**Version:** 8\n\n")
        f.write(f"**Mount point:** `{mount_point}`\n\n")
        f.write(f"**Index offset:** `{IDX_OFFSET:,}` (0x{IDX_OFFSET:X})\n\n")
        f.write(f"**Index size:** `{IDX_SIZE:,}` bytes ({IDX_SIZE/1024:.1f} KB)\n\n")
        f.write(f"**Total entries:** {total:,}\n\n")
        f.write(f"**Encryption:** None detected\n\n")
        f.write("## Relevance Summary\n\n")
        f.write(f"| Level | Count |\n|-------|-------|\n| HIGH | {len(high)} |\n| MEDIUM | {len(med):,} |\n| LOW | {len(low):,} |\n\n")
        f.write("## HIGH Relevance Entries\n\n")
        if high:
            for e in high:
                f.write(f"- `{e['path']}`\n  Offset: {e['offset']}, Compressed: {e['compressed_size']:,}, Uncompressed: {e['uncompressed_size']:,}\n\n")
        else:
            f.write("None.\n")
        f.write("\n## MEDIUM Relevance Sample\n\n")
        for e in med[:30]:
            f.write(f"- `{e['path']}`\n")
    print(f"[+] PAK inventory: {p2}")

def main():
    mount_point, entries = parse_index()
    write_listing(entries)
    write_reports(mount_point, entries)

    high = [e for e in entries if e['relevance'] == 'HIGH']
    med  = [e for e in entries if e['relevance'] == 'MEDIUM']
    print(f"\n[RESULT] {len(entries):,} entries  |  HIGH={len(high)}  MEDIUM={len(med)}")
    if high:
        print("HIGH paths:")
        for e in high:
            print(f"  {e['path']}")
    if med:
        print(f"First 10 MEDIUM paths:")
        for e in med[:10]:
            print(f"  {e['path']}")

if __name__ == '__main__':
    main()
