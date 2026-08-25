"""
Stage 4 - Step 3: Extract candidate JSON keys from
ParameterPlayerDefine::PrepareDataFromJson*.

The function compares incoming Json::Value object keys against string literals.
This script disassembles the relevant functions, resolves adrp/add literal
addresses into strings from libUE4.so, and writes a read-only key inventory.
"""
import csv
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
SYMBOLS_CSV = WORKSPACE / "analysis" / "stage4_player_schema" / "parameter_player_define_symbols.csv"
LIBUE4 = WORKSPACE / "extracted" / "apktool" / "PES-CLUB-MANAGER-v4-5-1" / "lib" / "arm64-v8a" / "libUE4.so"
R2 = WORKSPACE / "radare2" / "bin" / "radare2.exe"
OUT_DIR = WORKSPACE / "analysis" / "stage4_player_schema"
R2_SCRIPT = OUT_DIR / "player_json_key_probe.r2"
DISASM_OUT = OUT_DIR / "player_json_key_probe_disasm.txt"
CSV_OUT = OUT_DIR / "parameter_player_define_json_keys.csv"
JSON_OUT = OUT_DIR / "parameter_player_define_json_keys.json"
REPORT = WORKSPACE / "reports" / "stage4_player_json_keys.md"

TARGET_METHODS = {
    "PrepareDataFromJson",
    "PrepareDataFromJsonForScoutingList",
    "SetContractSalaryListFromJson",
    "SetCupEntryRuleStatusListFromJson",
    "SetMilestoneListFromJson",
}

FUNC_HEADER_RE = re.compile(r"^\s*;-- (?:method\.)?onlinemode::ParameterPlayerDefine\.?([A-Za-z0-9_]+)?")
INSTR_RE = re.compile(r"^.*?\b0x([0-9a-fA-F]+)\s+[0-9a-fA-F]+\s+([a-z0-9.]+)\s+(.+)$")
ADRP_RE = re.compile(r"adrp\s+(x\d+),\s*(0x[0-9a-fA-F]+)")
ADD_RE = re.compile(r"add\s+(x\d+),\s*(x\d+),\s*(0x[0-9a-fA-F]+|\d+)")


def load_targets():
    rows = []
    with SYMBOLS_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["owner"] == "onlinemode::ParameterPlayerDefine" and row["method"] in TARGET_METHODS:
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
            instr_count = max(16, int(row["size"]) // 4)
            f.write(f"s {row['address']}\n")
            f.write(f"pd {instr_count}\n")
        f.write("q\n")


def run_r2():
    result = subprocess.run(
        [str(R2), "-q", "-i", str(R2_SCRIPT), str(LIBUE4)],
        cwd=str(WORKSPACE),
        text=True,
        capture_output=True,
        timeout=360,
    )
    DISASM_OUT.write_text(result.stdout, encoding="utf-8", newline="\n")
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-4000:] or f"radare2 failed with {result.returncode}")


def read_c_string(data, offset, limit=128):
    if offset < 0 or offset >= len(data):
        return ""
    end = offset
    while end < len(data) and end - offset < limit and data[end] != 0:
        b = data[end]
        if b < 0x20 or b > 0x7e:
            return ""
        end += 1
    if end == offset:
        return ""
    return data[offset:end].decode("ascii", errors="ignore")


def is_interesting_key(text):
    if not text:
        return False
    if len(text) > 64:
        return False
    if "/" in text or "\\" in text:
        return False
    if text.startswith("_Z"):
        return False
    if not re.match(r"^[A-Za-z0-9_./:-]+$", text):
        return False
    return True


