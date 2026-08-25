import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "s6_02_trace_json_key_setters.py"
OUT_DIR = ROOT / "analysis" / "stage6"
MAPPING = OUT_DIR / "player_json_key_mapping.json"
CONFIDENCE = OUT_DIR / "mapping_confidence_report.csv"
NEW_FIELDS = OUT_DIR / "new_fields_candidates.json"
ADDRESS = OUT_DIR / "prepare_data_from_json_address.txt"


def main():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise SystemExit(result.returncode)

    data = json.loads(MAPPING.read_text(encoding="utf-8"))
    mappings = data["mappings"]
    by_key = {item["json_key"]: item for item in mappings}
    assert data["summary"]["prepare_function_count"] >= 1
    assert data["summary"]["json_key_count"] >= 100
    assert by_key["salary"]["confidence"] == "HIGH"
    assert by_key["salary"]["offsets"] == ["0x1e8"]
    assert by_key["salary"]["setter_functions"]
    assert by_key["param_speed"]["confidence"] == "MEDIUM"
    assert CONFIDENCE.exists()
    assert NEW_FIELDS.exists()
    assert ADDRESS.exists()
    print("Stage 6.2 JSON key mapping assertions passed")


if __name__ == "__main__":
    main()
