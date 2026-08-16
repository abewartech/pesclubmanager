"""
scripts/inspect_datatable.py
Read-only binary analysis tool for PES Club Manager data table files.
Usage: python scripts/inspect_datatable.py <path_to_file>

Outputs: File metadata, magic bytes, string scan, structure hints.
All results are candidate/hypothesis unless confirmed.
"""
import os, sys, struct, hashlib, re

CHUNK = 1024 * 1024

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            buf = f.read(CHUNK)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()

def identify_magic(data):
    checks = [
        (b'@UTF',          'CRIWARE @UTF table'),
        (b'CRID',          'CRIWARE CRID'),
        (b'CPK ',          'CRIWARE CPK'),
        (b'PK\x03\x04',   'ZIP archive'),
        (b'\x89PNG',       'PNG image'),
        (b'\xff\xd8\xff',  'JPEG image'),
        (b'\x1f\x8b',      'GZIP compressed'),
        (b'BZh',           'BZIP2 compressed'),
        (b'\x78\x9c',      'ZLIB (default)'),
        (b'\x78\xda',      'ZLIB (best)'),
        (b'\x78\x01',      'ZLIB (low)'),
        (b'UASSET',        'Unreal Asset (text)'),
    ]
    magic4 = data[:4]
    sig = struct.unpack_from('<I', data[:4])[0] if len(data) >= 4 else 0
    if sig == 0x5A6F12E1:
        return 'Unreal PAK'
    for magic, name in checks:
        if data[:len(magic)] == magic:
            return name
    # Check for UTF-16LE BOM
    if data[:2] == b'\xff\xfe':
        return 'UTF-16LE text'
    # Check for plain ASCII/text
    printable = sum(1 for b in data[:64] if 32 <= b < 127 or b in (9, 10, 13))
    if printable > 50:
        return 'Plain text / ASCII'
    return f'Unknown (hex: {magic4.hex()})'

def scan_strings_ascii(data, min_len=6, max_count=500):
    """Return list of (offset, string) for printable ASCII runs."""
    results = []
    for m in re.finditer(rb'[ -~]{' + str(min_len).encode() + rb',}', data):
        s = m.group().decode('ascii', errors='replace')
        results.append((m.start(), s))
        if len(results) >= max_count:
            break
    return results

def scan_strings_utf16(data, min_len=4, max_count=200):
    """Scan for UTF-16LE strings (printable ASCII chars as 2-byte sequences)."""
    results = []
    i = 0
    while i < len(data) - 2:
        # Check for ASCII char in UTF-16LE (low byte = printable, high byte = 0)
        if 32 <= data[i] < 127 and data[i+1] == 0:
            start = i
            chars = []
            while i < len(data) - 1 and 32 <= data[i] < 127 and data[i+1] == 0:
                chars.append(chr(data[i]))
                i += 2
            if len(chars) >= min_len:
                results.append((start, ''.join(chars)))
                if len(results) >= max_count:
                    break
        else:
            i += 1
    return results

def analyze_record_patterns(data, max_bytes=65536):
    """Heuristic: look for repeating fixed-stride patterns."""
    sample = data[:max_bytes]
    results = {}
    # Try common record sizes
    for stride in [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 48, 64, 128, 256]:
        if len(sample) < stride * 4:
            continue
        # Count how many strides have consistent byte patterns
        records = [sample[i:i+stride] for i in range(0, len(sample) - stride, stride)]
        # Check if any byte column has low entropy (repeating values)
        low_entropy_cols = 0
        for col in range(stride):
            vals = set(r[col] for r in records if col < len(r))
            if len(vals) <= 4:  # very few unique values
                low_entropy_cols += 1
        if low_entropy_cols >= stride // 4:
            results[stride] = low_entropy_cols
    return results

def analyze_int_patterns(data):
    """Look for arrays of sequential integers (like record IDs)."""
    results = []
    # Try to find sequential uint32 LE arrays
    for start in range(0, min(1024, len(data)-8), 4):
        a = struct.unpack_from('<I', data, start)[0]
        b = struct.unpack_from('<I', data, start+4)[0]
        if 0 < a < 100000 and b == a + 1:
            # Found start of sequential array
            count = 2
            pos = start + 8
            while pos + 4 <= len(data):
                c = struct.unpack_from('<I', data, pos)[0]
                if c == a + count:
                    count += 1
                    pos += 4
                else:
                    break
            if count >= 4:
                results.append((start, a, count, 'uint32_le_sequential'))
    # Also try uint16
    for start in range(0, min(1024, len(data)-4), 2):
        a = struct.unpack_from('<H', data, start)[0]
        b = struct.unpack_from('<H', data, start+2)[0]
        if 0 < a < 100000 and b == a + 1:
            count = 2
            pos = start + 4
            while pos + 2 <= len(data):
                c = struct.unpack_from('<H', data, pos)[0]
                if c == a + count:
                    count += 1
                    pos += 2
                else:
                    break
            if count >= 4:
                results.append((start, a, count, 'uint16_le_sequential'))
    return results

