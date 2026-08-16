"""
Stage 3 - Step 8+9+10: CRIWARE CPK Inspector (READ-ONLY)
Parses CPK header, UTF table, and file list.

CPK format:
  0x00: "CPK " magic (4 bytes) + 0xFF (1 byte) + reserved (3 bytes)
  0x08: CPK table offset (from file start) — actually the UTF table follows at 0x10
  
  CPK contains a UTF (Unicode Text Format) table starting at offset 0x10.
  UTF table:
    "@UTF" magic (4 bytes)
    table_size (uint32)
    rows_offset (uint32)  -- relative to table_data start
    strings_offset (uint32)
    data_offset (uint32)
    table_name_offset (uint32)
    num_columns (uint16)
    row_stride (uint16)
    num_rows (uint32)
    
    columns[num_columns]:
      flags (uint8)
      name_offset (uint32)
      default_value (variable)
    
    rows[num_rows]: row_stride bytes each

Output:
  reports/cpk_inventory.md
  analysis/cpk_listing/patch_cpk.txt
"""
import os, struct, sys, hashlib

WORKSPACE  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CPK_PATH   = os.path.join(WORKSPACE, "original", "patch.104050101.jp.konami.pesclubmanager.obb")
CHUNK      = 1024 * 1024

# Column storage types
COLUMN_TYPES = {
    0x00: ('uint8',  'B', 1),
    0x01: ('sint8',  'b', 1),
    0x02: ('uint16', 'H', 2),
    0x03: ('sint16', 'h', 2),
    0x04: ('uint32', 'I', 4),
    0x05: ('sint32', 'i', 4),
    0x06: ('uint64', 'Q', 8),
    0x07: ('sint64', 'q', 8),
    0x08: ('float',  'f', 4),
    0x09: ('double', 'd', 8),
    0x0A: ('string', None, 4),  # offset into string table
    0x0B: ('data',   None, 8),  # offset(4) + size(4)
}

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            buf = f.read(CHUNK)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()

def parse_utf_table(data, base_offset=0):
    """Parse a CRIWARE @UTF table from bytes. Returns dict with columns, rows."""
    if data[:4] != b'@UTF':
        return None
    
    table_size     = struct.unpack_from('>I', data, 4)[0]
    rows_offset    = struct.unpack_from('>I', data, 8)[0]
    strings_offset = struct.unpack_from('>I', data, 12)[0]
    data_offset    = struct.unpack_from('>I', data, 16)[0]
    table_name_off = struct.unpack_from('>I', data, 20)[0]
    num_columns    = struct.unpack_from('>H', data, 24)[0]
    row_stride     = struct.unpack_from('>H', data, 26)[0]
    num_rows       = struct.unpack_from('>I', data, 28)[0]
    
    # String table starts at 8 + strings_offset
    string_base = 8 + strings_offset
    
    def read_string(offset):
        end = data.index(b'\x00', string_base + offset)
        return data[string_base + offset:end].decode('utf-8', errors='replace')
    
    try:
        table_name = read_string(table_name_off)
    except:
        table_name = '?'
    
    # Parse columns (starting at offset 32)
    pos = 32
    columns = []
    for i in range(num_columns):
        if pos >= len(data):
            break
        flags = data[pos]; pos += 1
        storage = (flags >> 4) & 0x0F
        col_type = flags & 0x0F
        
        name_offset = struct.unpack_from('>I', data, pos)[0]; pos += 4
        try:
            col_name = read_string(name_offset)
        except:
            col_name = f'col{i}'
        
        # Default value for constant/zero storage
        default_val = None
        if storage == 1:  # constant
            if col_type in COLUMN_TYPES:
                tname, fmt, sz = COLUMN_TYPES[col_type]
                if fmt:
                    default_val = struct.unpack_from('>' + fmt, data, pos)[0]
                    pos += sz
                elif col_type == 0x0A:  # string
                    str_off = struct.unpack_from('>I', data, pos)[0]; pos += 4
                    try:
                        default_val = read_string(str_off)
                    except:
                        default_val = f'@{str_off}'
                elif col_type == 0x0B:  # data
                    d_off = struct.unpack_from('>I', data, pos)[0]; pos += 4
                    d_sz  = struct.unpack_from('>I', data, pos)[0]; pos += 4
                    default_val = (d_off, d_sz)
        elif storage == 3:  # zero
            pass  # no bytes in column def
        
        columns.append({'name': col_name, 'type': col_type, 'storage': storage, 'default': default_val})
    
    # Parse rows
    row_data_start = 8 + rows_offset
    rows = []
    for r in range(num_rows):
        row = {}
        row_pos = row_data_start + r * row_stride
        field_pos = row_pos
        for col in columns:
            storage = col['storage']
            col_type = col['type']
            
            if storage == 1:  # constant
                row[col['name']] = col['default']
            elif storage == 3:  # zero
                row[col['name']] = 0
            else:  # per-row (storage 0 or 2)
                if col_type not in COLUMN_TYPES:
                    row[col['name']] = None
                    continue
                tname, fmt, sz = COLUMN_TYPES[col_type]
                if fmt:
                    if field_pos + sz <= len(data):
                        val = struct.unpack_from('>' + fmt, data, field_pos)[0]
                        field_pos += sz
                    else:
                        val = None
                    row[col['name']] = val
                elif col_type == 0x0A:  # string
                    if field_pos + 4 <= len(data):
                        str_off = struct.unpack_from('>I', data, field_pos)[0]
                        field_pos += 4
                        try:
                            row[col['name']] = read_string(str_off)
                        except:
                            row[col['name']] = f'@{str_off}'
                    else:
                        row[col['name']] = None
                elif col_type == 0x0B:  # data blob
                    if field_pos + 8 <= len(data):
                        d_off = struct.unpack_from('>I', data, field_pos)[0]
                        d_sz  = struct.unpack_from('>I', data, field_pos+4)[0]
                        field_pos += 8
                        row[col['name']] = (d_off, d_sz)
                    else:
                        row[col['name']] = None
        rows.append(row)
    
    return {
        'name': table_name,
        'num_columns': num_columns,
        'num_rows': num_rows,
        'row_stride': row_stride,
        'columns': columns,
        'rows': rows,
    }

