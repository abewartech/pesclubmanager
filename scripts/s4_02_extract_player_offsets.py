"""
Stage 4 - Step 2: Extract candidate in-memory offsets from small
onlinemode::ParameterPlayerDefine accessors.

This is read-only analysis. It disassembles small exported getter/setter
functions and looks for the common pattern:

  ldr xN, [x0, 0x28]        ; backing player-data pointer
  ldr/str/... ?, [xN, off]  ; field access

The output is a candidate in-memory schema, not a file-format schema.
"""
import csv
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
CSV_IN = WORKSPACE / "analysis" / "stage4_player_schema" / "parameter_player_define_symbols.csv"
LIBUE4 = WORKSPACE / "extracted" / "apktool" / "PES-CLUB-MANAGER-v4-5-1" / "lib" / "arm64-v8a" / "libUE4.so"
R2 = WORKSPACE / "radare2" / "bin" / "radare2.exe"
OUT_DIR = WORKSPACE / "analysis" / "stage4_player_schema"
R2_SCRIPT = OUT_DIR / "player_offset_probe.r2"
DISASM_OUT = OUT_DIR / "player_offset_probe_disasm.txt"
CSV_OUT = OUT_DIR / "parameter_player_define_offsets.csv"
JSON_OUT = OUT_DIR / "parameter_player_define_offsets.json"
REPORT = WORKSPACE / "reports" / "stage4_player_offset_schema.md"

OWNER = "onlinemode::ParameterPlayerDefine"
ACCESSOR_CATEGORIES = {"Get", "Set", "Is", "Has"}
MAX_FUNC_SIZE = 96

FUNC_HEADER_RE = re.compile(r"^\s*;-- method\.onlinemode::ParameterPlayerDefine\.([A-Za-z0-9_]+)")
INSTR_RE = re.compile(r"^.*?\b0x([0-9a-fA-F]+)\s+[0-9a-fA-F]+\s+([a-z0-9.]+)\s+(.+)$")
BACKING_RE = re.compile(r"ldr\s+(x\d+),\s*\[x0,\s*0x28\]")
MEM_RE = re.compile(r"\[(x\d+),\s*(-?0x[0-9a-fA-F]+|-?\d+)\]")
ADD_RE = re.compile(r"add\s+(x\d+),\s*(x\d+),\s*(0x[0-9a-fA-F]+|\d+)")


def read_accessors():
    rows = []
    with CSV_IN.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            try:
                size = int(row["size"])
            except ValueError:
                continue
            if row["owner"] != OWNER:
                continue
            if row["category"] not in ACCESSOR_CATEGORIES:
                continue
            if size <= 0 or size > MAX_FUNC_SIZE:
                continue
            rows.append(row)
    rows.sort(key=lambda r: int(r["address"], 16))
    return rows


