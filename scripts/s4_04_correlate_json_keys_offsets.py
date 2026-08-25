"""
Stage 4 - Step 4: Correlate candidate JSON keys with native field offsets.

This creates a conservative bridge table for a read-only player parser/viewer:
JSON key -> native field candidate -> in-memory backing offset when available.
"""
import csv
import json
import re
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
KEYS_CSV = WORKSPACE / "analysis" / "stage4_player_schema" / "parameter_player_define_json_keys.csv"
OFFSETS_JSON = WORKSPACE / "analysis" / "stage4_player_schema" / "parameter_player_define_offsets.json"
OUT_DIR = WORKSPACE / "analysis" / "stage4_player_schema"
CSV_OUT = OUT_DIR / "player_json_key_offset_map.csv"
JSON_OUT = OUT_DIR / "player_json_key_offset_map.json"
REPORT = WORKSPACE / "reports" / "stage4_player_key_offset_map.md"

POSITION_KEYS = {
    "gk", "cb", "rsb", "lsb", "dmf", "cmf", "rmf", "lmf",
    "omf", "rwg", "lwg", "st", "cf",
}

DIRECT_SYNONYMS = {
    "name": "Name",
    "uniform_name": "NamePrint",
    "original_team_id": "OriginalTeamId",
    "licence": "License",
    "stronger_foot": "StrongerFoot",
    "next_salary": "NextSalary",
    "condition_status": "Condition",
    "camulative_yellow_cards": "SumYellow",
    "record_match_total": "GameSum",
    "record_match_season": "GameSeason",
    "record_goal_total": "GoalSum",
    "record_goal_season": "GoalSeason",
    "record_assist_total": "AssistSum",
    "record_assist_season": "AssistSeason",
    "record_yellow_card_total": "YellowSum",
    "record_yellow_card_season": "YellowSeason",
    "record_red_card_total": "RedSum",
    "record_red_card_season": "RedSeason",
    "record_average_rating_total": "PointSum",
    "record_average_rating_season": "PointSeason",
    "age": "Age",
    "nationality": "Nationality",
    "salary": "Salary",
    "sell_price": "SellPrice",
    "price": "MarketValue",
    "serial_id": "SerialId",
    "master_id": "MasterId",
    "rarity": "Rarity",
    "playstyle": "PlayStyle",
    "position": "RegisteredPosition",
    "uniform_number": "UniformNumber",
    "injury": "InjuryLength",
    "motivation": "MotivationValue",
    "contract_period": "ContractPeriod",
    "contract_period_max": "ContractPeriodMax",
    "contract_period_request": "ContractPeriodRequest",
    "contract_status": "ContractStatus",
    "salary_list": "ContractSalary",
    "deleted": "DeleteType",
}


def snake_to_pascal(text):
    return "".join(part.capitalize() for part in text.split("_") if part)


def load_offset_index():
    items = json.loads(OFFSETS_JSON.read_text(encoding="utf-8"))
    index = {}
    for item in items:
        offsets = item.get("offsets", [])
        index[item["field_candidate"]] = offsets
    return index


def key_category(key):
    if key.startswith("param_"):
        return "ability_parameter"
    if key.startswith("skill_"):
        return "skill_card"
    if key in POSITION_KEYS:
        return "position_aptitude"
    if key.startswith("record_"):
        return "record"
    if key.isdigit() or re.fullmatch(r"[A-Z]", key):
        return "enum_or_index"
    return "field"


