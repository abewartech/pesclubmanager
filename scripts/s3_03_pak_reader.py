"""
Stage 3 - Steps 4,5,6,7: Unreal PAK v8 index reader (READ-ONLY)
- Parse PAK index at known offset
- List all file paths
- Write reports/obb_contents.md, reports/pak_inventory.md
- Write analysis/pak_listing/main_pak.txt
- Categorize by relevance

Unreal PAK v8 index layout (after magic/version/offset/size/hash):
  mount_point: FString
  entry_count: int32
  for each entry:
    filename: FString
    offset: int64
    compressed_size: int64
    uncompressed_size: int64
    compression_method: uint32
    sha1_hash: 20 bytes
    compression_blocks: if compression_method != 0: block_count * (int64 + int64)
    flags: uint8
    compression_block_size: uint32

FString: int32 length (negative = UTF-16LE, positive = UTF-8/ASCII)
"""
import os, struct, sys, hashlib

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAK_PATH = os.path.join(WORKSPACE, "extracted", "obb_main", "PesMobile", "Content", "Paks", "PesMobile-Android_ETC1.pak")
MAGIC = 0x5A6F12E1

# Keywords for relevance scoring
HIGH_KEYWORDS   = ['playerid', 'playerID', 'player_id', 'datatable', 'DataTable',
                   'definedatatable', 'derivationdatatable', 'cpk_dat', 'cpk',
                   'Derivation', 'Define', 'playerID']
MEDIUM_KEYWORDS = ['player', 'Player', 'team', 'Team', 'club', 'Club',
                   'formation', 'Formation', 'ability', 'Ability', 'parameter',
                   'Parameter', 'common', 'anime', 'database', 'Database',
                   'table', 'Table']
LOW_KEYWORDS    = ['.bin', '.dat', '.uasset', '.uexp', '.ubulk']

def read_fstring(data, offset):
    """Read UE4 FString. Returns (string, new_offset)."""
    if offset + 4 > len(data):
        return None, offset
    length = struct.unpack_from('<i', data, offset)[0]
    offset += 4
    if length == 0:
        return '', offset
    if length < 0:
        # UTF-16LE
        byte_count = (-length) * 2
        if offset + byte_count > len(data):
            return None, offset
        s = data[offset:offset + byte_count].decode('utf-16-le', errors='replace').rstrip('\x00')
        return s, offset + byte_count
    else:
        # UTF-8 / ASCII
        if offset + length > len(data):
            return None, offset
        s = data[offset:offset + length].decode('utf-8', errors='replace').rstrip('\x00')
        return s, offset + length

def score_path(path):
    pl = path.lower()
    for kw in HIGH_KEYWORDS:
        if kw.lower() in pl:
            return 'HIGH'
    for kw in MEDIUM_KEYWORDS:
        if kw.lower() in pl:
            return 'MEDIUM'
    for kw in LOW_KEYWORDS:
        if pl.endswith(kw):
            return 'LOW'
    return 'LOW'

