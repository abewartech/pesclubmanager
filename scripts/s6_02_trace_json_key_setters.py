"""Build Stage 6.2 JSON-key-to-native-offset confidence evidence.

This is a static artifact combiner. It consumes Stage 4 JSON outputs and the
Stage 4 offset report; it does not execute, instrument, or modify a binary.
"""
import csv
import json
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal, Protocol, TypeAlias

JsonScalar: TypeAlias = None | bool | int | float | str
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonRecord: TypeAlias = dict[str, JsonValue]


CsvField: TypeAlias = Literal[
    "evidence_scope",
    "json_key",
    "field_candidate",
    "confidence",
    "offsets",
    "widths",
    "setter_functions",
    "accessor_functions",
    "mapping_reason",
]


class CsvWriter(Protocol):
    def writerow(self, rowdict: dict[CsvField, str]) -> int: ...

    def writerows(self, rowdicts: Iterable[dict[CsvField, str]]) -> None: ...


@dataclass(frozen=True, slots=True)
class OffsetRecord:
    offset_hex: str
    reads: tuple[str, ...]
    writes: tuple[str, ...]
    addresses: tuple[str, ...]
    widths: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NativeField:
    field_candidate: str
    offsets: tuple[OffsetRecord, ...]


@dataclass(frozen=True, slots=True)
class NativeEvidence:
    offsets: tuple[str, ...]
    widths: tuple[str, ...]
    setter_functions: tuple[str, ...]
    accessor_functions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class KeyMapItem:
    json_key: str
    category: str
    field_candidate: str
    mapping_reason: str


@dataclass(frozen=True, slots=True)
class PrepareEvidence:
    function_address: str
    instruction_address: str
    literal_address: str


@dataclass(frozen=True, slots=True)
class JsonKeyMapping:
    json_key: str
    category: str
    field_candidate: str
    confidence: str
    offsets: tuple[str, ...]
    widths: tuple[str, ...]
    setter_functions: tuple[str, ...]
    accessor_functions: tuple[str, ...]
    mapping_reason: str
    prepare_evidence: tuple[PrepareEvidence, ...]


@dataclass(frozen=True, slots=True)
class NewFieldCandidate:
    field_candidate: str
    offsets: tuple[str, ...]
    widths: tuple[str, ...]
    setter_functions: tuple[str, ...]
    accessor_functions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MappingOutput:
    mappings: tuple[JsonKeyMapping, ...]
    unknown_json_keys: tuple[JsonKeyMapping, ...]
    new_fields: tuple[NewFieldCandidate, ...]
    prepare_addresses: tuple[str, ...]


WORKSPACE: Final = Path(__file__).resolve().parents[1]
STAGE4_DIR: Final = WORKSPACE / "analysis" / "stage4_player_schema"
JSON_KEYS: Final = STAGE4_DIR / "parameter_player_define_json_keys.json"
KEY_MAP: Final = STAGE4_DIR / "player_json_key_offset_map.json"
OFFSETS: Final = STAGE4_DIR / "parameter_player_define_offsets.json"
OFFSET_REPORT: Final = WORKSPACE / "reports" / "stage4_player_offset_schema.md"
OUT_DIR: Final = WORKSPACE / "analysis" / "stage6"
MAPPING_OUT: Final = OUT_DIR / "player_json_key_mapping.json"
CSV_OUT: Final = OUT_DIR / "mapping_confidence_report.csv"
NEW_FIELDS_OUT: Final = OUT_DIR / "new_fields_candidates.json"
ADDRESS_OUT: Final = OUT_DIR / "prepare_data_from_json_address.txt"
REPORT_OUT: Final = WORKSPACE / "reports" / "stage6_json_key_mapping_report.md"
CSV_FIELDS: Final[tuple[CsvField, ...]] = (
    "evidence_scope",
    "json_key",
    "field_candidate",
    "confidence",
    "offsets",
    "widths",
    "setter_functions",
    "accessor_functions",
    "mapping_reason",
)


