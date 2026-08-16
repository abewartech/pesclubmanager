"""
CPK string scanner: scan raw binary for ASCII strings.
Look for filenames like .bin, .cpk, paths like cpk_dat/, playerID/, etc.
Process in 1MB chunks to avoid RAM issues.
READ-ONLY.
"""
import os, re, struct

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CPK = os.path.join(WORKSPACE, "original", "patch.104050101.jp.konami.pesclubmanager.obb")
CHUNK_SIZE = 1024 * 1024   # 1 MB
MIN_STR_LEN = 6

TARGET_PATTERNS = [
    r'playerid', r'player_id', r'playerID', r'PlayerID',
    r'datatable', r'DataTable', r'definedatatable', r'Definedatatable',
    r'derivationdatatable', r'Derivationdatatable',
    r'cpk_dat', r'cpk_dat/',
    r'\.cpk\b', r'\.bin\b', r'\.dat\b',
    r'common/anime', r'common\\anime',
    r'player', r'Player',
    r'formation', r'parameter', r'ability',
    r'team', r'Team',
    r'masterdata', r'MasterData',
]

def scan_strings(path, chunk_size=CHUNK_SIZE, min_len=MIN_STR_LEN, max_scan=None):
    """Yield (offset, string) for all printable ASCII runs >= min_len."""
    file_size = os.path.getsize(path)
    scan_limit = min(file_size, max_scan) if max_scan else file_size
    
    with open(path, 'rb') as f:
        offset = 0
        overlap = b''
        while offset < scan_limit:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            data = overlap + chunk
            # Find all printable ASCII runs
            for m in re.finditer(rb'[ -~]{' + str(min_len).encode() + rb',}', data):
                start = offset - len(overlap) + m.start()
                s = m.group().decode('ascii', errors='replace')
                yield start, s
            # Keep last min_len-1 bytes as overlap for cross-boundary strings
            overlap = chunk[-(min_len-1):]
            offset += len(chunk)

def main():
    file_size = os.path.getsize(CPK)
    print(f"[*] Scanning {CPK}")
    print(f"[*] File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
    print(f"[*] Scanning full file for ASCII strings >= {MIN_STR_LEN} chars...")
    print(f"[*] (This may take a few minutes for 832 MB)")
    
    # Compile target patterns
    patterns = [re.compile(p, re.IGNORECASE) for p in TARGET_PATTERNS]
    
    hits = []
    all_extensions = {}
    string_count = 0
    
    for off, s in scan_strings(CPK):
        string_count += 1
        # Check extension
        if '.' in s:
            ext_m = re.search(r'\.(cpk|bin|dat|csv|txt|xml|json|lua|pac|acb|awb|usm)\b', s, re.IGNORECASE)
            if ext_m:
                ext = ext_m.group(1).lower()
                all_extensions[ext] = all_extensions.get(ext, 0) + 1
        # Check target patterns
        for pat in patterns:
            if pat.search(s):
                hits.append((off, s, pat.pattern))
                break
    
    print(f"[*] Total strings found: {string_count:,}")
    print(f"[*] Keyword hits: {len(hits)}")
    
    # Write results
    out_dir = os.path.join(WORKSPACE, 'analysis', 'cpk_listing')
    os.makedirs(out_dir, exist_ok=True)
    
    out_file = os.path.join(out_dir, 'patch_cpk_strings.txt')
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write("# CPK String Scan Results\n")
        f.write(f"# File: patch.104050101.jp.konami.pesclubmanager.obb\n")
        f.write(f"# Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)\n")
        f.write(f"# Total strings: {string_count:,}\n")
        f.write(f"# Keyword hits: {len(hits)}\n")
        f.write("#\n")
        f.write("# Extensions found in strings:\n")
        for ext, cnt in sorted(all_extensions.items(), key=lambda x: -x[1]):
            f.write(f"#   .{ext}: {cnt}\n")
        f.write("#\n")
        f.write("# --- KEYWORD HITS ---\n")
        for off, s, pat in hits:
            f.write(f"0x{off:012x}  [{pat}]  {s}\n")
    
    print(f"[+] Results: {out_file}")
    print(f"\n=== Extension summary ===")
    for ext, cnt in sorted(all_extensions.items(), key=lambda x: -x[1]):
        print(f"  .{ext}: {cnt}")
    
    print(f"\n=== First 50 keyword hits ===")
    for off, s, pat in hits[:50]:
        print(f"  0x{off:012x}  {s!r}")
    
    return hits, all_extensions

if __name__ == '__main__':
    main()