def parse_cpk(cpk_path):
    print(f"[*] Opening CPK: {cpk_path}")
    size = os.path.getsize(cpk_path)
    print(f"[*] Size: {size:,} bytes ({size/1024/1024:.1f} MB)")

    with open(cpk_path, 'rb') as f:
        # Read header
        header = f.read(2048)
    
    magic = header[:4]
    assert magic == b'CPK ', f"Not a CPK file: {magic!r}"
    
    unk1 = struct.unpack_from('<I', header, 4)[0]
    utf_size = struct.unpack_from('<q', header, 8)[0]
    print(f"[*] CPK magic OK. UTF size field: {utf_size}")
    
    # UTF table starts at offset 0x10
    utf_offset = 0x10
    with open(cpk_path, 'rb') as f:
        f.seek(utf_offset)
        # Read UTF header to get table size
        utf_hdr = f.read(32)
    
    if utf_hdr[:4] != b'@UTF':
        print(f"[!] Expected @UTF at 0x10, got: {utf_hdr[:4].hex()}")
        return None
    
    table_size = struct.unpack_from('>I', utf_hdr, 4)[0]
    print(f"[*] UTF table size: {table_size:,} bytes")
    
    with open(cpk_path, 'rb') as f:
        f.seek(utf_offset)
        utf_data = f.read(table_size + 8)  # +8 for the header before table_size
    
    print(f"[*] Parsing CPK header UTF table...")
    cpk_table = parse_utf_table(utf_data)
    if not cpk_table:
        print("[!] Failed to parse UTF table")
        return None
    
    print(f"[*] CPK table: '{cpk_table['name']}', {cpk_table['num_columns']} columns, {cpk_table['num_rows']} rows")
    
    # Extract key CPK header values from first row
    row0 = cpk_table['rows'][0] if cpk_table['rows'] else {}
    print(f"[*] CPK header fields found: {list(row0.keys())}")
    
    # Get ITOC/ETOC/GTOC offsets
    itoc_offset = row0.get('ItocOffset', None)
    etoc_offset = row0.get('EtocOffset', None)
    gtoc_offset = row0.get('GtocOffset', None)
    content_offset = row0.get('ContentOffset', None)
    files_count = row0.get('Files', None)
    
    print(f"[*] ItocOffset: {itoc_offset}")
    print(f"[*] EtocOffset: {etoc_offset}")
    print(f"[*] GtocOffset: {gtoc_offset}")
    print(f"[*] ContentOffset: {content_offset}")
    print(f"[*] Files: {files_count}")
    
    # Parse ITOC (Index Table Of Contents)
    itoc_entries = []
    if itoc_offset and isinstance(itoc_offset, int) and itoc_offset > 0:
        print(f"\n[*] Parsing ITOC at offset {itoc_offset:,}...")
        with open(cpk_path, 'rb') as f:
            f.seek(itoc_offset)
            itoc_hdr = f.read(8)
        
        if itoc_hdr[:4] == b'ITOC':
            with open(cpk_path, 'rb') as f:
                f.seek(itoc_offset + 0x10)
                itoc_utf_hdr = f.read(8)
            if itoc_utf_hdr[:4] == b'@UTF':
                itoc_tbl_size = struct.unpack_from('>I', itoc_utf_hdr, 4)[0]
                with open(cpk_path, 'rb') as f:
                    f.seek(itoc_offset + 0x10)
                    itoc_utf_data = f.read(itoc_tbl_size + 8)
                itoc_table = parse_utf_table(itoc_utf_data)
                if itoc_table:
                    print(f"[*] ITOC table: '{itoc_table['name']}', {itoc_table['num_rows']} rows")
                    itoc_entries = itoc_table['rows']
                    print(f"[*] ITOC columns: {[c['name'] for c in itoc_table['columns']]}")
    
    # Parse GTOC (filename table) if present
    gtoc_entries = []
    if gtoc_offset and isinstance(gtoc_offset, int) and gtoc_offset > 0:
        print(f"\n[*] Parsing GTOC at offset {gtoc_offset:,}...")
        with open(cpk_path, 'rb') as f:
            f.seek(gtoc_offset)
            gtoc_hdr = f.read(8)
        if gtoc_hdr[:4] == b'GTOC':
            with open(cpk_path, 'rb') as f:
                f.seek(gtoc_offset + 0x10)
                gtoc_utf_hdr = f.read(8)
            if gtoc_utf_hdr[:4] == b'@UTF':
                gtoc_tbl_size = struct.unpack_from('>I', gtoc_utf_hdr, 4)[0]
                with open(cpk_path, 'rb') as f:
                    f.seek(gtoc_offset + 0x10)
                    gtoc_utf_data = f.read(gtoc_tbl_size + 8)
                gtoc_table = parse_utf_table(gtoc_utf_data)
                if gtoc_table:
                    print(f"[*] GTOC table: '{gtoc_table['name']}', {gtoc_table['num_rows']} rows")
                    gtoc_entries = gtoc_table['rows']

    # Parse ETOC (extended TOC with filenames)
    etoc_entries = []
    if etoc_offset and isinstance(etoc_offset, int) and etoc_offset > 0:
        print(f"\n[*] Parsing ETOC at offset {etoc_offset:,}...")
        with open(cpk_path, 'rb') as f:
            f.seek(etoc_offset)
            etoc_hdr = f.read(8)
        if etoc_hdr[:4] == b'ETOC':
            with open(cpk_path, 'rb') as f:
                f.seek(etoc_offset + 0x10)
                etoc_utf_hdr = f.read(8)
            if etoc_utf_hdr[:4] == b'@UTF':
                etoc_tbl_size = struct.unpack_from('>I', etoc_utf_hdr, 4)[0]
                with open(cpk_path, 'rb') as f:
                    f.seek(etoc_offset + 0x10)
                    etoc_utf_data = f.read(etoc_tbl_size + 8)
                etoc_table = parse_utf_table(etoc_utf_data)
                if etoc_table:
                    print(f"[*] ETOC table: '{etoc_table['name']}', {etoc_table['num_rows']} rows")
                    etoc_entries = etoc_table['rows']
                    if etoc_entries:
                        print(f"[*] ETOC columns: {[c['name'] for c in etoc_table['columns']]}")
                        print(f"[*] ETOC row sample: {etoc_entries[0]}")
    
    return {
        'size': size,
        'cpk_table': cpk_table,
        'row0': row0,
        'itoc_entries': itoc_entries,
        'etoc_entries': etoc_entries,
        'gtoc_entries': gtoc_entries,
    }