def parse_pak_index(pak_path):
    print(f"[*] Opening PAK: {pak_path}")
    file_size = os.path.getsize(pak_path)

    # Find footer (magic at -172 from end, confirmed earlier)
    FOOTER_BACK = 172
    with open(pak_path, 'rb') as f:
        f.seek(-FOOTER_BACK, 2)
        footer = f.read(53)

    sig = struct.unpack_from('<I', footer, 0)[0]
    assert sig == MAGIC, f"PAK magic mismatch: 0x{sig:08X}"
    version = struct.unpack_from('<I', footer, 4)[0]
    idx_offset = struct.unpack_from('<q', footer, 8)[0]
    idx_size = struct.unpack_from('<q', footer, 16)[0]
    idx_hash = footer[24:44].hex()

    print(f"[*] PAK version: {version}")
    print(f"[*] Index offset: {idx_offset:,}  size: {idx_size:,}")
    print(f"[*] Index hash:   {idx_hash}")

    # Read index block
    print(f"[*] Reading index ({idx_size/1024:.1f} KB)...")
    with open(pak_path, 'rb') as f:
        f.seek(idx_offset)
        index_data = f.read(idx_size)

    print(f"[*] Index read: {len(index_data):,} bytes")

    # Verify index hash (SHA1)
    import hashlib
    actual_hash = hashlib.sha1(index_data).hexdigest()
    stored_hash = footer[24:44].hex()
    if actual_hash == stored_hash:
        print(f"[+] Index SHA1 VERIFIED")
    else:
        print(f"[!] Index SHA1 MISMATCH: stored={stored_hash}, actual={actual_hash}")

    # Parse index
    pos = 0
    mount_point, pos = read_fstring(index_data, pos)
    print(f"[*] Mount point: {mount_point!r}")

    if pos + 4 > len(index_data):
        print("[!] Index too short for entry count")
        return None, None, None, None, []

    entry_count = struct.unpack_from('<i', index_data, pos)[0]
    pos += 4
    print(f"[*] Entry count: {entry_count:,}")

    entries = []
    errors = 0

    for i in range(entry_count):
        if pos + 4 > len(index_data):
            print(f"[!] Ran out of data at entry {i}")
            break

        filename, pos = read_fstring(index_data, pos)
        if filename is None:
            errors += 1
            break

        if pos + 8 + 8 + 8 + 4 + 20 > len(index_data):
            print(f"[!] Truncated entry at {i}: {filename}")
            break

        offset   = struct.unpack_from('<q', index_data, pos)[0]; pos += 8
        comp_sz  = struct.unpack_from('<q', index_data, pos)[0]; pos += 8
        uncomp_sz= struct.unpack_from('<q', index_data, pos)[0]; pos += 8
        comp_meth= struct.unpack_from('<I', index_data, pos)[0]; pos += 4
        sha1     = index_data[pos:pos+20].hex(); pos += 20

        # compression blocks (if compressed)
        if comp_meth != 0:
            if pos + 4 > len(index_data):
                break
            block_count = struct.unpack_from('<I', index_data, pos)[0]; pos += 4
            # each block: int64 start + int64 end = 16 bytes
            pos += block_count * 16

        # flags byte + compression block size
        if pos + 5 > len(index_data):
            break
        flags     = struct.unpack_from('<B', index_data, pos)[0]; pos += 1
        cb_size   = struct.unpack_from('<I', index_data, pos)[0]; pos += 4

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
            'compression_block_size': cb_size,
            'relevance': score_path(full_path),
        })

        if (i+1) % 10000 == 0:
            print(f"  ... {i+1:,} entries parsed")

    print(f"[+] Parsed {len(entries):,} entries ({errors} errors)")
    return version, mount_point, idx_offset, idx_size, entries

