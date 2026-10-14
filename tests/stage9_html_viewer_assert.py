import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "s9_01_html_viewer.py"
PLAYERS = ROOT / "analysis" / "stage5_player_json" / "normalized_players.json"
MAPPING = ROOT / "analysis" / "stage6" / "player_json_key_mapping.json"
OUT_DIR = ROOT / "analysis" / "stage9_player_view"
OUT_HTML = OUT_DIR / "player_db_viewer.html"

EXPECTED_UNKNOWN = {
    "LeftRight", "durability", "e_09", "energy",
    "er_home_10", "height", "stability", "weight",
}


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

    html_text = OUT_HTML.read_text(encoding="utf-8")
    players = json.loads(PLAYERS.read_text(encoding="utf-8"))["players"]
    mapping = json.loads(MAPPING.read_text(encoding="utf-8"))

    # 1. every fixture player is embedded
    assert len(players) >= 1, "no players in fixture artifact"
    for p in players:
        name = (p.get("profile") or {}).get("name", "")
        assert name and name in html_text, f"player {name!r} missing from viewer"

    # 2. all 105 mapped keys are embedded in the schema tab data
    assert len(mapping["mappings"]) == 105, "mapping key count changed"
    for m in mapping["mappings"]:
        assert m["json_key"] in html_text, f"key {m['json_key']!r} missing from viewer"

    # 3. unknown keys are listed, preserved as-is
    unknown = {u["json_key"] for u in mapping.get("unknown_json_keys", [])}
    assert unknown == EXPECTED_UNKNOWN, f"unknown key set changed: {unknown}"
    for key in EXPECTED_UNKNOWN:
        assert key in html_text, f"unknown key {key!r} missing from viewer"

    # 4. offline guarantee: no external URLs, no CDN
    for marker in ("http://", "https://", "cdn.", "//cdn"):
        assert marker not in html_text, f"viewer is not offline-safe: {marker!r} found"

    print(f"stage9 viewer OK: {len(players)} players, 105 keys, 8 unknowns, offline")


if __name__ == "__main__":
    main()
