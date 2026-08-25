"""
Stage 6 - Cross-reference normalized player JSON with native evidence.

This read-only tool measures how much of the Stage 5 normalized player shape is
supported by Stage 4 JSON-key and native-offset evidence.
"""
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_NORMALIZED = WORKSPACE / "analysis" / "stage5_player_json" / "normalized_players.json"
DEFAULT_KEY_MAP = WORKSPACE / "analysis" / "stage4_player_schema" / "player_json_key_offset_map.json"
DEFAULT_OUT_DIR = WORKSPACE / "analysis" / "stage6_player_cross_reference"
DEFAULT_JSON_OUT = DEFAULT_OUT_DIR / "player_field_coverage.json"
DEFAULT_CSV_OUT = DEFAULT_OUT_DIR / "player_field_coverage.csv"
DEFAULT_REPORT = WORKSPACE / "reports" / "stage6_player_cross_reference.md"

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


def split_list(value):
    if isinstance(value, list):
        return value
    if not value:
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_key_map(path):
    items = load_json(path)
    return {item["json_key"]: item for item in items if item.get("json_key")}


def collect_observed_keys(normalized):
    observed = {}
    occurrences = Counter()
    sections_by_key = defaultdict(set)

    for player_index, player in enumerate(normalized.get("players", [])):
        for section in PLAYER_SECTIONS:
            values = player.get(section, {})
            if not isinstance(values, dict):
                continue
            for key, value in values.items():
                occurrences[key] += 1
                sections_by_key[key].add(section)
                observed.setdefault(key, {"examples": []})
                if len(observed[key]["examples"]) < 3:
                    observed[key]["examples"].append(
                        {
                            "player_index": player_index,
                            "section": section,
                            "value": value,
                            "source": player.get("provenance", {}).get("source"),
                            "json_pointer": player.get("provenance", {}).get("json_pointer"),
                        }
                    )

    for key, item in observed.items():
        item["json_key"] = key
        item["occurrences"] = occurrences[key]
        item["sections"] = sorted(sections_by_key[key])

    return observed


def evidence_for(key, key_map):
    item = key_map.get(key)
    if not item:
        return None
    offsets = split_list(item.get("native_offsets"))
    widths = split_list(item.get("widths"))
    return {
        "field_candidate": item.get("field_candidate"),
        "category": item.get("category"),
        "confidence": item.get("confidence"),
        "offsets": offsets,
        "widths": widths,
        "mapping_reason": item.get("mapping_reason"),
    }


def build_observed_item(key, observed_item, key_map):
    evidence = evidence_for(key, key_map)
    result = {
        "json_key": key,
        "sections": observed_item["sections"],
        "occurrences": observed_item["occurrences"],
        "examples": observed_item["examples"],
    }
    if evidence:
        result.update(evidence)
    return result


def build_cross_reference(normalized, key_map):
    observed = collect_observed_keys(normalized)
    coverage = {
        "observed_with_offset": [],
        "observed_without_offset": [],
        "observed_unmapped": [],
        "native_unobserved": [],
    }

    for key in sorted(observed):
        item = build_observed_item(key, observed[key], key_map)
        evidence = evidence_for(key, key_map)
        if evidence and evidence["offsets"]:
            coverage["observed_with_offset"].append(item)
        elif evidence:
            coverage["observed_without_offset"].append(item)
        else:
            coverage["observed_unmapped"].append(item)

    for key in sorted(set(key_map) - set(observed)):
        evidence = evidence_for(key, key_map)
        coverage["native_unobserved"].append({"json_key": key, **evidence})

    summary = {
        "player_count": len(normalized.get("players", [])),
        "observed_key_count": len(observed),
        "mapped_key_count": len(key_map),
        "observed_with_offset_count": len(coverage["observed_with_offset"]),
        "observed_without_offset_count": len(coverage["observed_without_offset"]),
        "observed_unmapped_count": len(coverage["observed_unmapped"]),
        "native_unobserved_count": len(coverage["native_unobserved"]),
        "read_only": True,
    }

    return {
        "summary": summary,
        "sources": {
            "normalized_players": normalized.get("meta", {}).get("input"),
            "key_offset_map": str(DEFAULT_KEY_MAP),
        },
        "coverage": coverage,
    }