def load_json(path: Path) -> JsonValue:
    return normalize_json_value(json.loads(path.read_text(encoding="utf-8")))


def normalize_json_value(value: JsonValue) -> JsonValue:
    return value


def require_record(value: JsonValue, context: str) -> JsonRecord:
    if isinstance(value, dict):
        return value
    raise SystemExit(f"Expected a JSON object for {context}")


def require_records(value: JsonValue, context: str) -> list[JsonRecord]:
    if not isinstance(value, list):
        raise SystemExit(f"Expected a JSON list for {context}")
    return [require_record(item, context) for item in value]


def optional_records(record: JsonRecord, key: str, context: str) -> list[JsonRecord]:
    value = record.get(key)
    if value is None:
        return []
    return require_records(value, f"{context}.{key}")


def required_string(record: JsonRecord, key: str, context: str) -> str:
    value = record.get(key)
    if isinstance(value, str):
        return value
    raise SystemExit(f"Expected a string for {context}.{key}")


def optional_string(record: JsonRecord, key: str, context: str) -> str:
    value = record.get(key)
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    raise SystemExit(f"Expected a string for {context}.{key}")


def optional_strings(record: JsonRecord, key: str, context: str) -> tuple[str, ...]:
    value = record.get(key)
    if value is None:
        return ()
    if not isinstance(value, list):
        raise SystemExit(f"Expected a string list for {context}.{key}")
    strings: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise SystemExit(f"Expected a string list for {context}.{key}")
        strings.append(item)
    return tuple(strings)


def sorted_unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted({value for value in values if value}))


def parse_native_fields(value: JsonValue) -> tuple[NativeField, ...]:
    fields: list[NativeField] = []
    for item in require_records(value, "native offsets"):
        records: list[OffsetRecord] = []
        for offset in optional_records(item, "offsets", "native field"):
            records.append(
                OffsetRecord(
                    offset_hex=optional_string(offset, "offset_hex", "native offset"),
                    reads=optional_strings(offset, "reads", "native offset"),
                    writes=optional_strings(offset, "writes", "native offset"),
                    addresses=optional_strings(offset, "addresses", "native offset"),
                    widths=optional_strings(offset, "widths", "native offset"),
                )
            )
        fields.append(
            NativeField(
                field_candidate=required_string(item, "field_candidate", "native field"),
                offsets=tuple(records),
            )
        )
    return tuple(fields)


def parse_key_map(value: JsonValue) -> tuple[KeyMapItem, ...]:
    items: list[KeyMapItem] = []
    for item in require_records(value, "key map"):
        items.append(
            KeyMapItem(
                json_key=required_string(item, "json_key", "key map item"),
                category=optional_string(item, "category", "key map item"),
                field_candidate=optional_string(item, "field_candidate", "key map item"),
                mapping_reason=optional_string(item, "mapping_reason", "key map item"),
            )
        )
    return tuple(items)


def parse_prepare_evidence(value: JsonValue) -> tuple[dict[str, tuple[PrepareEvidence, ...]], tuple[str, ...]]:
    payload = require_record(value, "PrepareDataFromJson literals")
    by_key: dict[str, list[PrepareEvidence]] = {}
    addresses: list[str] = []
    for item in optional_records(payload, "PrepareDataFromJson", "JSON literals"):
        literal = optional_string(item, "literal", "PrepareDataFromJson literal")
        evidence = PrepareEvidence(
            function_address=optional_string(item, "function_address", "PrepareDataFromJson literal"),
            instruction_address=optional_string(item, "instruction_address", "PrepareDataFromJson literal"),
            literal_address=optional_string(item, "literal_address", "PrepareDataFromJson literal"),
        )
        addresses.append(evidence.function_address)
        by_key.setdefault(literal, []).append(evidence)
    return {key: tuple(items) for key, items in by_key.items()}, sorted_unique(addresses)


def collect_functions(offsets: Sequence[OffsetRecord], prefixes: tuple[str, ...]) -> tuple[str, ...]:
    names: list[str] = []
    for offset in offsets:
        names.extend(offset.reads)
        names.extend(offset.writes)
        names.extend(offset.addresses)
    return sorted_unique(name for name in names if name.startswith(prefixes))


