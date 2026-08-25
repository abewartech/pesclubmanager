import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "s6_01_cross_reference_player_schema.py"
NORMALIZED = ROOT / "analysis" / "stage5_player_json" / "normalized_players.json"
OUTPUT = ROOT / "analysis" / "stage6_player_cross_reference" / "player_field_coverage.json"


def main():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--normalized",
            str(NORMALIZED),
            "--json-output",
            str(OUTPUT),
        ],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise SystemExit(result.returncode)

    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    summary = data["summary"]
    assert summary["player_count"] == 2
    assert summary["observed_key_count"] >= 15
    assert summary["observed_with_offset_count"] >= 8
    assert summary["observed_unmapped_count"] == 1
    assert data["coverage"]["observed_unmapped"][0]["json_key"] == "mystery_flag"
    assert any(item["json_key"] == "salary" for item in data["coverage"]["observed_with_offset"])
    print("Stage 6 cross-reference assertions passed")


if __name__ == "__main__":
    main()