def find_player_files(itoc_entries, etoc_entries, gtoc_entries):
    """Search all entries for playerID/datatable related names."""
    keywords = ['playerid', 'datatable', 'definedatatable', 'derivationdatatable',
                'cpk_dat', 'player', 'team', 'parameter', 'ability', 'formation',
                'define', 'derive', 'common', 'anime', '.bin', '.dat']
    
    results = []
    all_entries = list(itoc_entries) + list(etoc_entries) + list(gtoc_entries)
    
    for e in all_entries:
        for key, val in e.items():
            if isinstance(val, str):
                vl = val.lower()
                for kw in keywords:
                    if kw in vl:
                        results.append({'source': 'entry', 'key': key, 'value': val, 'entry': e, 'keyword': kw})
                        break
    return results

def main():
    # Compute SHA256 first
    print(f"[*] Computing SHA-256 (may take ~30s)...")
    sha = sha256_file(CPK_PATH)
    print(f"[+] SHA-256: {sha}")

    # Parse CPK
    result = parse_cpk(CPK_PATH)
    if not result:
        print("[!] CPK parse failed")
        write_failure_report(sha)
        return

    # Search for player-related entries
    hits = find_player_files(
        result['itoc_entries'],
        result['etoc_entries'],
        result['gtoc_entries'],
    )

    print(f"\n[*] Player/team/table keyword hits: {len(hits)}")
    for h in hits[:20]:
        print(f"  {h['keyword']} => {h['key']}: {h['value']!r}")

    # Write outputs
    write_cpk_inventory(result, sha, hits)
    write_cpk_listing(result, hits)

