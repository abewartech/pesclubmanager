"""Stage 10: static analysis helpers for libUE4.so (arm64).

- Enumerate dynamic symbols matching a substring.
- Scan .text for aarch64 ADRP+ADD string xrefs to a set of target
  .rodata addresses (raw-bytes scan, no disassembler needed for xrefs).
- Resolve PLT stubs to import names via JUMP_SLOT relocations.

Read-only: never modifies the input binary.

Requires: capstone, pyelftools.
"""

import argparse
import bisect
import struct
import sys
from pathlib import Path

from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection
from elftools.elf.sections import SymbolTableSection

WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_LIB = WORKSPACE / "original" / "extracted" / "apk" / "lib" / "arm64-v8a" / "libUE4.so"

R_AARCH64_JUMP_SLOT = 1026


class Lib:
    def __init__(self, path):
        self.f = open(path, "rb")
        self.elffile = ELFFile(self.f)
        text = self.elffile.get_section_by_name(".text")
        self.tdata = text.data()
        self.tbase = text["sh_addr"]
        rodata = self.elffile.get_section_by_name(".rodata")
        self.rdata = rodata.data()
        self.rbase = rodata["sh_addr"]
        self.dynsym = self.elffile.get_section_by_name(".dynsym")
        plt = self.elffile.get_section_by_name(".plt")
        self.plt_base = plt["sh_addr"]
        self.pdata = plt.data()

        self.funcs = []
        for sec in self.elffile.iter_sections():
            if isinstance(sec, SymbolTableSection) and sec.name == ".dynsym":
                for s in sec.iter_symbols():
                    if s.entry["st_info"]["type"] == "STT_FUNC" and s.entry["st_value"]:
                        self.funcs.append((s.entry["st_value"], s.entry["st_size"], s.name))
        self.funcs.sort()
        self.faddrs = [a for a, _, _ in self.funcs]

        self.rels = {}
        for sec in self.elffile.iter_sections():
            if isinstance(sec, RelocationSection):
                for rel in sec.iter_relocations():
                    if rel["r_info_type"] == R_AARCH64_JUMP_SLOT:
                        sym = self.dynsym.get_symbol(rel["r_info_sym"])
                        self.rels[rel["r_offset"]] = sym.name if sym else "?"

    def func_at(self, addr, width=80):
        i = bisect.bisect_right(self.faddrs, addr) - 1
        return self.funcs[i][2][:width] if i >= 0 else "?"

    def close(self):
        self.f.close()

    def func_named(self, substr):
        return [(a, sz, n) for a, sz, n in self.funcs if substr in n]

    def rstr(self, addr, maxlen=100):
        if self.rbase <= addr < self.rbase + len(self.rdata):
            e = self.rdata.find(b"\x00", addr - self.rbase)
            s = self.rdata[addr - self.rbase:e]
            if 2 < len(s) < maxlen and all(32 <= c < 127 for c in s):
                return s.decode()
        return None

    def plt_name(self, addr):
        off = addr - self.plt_base
        if not (0 <= off <= len(self.pdata) - 8):
            return self.func_at(addr)
        w0, = struct.unpack_from("<I", self.pdata, off)
        w1, = struct.unpack_from("<I", self.pdata, off + 4)
        if w0 & 0x9F000000 != 0x90000000 or w1 & 0xFF000000 != 0x91000000:
            # Not an ADRP+ADD PLT stub — don't decode garbage.
            return self.func_at(addr)
        immlo = (w0 >> 29) & 3
        immhi = (w0 >> 5) & 0x7FFFF
        pg = ((immhi << 2) | immlo) << 12
        page = (addr & ~0xFFF) + pg
        if pg & (1 << 32):
            page -= 1 << 33
        got = page + (((w1 >> 10) & 0xFFF) << 3)
        return self.rels.get(got, self.func_at(addr))

    def xrefs_to_strings(self, targets):
        """targets: {addr: label}. Returns {label: [(insn_addr, func_name)]}.

        Raw scan for ADRP to the target page followed within 8
        instructions by ADD xd, xd, #imm resolving exactly to target.
        """
        pages = {}
        for addr, label in targets.items():
            pages.setdefault(addr & ~0xFFF, []).append((addr, label))
        hits = {label: [] for label in targets.values()}
        n = len(self.tdata) // 4
        for i in range(n):
            w, = struct.unpack_from("<I", self.tdata, i * 4)
            if w & 0x9F000000 != 0x90000000:
                continue
            immlo = (w >> 29) & 0x3
            immhi = (w >> 5) & 0x7FFFF
            off = ((immhi << 2) | immlo) << 12
            pc = self.tbase + i * 4
            page = (pc & ~0xFFF) + off
            if page not in pages:
                continue
            rd = w & 0x1F
            for j in range(1, 9):
                if (i + j) * 4 + 4 > len(self.tdata):
                    break
                w2, = struct.unpack_from("<I", self.tdata, (i + j) * 4)
                if (w2 & 0xFF000000 == 0x91000000 and (w2 & 0x1F) == rd
                        and ((w2 >> 5) & 0x1F) == rd):
                    imm12 = (w2 >> 10) & 0xFFF
                    if (w2 >> 22) & 0x3 == 1:
                        imm12 <<= 12
                    saddr = page + imm12
                    for ta, label in pages[page]:
                        if ta == saddr:
                            hits[label].append((pc, self.func_at(pc)))
                    break
        return hits


def main():
    ap = argparse.ArgumentParser(description="Stage 10 libUE4.so static analysis helpers")
    ap.add_argument("--lib", default=str(DEFAULT_LIB))
    ap.add_argument("--symbols", help="list dynsym names containing SUBSTR")
    ap.add_argument("--xrefs", help="comma-separated hex .rodata addrs to find xrefs to")
    args = ap.parse_args()

    lib = Lib(args.lib)
    try:
        if args.symbols:
            for a, sz, n in lib.func_named(args.symbols):
                print(f"  {hex(a)} (+{sz}) {n[:110]}")
        if args.xrefs:
            targets = {}
            for x in args.xrefs.split(","):
                addr = int(x.strip(), 16)
                s = lib.rstr(addr) or ""
                targets[addr] = f"{hex(addr)} {s[:40]}"
            for label, hs in lib.xrefs_to_strings(targets).items():
                print(f"--- {label}: {len(hs)} xrefs")
                for a, fn in sorted(set(hs))[:20]:
                    print(f"  {hex(a)} in {fn}")
    finally:
        lib.close()


if __name__ == "__main__":
    main()