def write_r2_script(rows):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with R2_SCRIPT.open("w", encoding="utf-8", newline="\n") as f:
        f.write("e scr.color=false\n")
        f.write("e asm.bytes=true\n")
        f.write("e asm.comments=true\n")
        for row in rows:
            instr_count = max(4, min(24, (int(row["size"]) // 4) + 3))
            f.write(f"s {row['address']}\n")
            f.write(f"pd {instr_count}\n")
        f.write("q\n")


def run_r2():
    result = subprocess.run(
        [str(R2), "-q", "-i", str(R2_SCRIPT), str(LIBUE4)],
        cwd=str(WORKSPACE),
        text=True,
        capture_output=True,
        timeout=240,
    )
    DISASM_OUT.write_text(result.stdout, encoding="utf-8", newline="\n")
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-4000:] or f"radare2 failed with {result.returncode}")


def parse_disasm(rows):
    method_rows = sorted(rows, key=lambda r: len(r["method"]), reverse=True)

    def row_for_slug(method_slug):
        for row in method_rows:
            method = row["method"]
            if method_slug == method or method_slug.startswith(method + "_"):
                return row
        return None

    current = None
    parsed = defaultdict(list)
    for line in DISASM_OUT.read_text(encoding="utf-8", errors="replace").splitlines():
        header = FUNC_HEADER_RE.match(line)
        if header:
            method_slug = header.group(1)
            current = row_for_slug(method_slug)
            continue
        if not current:
            continue
        instr = INSTR_RE.match(line)
        if not instr:
            continue
        addr, op, args = instr.groups()
        ins_addr = int(addr, 16)
        func_start = int(current["address"], 16)
        func_end = func_start + int(current["size"])
        if not (func_start <= ins_addr < func_end):
            continue
        parsed[current["method"]].append({
            "address": "0x" + addr.lower(),
            "op": op,
            "args": args.strip(),
            "text": line.strip(),
        })
    return parsed


def extract_offset(row, instructions):
    backing_regs = set()
    accesses = []
    for ins in instructions:
        text = f"{ins['op']} {ins['args']}"
        backing = BACKING_RE.search(text)
        if backing:
            backing_regs.add(backing.group(1))
            continue
        mem = MEM_RE.search(ins["args"])
        if mem:
            reg, raw_off = mem.groups()
            if reg in backing_regs:
                if raw_off.startswith("-0x"):
                    offset = -int(raw_off[3:], 16)
                elif raw_off.startswith("0x"):
                    offset = int(raw_off, 16)
                else:
                    offset = int(raw_off, 10)
                if ins["op"].startswith(("ldr", "ldur")):
                    access = "read"
                elif ins["op"].startswith(("str", "stur")):
                    access = "write"
                else:
                    access = "other"
                width = "unknown"
                if ins["op"].endswith("b"):
                    width = "u8"
                elif ins["op"].endswith("h"):
                    width = "u16"
                elif re.search(r"\bw\d+", ins["args"]):
                    width = "u32"
                elif re.search(r"\bx\d+", ins["args"]):
                    width = "u64"
                accesses.append({
                    "offset": offset,
                    "offset_hex": f"0x{offset:x}" if offset >= 0 else f"-0x{-offset:x}",
                    "access": access,
                    "width": width,
                    "instruction": ins["text"],
                })

        add = ADD_RE.search(text)
        if add:
            _dst, reg, raw_off = add.groups()
            if reg in backing_regs:
                offset = int(raw_off, 16) if raw_off.startswith("0x") else int(raw_off, 10)
                accesses.append({
                    "offset": offset,
                    "offset_hex": f"0x{offset:x}",
                    "access": "address",
                    "width": "pointer",
                    "instruction": ins["text"],
                })

    bitfield = None
    for ins in instructions:
        if ins["op"] in {"and", "bfi", "ubfx", "sbfiz"}:
            bitfield = (bitfield or []) + [ins["text"]]

    deduped = []
    seen = set()
    for access in accesses:
        key = (access["offset"], access["access"], access["width"], access["instruction"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(access)

    return deduped, bitfield


def main():
    accessors = read_accessors()
    print(f"[*] Accessors selected: {len(accessors)}")
    write_r2_script(accessors)
    print(f"[*] Running radare2: {R2_SCRIPT}")
    run_r2()

    instructions_by_method = parse_disasm(accessors)
    records = []
    for row in accessors:
        instructions = instructions_by_method.get(row["method"], [])
        accesses, bitfield = extract_offset(row, instructions)
        for access in accesses:
            records.append({
                "field_candidate": row["field_candidate"],
                "method": row["method"],
                "category": row["category"],
                "function_address": row["address"],
                "function_size": row["size"],
                **access,
                "bitfield_evidence": " | ".join(bitfield or []),
            })

    records.sort(key=lambda r: (r["offset"], r["field_candidate"], r["method"], r["access"]))
    with CSV_OUT.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "field_candidate", "method", "category", "function_address",
            "function_size", "offset_hex", "offset", "access", "width",
            "instruction", "bitfield_evidence",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    grouped = defaultdict(lambda: {
        "field_candidate": "",
        "offsets": defaultdict(lambda: {
            "offset_hex": "",
            "reads": [],
            "writes": [],
            "addresses": [],
            "widths": set(),
            "bitfield_evidence": set(),
        }),
    })
    for rec in records:
        item = grouped[rec["field_candidate"]]
        item["field_candidate"] = rec["field_candidate"]
        off = item["offsets"][rec["offset_hex"]]
        off["offset_hex"] = rec["offset_hex"]
        off["widths"].add(rec["width"])
        if rec["access"] == "read":
            off["reads"].append(rec["method"])
        elif rec["access"] == "write":
            off["writes"].append(rec["method"])
        elif rec["access"] == "address":
            off["addresses"].append(rec["method"])
        if rec["bitfield_evidence"]:
            off["bitfield_evidence"].add(rec["bitfield_evidence"])

    json_ready = []
    for item in grouped.values():
        offsets = []
        for off in item["offsets"].values():
            offsets.append({
                "offset_hex": off["offset_hex"],
                "reads": sorted(set(off["reads"])),
                "writes": sorted(set(off["writes"])),
                "addresses": sorted(set(off["addresses"])),
                "widths": sorted(off["widths"]),
                "bitfield_evidence": sorted(off["bitfield_evidence"]),
            })
        offsets.sort(key=lambda x: int(x["offset_hex"], 16) if not x["offset_hex"].startswith("-") else -1)
        json_ready.append({
            "field_candidate": item["field_candidate"],
            "offsets": offsets,
        })
    json_ready.sort(key=lambda x: x["field_candidate"].lower())
    JSON_OUT.write_text(json.dumps(json_ready, indent=2), encoding="utf-8")

    high_conf = [
        item for item in json_ready
        if len(item["offsets"]) == 1 and (
            item["offsets"][0]["reads"]
            or item["offsets"][0]["writes"]
            or item["offsets"][0]["addresses"]
        )
    ]
    with REPORT.open("w", encoding="utf-8", newline="\n") as f:
        f.write("# Stage 4 Player Offset Schema\n\n")
        f.write("Scope: automated read-only disassembly of small `onlinemode::ParameterPlayerDefine` accessors. These are candidate in-memory backing-data offsets, not confirmed file offsets.\n\n")
        f.write(f"**Accessors selected:** {len(accessors):,}\n\n")
        f.write(f"**Field access records:** {len(records):,}\n\n")
        f.write(f"**Single-offset field candidates:** {len(high_conf):,}\n\n")
        f.write("## High-Confidence Offset Candidates\n\n")
        f.write("| Field | Offset | Widths | Reads | Writes | Address refs | Notes |\n")
        f.write("|---|---:|---|---|---|---|---|\n")
        for item in high_conf[:140]:
            off = item["offsets"][0]
            notes = "bitfield" if off["bitfield_evidence"] else ""
            f.write(
                f"| `{item['field_candidate']}` | `{off['offset_hex']}` | "
                f"`{', '.join(off['widths'])}` | `{', '.join(off['reads']) or '-'}` | "
                f"`{', '.join(off['writes']) or '-'}` | "
                f"`{', '.join(off['addresses']) or '-'}` | {notes} |\n"
            )
        f.write("\n## Outputs\n\n")
        f.write(f"- `{CSV_OUT.relative_to(WORKSPACE)}`\n")
        f.write(f"- `{JSON_OUT.relative_to(WORKSPACE)}`\n")
        f.write(f"- `{DISASM_OUT.relative_to(WORKSPACE)}`\n")
        f.write("\n## Next\n\n")
        f.write("- Manually review fields with multiple offsets or bitfield evidence.\n")
        f.write("- Map `PrepareDataFromJson*` JSON keys onto this in-memory schema.\n")
        f.write("- Only after a real record is found, test read-only binary-to-JSON parsing against known values.\n")

    print(f"[+] Records: {len(records)}")
    print(f"[+] Wrote {CSV_OUT}")
    print(f"[+] Wrote {JSON_OUT}")
    print(f"[+] Wrote {REPORT}")


if __name__ == "__main__":
    main()