def parse_disasm(rows):
    row_by_start = {int(row["address"], 16): row for row in rows}
    ranges = [
        (int(row["address"], 16), int(row["address"], 16) + int(row["size"]), row)
        for row in rows
    ]

    def row_for_addr(addr):
        for start, end, row in ranges:
            if start <= addr < end:
                return row
        return row_by_start.get(addr)

    data = LIBUE4.read_bytes()
    reg_pages = {}
    records = []
    seen = set()
    for line in DISASM_OUT.read_text(encoding="utf-8", errors="replace").splitlines():
        instr = INSTR_RE.match(line)
        if not instr:
            continue
        addr_s, op, args = instr.groups()
        ins_addr = int(addr_s, 16)
        row = row_for_addr(ins_addr)
        if not row:
            continue
        text = f"{op} {args}"
        adrp = ADRP_RE.search(text)
        if adrp:
            reg, page = adrp.groups()
            reg_pages[(row["method"], reg)] = int(page, 16)
            continue
        add = ADD_RE.search(text)
        if not add:
            continue
        dst, src, raw_off = add.groups()
        page = reg_pages.get((row["method"], src))
        if page is None:
            continue
        off = int(raw_off, 16) if raw_off.startswith("0x") else int(raw_off, 10)
        literal_addr = page + off
        literal = read_c_string(data, literal_addr)
        if not is_interesting_key(literal):
            continue
        key = (row["method"], literal_addr, literal)
        if key in seen:
            continue
        seen.add(key)
        records.append({
            "method": row["method"],
            "function_address": row["address"],
            "instruction_address": f"0x{ins_addr:08x}",
            "literal_address": f"0x{literal_addr:08x}",
            "literal": literal,
            "instruction": line.strip(),
        })
    records.sort(key=lambda r: (r["method"], int(r["literal_address"], 16), r["instruction_address"]))
    return records


def main():
    targets = load_targets()
    print(f"[*] JSON-related functions: {len(targets)}")
    write_r2_script(targets)
    print(f"[*] Running radare2: {R2_SCRIPT}")
    run_r2()
    records = parse_disasm(targets)

    with CSV_OUT.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "method", "function_address", "instruction_address",
            "literal_address", "literal", "instruction",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    by_method = defaultdict(list)
    for rec in records:
        by_method[rec["method"]].append(rec)
    JSON_OUT.write_text(json.dumps(by_method, indent=2), encoding="utf-8")

    literal_counts = Counter(rec["literal"] for rec in records)
    meaningful = [
        lit for lit in literal_counts
        if len(lit) > 1 and not lit.isdigit()
    ]

    with REPORT.open("w", encoding="utf-8", newline="\n") as f:
        f.write("# Stage 4 Player JSON Key Inventory\n\n")
        f.write("Scope: read-only extraction of string literals referenced by `ParameterPlayerDefine` JSON preparation methods. These are candidate JSON keys or enum/string constants and require cross-checking.\n\n")
        f.write(f"**Functions scanned:** {len(targets):,}\n\n")
        f.write(f"**Literal references:** {len(records):,}\n\n")
        f.write(f"**Meaningful non-numeric literals:** {len(meaningful):,}\n\n")
        f.write("## By Function\n\n")
        f.write("| Function | Literal refs | Example literals |\n")
        f.write("|---|---:|---|\n")
        for method, items in sorted(by_method.items()):
            examples = []
            for item in items:
                lit = item["literal"]
                if lit not in examples and len(lit) > 1:
                    examples.append(lit)
                if len(examples) >= 12:
                    break
            f.write(f"| `{method}` | {len(items):,} | `{', '.join(examples)}` |\n")
        f.write("\n## Candidate Keys\n\n")
        for lit in sorted(meaningful)[:250]:
            f.write(f"- `{lit}`\n")
        f.write("\n## Outputs\n\n")
        f.write(f"- `{CSV_OUT.relative_to(WORKSPACE)}`\n")
        f.write(f"- `{JSON_OUT.relative_to(WORKSPACE)}`\n")
        f.write(f"- `{DISASM_OUT.relative_to(WORKSPACE)}`\n")
        f.write("\n## Next\n\n")
        f.write("- Correlate key order with nearby setter calls in `PrepareDataFromJson`.\n")
        f.write("- Build a conservative read-only JSON normalizer for any captured/local JSON records.\n")
        f.write("- Keep binary editor disabled until file/local record layout is confirmed.\n")

    print(f"[+] Literal refs: {len(records)}")
    print(f"[+] Wrote {CSV_OUT}")
    print(f"[+] Wrote {JSON_OUT}")
    print(f"[+] Wrote {REPORT}")


if __name__ == "__main__":
    main()
