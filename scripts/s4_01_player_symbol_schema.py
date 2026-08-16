"""
Stage 4 - Step 1: Build a candidate Player schema from native exported symbols.

Input: analysis/libUE4_arm64_exports.json from rabin2.
Output:
  analysis/stage4_player_schema/parameter_player_define_symbols.csv
  analysis/stage4_player_schema/player_schema_candidates.json
  reports/stage4_player_symbol_schema.md

This is read-only analysis. It does not infer offsets as facts.
"""
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
EXPORTS_JSON = WORKSPACE / "analysis" / "libUE4_arm64_exports.json"
OUT_DIR = WORKSPACE / "analysis" / "stage4_player_schema"
REPORT = WORKSPACE / "reports" / "stage4_player_symbol_schema.md"


def parse_itanium_nested(name: str):
    if not name.startswith("_ZN"):
        return None
    i = 3
    const = False
    if i < len(name) and name[i] == "K":
        const = True
        i += 1
    parts = []
    while i < len(name) and name[i] != "E":
        m = re.match(r"(\d+)", name[i:])
        if not m:
            break
        n = int(m.group(1))
        i += len(m.group(1))
        parts.append(name[i:i + n])
        i += n
    if not parts:
        return None
    return {
        "const": const,
        "parts": parts,
        "qualified": "::".join(parts),
        "method": parts[-1],
        "owner": "::".join(parts[:-1]),
    }


def field_from_method(method: str):
    for prefix in ("Get", "Set", "Is", "Has", "Clear", "Prepare"):
        if method.startswith(prefix) and len(method) > len(prefix):
            return prefix, method[len(prefix):]
    if method in ("C1", "C2", "D1", "D2", "D0"):
        return "lifecycle", method
    return "other", method


def load_exports():
    with EXPORTS_JSON.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("exports", data)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    schema = defaultdict(lambda: {
        "field": "",
        "getters": [],
        "setters": [],
        "predicates": [],
        "other_methods": [],
        "evidence": [],
    })

    for exp in load_exports():
        name = exp.get("realname") or exp.get("name") or ""
        if "ParameterPlayerDefine" not in name and "tmpdb6Player" not in name:
            continue
        parsed = parse_itanium_nested(name)
        if not parsed:
            continue
        method = parsed["method"]
        owner = parsed["owner"]
        category, field = field_from_method(method)
        row = {
            "address": f"0x{int(exp.get('vaddr', 0)):08x}",
            "size": exp.get("size", 0),
            "owner": owner,
            "method": method,
            "category": category,
            "field_candidate": field,
            "symbol": name,
        }
        rows.append(row)

        if "ParameterPlayerDefine" in owner and category in ("Get", "Set", "Is", "Has", "Clear", "Prepare"):
            item = schema[field]
            item["field"] = field
            item["evidence"].append({
                "method": method,
                "address": row["address"],
                "size": row["size"],
            })
            if category == "Get":
                item["getters"].append(method)
            elif category == "Set":
                item["setters"].append(method)
            elif category in ("Is", "Has"):
                item["predicates"].append(method)
            else:
                item["other_methods"].append(method)

    rows.sort(key=lambda r: (r["owner"], r["field_candidate"], r["method"], r["address"]))
    csv_path = OUT_DIR / "parameter_player_define_symbols.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [
            "address", "size", "owner", "method", "category", "field_candidate", "symbol"
        ])
        writer.writeheader()
        writer.writerows(rows)

    schema_items = sorted(schema.values(), key=lambda x: x["field"].lower())
    schema_path = OUT_DIR / "player_schema_candidates.json"
    with schema_path.open("w", encoding="utf-8") as f:
        json.dump(schema_items, f, indent=2, ensure_ascii=False)

    category_counts = Counter(r["category"] for r in rows)
    owner_counts = Counter(r["owner"] for r in rows)
    high_signal = [
        item for item in schema_items
        if item["getters"] or item["setters"] or item["predicates"]
    ]

    with REPORT.open("w", encoding="utf-8", newline="\n") as f:
        f.write("# Stage 4 Player Symbol Schema\n\n")
        f.write("Scope: exported native symbol analysis only. Field names below are candidates, not confirmed binary offsets/types.\n\n")
        f.write(f"**Symbols analyzed:** {len(rows):,}\n\n")
        f.write(f"**ParameterPlayerDefine field candidates:** {len(high_signal):,}\n\n")
        f.write("## Category Counts\n\n")
        f.write("| Category | Count |\n|---|---:|\n")
        for cat, count in category_counts.most_common():
            f.write(f"| `{cat}` | {count:,} |\n")
        f.write("\n## Top Owners\n\n")
        f.write("| Owner | Count |\n|---|---:|\n")
        for owner, count in owner_counts.most_common(20):
            f.write(f"| `{owner}` | {count:,} |\n")
        f.write("\n## High-Signal Field Candidates\n\n")
        f.write("| Field candidate | Getter | Setter | Predicate/Other evidence |\n")
        f.write("|---|---|---|---|\n")
        for item in high_signal[:120]:
            getters = ", ".join(sorted(set(item["getters"]))) or "-"
            setters = ", ".join(sorted(set(item["setters"]))) or "-"
            other = ", ".join(sorted(set(item["predicates"] + item["other_methods"]))) or "-"
            f.write(f"| `{item['field']}` | `{getters}` | `{setters}` | `{other}` |\n")
        f.write("\n## Outputs\n\n")
        f.write(f"- `{csv_path.relative_to(WORKSPACE)}`\n")
        f.write(f"- `{schema_path.relative_to(WORKSPACE)}`\n")
        f.write("\n## Next Analysis\n\n")
        f.write("- Disassemble tiny getters/setters to recover field offsets.\n")
        f.write("- Use large `PrepareDataFromJson*` methods to map JSON keys to these fields.\n")
        f.write("- Cross-check any local extracted records before enabling write/edit behavior.\n")

    print(f"[+] Wrote {csv_path}")
    print(f"[+] Wrote {schema_path}")
    print(f"[+] Wrote {REPORT}")


if __name__ == "__main__":
    main()