def build_offset_index(fields: Sequence[NativeField]) -> dict[str, NativeEvidence]:
    index: dict[str, NativeEvidence] = {}
    for field in fields:
        index[field.field_candidate] = NativeEvidence(
            offsets=sorted_unique(offset.offset_hex for offset in field.offsets),
            widths=sorted_unique(width for offset in field.offsets for width in offset.widths),
            setter_functions=collect_functions(field.offsets, ("Set",)),
            accessor_functions=collect_functions(field.offsets, ("Get", "Is")),
        )
    return index


def confidence_for(field_candidate: str, offsets: Sequence[str]) -> str:
    if not field_candidate:
        return "UNKNOWN"
    if offsets:
        return "HIGH"
    return "MEDIUM"


def build_mappings(
    key_map_items: Sequence[KeyMapItem],
    offset_index: dict[str, NativeEvidence],
    prepare_by_key: dict[str, tuple[PrepareEvidence, ...]],
) -> tuple[JsonKeyMapping, ...]:
    mappings: list[JsonKeyMapping] = []
    empty_native = NativeEvidence((), (), (), ())
    for item in key_map_items:
        native = offset_index.get(item.field_candidate, empty_native)
        mappings.append(
            JsonKeyMapping(
                json_key=item.json_key,
                category=item.category,
                field_candidate=item.field_candidate,
                confidence=confidence_for(item.field_candidate, native.offsets),
                offsets=native.offsets,
                widths=native.widths,
                setter_functions=native.setter_functions,
                accessor_functions=native.accessor_functions,
                mapping_reason=item.mapping_reason,
                prepare_evidence=prepare_by_key.get(item.json_key, ()),
            )
        )
    return tuple(sorted(mappings, key=lambda item: item.json_key))


def build_new_fields(
    offset_index: dict[str, NativeEvidence], mappings: Sequence[JsonKeyMapping]
) -> tuple[NewFieldCandidate, ...]:
    mapped_fields = {mapping.field_candidate for mapping in mappings if mapping.field_candidate}
    return tuple(
        NewFieldCandidate(
            field_candidate=field_candidate,
            offsets=evidence.offsets,
            widths=evidence.widths,
            setter_functions=evidence.setter_functions,
            accessor_functions=evidence.accessor_functions,
        )
        for field_candidate, evidence in sorted(offset_index.items())
        if field_candidate not in mapped_fields
    )


def build_output(
    mappings: tuple[JsonKeyMapping, ...],
    new_fields: tuple[NewFieldCandidate, ...],
    prepare_addresses: tuple[str, ...],
) -> MappingOutput:
    unknown = tuple(mapping for mapping in mappings if mapping.confidence == "UNKNOWN")
    return MappingOutput(mappings, unknown, new_fields, prepare_addresses)


def evidence_json(evidence: PrepareEvidence) -> JsonRecord:
    return {
        "function_address": evidence.function_address,
        "instruction_address": evidence.instruction_address,
        "literal_address": evidence.literal_address,
    }


def mapping_json(mapping: JsonKeyMapping) -> JsonRecord:
    return {
        "json_key": mapping.json_key,
        "category": mapping.category,
        "field_candidate": mapping.field_candidate,
        "confidence": mapping.confidence,
        "offsets": list(mapping.offsets),
        "widths": list(mapping.widths),
        "setter_functions": list(mapping.setter_functions),
        "accessor_functions": list(mapping.accessor_functions),
        "mapping_reason": mapping.mapping_reason,
        "prepare_data_from_json_evidence": [evidence_json(item) for item in mapping.prepare_evidence],
    }


def new_field_json(field: NewFieldCandidate) -> JsonRecord:
    return {
        "field_candidate": field.field_candidate,
        "confidence": "LOW",
        "offsets": list(field.offsets),
        "widths": list(field.widths),
        "setter_functions": list(field.setter_functions),
        "accessor_functions": list(field.accessor_functions),
        "reason": "native offset evidence has no Stage 4 JSON-key correlation",
    }


