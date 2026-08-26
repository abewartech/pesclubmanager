"""Render normalized offline player artifacts without modifying source inputs."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_NORMALIZED = WORKSPACE / "analysis" / "stage5_player_json" / "normalized_players.json"
PLAYER_SECTIONS = (
    "identity",
    "profile",
    "team",
    "contract",
    "abilities",
    "skills",
    "positions",
    "records",
    "raw_unmapped",
)
ROW_FIELDS = (
    "index",
    "name",
    "serial_id",
    "master_id",
    "position",
    "original_team_id",
    "salary",
    "mapping_summary",
)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_normalized(path):
    payload = load_json(path)
    if not isinstance(payload, dict) or not isinstance(payload.get("players"), list):
        raise SystemExit(f"Normalized input must be a Stage 5 player artifact: {path}")
    return payload


def load_mapping(path):
    payload = load_json(path)
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        items = payload.get("mappings", [])
    else:
        raise SystemExit(f"Mapping input must be a Stage 4 list or Stage 6.2 mapping artifact: {path}")
    if not isinstance(items, list):
        raise SystemExit(f"Mapping input has no mapping list: {path}")
    return {item["json_key"]: item for item in items if isinstance(item, dict) and item.get("json_key")}


def section_value(player, section, key):
    values = player.get(section, {})
    if isinstance(values, dict):
        return values.get(key, "")
    return ""


def player_position(player):
    position = section_value(player, "profile", "position")
    if position:
        return position
    positions = player.get("positions", {})
    if isinstance(positions, dict):
        return ", ".join(sorted(positions))
    return ""


def player_keys(player):
    for section in PLAYER_SECTIONS:
        values = player.get(section, {})
        if isinstance(values, dict):
            yield from values


def split_evidence(value):
    if isinstance(value, list):
        return value
    if not value:
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


def mapping_evidence(player, mapping_index):
    evidence = []
    confidence_counts = Counter()
    for key in sorted(set(player_keys(player))):
        item = mapping_index.get(key)
        if item:
            confidence = item.get("confidence", "UNKNOWN").upper()
            record = {
                "json_key": key,
                "field_candidate": item.get("field_candidate", ""),
                "confidence": confidence,
                "offsets": split_evidence(item.get("offsets", item.get("native_offsets", []))),
                "widths": split_evidence(item.get("widths", [])),
                "setter_functions": item.get("setter_functions", []),
                "accessor_functions": item.get("accessor_functions", []),
            }
        else:
            confidence = "UNKNOWN"
            record = {
                "json_key": key,
                "field_candidate": "",
                "confidence": confidence,
                "offsets": [],
                "widths": [],
                "setter_functions": [],
                "accessor_functions": [],
            }
        confidence_counts[confidence] += 1
        evidence.append(record)
    summary = ", ".join(
        f"{confidence}:{count}" for confidence, count in sorted(confidence_counts.items())
    )
    return evidence, summary


def render_players(players, mapping_index):
    rows = []
    for index, player in enumerate(players, start=1):
        row = {
            "index": index,
            "name": section_value(player, "profile", "name"),
            "serial_id": section_value(player, "identity", "serial_id"),
            "master_id": section_value(player, "identity", "master_id"),
            "position": player_position(player),
            "original_team_id": section_value(player, "team", "original_team_id"),
            "salary": section_value(player, "contract", "salary"),
            "mapping_summary": "",
            "mapping_evidence": [],
        }
        if mapping_index is not None:
            evidence, summary = mapping_evidence(player, mapping_index)
            row["mapping_evidence"] = evidence
            row["mapping_summary"] = summary
        rows.append(row)
    return rows


def display_value(value):
    return str(value) if value not in (None, "") else "-"


def terminal_table(rows, include_mapping):
    columns = [
        ("#", "index"),
        ("Name", "name"),
        ("Serial ID", "serial_id"),
        ("Master ID", "master_id"),
        ("Position", "position"),
        ("Team ID", "original_team_id"),
        ("Salary", "salary"),
    ]
    if include_mapping:
        columns.append(("Mapping", "mapping_summary"))
    widths = {
        key: max(len(title), *(len(display_value(row[key])) for row in rows))
        for title, key in columns
    }
    header = " | ".join(title.ljust(widths[key]) for title, key in columns)
    divider = "-+-".join("-" * widths[key] for _, key in columns)
    body = [
        " | ".join(display_value(row[key]).ljust(widths[key]) for _, key in columns)
        for row in rows
    ]
    return "\n".join([header, divider, *body])


def write_csv(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ROW_FIELDS)
        writer.writeheader()
        writer.writerows({field: row[field] for field in ROW_FIELDS} for row in rows)


def write_json_output(rows, normalized_path, mapping_path, path):
    payload = {
        "meta": {
            "normalized_input": str(normalized_path),
            "mapping_input": str(mapping_path) if mapping_path else None,
            "player_count": len(rows),
            "read_only": True,
        },
        "players": rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def assert_outputs_are_derived(output_paths, source_paths):
    source_resolved = {path.resolve() for path in source_paths}
    for path in output_paths:
        if path and path.resolve() in source_resolved:
            raise SystemExit(f"Refusing to overwrite a read-only source input: {path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Render Stage 5 normalized players without modifying source inputs."
    )
    parser.add_argument("normalized", nargs="?", type=Path, help="Stage 5 normalized player JSON")
    parser.add_argument("--normalized", dest="normalized_option", type=Path, help="Stage 5 normalized player JSON")
    parser.add_argument("--mapping", type=Path, help="Optional Stage 4 or Stage 6.2 mapping JSON")
    parser.add_argument("--csv-output", type=Path, help="Optional derived CSV output path")
    parser.add_argument("--json-output", type=Path, help="Optional derived JSON output path")
    args = parser.parse_args()
    if args.normalized and args.normalized_option:
        parser.error("use either the positional normalized input or --normalized, not both")
    return args


def main():
    args = parse_args()
    normalized_path = (args.normalized_option or args.normalized or DEFAULT_NORMALIZED).resolve()
    mapping_path = args.mapping.resolve() if args.mapping else None
    if not normalized_path.exists():
        raise SystemExit(f"Normalized input does not exist: {normalized_path}")
    if mapping_path and not mapping_path.exists():
        raise SystemExit(f"Mapping input does not exist: {mapping_path}")
    assert_outputs_are_derived(
        (args.csv_output, args.json_output),
        (normalized_path, *([mapping_path] if mapping_path else [])),
    )

    normalized = load_normalized(normalized_path)
    mapping_index = load_mapping(mapping_path) if mapping_path else None
    rows = render_players(normalized["players"], mapping_index)
    print(terminal_table(rows, mapping_index is not None))
    print(f"\nPlayer records: {len(rows)}")
    print("Read-only: source inputs were not modified")

    if args.csv_output:
        write_csv(rows, args.csv_output.resolve())
        print(f"CSV output: {args.csv_output.resolve()}")
    if args.json_output:
        write_json_output(rows, normalized_path, mapping_path, args.json_output.resolve())
        print(f"JSON output: {args.json_output.resolve()}")


if __name__ == "__main__":
    main()
