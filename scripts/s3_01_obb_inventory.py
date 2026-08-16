"""
Stage 3 - Step 1: OBB Inventory
Locate all *.obb files, read magic bytes, compute SHA-256, classify.
Output: reports/obb_inventory.md
READ-ONLY.
"""
import os, hashlib, struct, sys

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHUNK = 1024 * 1024  # 1 MB

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            buf = f.read(CHUNK)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()

def read_magic(path, n=16):
    with open(path, "rb") as f:
        return f.read(n)

def identify_format(magic):
    if magic[:4] == b'PK\x03\x04':
        return "ZIP (PK signature) — OBB is ZIP-compatible container"
    if magic[:4] == b'PK\x05\x06':
        return "ZIP (empty archive)"
    if magic[:4] == b'PK\x07\x08':
        return "ZIP (spanned)"
    if magic[:4] == b'\x1f\x8b':
        return "GZIP"
    if magic[:3] == b'Rar':
        return "RAR"
    if magic[:6] == b'7z\xbc\xaf\x27\x1c':
        return "7-Zip"
    if magic[:4] == b'\x89PNG':
        return "PNG"
    if magic[:4] == b'CRID':
        return "CRIWARE CPK (CRID magic)"
    if magic[:4] == b'@UTF':
        return "CRIWARE UTF table"
    sig_le = struct.unpack_from('<I', magic[:4])[0] if len(magic) >= 4 else 0
    if sig_le == 0x5A6F12E1:
        return "Unreal PAK"
    return f"UNKNOWN (hex: {magic[:8].hex()})"

def classify_role(filename, size, fmt):
    name_lower = filename.lower()
    if 'main' in name_lower:
        role = "MAIN OBB — primary game data container"
    elif 'patch' in name_lower:
        role = "PATCH OBB — update/patch data"
    elif 'expansion' in name_lower:
        role = "EXPANSION OBB"
    else:
        role = "UNKNOWN role — filename does not indicate type"
    return role

def find_obb_files(root):
    results = []
    for dirpath, dirs, files in os.walk(root):
        # Skip tool directories
        skip = False
        for skip_dir in ['ghidra', 'radare2', 'Cutter', 'reverse-skill', '.git']:
            if skip_dir in dirpath.replace(root, '').split(os.sep):
                skip = True
                break
        if skip:
            continue
        for fn in files:
            if fn.lower().endswith('.obb'):
                results.append(os.path.join(dirpath, fn))
    return results

def main():
    print("[*] Scanning for *.obb files...")
    obb_files = find_obb_files(WORKSPACE)
    print(f"[*] Found {len(obb_files)} OBB file(s)")

    entries = []
    for path in obb_files:
        rel = os.path.relpath(path, WORKSPACE)
        size = os.path.getsize(path)
        magic = read_magic(path)
        fmt = identify_format(magic)
        role = classify_role(os.path.basename(path), size, fmt)
        print(f"[*] Hashing {rel} ({size/1024/1024:.1f} MB)...")
        sha = sha256_file(path)
        entries.append({
            'path': path,
            'rel': rel,
            'filename': os.path.basename(path),
            'size': size,
            'sha256': sha,
            'magic_hex': magic[:16].hex(),
            'magic_ascii': repr(magic[:16]),
            'format': fmt,
            'role': role,
        })

    # Write report
    out_path = os.path.join(WORKSPACE, 'reports', 'obb_inventory.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("# OBB Inventory\n\n")
        f.write(f"Generated: Stage 3 analysis\n\n")
        f.write(f"Total OBB files found: **{len(entries)}**\n\n")
        f.write("---\n\n")

        for i, e in enumerate(entries, 1):
            f.write(f"## OBB #{i}: {e['filename']}\n\n")
            f.write(f"**Path:** `{e['rel']}`\n\n")
            f.write(f"**Filename:** `{e['filename']}`\n\n")
            f.write(f"**Size:** {e['size']:,} bytes ({e['size']/1024/1024:.2f} MB)\n\n")
            f.write(f"**SHA-256:** `{e['sha256']}`\n\n")
            f.write(f"**Magic bytes (hex):** `{e['magic_hex']}`\n\n")
            f.write(f"**Magic bytes (repr):** `{e['magic_ascii']}`\n\n")
            f.write(f"**Format detected:** {e['format']}\n\n")
            f.write(f"**Likely role:** {e['role']}\n\n")
            f.write("---\n\n")

        # Summary table
        f.write("## Summary Table\n\n")
        f.write("| # | Filename | Size (MB) | Format | Role |\n")
        f.write("|---|----------|-----------|--------|------|\n")
        for i, e in enumerate(entries, 1):
            f.write(f"| {i} | `{e['filename']}` | {e['size']/1024/1024:.2f} | {e['format'].split('—')[0].strip()} | {e['role'].split('—')[0].strip()} |\n")

        f.write("\n## Main OBB Identification\n\n")
        main_obbs = [e for e in entries if 'MAIN OBB' in e['role']]
        if main_obbs:
            m = main_obbs[0]
            f.write(f"**Identified main OBB:** `{m['filename']}`\n\n")
            f.write(f"**Evidence:** Filename contains 'main' prefix following Android OBB naming convention.\n\n")
            f.write(f"**Format:** {m['format']}\n\n")
            f.write(f"**Confidence:** HIGH — Android OBB naming convention `main.<version>.<package>.obb`\n\n")
        else:
            f.write("No file with 'main' in filename found. Manual review required.\n\n")

    print(f"[+] Report written: {out_path}")

    # Print summary for next steps
    for e in entries:
        if 'MAIN OBB' in e['role']:
            print(f"[MAIN OBB] {e['rel']} | {e['format']} | {e['size']/1024/1024:.1f} MB")
        elif 'PATCH OBB' in e['role']:
            print(f"[PATCH OBB] {e['rel']} | {e['format']} | {e['size']/1024/1024:.1f} MB")

if __name__ == '__main__':
    main()