def payload_json(output: MappingOutput) -> JsonRecord:
    confidence_counts: Counter[str] = Counter(mapping.confidence for mapping in output.mappings)
    counts: JsonRecord = {key: value for key, value in sorted(confidence_counts.items())}
    return {
        "summary": {
            "prepare_function_count": len(output.prepare_addresses),
            "json_key_count": len(output.mappings),
            "mapped_json_key_count": len(output.mappings) - len(output.unknown_json_keys),
            "unknown_json_key_count": len(output.unknown_json_keys),
            "native_offset_fields_without_json_key_count": len(output.new_fields),
            "confidence_counts": counts,
            "read_only": True,
        },
        "sources": {
            "json_keys": str(JSON_KEYS.relative_to(WORKSPACE)),
            "key_offset_map": str(KEY_MAP.relative_to(WORKSPACE)),
            "offsets": str(OFFSETS.relative_to(WORKSPACE)),
            "offset_report": str(OFFSET_REPORT.relative_to(WORKSPACE)),
            "prepare_data_from_json_addresses": list(output.prepare_addresses),
        },
        "mappings": [mapping_json(mapping) for mapping in output.mappings],
        "unknown_json_keys": [mapping_json(mapping) for mapping in output.unknown_json_keys],
    }


def write_json(value: JsonValue, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def csv_row(
    scope: str,
    json_key: str,
    field_candidate: str,
    confidence: str,
    offsets: Sequence[str],
    widths: Sequence[str],
    setter_functions: Sequence[str],
    accessor_functions: Sequence[str],
    mapping_reason: str,
) -> dict[CsvField, str]:
    return {
        "evidence_scope": scope,
        "json_key": json_key,
        "field_candidate": field_candidate,
        "confidence": confidence,
        "offsets": ", ".join(offsets),
        "widths": ", ".join(widths),
        "setter_functions": ", ".join(setter_functions),
        "accessor_functions": ", ".join(accessor_functions),
        "mapping_reason": mapping_reason,
    }


def write_csv(output: MappingOutput, path: Path) -> None:
    rows: list[dict[CsvField, str]] = [
        csv_row(
            "json_key_mapping",
            mapping.json_key,
            mapping.field_candidate,
            mapping.confidence,
            mapping.offsets,
            mapping.widths,
            mapping.setter_functions,
            mapping.accessor_functions,
            mapping.mapping_reason,
        )
        for mapping in output.mappings
    ]
    rows.extend(
        csv_row(
            "native_field_without_json_key",
            "",
            field.field_candidate,
            "LOW",
            field.offsets,
            field.widths,
            field.setter_functions,
            field.accessor_functions,
            "native offset evidence has no Stage 4 JSON-key correlation",
        )
        for field in output.new_fields
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        write_csv_rows(csv.DictWriter(handle, fieldnames=CSV_FIELDS), rows)


def write_csv_rows(writer: CsvWriter, rows: Iterable[dict[CsvField, str]]) -> None:
    _ = writer.writerow({field: field for field in CSV_FIELDS})
    writer.writerows(rows)


def markdown_table(rows: Sequence[Sequence[str]], columns: Sequence[str], limit: int = 30) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(value or "-" for value in row) + " |")
    if len(rows) > limit:
        lines.append(f"| ... | {len(rows) - limit} more rows omitted | | | |")
    return "\n".join(lines)


def write_report(output: MappingOutput) -> None:
    high = tuple(mapping for mapping in output.mappings if mapping.confidence == "HIGH")
    high_rows = [
        (
            mapping.json_key,
            mapping.field_candidate,
            ", ".join(mapping.offsets),
            ", ".join(mapping.setter_functions),
            ", ".join(mapping.accessor_functions),
        )
        for mapping in high
    ]
    native_rows = [
        (
            field.field_candidate,
            ", ".join(field.offsets),
            ", ".join(field.setter_functions),
            ", ".join(field.accessor_functions),
        )
        for field in output.new_fields
    ]
    lines = [
        "# Stage 6.2 JSON Key Mapping",
        "",
        "## Scope",
        "",
        "This read-only static artifact combines Stage 4 JSON literal references, key correlations, native accessor offset evidence, and the Stage 4 offset report. It does not trace code at runtime, instrument processes, or establish an on-disk player layout.",
        "",
        "## Confidence Rules",
        "",
        "- `HIGH`: a JSON key has a direct native field candidate and one or more concrete in-memory offsets.",
        "- `MEDIUM`: grouped ability/skill/position evidence, or a direct field candidate without a recovered offset.",
        "- `LOW`: a native offset field has no Stage 4 JSON-key correlation; these are separate candidates, not mappings.",
        "- `UNKNOWN`: a JSON-like key has no field mapping and remains preserved for later analysis.",
        "",
        "## Summary",
        "",
        f"- PrepareDataFromJson functions: {len(output.prepare_addresses)}",
        f"- JSON keys: {len(output.mappings)}",
        f"- JSON keys with candidates: {len(output.mappings) - len(output.unknown_json_keys)}",
        f"- Unknown JSON keys: {len(output.unknown_json_keys)}",
        f"- Native-only field candidates: {len(output.new_fields)}",
        "",
        "## High-Confidence JSON Mappings",
        "",
        markdown_table(high_rows, ["json_key", "field_candidate", "offsets", "setter_functions", "accessor_functions"]),
        "",
        "## Unknown JSON Keys",
        "",
        ", ".join(f"`{mapping.json_key}`" for mapping in output.unknown_json_keys) or "None.",
        "",
        "## Native-Only Candidate Fields",
        "",
        markdown_table(native_rows, ["field_candidate", "offsets", "setter_functions", "accessor_functions"]),
        "",
        "## Outputs",
        "",
        f"- `{MAPPING_OUT.relative_to(WORKSPACE)}`",
        f"- `{CSV_OUT.relative_to(WORKSPACE)}`",
        f"- `{NEW_FIELDS_OUT.relative_to(WORKSPACE)}`",
        f"- `{ADDRESS_OUT.relative_to(WORKSPACE)}`",
        "",
        "## Boundary",
        "",
        "Offsets in this report are candidate in-memory backing-data offsets recovered from accessors. They are not file offsets, a player binary table format, or authority to edit save data or game assets.",
    ]
    _ = REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    for path in (JSON_KEYS, KEY_MAP, OFFSETS, OFFSET_REPORT):
        if not path.exists():
            raise SystemExit(f"Required static evidence is missing: {path}")
    if "candidate in-memory backing-data offsets" not in OFFSET_REPORT.read_text(encoding="utf-8"):
        raise SystemExit(f"Static offset-report scope is not recognized: {OFFSET_REPORT}")
    offset_index = build_offset_index(parse_native_fields(load_json(OFFSETS)))
    prepare_by_key, prepare_addresses = parse_prepare_evidence(load_json(JSON_KEYS))
    mappings = build_mappings(parse_key_map(load_json(KEY_MAP)), offset_index, prepare_by_key)
    output = build_output(mappings, build_new_fields(offset_index, mappings), prepare_addresses)

    write_json(payload_json(output), MAPPING_OUT)
    write_csv(output, CSV_OUT)
    write_json([new_field_json(field) for field in output.new_fields], NEW_FIELDS_OUT)
    _ = ADDRESS_OUT.write_text("\n".join(output.prepare_addresses) + "\n", encoding="utf-8")
    write_report(output)

    print(f"PrepareDataFromJson functions: {len(output.prepare_addresses)}")
    print(f"JSON keys: {len(output.mappings)}")
    print(f"Mapping output: {MAPPING_OUT}")
    print(f"Confidence CSV: {CSV_OUT}")
    print(f"Native-only candidates: {NEW_FIELDS_OUT}")
    print(f"Report: {REPORT_OUT}")


if __name__ == "__main__":
    main()
