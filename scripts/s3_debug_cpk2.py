"""
CPK deeper probe:
1. Check TOC section at 0x800
2. Try CRIWARE CPK decryption (common XOR key)
3. Scan 0x10..0x350 for patterns
4. Look for filenames via string scan in TOC data
"""
import struct, os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CPK = os.path.join(WORKSPACE, "original", "patch.104050101.jp.konami.pesclubmanager.obb")

with open(CPK, 'rb') as f:
    first_8kb = f.read(8192)

# --- Section 1: Analyze TOC at 0x800 ---
print("=== TOC at 0x800 ===")
toc_data = first_8kb[0x800:]
print(f"TOC magic: {toc_data[:4].hex()} = {toc_data[:4]!r}")
# TOC header: magic(4) + unk(4) + utf_offset(8)
utf_rel = struct.unpack_from('<Q', toc_data, 8)[0]
print(f"UTF rel offset in TOC section: {utf_rel}")
print(f"TOC utf would be at file offset: {0x800 + 0x10 + utf_rel}")
# Dump TOC[0..80]
print("TOC header dump:")
for i in range(0, 80, 16):
    chunk = toc_data[i:i+16]
    hexpart = ' '.join(f'{b:02x}' for b in chunk)
    ascpart = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
    print(f"  {0x800+i:04x}  {hexpart:<48}  {ascpart}")

# --- Section 2: Check ITOC at 0x7FF ---
print("\n=== ITOC at 0x7FF ===")
itoc_data = first_8kb[0x7FF:]
print(f"Bytes: {itoc_data[:32].hex()}")

# --- Section 3: Try decrypting the block at 0x10..0x350 (size=0x340=832) ---
# CRIWARE uses a simple XOR with a rotating key 0x655F or similar
# Most common PES/ACB key: CRILAYLA zlib trick doesn't apply to CPK header
# Check if bytes 0x10..0x350 follow a pattern
enc_block = first_8kb[0x10:0x10+832]
print(f"\n=== Encrypted UTF block (0x10..0x350, size={len(enc_block)}) ===")
# Check if it's zlib compressed (common for CPK UTF tables)
# zlib starts with 0x78 0x9C or 0x78 0xDA
print(f"First 16 bytes: {enc_block[:16].hex()}")
print(f"Possible zlib header: {enc_block[:2].hex()} (0x789C=zlib default)")

# Try XOR with common PES/CRIWARE keys
known_keys = [
    (0x655F, "standard 0x655F"),
    (0, "no XOR"),
    (0xFF, "0xFF XOR"),
]

print("\n=== XOR decrypt attempts ===")
def xor_decrypt(data, key_bytes):
    result = bytearray(len(data))
    for i, b in enumerate(data):
        result[i] = b ^ key_bytes[i % len(key_bytes)]
    return bytes(result)

for key_val, key_name in known_keys:
    if key_val == 0:
        decrypted = enc_block
    else:
        key_bytes = struct.pack('>H', key_val)
        decrypted = xor_decrypt(enc_block, key_bytes)
    if decrypted[:4] == b'@UTF':
        print(f"  [{key_name}] -> @UTF FOUND!")
    else:
        print(f"  [{key_name}] -> first 4: {decrypted[:4].hex()} {decrypted[:4]!r}")

# --- Section 4: Scan from TOC area for actual @UTF ---
print("\n=== Scanning for @UTF in full 8KB ===")
for i in range(0, len(first_8kb)-4):
    if first_8kb[i:i+4] == b'@UTF':
        print(f"  @UTF at 0x{i:04x}")
        tbl_sz = struct.unpack_from('>I', first_8kb, i+4)[0]
        print(f"  table_size: {tbl_sz}")

# --- Section 5: Read TOC@UTF (which is at TOC+0x10) ---
print("\n=== TOC @UTF check at 0x800+0x10=0x810 ===")
toc_utf = first_8kb[0x810:]
print(f"Magic at 0x810: {toc_utf[:4].hex()} = {toc_utf[:4]!r}")

# --- Section 6: Scan first 500 bytes of TOC for @UTF ---
with open(CPK, 'rb') as f:
    f.seek(0x800)
    toc_section = f.read(0x1000)
print(f"\nScanning TOC section (0x800..0x1800) for @UTF:")
for i in range(0, len(toc_section)-4):
    if toc_section[i:i+4] == b'@UTF':
        file_off = 0x800 + i
        print(f"  @UTF at file offset 0x{file_off:06x} ({file_off})")
        tbl_sz = struct.unpack_from('>I', toc_section, i+4)[0]
        print(f"  table_size: {tbl_sz}")
        # try reading it
        rows_off = struct.unpack_from('>I', toc_section, i+8)[0]
        strings_off = struct.unpack_from('>I', toc_section, i+12)[0]
        data_off = struct.unpack_from('>I', toc_section, i+16)[0]
        tname_off = struct.unpack_from('>I', toc_section, i+20)[0]
        ncols = struct.unpack_from('>H', toc_section, i+24)[0]
        stride = struct.unpack_from('>H', toc_section, i+26)[0]
        nrows = struct.unpack_from('>I', toc_section, i+28)[0]
        print(f"  rows_off={rows_off}, strings_off={strings_off}, ncols={ncols}, stride={stride}, nrows={nrows}")
        # Read table name
        str_base = i + 8 + strings_off
        try:
            end = toc_section.index(b'\x00', str_base + tname_off)
            tname = toc_section[str_base + tname_off:end].decode('utf-8', errors='replace')
            print(f"  Table name: {tname!r}")
        except:
            print("  (could not read table name)")
