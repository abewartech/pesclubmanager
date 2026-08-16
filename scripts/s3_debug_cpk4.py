"""Test period-4 XOR key on CPK header UTF block."""
import struct, os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CPK = os.path.join(WORKSPACE, "original", "patch.104050101.jp.konami.pesclubmanager.obb")

with open(CPK, 'rb') as f:
    header = f.read(4096)

enc = header[0x10:0x10+832]

# Key derived from enc[0:4] XOR '@UTF' = 5f cb a7 b3
key4 = bytes([0x5f, 0xcb, 0xa7, 0xb3])
dec4 = bytes(enc[i] ^ key4[i % 4] for i in range(len(enc)))

print(f"Period-4 decrypted start: {dec4[:4].hex()} = {dec4[:4]!r}")

table_size     = struct.unpack_from('>I', dec4, 4)[0]
rows_offset    = struct.unpack_from('>I', dec4, 8)[0]
strings_offset = struct.unpack_from('>I', dec4, 12)[0]
data_offset    = struct.unpack_from('>I', dec4, 16)[0]
tname_off      = struct.unpack_from('>I', dec4, 20)[0]
ncols          = struct.unpack_from('>H', dec4, 24)[0]
stride         = struct.unpack_from('>H', dec4, 26)[0]
nrows          = struct.unpack_from('>I', dec4, 28)[0]

print(f"table_size:     {table_size}")
print(f"rows_offset:    {rows_offset}")
print(f"strings_offset: {strings_offset}")
print(f"data_offset:    {data_offset}")
print(f"tname_off:      {tname_off}")
print(f"ncols:          {ncols}")
print(f"stride:         {stride}")
print(f"nrows:          {nrows}")

# Sanity check: reasonable values?
# table_size should be ~820 (block is 832 but includes @UTF header size field)
# ncols should be ~10-50 for CPK header
# nrows should be 1 for CPK header table
# strings_offset should be > rows_offset
ok = (
    0 < table_size < 10000 and
    0 < ncols < 100 and
    0 < nrows < 100 and
    strings_offset > rows_offset
)
print(f"\nSanity check: {'PASS' if ok else 'FAIL'}")

if ok:
    # Try to read table name from string table
    string_base = 8 + strings_offset
    if string_base + tname_off < len(dec4):
        end = dec4.find(b'\x00', string_base + tname_off)
        if end > 0:
            tname = dec4[string_base + tname_off:end].decode('utf-8', errors='replace')
            print(f"Table name: {tname!r}")
    
    # Show first 100 bytes of decrypted UTF
    print("\nFirst 100 bytes decrypted:")
    for i in range(0, min(100, len(dec4)), 16):
        chunk = dec4[i:i+16]
        hexpart = ' '.join(f'{b:02x}' for b in chunk)
        ascpart = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"  {i:04x}  {hexpart:<48}  {ascpart}")
else:
    print("Period-4 key does not produce valid UTF structure.")
    print("The encryption may use a longer key or different algorithm.")
    print(f"\nRaw dec4 first 64 bytes: {dec4[:64].hex()}")
    
    # Try period 8,16 with additional known plaintext
    # After @UTF (4 bytes) comes table_size (uint32 BE)
    # We don't know table_size but it should be in range 600-900
    print("\n=== Trying period 8 (need more known plaintext) ===")
    # If table_size = 820 (0x00000334):
    # enc[4:8] XOR 00000334 = key[4:8]
    for ts_guess in [820, 824, 828, 832, 816, 808]:
        ts_bytes = struct.pack('>I', ts_guess)
        key8 = bytearray(8)
        for i in range(4):
            key8[i] = enc[i] ^ b'@UTF'[i]
        for i in range(4):
            key8[4+i] = enc[4+i] ^ ts_bytes[i]
        dec8 = bytes(enc[i] ^ key8[i % 8] for i in range(min(64, len(enc))))
        r_off = struct.unpack_from('>I', dec8, 8)[0]
        s_off = struct.unpack_from('>I', dec8, 12)[0]
        nc    = struct.unpack_from('>H', dec8, 24)[0]
        st    = struct.unpack_from('>H', dec8, 26)[0]
        nr    = struct.unpack_from('>I', dec8, 28)[0]
        plausible = (0 < nc < 100 and 0 < nr < 1000 and r_off < s_off)
        marker = "<<< PLAUSIBLE" if plausible else ""
        print(f"  ts={ts_guess} key8={bytes(key8).hex()} r_off={r_off} s_off={s_off} nc={nc} nr={nr} {marker}")
