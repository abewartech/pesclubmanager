"""Probe the actual CPK header structure of the patch OBB."""
import struct, os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CPK = os.path.join(WORKSPACE, "original", "patch.104050101.jp.konami.pesclubmanager.obb")

with open(CPK, 'rb') as f:
    header = f.read(4096)

print("=== First 512 bytes (hex + ASCII) ===")
for i in range(0, 512, 16):
    chunk = header[i:i+16]
    hexpart = ' '.join(f'{b:02x}' for b in chunk)
    ascpart = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
    print(f"  {i:04x}  {hexpart:<48}  {ascpart}")

# Check all known CPK magic strings in first 4096 bytes
print("\n=== Magic string search in first 4096 bytes ===")
magics = [b'CPK ', b'@UTF', b'ITOC', b'ETOC', b'GTOC', b'TOC ', b'CPAK']
for magic in magics:
    offset = 0
    while True:
        pos = header.find(magic, offset)
        if pos == -1:
            break
        print(f"  Found {magic!r} at offset 0x{pos:04x} ({pos})")
        # show context
        chunk = header[pos:pos+32]
        print(f"    hex: {chunk.hex()}")
        offset = pos + 1

# Check bytes at 0x08-0x10 (CPK header fields)
print("\n=== CPK header fields (little-endian u64 at 0x08) ===")
val_08 = struct.unpack_from('<Q', header, 8)[0]
val_10 = struct.unpack_from('<Q', header, 16)[0]
val_18 = struct.unpack_from('<Q', header, 24)[0]
print(f"  0x08: {val_08} (0x{val_08:016x})")
print(f"  0x10: {val_10} (0x{val_10:016x})")
print(f"  0x18: {val_18} (0x{val_18:016x})")

# Standard CPK: first 0x10 bytes are "CPK " magic + 0xFFFFFFFF + packet_size (uint64)
# Then @UTF table at 0x10
# But some CPK versions have the UTF compressed
print("\n=== Check if UTF might be at different location ===")
# UTF table signature might be present elsewhere
for i in range(0, 4096):
    if header[i:i+4] == b'@UTF':
        print(f"  @UTF found at byte {i} (0x{i:04x})")
        tbl_sz = struct.unpack_from('>I', header, i+4)[0]
        print(f"    table_size (big-endian): {tbl_sz}")
        break

# Check for CRIWARE CPK v2 structure (different offsets)
print("\n=== u32 values at 0x04..0x20 ===")
for off in range(0, 0x20, 4):
    v = struct.unpack_from('<I', header, off)[0]
    print(f"  0x{off:02x}: 0x{v:08x} ({v})")

# Show bytes 0x800 and 0x900 area (alternative header location)
print("\n=== Bytes around 0x800 ===")
for i in range(0x800, 0x840, 16):
    chunk = header[i:i+16]
    hexpart = ' '.join(f'{b:02x}' for b in chunk)
    ascpart = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
    print(f"  {i:04x}  {hexpart:<48}  {ascpart}")
