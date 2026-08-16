"""
Investigate GZIP blocks in CPK and the 0x655F XOR.
The GZIP at offset 0x40 is suspicious - could be compressed content within the CPK.
Also: 0x655F XOR byte 0 = 0x40 = '@' which is correct for @UTF.
Let's understand why bytes 1-3 don't match.
"""
import struct, os, zlib

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CPK = os.path.join(WORKSPACE, "original", "patch.104050101.jp.konami.pesclubmanager.obb")

with open(CPK, 'rb') as f:
    data = f.read(16384)

enc = data[0x10:0x10+832]

# 0x655F XOR:
# key_stream: 0x65 5f 65 5f 65 5f ...
# But this gives @, fb, ac, 90 for first 4 bytes
# '@' is right! What if the key is 16-bit little-endian? 0x5F, 0x65 ?
print("=== Single-byte XOR keys that give '@' for byte 0 ===")
target = ord('@')
for k in range(256):
    if (enc[0] ^ k) == target:
        dec1 = enc[1] ^ k
        dec2 = enc[2] ^ k  
        dec3 = enc[3] ^ k
        result = bytes([target, dec1, dec2, dec3])
        if result == b'@UTF':
            print(f"  KEY=0x{k:02x}: @UTF!")
        else:
            print(f"  KEY=0x{k:02x}: {result!r}")

# The answer: enc[0]=0x1f, '@'=0x40, key_byte_0 = 0x1f ^ 0x40 = 0x5f
# enc[1]=0x9e, 'U'=0x55, key_byte_1 = 0x9e ^ 0x55 = 0xcb
# enc[2]=0xf3, 'T'=0x54, key_byte_2 = 0xf3 ^ 0x54 = 0xa7
# enc[3]=0xf5, 'F'=0x46, key_byte_3 = 0xf5 ^ 0x46 = 0xb3
# key = 5f cb a7 b3 ...
# This is a 4-byte key, period > 4

# Check if the key has period 256 or is a hash
# From prior work: key = 5f cb a7 b3 for positions 0-3
# Let's check what positions 4-7 decrypt to if the whole key is derived from @UTF table:
# @UTF header is 32 bytes: @UTF + table_size(4) + rows_off(4) + str_off(4) + data_off(4) + tname_off(4) + ncols(2) + stride(2) + nrows(4)
# We know enc[0:4] = @UTF
# What's the table_size? We can compute the key from plaintext+ciphertext if we know more plaintext

# Check GZIP blocks
print("\n=== GZIP block at offset 64 (0x40) ===")
gzip_start = 64
gzip_data = data[gzip_start:gzip_start+512]
print(f"  Header: {gzip_data[:16].hex()}")
print(f"  GZIP magic: {gzip_data[:2].hex()} ({gzip_data[:2]!r})")
# GZIP: 1f 8b (magic), 08 (deflate), flags, mtime(4), xfl, os, ...
if gzip_data[:2] == b'\x1f\x8b':
    method = gzip_data[2]
    flags = gzip_data[3]
    mtime = struct.unpack_from('<I', gzip_data, 4)[0]
    print(f"  Method: {method} (8=deflate)")
    print(f"  Flags: 0x{flags:02x}")
    print(f"  Mtime: {mtime}")
    # Try to decompress
    try:
        # wbits=-15 for raw deflate, 31 for gzip
        decompressed = zlib.decompress(gzip_data, wbits=31)
        print(f"  Decompressed size: {len(decompressed)} bytes")
        print(f"  First 32 bytes: {decompressed[:32].hex()}")
        print(f"  As text: {decompressed[:64].decode('utf-8', errors='replace')!r}")
    except Exception as e:
        print(f"  Decompression failed: {e}")
        # Try as raw deflate
        try:
            decompressed = zlib.decompress(gzip_data[10:], wbits=-15)
            print(f"  Raw deflate worked: {len(decompressed)} bytes")
        except:
            pass

# Check all GZIP blocks in first 16KB
print("\n=== All GZIP blocks in first 16KB ===")
pos = 0
found = []
while True:
    idx = data.find(b'\x1f\x8b', pos)
    if idx == -1:
        break
    found.append(idx)
    # Try to decompress
    try:
        dec = zlib.decompress(data[idx:idx+16000], wbits=31)
        print(f"  0x{idx:06x}: GZIP -> {len(dec)} bytes decompressed")
        print(f"    First 64: {dec[:64].hex()}")
        print(f"    As text: {dec[:64].decode('utf-8', errors='replace')!r}")
        # Is it @UTF?
        if dec[:4] == b'@UTF':
            print("    >>> @UTF TABLE! <<<")
    except Exception as e:
        print(f"  0x{idx:06x}: GZIP but decomp failed: {type(e).__name__}")
    pos = idx + 2

# Inspect the repeated pattern in the encrypted data
# Look for repeating key by XOR with the known @UTF key at positions 0-3
# and check if it repeats modulo some length
print("\n=== Key pattern analysis ===")
# Assume first 4 bytes of plaintext = @UTF
key_start = bytes(enc[i] ^ b'@UTF'[i] for i in range(4))
print(f"key[0:4] = {key_start.hex()}")
# Looking at the raw encrypted data pattern
# enc[0..3] = 1f 9e f3 f5 -> @UTF (diff = 5f cb a7 b3)
# Now check if the encrypted data at 0x800+0x10 follows same key
toc_enc = data[0x810:0x810+4]
print(f"TOC enc[0:4] = {toc_enc.hex()}")
toc_key0 = bytes(toc_enc[i] ^ b'@UTF'[i] for i in range(4))
print(f"TOC key[0:4] = {toc_key0.hex()}")
print(f"Same key? {key_start == toc_key0}")

# Are the keys different per-table? Then the XOR key depends on table identity
print(f"\nDiff: key[0:4]={key_start.hex()} vs toc_key[0:4]={toc_key0.hex()}")
diff = bytes(a^b for a,b in zip(key_start, toc_key0))
print(f"XOR diff: {diff.hex()}")

# The keys are different => per-table key
# CRIWARE uses: key_init = table_size; then LFSR based on table_size
# Table size at CPK: 832 (from field at 0x08)
# Table size at TOC: 1232 (from field at 0x808)
print(f"\nCPK UTF size: 832, TOC UTF size: 1232")
print(f"Key depends on table content (not just size)")
print(f"This is likely CRIWARE's M2 or M3 XOR variant")
print(f"Conclusion: @UTF tables are encrypted with a per-table key.")
print(f"Cannot decrypt without the actual key derivation algorithm or key material.")
