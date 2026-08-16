"""
CPK section analysis - find TOC content structure.
The CPK TOC is at 0x800. Its structure:
  TOC magic (4) + unk(4) + content_offset(8)
  Then @UTF encrypted table starting at TOC+0x10

But content files referenced by the TOC should start at 'ContentOffset'
from the CPK header. Let's examine the CPK file structure at various offsets.

Also: check if CRIWARE CPK uses CRI-standard UTF XOR encryption.
The CPK standard XOR uses key: (table_size ^ 0xFFFF) as uint16 rolling key.
Let's test that.
"""
import struct, os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CPK = os.path.join(WORKSPACE, "original", "patch.104050101.jp.konami.pesclubmanager.obb")

with open(CPK, 'rb') as f:
    first_16k = f.read(16384)

print("=== CPK Header: first 16 bytes ===")
print(f"  {first_16k[:16].hex()}")
print(f"  Magic: {first_16k[:4]!r}")
# CPK[4:8] = unk = 0x00000000
# CPK[8:16] = size of UTF block at 0x10 = 832 (0x340)
utf_blk_size = struct.unpack_from('<Q', first_16k, 8)[0]
print(f"  UTF block size: {utf_blk_size}")

print("\n=== Known CPK UTF XOR decryption ===")
# Standard CRIWARE UTF XOR key:
# key = (table_size + table_size >> 2 + 0x655F) & 0xFFFF  (some variants)
# OR: iterative XOR with init key 0x655F
# Let's try: key_i = key_{i-1} + key_{i-1} >> 8, init = table_size ^ 0xFFFF

# The encrypted block at 0x10 has size 832 bytes
enc = first_16k[0x10:0x10+832]

# Try CRIWARE standard M3U/HCA/UTF XOR:
# seed = (uint16_t)(table_size ^ 0xFFFF)
# for each byte: key = (seed * 0xC35B + 0x2699) & 0xFFFF; seed = key; xor byte with (key >> 8)
table_size = 832
seed = (table_size ^ 0xFFFF) & 0xFFFF
print(f"  Seed: 0x{seed:04x}")

decrypted = bytearray(len(enc))
s = seed
for i, b in enumerate(enc):
    s = (s * 0x4E6F + 0x5D) & 0xFFFF
    decrypted[i] = b ^ (s >> 8)

print(f"  Decrypted[0:4]: {bytes(decrypted[:4]).hex()} = {bytes(decrypted[:4])!r}")

if bytes(decrypted[:4]) == b'@UTF':
    print("  SUCCESS! @UTF found with CRIWARE standard XOR!")
    # Parse the table
    ts = struct.unpack_from('>I', decrypted, 4)[0]
    rows_off = struct.unpack_from('>I', decrypted, 8)[0]
    str_off = struct.unpack_from('>I', decrypted, 12)[0]
    ncols = struct.unpack_from('>H', decrypted, 24)[0]
    stride = struct.unpack_from('>H', decrypted, 26)[0]
    nrows = struct.unpack_from('>I', decrypted, 28)[0]
    print(f"  table_size={ts} rows_off={rows_off} str_off={str_off} ncols={ncols} stride={stride} nrows={nrows}")
else:
    print("  Failed. Trying alternative seeds...")
    
    # Try with actual UTF table size (table_size = data AFTER the 8-byte header)
    # So effective table data size = 832 - 8 = 824
    for ts_try in [824, 830, 832, 840, 848]:
        seed2 = (ts_try ^ 0xFFFF) & 0xFFFF
        dec2 = bytearray(len(enc))
        s2 = seed2
        for i, b in enumerate(enc):
            s2 = (s2 * 0x4E6F + 0x5D) & 0xFFFF
            dec2[i] = b ^ (s2 >> 8)
        if bytes(dec2[:4]) == b'@UTF':
            print(f"  SUCCESS with ts_try={ts_try}!")
            break
        print(f"  ts_try={ts_try}: {bytes(dec2[:4]).hex()!r}")

    # Try another CRIWARE variant: XOR key = 0x655F, mask based on index
    print("\n  Trying 0x655F-based XOR...")
    xor_key = 0x655F
    dec3 = bytearray(len(enc))
    for i, b in enumerate(enc):
        dec3[i] = b ^ (xor_key >> (8 * (i % 2)) & 0xFF)
    print(f"  0x655F XOR: {bytes(dec3[:4]).hex()!r}")

    # Try: key is derived from file offset
    # CPK @UTF at offset 0x10: key = 0x10 XOR'd somehow?
    print("\n  Checking TOC section at 0x800+0x10...")
    toc_enc = first_16k[0x810:0x810+0x400]  # 1KB of TOC UTF data
    
    # TOC magic is 'TOC ' at 0x800; TOC size field at 0x808
    toc_size = struct.unpack_from('<Q', first_16k, 0x808)[0]
    print(f"  TOC data size: {toc_size}")
    
    # Try same XOR with TOC's table size as seed
    # We need to know TOC's table size - it's at offset 0x10 within TOC section
    # So file offset 0x810, first 8 bytes are encrypted
    # First try: assume TOC size == toc_size
    for ts_try2 in [toc_size, toc_size - 8, toc_size & 0xFFFF]:
        ts_val = int(ts_try2) & 0xFFFF
        seed3 = (ts_val ^ 0xFFFF) & 0xFFFF
        dec4 = bytearray(min(32, len(toc_enc)))
        s3 = seed3
        for i, b in enumerate(toc_enc[:32]):
            s3 = (s3 * 0x4E6F + 0x5D) & 0xFFFF
            dec4[i] = b ^ (s3 >> 8)
        if bytes(dec4[:4]) == b'@UTF':
            print(f"  TOC SUCCESS with ts={ts_try2}!")
        else:
            print(f"  TOC ts={ts_val}: {bytes(dec4[:4]).hex()!r}")

# Look for unencrypted content starting after the TOC area
# Standard CPK: files start at ContentOffset
# ContentOffset is in the encrypted CPK UTF at 0x10 — we can't read it directly
# But we can scan for known file signatures in the CPK payload
print("\n=== Scanning for known file signatures in CPK ===")
# Read 32KB starting from various offsets
SIGNATURES = {
    b'\x89PNG': 'PNG',
    b'\xff\xd8\xff': 'JPEG',
    b'@UTF': 'CRIWARE UTF',
    b'HCAX': 'CRIWARE HCA audio',
    b'ADX\x00': 'CRIWARE ADX audio',
    b'\x80\x00': 'CRIWARE ADX (alt)',
    b'OggS': 'OGG',
    b'\x1f\x8b': 'GZIP',
}

# Check at various 0x800-aligned offsets through first 256KB
print("Scanning first 256KB for file signatures...")
with open(CPK, 'rb') as f:
    scan_data = f.read(256 * 1024)

found = {}
for magic, name in SIGNATURES.items():
    off = 0
    while True:
        pos = scan_data.find(magic, off)
        if pos == -1:
            break
        if name not in found:
            found[name] = []
        found[name].append(pos)
        off = pos + 1

for name, offsets in found.items():
    print(f"  {name}: found at {offsets[:5]}")