def write_failure_report(sha):
    ws = WORKSPACE
    cpk_size = os.path.getsize(CPK_PATH)
    with open(os.path.join(ws, 'reports', 'cpk_inventory.md'), 'w', encoding='utf-8') as f:
        f.write("# CPK Inventory\n\n")
        f.write(f"**File:** `{os.path.relpath(CPK_PATH, ws)}`\n\n")
        f.write(f"**Size:** {cpk_size:,} bytes\n\n")
        f.write(f"**SHA-256:** `{sha}`\n\n")
        f.write(f"**Magic:** `CPK ` (0x43504B20) — CRIWARE CPK confirmed\n\n")
        f.write("**Parse result:** FAILED — see debug output\n\n")

def write_cpk_inventory(result, sha, hits):
    ws = WORKSPACE
    cpk_rel = os.path.relpath(CPK_PATH, ws)
    row0 = result['row0']
    
    out = os.path.join(ws, 'reports', 'cpk_inventory.md')
    with open(out, 'w', encoding='utf-8') as f:
        f.write("# CPK Inventory\n\n")
        f.write("## Patch OBB (CRIWARE CPK)\n\n")
        f.write(f"**Path:** `{cpk_rel}`\n\n")
        f.write(f"**Size:** {result['size']:,} bytes ({result['size']/1024/1024:.2f} MB)\n\n")
        f.write(f"**SHA-256:** `{sha}`\n\n")
        f.write(f"**Magic:** `CPK ` (0x43504B20 big-endian / 0x20 0x4B 0x50 0x43) — CRIWARE CPK\n\n")
        f.write(f"**Format verified:** YES — @UTF table found at offset 0x10\n\n")
        f.write("\n## CPK Header Fields (from @UTF table)\n\n")
        f.write("| Field | Value |\n|-------|-------|\n")
        for k, v in row0.items():
            f.write(f"| {k} | `{v}` |\n")
        
        f.write("\n## Table Counts\n\n")
        f.write(f"| Table | Rows |\n|-------|------|\n")
        f.write(f"| ITOC | {len(result['itoc_entries']):,} |\n")
        f.write(f"| ETOC | {len(result['etoc_entries']):,} |\n")
        f.write(f"| GTOC | {len(result['gtoc_entries']):,} |\n")
        
        f.write("\n## Player/Table/CPK Keyword Hits\n\n")
        if hits:
            f.write(f"Found **{len(hits)}** entries matching player/table/CPK keywords.\n\n")
            f.write("| Keyword | Key | Value |\n|---------|-----|-------|\n")
            for h in hits[:50]:
                f.write(f"| `{h['keyword']}` | `{h['key']}` | `{str(h['value'])[:80]}` |\n")
        else:
            f.write("No entries with player/table/CPK keywords found in parsed tables.\n\n")
            f.write("> NOTE: ITOC/ETOC may not contain filenames — GTOC or TOC might hold them.\n\n")

        f.write("\n## ETOC Sample (first 10 rows)\n\n")
        for r in result['etoc_entries'][:10]:
            f.write(f"- `{r}`\n")

        f.write("\n## ITOC Sample (first 10 rows)\n\n")
        for r in result['itoc_entries'][:10]:
            f.write(f"- `{r}`\n")

    print(f"[+] CPK inventory: {out}")

def write_cpk_listing(result, hits):
    ws = WORKSPACE
    os.makedirs(os.path.join(ws, 'analysis', 'cpk_listing'), exist_ok=True)
    out = os.path.join(ws, 'analysis', 'cpk_listing', 'patch_cpk.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write("# CRIWARE CPK Listing — patch.104050101.jp.konami.pesclubmanager.obb\n#\n")
        f.write(f"# ITOC rows: {len(result['itoc_entries'])}\n")
        f.write(f"# ETOC rows: {len(result['etoc_entries'])}\n")
        f.write(f"# GTOC rows: {len(result['gtoc_entries'])}\n#\n")
        f.write("# --- ITOC ---\n")
        for r in result['itoc_entries']:
            f.write(str(r) + '\n')
        f.write("# --- ETOC ---\n")
        for r in result['etoc_entries']:
            f.write(str(r) + '\n')
        f.write("# --- GTOC ---\n")
        for r in result['gtoc_entries']:
            f.write(str(r) + '\n')
        if hits:
            f.write("\n# --- KEYWORD HITS ---\n")
            for h in hits:
                f.write(f"# KW={h['keyword']} KEY={h['key']} VAL={h['value']!r}\n")
    print(f"[+] CPK listing: {out}")

if __name__ == '__main__':
    main()
