"""
CPK XOR key recovery.
Known: encrypted bytes at 0x10 = 1f 9e f3 f5 af 5b 74 fb ...
Expected plaintext at start of @UTF: 40 55 54 46 xx xx xx xx ...

XOR: 1f^40=5f, 9e^55=cb, f3^54=a7, f5^46=b3 ...
Key bytes: 5f cb a7 b3 ...

Also check: CRIWARE standard key is often 0x6553 or uses a known stream.
Let's recover the full key and decrypt, then parse.
"""
import struct, os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CPK = os.path.join(WORKSPACE, "original", "patch.104050101.jp.konami.pesclubmanager.obb")

with open(CPK, 'rb') as f:
    header = f.read(4096)

# Encrypted block at 0x10
enc = header[0x10:0x10+832]

# The plaintext should be @UTF table
# @UTF header is: "@UTF" + table_size(uint32 big-endian) + ...
# Known: encrypted[0] = 0x1f, plaintext[0] = 0x40 ('@')
# key[0] = 0x1f ^ 0x40 = 0x5f
known_plain = b'@UTF'
key_start = bytes(enc[i] ^ known_plain[i] for i in range(4))
print(f"Key bytes from @UTF recovery: {key_start.hex()} = {key_start!r}")
# key = 5f cb a7 b3 ...

# Look at what 16-byte XOR pattern produces @UTF
# Try all multiples of 2,4,8,16 period
print("\n=== Testing XOR period ===")
# Look at repeated pattern in key bytes
# enc[0..3] XOR @UTF[0..3] = key
# enc[4..7] should XOR to UTF table_size...
# let's XOR first 64 bytes assuming @UTF structure is known
# @UTF: "@UTF" + table_size(4) + rows_off(4) + strings_off(4) + data_off(4) + tname_off(4) + ncols(2) + stride(2) + nrows(4) = 32 bytes

# We know enc[0:4] XOR "@ U T F"
key_known = bytearray(4)
for i in range(4):
    key_known[i] = enc[i] ^ b'@UTF'[i]
print(f"Key[0..3] = {key_known.hex()} ({key_known!r})")

# Now check repeating period
# Try period 4
print("\nKey with period 4:")
k4 = bytes(key_known)
dec4 = bytes(enc[i] ^ k4[i % 4] for i in range(len(enc)))
print(f"  First 16 bytes decrypted: {dec4[:16].hex()}")
print(f"  As ASCII: {repr(dec4[:16])}")

# Try period 8 — need more known plaintext
# table_size is a uint32 big-endian, typically < 1MB so upper 2 bytes = 0
# enc[4:6] ^ 0x00,0x?? = key[4:6]
# But we don't know the table_size exactly
# Let's look at structure differently

# Try scanning the TOC data: TOC is at 0x800 with same encryption pattern
# TOC at 0x810 has same encrypted bytes as CPK @UTF at 0x10
toc_enc = header[0x810:0x810+832]
print(f"\nTOC enc[0:4]: {toc_enc[:4].hex()}")
print(f"CPK enc[0:4]: {enc[:4].hex()}")
print(f"Same? {toc_enc[:4] == enc[:4]}")
print(f"XOR diff: {bytes(a^b for a,b in zip(toc_enc[:16], enc[:16])).hex()}")

# Try larger key: look for repeating pattern in enc XOR enc with offset
print("\n=== Key period detection (autocorrelation) ===")
for period in [4, 8, 16, 32, 64]:
    mismatches = 0
    for i in range(period, min(256, len(enc))):
        expected_key = enc[i - period] ^ dec4[i - period]
        actual_key = enc[i] ^ dec4[i % period]
        # Can't really do this without knowing more plaintext
    # Alternative: check if dec4 has any known @UTF structure
    pass

# Best approach: check dec4 more carefully
# @UTF structure:
# bytes 4..7: table_size (big-endian uint32) - this is 832-8=824 typically
expected_table_size = 832 - 8  # 0x338 = 824
ts_enc = enc[4:8]
for ts in [824, 826, 828, 830, 832, 840, 848, 900, 1000]:
    key_b = bytes([ts_enc[i] ^ b for i, b in enumerate(struct.pack('>I', ts))[:4]])
    dec_try = bytes(enc[i] ^ key_b[i % 4] for i in range(32))
    # Check if result looks like valid UTF header
    roff = struct.unpack_from('>I', dec_try, 8)[0]
    soff = struct.unpack_from('>I', dec_try, 12)[0]
    doff = struct.unpack_from('>I', dec_try, 16)[0]
    toff = struct.unpack_from('>I', dec_try, 20)[0]
    ncols = struct.unpack_from('>H', dec_try, 24)[0]
    stride = struct.unpack_from('>H', dec_try, 26)[0]
    nrows = struct.unpack_from('>I', dec_try, 28)[0]
    print(f"  ts={ts}: key={key_b.hex()} roff={roff} soff={soff} ncols={ncols} stride={stride} nrows={nrows}")

# Check the CRIWARE standard XOR approach: key = 0x655F (uint16 big-endian = 0x65, 0x5F)
print("\n=== CRIWARE standard XOR key attempts ===")
criware_keys = [
    b'\x65\x5f',   # standard 0x655F
    b'\x5f\x65',
    b'\x63\x6f',   # some variants
    b'\x40\x55',   # first chars of @UTF
    b'\x6f\x63',
]
for key_b in criware_keys:
    dec = bytes(enc[i] ^ key_b[i % len(key_b)] for i in range(32))
    print(f"  key={key_b.hex()}: first4={dec[:4].hex()} {dec[:4]!r}")

# Also check known CRIWARE key from community: 0x655F is XOR'd with position
# Actually: key[i] = ((0x655F >> 8) * (i % ... )) — this is the CRIWARE CRI middleware crypto
# The real CRIWARE encryption uses:
#   for i in range(len): data[i] ^= key_init ^ (m * i) (linear feedback)
# Let's try the known PES series keys
print("\n=== Linear key brute force ===")
# key[i] = (base + step * i) & 0xFF
for base in range(0, 256, 16):
    for step in [0, 1, 2, 3, 5, 7, 11, 13]:
        dec = bytes(enc[i] ^ ((base + step * i) & 0xFF) for i in range(4))
        if dec == b'@UTF':
            print(f"  base=0x{base:02x} step={step} -> @UTF!")
            # Decrypt full block
            full_dec = bytes(enc[i] ^ ((base + step * i) & 0xFF) for i in range(len(enc)))
            ts = struct.unpack_from('>I', full_dec, 4)[0]
            print(f"    table_size={ts}")
            print(f"    header: {full_dec[:32].hex()}")
