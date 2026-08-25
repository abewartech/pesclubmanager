"""
Stage 5 - Step 1: Normalize offline player-shaped JSON.

This is a read-only parser for local JSON artifacts. It does not patch game
files, save data, APK/OBB/PAK/CPK containers, or online services.
"""
import argparse
import json
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_OUT = WORKSPACE / "analysis" / "stage5_player_json" / "normalized_players.json"
KEY_OFFSET_MAP = WORKSPACE / "analysis" / "stage4_player_schema" / "player_json_key_offset_map.json"

STRONG_KEYS = {
    "serial_id",
    "master_id",
    "original_team_id",
    "salary",
    "contract_period",
    "rarity",
    "position",
}

IDENTITY_KEYS = {"id", "player_id", "serial_id", "master_id"}
PROFILE_KEYS = {
    "name",
    "uniform_name",
    "age",
    "nationality",
    "position",
    "rarity",
    "playstyle",
    "stronger_foot",
    "height",
    "weight",
    "durability",
    "stability",
    "energy",
    "uniform_number",
    "condition_status",
    "injury",
    "motivation",
    "deleted",
    "licence",
}
TEAM_KEYS = {"original_team_id", "team_id"}
CONTRACT_KEYS = {
    "salary",
    "next_salary",
    "salary_list",
    "price",
    "sell_price",
    "contract_period",
    "contract_period_max",
    "contract_period_request",
    "contract_status",
}
RECORD_KEYS = {
    "camulative_yellow_cards",
    "record_match_total",
    "record_match_season",
    "record_goal_total",
    "record_goal_season",
    "record_assist_total",
    "record_assist_season",
    "record_point_total",
    "record_point_season",
    "record_average_rating_total",
    "record_average_rating_season",
    "record_yellow_card_total",
    "record_yellow_card_season",
    "record_red_card_total",
    "record_red_card_season",
}
POSITION_KEYS = {
    "gk",
    "cb",
    "rsb",
    "lsb",
    "dmf",
    "cmf",
    "rmf",
    "lmf",
    "omf",
    "rwg",
    "lwg",
    "st",
    "cf",
}


def load_key_map():
    if not KEY_OFFSET_MAP.exists():
        return {}
    items = json.loads(KEY_OFFSET_MAP.read_text(encoding="utf-8"))
    return {item.get("json_key"): item for item in items if item.get("json_key")}


def is_player_candidate(value):
    if not isinstance(value, dict):
        return False

    keys = set(value)
    score = sum(1 for key in STRONG_KEYS if key in keys)
    score += sum(1 for key in keys if key.startswith("param_"))
    score += sum(1 for key in keys if key.startswith("skill_"))

    if "name" in keys and ({"serial_id", "master_id"} & keys):
        score += 1

    return score >= 2


def pointer_join(parent, part):
    escaped = str(part).replace("~", "~0").replace("/", "~1")
    if parent == "":
        return "/" + escaped
    return parent + "/" + escaped


def walk_json(value, pointer=""):
    yield pointer, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk_json(child, pointer_join(pointer, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_json(child, pointer_join(pointer, index))


def classify_key(key):
    if key in IDENTITY_KEYS:
        return "identity"
    if key in PROFILE_KEYS:
        return "profile"
    if key in TEAM_KEYS:
        return "team"
    if key in CONTRACT_KEYS:
        return "contract"
    if key.startswith("param_"):
        return "abilities"
    if key.startswith("skill_"):
        return "skills"
    if key in POSITION_KEYS:
        return "positions"
    if key in RECORD_KEYS or key.startswith("record_"):
        return "records"
    return "raw_unmapped"


def normalize_player(record, source, pointer, key_map):
    normalized = {
        "identity": {},
        "profile": {},
        "team": {},
        "contract": {},
        "abilities": {},
        "skills": {},
        "positions": {},
        "records": {},
        "raw_unmapped": {},
        "native_evidence": {},
        "provenance": {"source": source, "json_pointer": pointer},
    }

    for key, value in record.items():
        section = classify_key(key)
        normalized[section][key] = value
        if key in key_map:
            evidence = {
                "field_candidate": key_map[key].get("field_candidate"),
                "confidence": key_map[key].get("confidence"),
                "offsets": split_evidence_list(key_map[key].get("native_offsets")),
                "widths": split_evidence_list(key_map[key].get("widths")),
            }
            normalized["native_evidence"][key] = evidence

    return normalized


def split_evidence_list(value):
    if isinstance(value, list):
        return value
    if not value:
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


def iter_input_files(path):
    if path.is_file():
        if path.suffix.lower() == ".json":
            yield path
        return

    for child in sorted(path.rglob("*.json")):
        if child.is_file():
            yield child


def load_json_file(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_sources(input_path):
    key_map = load_key_map()
    records = []
    scanned_files = []

    for path in iter_input_files(input_path):
        scanned_files.append(str(path))
        data = load_json_file(path)
        for pointer, value in walk_json(data):
            if is_player_candidate(value):
                records.append(normalize_player(value, str(path), pointer, key_map))

    return {
        "meta": {
            "stage": "stage5_player_json_normalizer",
            "input": str(input_path),
            "scanned_files": scanned_files,
            "player_record_count": len(records),
            "read_only": True,
            "key_offset_map": str(KEY_OFFSET_MAP) if KEY_OFFSET_MAP.exists() else None,
        },
        "players": records,
    }


def write_output(payload, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="Normalize offline player-shaped JSON into a read-only analysis artifact.")
    parser.add_argument("input", type=Path, help="JSON file or directory containing JSON files")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT, help="Output JSON path")
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = args.input.resolve()
    output_path = args.output.resolve()

    if not input_path.exists():
        raise SystemExit(f"Input does not exist: {input_path}")

    payload = normalize_sources(input_path)
    write_output(payload, output_path)

    print(f"Scanned files: {len(payload['meta']['scanned_files'])}")
    print(f"Player records: {payload['meta']['player_record_count']}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
