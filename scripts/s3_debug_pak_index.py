"""Helper: inspect raw PAK index bytes to understand actual structure."""
import struct, os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAK = os.path.join(WORKSPACE, "extracted", "obb_main", "PesMobile", "Content", "Paks", "PesMobile-Android_ETC1.pak")
IDX_OFFSET = 782104571
IDX_SIZE   = 7380528

with open(PAK, 'rb') as f:
    f.seek(IDX_OFFSET)
    idx = f.read(IDX_SIZE)

print(f"Index size: {len(idx)} bytes")

print("\n=== First 256 bytes of index ===")
for i in range(0, 256, 16):
    chunk = idx[i:i+16]
    hexpart = ' '.join(f'{b:02x}' for b in chunk)
    ascpart = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
    print(f"{IDX_OFFSET+i:10x}  {hexpart:<48}  {ascpart}")

# Try FString at offset 0
slen = struct.unpack_from('<i', idx, 0)[0]
print(f"\nFString length at 0: {slen}")
if 0 < slen < 512:
    s = idx[4:4+slen]
    decoded = s.decode('utf-8', errors='replace')
    print(f"  string: {decoded!r}")
    entry_count_offset = 4 + slen
    ecount = struct.unpack_from('<i', idx, entry_count_offset)[0]
    print(f"  entry count at {entry_count_offset}: {ecount}")

    # Peek first entry
    pos = entry_count_offset + 4
    elen = struct.unpack_from('<i', idx, pos)[0]
    print(f"\n  First entry FString length: {elen}")
    if 0 < elen < 1024:
        fname = idx[pos+4:pos+4+elen].decode('utf-8', errors='replace')
        print(f"  First filename: {fname!r}")
        # After filename: offset(8) + compsz(8) + uncompsz(8) + comprmethod(4) + sha1(20) = 48
        pos2 = pos + 4 + elen
        print(f"  Bytes after filename: {idx[pos2:pos2+60].hex()}")
        off_val = struct.unpack_from('<q', idx, pos2)[0]
        compsz  = struct.unpack_from('<q', idx, pos2+8)[0]
        uncompsz= struct.unpack_from('<q', idx, pos2+16)[0]
        cmeth   = struct.unpack_from('<I', idx, pos2+24)[0]
        sha1    = idx[pos2+28:pos2+48].hex()
        print(f"  offset={off_val}, comp_sz={compsz}, uncomp_sz={uncompsz}, method={cmeth}")
        print(f"  sha1={sha1}")
        # flags/blocksize
        flags = idx[pos2+48]
        blocksize = struct.unpack_from('<I', idx, pos2+49)[0]
        print(f"  flags={flags}, block_size={blocksize}")
        next_entry = pos2 + 48 + 1 + 4
        print(f"\n  Second entry starts at: {next_entry}")
        elen2 = struct.unpack_from('<i', idx, next_entry)[0]
        print(f"  Second FString length: {elen2}")
        if 0 < elen2 < 1024:
            fname2 = idx[next_entry+4:next_entry+4+elen2].decode('utf-8', errors='replace')
            print(f"  Second filename: {fname2!r}")
elif slen < 0:
    byte_len = (-slen) * 2
    s = idx[4:4+byte_len]
    decoded = s.decode('utf-16-le', errors='replace')
    print(f"  UTF-16 string: {decoded!r}")