def write_json(payload, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(payload, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for bucket, items in payload["coverage"].items():
        for item in items:
            rows.append(
                {
                    "bucket": bucket,
                    "json_key": item.get("json_key", ""),
                    "sections": ", ".join(item.get("sections", [])),
                    "occurrences": item.get("occurrences", ""),
                    "field_candidate": item.get("field_candidate", ""),
                    "category": item.get("category", ""),
                    "confidence": item.get("confidence", ""),
                    "offsets": ", ".join(item.get("offsets", [])),
                    "widths": ", ".join(item.get("widths", [])),
                    "mapping_reason": item.get("mapping_reason", ""),
                }
            )

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "bucket",
                "json_key",
                "sections",
                "occurrences",
                "field_candidate",
                "category",
                "confidence",
                "offsets",
                "widths",
                "mapping_reason",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(items, columns, limit=40):
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for item in items[:limit]:
        row = []
        for column in columns:
            value = item.get(column, "")
            if isinstance(value, list):
                value = ", ".join(str(part) for part in value)
            row.append(str(value) if value not in (None, "") else "-")
        lines.append("| " + " | ".join(row) + " |")
    if len(items) > limit:
        lines.append(f"| ... | {len(items) - limit} more rows omitted | | | | | | | |")
    return "\n".join(lines)


def write_report(payload, path, json_out, csv_out):
    summary = payload["summary"]
    coverage = payload["coverage"]
    lines = [
        "# Stage 6 Player Cross-Reference",
        "",
        "## Purpose",
        "",
        "Stage 6 compares Stage 5 normalized player-shaped JSON with Stage 4 native key/offset evidence. This is a read-only validation step, not an editor or binary file parser.",
        "",
        "## Summary",
        "",
        f"- Player records: {summary['player_count']}",
        f"- Observed unique keys: {summary['observed_key_count']}",
        f"- Stage 4 mapped keys: {summary['mapped_key_count']}",
        f"- Observed keys with offset evidence: {summary['observed_with_offset_count']}",
        f"- Observed keys without offset evidence: {summary['observed_without_offset_count']}",
        f"- Observed unmapped keys: {summary['observed_unmapped_count']}",
        f"- Native mapped keys not observed in Stage 5 input: {summary['native_unobserved_count']}",
        "",
        "## Outputs",
        "",
        f"- JSON: `{json_out}`",
        f"- CSV: `{csv_out}`",
        "",
        "## Observed With Offset",
        "",
        markdown_table(
            coverage["observed_with_offset"],
            ["json_key", "sections", "occurrences", "field_candidate", "offsets", "widths", "confidence"],
        ),
        "",
        "## Observed Without Offset",
        "",
        markdown_table(
            coverage["observed_without_offset"],
            ["json_key", "sections", "occurrences", "field_candidate", "category", "confidence", "mapping_reason"],
        ),
        "",
        "## Observed Unmapped",
        "",
        markdown_table(
            coverage["observed_unmapped"],
            ["json_key", "sections", "occurrences"],
        ),
        "",
        "## Interpretation",
        "",
        "- `observed_with_offset` is the strongest current evidence path: the key exists in normalized records and has native offset support.",
        "- `observed_without_offset` usually means grouped data such as ability, skill, or position arrays, or native strings whose storage still needs tracing.",
        "- `observed_unmapped` must be preserved and reviewed; do not discard these fields.",
        "- `native_unobserved` shows known Stage 4 fields that did not appear in the current Stage 5 input.",
        "",
        "## Safety Boundary",
        "",
        "This report is derived from local analysis artifacts only. It does not modify game data, containers, saves, binaries, or network state.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="Cross-reference Stage 5 normalized players with Stage 4 native evidence.")
    parser.add_argument("--normalized", type=Path, default=DEFAULT_NORMALIZED)
    parser.add_argument("--key-map", type=Path, default=DEFAULT_KEY_MAP)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV_OUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main():
    args = parse_args()
    normalized_path = args.normalized.resolve()
    key_map_path = args.key_map.resolve()
    json_out = args.json_output.resolve()
    csv_out = args.csv_output.resolve()
    report = args.report.resolve()

    if not normalized_path.exists():
        raise SystemExit(f"Normalized players file does not exist: {normalized_path}")
    if not key_map_path.exists():
        raise SystemExit(f"Key map file does not exist: {key_map_path}")

    normalized = load_json(normalized_path)
    key_map = load_key_map(key_map_path)
    payload = build_cross_reference(normalized, key_map)
    payload["sources"]["normalized_players"] = str(normalized_path)
    payload["sources"]["key_offset_map"] = str(key_map_path)

    write_json(payload, json_out)
    write_csv(payload, csv_out)
    write_report(payload, report, json_out, csv_out)

    summary = payload["summary"]
    print(f"Player records: {summary['player_count']}")
    print(f"Observed keys: {summary['observed_key_count']}")
    print(f"Observed with offsets: {summary['observed_with_offset_count']}")
    print(f"Observed without offsets: {summary['observed_without_offset_count']}")
    print(f"Observed unmapped: {summary['observed_unmapped_count']}")
    print(f"Native unobserved: {summary['native_unobserved_count']}")
    print(f"JSON output: {json_out}")
    print(f"CSV output: {csv_out}")
    print(f"Report: {report}")


if __name__ == "__main__":
    main()
