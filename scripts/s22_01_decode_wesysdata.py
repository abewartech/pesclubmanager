"""Stage 22: offline WesysData payload decoder.

Decodes the `multi_stats_data` value from OnSysData.dat (see Stages 20-21).
The payload is a sys::WesysData binary blob:

    offset  size  field
    0       1     byte 0 (uninterpreted)
    1       1     byte 1 (uninterpreted)
    2       1     flags: bit0 = zip-compressed, bit1 = xorshift-encrypted
    3       5     magic "WESYS"
    8       4     uint32 LE stored size
    12      4     uint32 LE original size
    16      ...   payload (GetData: buf+0x10)

Read-only. Handles zlib decompression via Python's zlib (standard).
The xorshift decryption routine was not recovered from the binary, so
payloads with the xorshift flag set are reported, not decrypted.

Input: raw binary file, or hex/base64 text. Use --from-json to extract
the multi_stats_data value from an OnSysData.dat JSON file directly.
"""

import argparse
import base64
import binascii
import json
import struct
import sys
import zlib
from pathlib import Path

MAGIC = b"WESYS"
HEADER_SIZE = 16


def load_payload(path, from_json):
    raw = Path(path).read_bytes()
    if from_json:
        try:
            data = json.loads(raw.decode("utf-8-sig"))
        except UnicodeDecodeError as e:
            raise ValueError(f"file is not valid UTF-8 JSON: {e}")
        val = data.get("multi_stats_data")
        if val is None:
            raise ValueError("JSON has no 'multi_stats_data' key")
        if isinstance(val, str):
            raw = val.encode("ascii")
        else:
            raise ValueError(f"multi_stats_data is {type(val).__name__}, expected str")
    # strip whitespace
    raw = raw.strip()
    # try raw binary first (must start with plausible header)
    if len(raw) >= HEADER_SIZE and raw[3:8] == MAGIC:
        return raw
    # try hex
    try:
        h = binascii.unhexlify(raw)
        if len(h) >= HEADER_SIZE and h[3:8] == MAGIC:
            return h
    except (binascii.Error, ValueError):
        pass
    # try base64
    try:
        b = base64.b64decode(raw, validate=True)
        if len(b) >= HEADER_SIZE and b[3:8] == MAGIC:
            return b
    except (binascii.Error, ValueError):
        pass
    raise ValueError("could not decode input as raw/hex/base64 WesysData")


def decode(buf):
    """Returns (info dict, payload bytes or None, warnings)."""
    warnings = []
    if len(buf) < HEADER_SIZE:
        raise ValueError(f"buffer {len(buf)} bytes < 16-byte header")
    if buf[3:8] != MAGIC:
        raise ValueError(f"bad magic: {buf[3:8]!r} != b'WESYS'")
    flags = buf[2]
    zip_flag = bool(flags & 1)
    xor_flag = bool(flags & 2)
    stored_size, org_size = struct.unpack("<II", buf[8:16])
    info = {
        "byte0": buf[0], "byte1": buf[1],
        "flags": flags, "zip_compressed": zip_flag,
        "xorshift_encrypted": xor_flag,
        "stored_size": stored_size, "original_size": org_size,
        "total_len": len(buf),
    }
    payload = buf[16:]
    if len(payload) < stored_size:
        warnings.append(f"truncated: have {len(payload)} payload bytes, header says {stored_size}")
        payload = payload[:stored_size]
    else:
        payload = payload[:stored_size]

    if xor_flag:
        warnings.append("xorshift-encrypted: decryption routine not recovered; payload returned as-is")
        return info, payload, warnings
    if zip_flag:
        try:
            # try zlib wrapper, then raw deflate
            try:
                out = zlib.decompress(payload)
            except zlib.error:
                out = zlib.decompress(payload, -15)
        except zlib.error as e:
            warnings.append(f"zlib decompress failed: {e}")
            return info, payload, warnings
        if len(out) != org_size:
            warnings.append(f"decompressed {len(out)} bytes != header original_size {org_size}")
        return info, out, warnings
    if len(payload) != org_size:
        warnings.append(f"raw payload {len(payload)} bytes != header original_size {org_size}")
    return info, payload, warnings


def main():
    ap = argparse.ArgumentParser(description="Stage 22 WesysData offline decoder")
    ap.add_argument("path", help="binary/hex/base64 payload file, or OnSysData.dat with --from-json")
    ap.add_argument("--from-json", action="store_true",
                    help="extract multi_stats_data from OnSysData.dat JSON")
    ap.add_argument("-o", "--output", help="write decoded payload to file")
    args = ap.parse_args()

    try:
        buf = load_payload(args.path, args.from_json)
        info, payload, warnings = decode(buf)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(f"header OK: magic WESYS, flags=0x{info['flags']:02x} "
          f"(zip={info['zip_compressed']}, xor={info['xorshift_encrypted']})")
    print(f"stored_size={info['stored_size']}, original_size={info['original_size']}")
    for w in warnings:
        print(f"warn: {w}")
    if payload is not None:
        print(f"payload: {len(payload)} bytes")
        if args.output:
            Path(args.output).write_bytes(payload)
            print(f"wrote {args.output}")
        elif not info["xorshift_encrypted"]:
            # show a preview for non-encrypted payloads
            print(f"preview: {payload[:64]!r}")
    return 2 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