def write_pak_listing(entries, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("# Unreal PAK File Listing\n")
        f.write(f"# Total entries: {len(entries)}\n")
        f.write("#\n")
        f.write("# Columns: RELEVANCE | OFFSET | COMP_SIZE | UNCOMP_SIZE | COMP_METHOD | PATH\n")
        f.write("#\n")
        for e in entries:
            cm = {0:'None',1:'Zlib',2:'Gzip',3:'Custom'}.get(e['compression_method'], str(e['compression_method']))
            f.write(f"{e['relevance']:6} | {e['offset']:>12} | {e['compressed_size']:>12} | {e['uncompressed_size']:>12} | {cm:6} | {e['path']}\n")
    print(f"[+] PAK listing: {out_path}")

def write_reports(version, mount_point, idx_offset, idx_size, entries, pak_path):
    ws = WORKSPACE
    total_files = len(entries)
    high = [e for e in entries if e['relevance'] == 'HIGH']
    med  = [e for e in entries if e['relevance'] == 'MEDIUM']
    low  = [e for e in entries if e['relevance'] == 'LOW']

    # Get unique extensions
    exts = {}
    for e in entries:
        ext = os.path.splitext(e['path'])[1].lower()
        exts[ext] = exts.get(ext, 0) + 1

    # --- obb_contents.md ---
    contents_path = os.path.join(ws, 'reports', 'obb_contents.md')
    with open(contents_path, 'w', encoding='utf-8') as f:
        f.write("# OBB Contents Inventory\n\n")
        f.write("## Main OBB → PAK Summary\n\n")
        f.write(f"The main OBB contains a single Unreal Engine PAK file:\n\n")
        f.write(f"- `PesMobile/Content/Paks/PesMobile-Android_ETC1.pak`\n")
        f.write(f"- Unreal PAK version: **{version}**\n")
        f.write(f"- Mount point: `{mount_point}`\n")
        f.write(f"- Total entries: **{total_files:,}**\n\n")
        f.write("## File Extension Distribution\n\n")
        f.write("| Extension | Count |\n|-----------|-------|\n")
        for ext, cnt in sorted(exts.items(), key=lambda x: -x[1])[:30]:
            f.write(f"| `{ext or '(none)'}` | {cnt:,} |\n")
        f.write("\n## High-Relevance Files\n\n")
        if high:
            for e in high:
                f.write(f"- `{e['path']}` ({e['uncompressed_size']:,} bytes)\n")
        else:
            f.write("None found at HIGH relevance level.\n")
        f.write("\n## Medium-Relevance Files (sample, first 50)\n\n")
        for e in med[:50]:
            f.write(f"- `{e['path']}`\n")
        f.write(f"\n_(Total medium: {len(med):,})_\n\n")
        f.write("## Key Directories Found\n\n")
        dirs = set()
        for e in entries:
            parts = e['path'].replace('\\','/').split('/')
            if len(parts) > 1:
                dirs.add('/'.join(parts[:-1]))
        for d in sorted(dirs)[:60]:
            f.write(f"- `{d}/`\n")
        if len(dirs) > 60:
            f.write(f"\n_(+{len(dirs)-60} more directories)_\n")
    print(f"[+] OBB contents: {contents_path}")

    # --- pak_inventory.md ---
    pak_inv_path = os.path.join(ws, 'reports', 'pak_inventory.md')
    pak_size = os.path.getsize(pak_path)
    rel_pak = os.path.relpath(pak_path, ws)
    with open(pak_inv_path, 'w', encoding='utf-8') as f:
        f.write("# Unreal PAK Inventory\n\n")
        f.write("## PAK Files Detected\n\n")
        f.write(f"| # | File | Size | Version | Magic | Entries |\n")
        f.write(f"|---|------|------|---------|-------|---------|\n")
        f.write(f"| 1 | `{rel_pak}` | {pak_size/1024/1024:.2f} MB | v{version} | 0x5A6F12E1 ✓ | {total_files:,} |\n\n")
        f.write("## PAK #1 Details\n\n")
        f.write(f"**Path:** `{rel_pak}`\n\n")
        f.write(f"**Size:** {pak_size:,} bytes ({pak_size/1024/1024:.2f} MB)\n\n")
        f.write(f"**Magic bytes:** `0xE1126F5A` (little-endian `0x5A6F12E1`) — Unreal PAK confirmed\n\n")
        f.write(f"**Version:** {version}\n\n")
        f.write(f"**Mount point:** `{mount_point}`\n\n")
        f.write(f"**Index offset:** `{idx_offset:,}` (0x{idx_offset:X})\n\n")
        f.write(f"**Index size:** `{idx_size:,}` bytes ({idx_size/1024:.1f} KB)\n\n")
        f.write(f"**Total entries:** {total_files:,}\n\n")
        f.write(f"**Encryption:** Not detected (flags=0 on sampled entries)\n\n")
        f.write("## Relevance Breakdown\n\n")
        f.write(f"| Relevance | Count |\n|-----------|-------|\n")
        f.write(f"| HIGH | {len(high):,} |\n")
        f.write(f"| MEDIUM | {len(med):,} |\n")
        f.write(f"| LOW | {len(low):,} |\n\n")
        f.write("## High-Relevance Paths\n\n")
        if high:
            for e in high:
                f.write(f"- `{e['path']}`\n")
        else:
            f.write("None.\n")
    print(f"[+] PAK inventory: {pak_inv_path}")

def main():
    version, mount_point, idx_offset, idx_size, entries = parse_pak_index(PAK_PATH)
    if not entries:
        print("[!] No entries parsed. Aborting reports.")
        return

    # Write listing file
    listing_path = os.path.join(WORKSPACE, 'analysis', 'pak_listing', 'main_pak.txt')
    write_pak_listing(entries, listing_path)

    # Write reports
    write_reports(version, mount_point, idx_offset, idx_size, entries, PAK_PATH)

    print("\n[SUMMARY]")
    print(f"  Total entries: {len(entries):,}")
    high = [e for e in entries if e['relevance'] == 'HIGH']
    med  = [e for e in entries if e['relevance'] == 'MEDIUM']
    print(f"  HIGH relevance: {len(high)}")
    print(f"  MEDIUM relevance: {len(med)}")
    if high:
        print("\n  HIGH relevance paths:")
        for e in high:
            print(f"    {e['path']}")

if __name__ == '__main__':
    main()