def map_key(key, offset_index):
    category = key_category(key)
    if category == "ability_parameter":
        return "AbilityParameter", "group: ability parameter array"
    if category == "skill_card":
        return "SkillCard", "group: skill-card flags/list"
    if category == "position_aptitude":
        return "PositionAptitude", "group: position aptitude bitfield/table"
    if key in DIRECT_SYNONYMS:
        return DIRECT_SYNONYMS[key], "direct synonym"
    pascal = snake_to_pascal(key)
    if pascal in offset_index:
        return pascal, "normalized exact match"
    return "", "unmapped"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    offset_index = load_offset_index()

    key_rows = []
    with KEYS_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            lit = row["literal"]
            if len(lit) <= 1 or lit.isdigit():
                continue
            if lit.startswith("EMouseCursor") or lit in {"ursor::TextEditBeam", "ure", "vvx", "epad"}:
                continue
            key_rows.append(row)

    seen = set()
    records = []
    for row in key_rows:
        key = row["literal"]
        if key in seen:
            continue
        seen.add(key)
        field, reason = map_key(key, offset_index)
        offsets = offset_index.get(field, []) if field else []
        offset_s = ", ".join(o["offset_hex"] for o in offsets) if offsets else ""
        width_s = ", ".join(sorted({w for o in offsets for w in o.get("widths", [])})) if offsets else ""
        records.append({
            "json_key": key,
            "category": key_category(key),
            "field_candidate": field,
            "native_offsets": offset_s,
            "widths": width_s,
            "confidence": "medium" if field else "low",
            "mapping_reason": reason,
        })

    records.sort(key=lambda r: (r["category"], r["json_key"]))
    with CSV_OUT.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "json_key", "category", "field_candidate", "native_offsets",
            "widths", "confidence", "mapping_reason",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    JSON_OUT.write_text(json.dumps(records, indent=2), encoding="utf-8")

    mapped = [r for r in records if r["field_candidate"]]
    grouped = {}
    for rec in records:
        grouped.setdefault(rec["category"], []).append(rec)

    with REPORT.open("w", encoding="utf-8", newline="\n") as f:
        f.write("# Stage 4 Player Key/Offset Map\n\n")
        f.write("Scope: conservative correlation of extracted JSON-key literals with candidate native `ParameterPlayerDefine` backing-data offsets. This is not yet a file-format parser.\n\n")
        f.write(f"**Unique useful JSON keys:** {len(records):,}\n\n")
        f.write(f"**Mapped keys:** {len(mapped):,}\n\n")
        f.write("## Core Field Map\n\n")
        f.write("| JSON key | Field candidate | Native offset(s) | Widths | Confidence |\n")
        f.write("|---|---|---:|---|---|\n")
        for rec in records:
            if rec["category"] not in {"field", "record"}:
                continue
            if not rec["field_candidate"]:
                continue
            f.write(
                f"| `{rec['json_key']}` | `{rec['field_candidate']}` | "
                f"`{rec['native_offsets'] or '?'}` | `{rec['widths'] or '?'}` | {rec['confidence']} |\n"
            )
        f.write("\n## Grouped Keys\n\n")
        for category in ["ability_parameter", "skill_card", "position_aptitude", "enum_or_index", "field"]:
            items = grouped.get(category, [])
            if not items:
                continue
            f.write(f"### {category}\n\n")
            f.write(", ".join(f"`{item['json_key']}`" for item in items[:80]))
            if len(items) > 80:
                f.write(f", ... ({len(items) - 80} more)")
            f.write("\n\n")
        unmapped = [r for r in records if not r["field_candidate"] and r["category"] == "field"]
        f.write("## Unmapped Field-like Keys\n\n")
        if unmapped:
            for rec in unmapped:
                f.write(f"- `{rec['json_key']}`\n")
        else:
            f.write("None.\n")
        f.write("\n## Outputs\n\n")
        f.write(f"- `{CSV_OUT.relative_to(WORKSPACE)}`\n")
        f.write(f"- `{JSON_OUT.relative_to(WORKSPACE)}`\n")
        f.write("\n## Next\n\n")
        f.write("- Trace nearby setter calls for each JSON key to raise confidence from medium to high.\n")
        f.write("- Use this map as the schema for a read-only JSON player normalizer/viewer.\n")
        f.write("- Keep binary editing out of scope until a real local file layout is proven.\n")

    print(f"[+] Unique useful keys: {len(records)}")
    print(f"[+] Mapped keys: {len(mapped)}")
    print(f"[+] Wrote {CSV_OUT}")
    print(f"[+] Wrote {JSON_OUT}")
    print(f"[+] Wrote {REPORT}")


if __name__ == "__main__":
    main()