def analyze_header_candidates(data):
    """Look for common binary table header patterns."""
    results = []
    # Pattern: magic(4) + version(4) + count(4) + ...
    if len(data) >= 16:
        for endian in ['<', '>']:
            m1 = struct.unpack_from(endian + 'I', data, 0)[0]
            m2 = struct.unpack_from(endian + 'I', data, 4)[0]
            count = struct.unpack_from(endian + 'I', data, 8)[0]
            stride = struct.unpack_from(endian + 'I', data, 12)[0] if len(data) >= 16 else 0
            
            # Heuristic: count * stride ≈ file_size
            if count > 0 and stride > 0 and stride < 10000:
                predicted_size = count * stride
                tolerance = 0.15  # 15%
                if abs(predicted_size - len(data)) / len(data) < tolerance:
                    results.append({
                        'endian': 'little' if endian == '<' else 'big',
                        'offset_0': m1,
                        'offset_4': m2,
                        'count_candidate': count,
                        'stride_candidate': stride,
                        'predicted_size': predicted_size,
                        'actual_size': len(data),
                    })
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python inspect_datatable.py <file>")
        print("Example: python inspect_datatable.py path\\to\\Definedatatable.bin")
        sys.exit(1)
    
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"Error: File not found: {path}")
        sys.exit(1)
    
    file_size = os.path.getsize(path)
    print(f"\n{'='*60}")
    print(f"File:    {path}")
    print(f"Size:    {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    print(f"\n[*] Computing SHA-256...")
    sha = sha256_file(path)
    print(f"SHA-256: {sha}")
    
    # Read file (up to 1MB for analysis)
    read_size = min(file_size, 1024 * 1024)
    with open(path, 'rb') as f:
        data = f.read(read_size)
    
    # Magic
    magic = identify_magic(data)
    print(f"\nMagic:   {magic}")
    print(f"Hex[0:16]: {data[:16].hex()}")
    
    # Hex dump of first 64 bytes
    print(f"\n{'='*60}")
    print("Hex dump (first 128 bytes):")
    for i in range(0, min(128, len(data)), 16):
        chunk = data[i:i+16]
        hexpart = ' '.join(f'{b:02x}' for b in chunk)
        ascpart = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"  {i:06x}  {hexpart:<48}  {ascpart}")
    
    # ASCII strings
    print(f"\n{'='*60}")
    print("ASCII strings (>= 6 chars, first 30):")
    astrings = scan_strings_ascii(data, min_len=6, max_count=30)
    if astrings:
        for off, s in astrings:
            short = s[:80]
            print(f"  0x{off:06x}: {short!r}")
    else:
        print("  None found.")
    
    # UTF-16LE strings
    print(f"\n{'='*60}")
    print("UTF-16LE strings (>= 4 chars, first 20):")
    ustrings = scan_strings_utf16(data, min_len=4, max_count=20)
    if ustrings:
        for off, s in ustrings:
            print(f"  0x{off:06x}: {s!r}")
    else:
        print("  None found.")
    
    # Integer patterns
    print(f"\n{'='*60}")
    print("Sequential integer arrays (candidate record IDs):")
    int_patterns = analyze_int_patterns(data)
    if int_patterns:
        for start, first_val, count, ptype in int_patterns[:5]:
            print(f"  CANDIDATE: 0x{start:06x} — {ptype} starting at {first_val}, length {count}")
    else:
        print("  None detected.")
    
    # Record stride analysis
    print(f"\n{'='*60}")
    print("Repeating-stride pattern analysis (candidate record size):")
    strides = analyze_record_patterns(data)
    if strides:
        for stride, score in sorted(strides.items(), key=lambda x: -x[1])[:5]:
            n_records = len(data) // stride
            print(f"  CANDIDATE stride={stride} bytes ({n_records} records @ stride), low-entropy-cols={score}")
    else:
        print("  No strong stride patterns detected.")
    
    # Header candidates
    print(f"\n{'='*60}")
    print("Binary table header candidates (magic+count+stride heuristic):")
    hdr = analyze_header_candidates(data)
    if hdr:
        for h in hdr:
            print(f"  CANDIDATE: endian={h['endian']}, count={h['count_candidate']}, stride={h['stride_candidate']}, predicted_size={h['predicted_size']:,}")
    else:
        print("  None (no matching count*stride ~= file_size pattern found).")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY (all values are candidates unless confirmed):")
    print(f"  File:              {os.path.basename(path)}")
    print(f"  Size:              {file_size:,} bytes")
    print(f"  SHA-256:           {sha}")
    print(f"  Magic:             {magic}")
    print(f"  ASCII strings:     {len(scan_strings_ascii(data, max_count=9999)):,}")
    print(f"  UTF-16 strings:    {len(scan_strings_utf16(data, max_count=9999)):,}")
    print(f"  Potential strides: {sorted(strides.keys()) if strides else 'none'}")
    print(f"  Header candidates: {len(hdr)}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
