"""Stage 16: offline parser/validator for PES Club Manager save files.

Read-only: parses the JSON save files mapped in Stages 14-15 and
validates them against the native loader schemas. Never modifies inputs.

- SystemData.dat  (sys::SaveData::LoadSystemData  0x4db1508)
- UserInfoData.dat (sys::SaveData::LoadUserInfoData 0x4db63a4)
- OnSysData.dat    (sys::SaveData::LoadOnsysData   0x4dbc064)

Mirrors loader tolerance: unknown keys are reported, not rejected;
missing keys fall back to loader defaults.
"""

import argparse
import json
import sys
from pathlib import Path

LANG_MIN, LANG_MAX = 0, 14  # text_language / sound_language enum range (Stage 14)

SCHEMAS = {
    "SystemData.dat": {
        "SystemDataVersion": {"types": (int,), "desc": "save format version gate"},
        "text_language": {"types": (int,), "range": (LANG_MIN, LANG_MAX),
                          "default": 0, "desc": "text language enum 0-14"},
        "sound_language": {"types": (int,), "range": (LANG_MIN, LANG_MAX),
                           "default": 0, "desc": "sound language enum 0-14"},
        "vibration": {"types": (bool, int), "default": 0,
                      "desc": "vibration on/off"},
    },
    "UserInfoData.dat": {
        "auth_code": {"types": (str,), "desc": "sign-in auth code"},
        "user_code": {"types": (str,), "desc": "user code"},
        "user_id": {"types": (str,), "desc": "user id"},
        "account_status": {"types": (str, int), "desc": "account status (read path partially traced)"},
    },
    "OnSysData.dat": {
        "multi_stats_wait_upload_flag": {"types": (bool, int),
                                         "desc": "pending stats upload flag"},
        "match_id": {"types": (str, int), "desc": "match identifier"},
        "pid": {"types": (str, int), "desc": "local player id"},
        "peer_pid": {"types": (str, int), "desc": "peer player id"},
        "multi_stats_data": {"types": (dict, list, str),
                             "desc": "match stats payload"},
    },
}


def parse_file(path):
    """Returns (data_dict_or_None, warnings list)."""
    warnings = []
    try:
        # utf-8-sig tolerates a BOM (e.g. file edited on Windows); the
        # native loader path is unchanged, this only affects our read
        raw = Path(path).read_text(encoding="utf-8-sig")
    except OSError as e:
        return None, [f"cannot read file: {e}"]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        return None, [f"not valid JSON: {e}"]
    if not isinstance(data, dict):
        return None, [f"top-level JSON is {type(data).__name__}, expected object"]

    name = Path(path).name
    schema = SCHEMAS.get(name)
    if schema is None:
        return data, [f"unknown save file '{name}'; no schema, parsed raw"]
    for key, value in data.items():
        if key not in schema:
            warnings.append(f"unknown key '{key}' (loader ignores it)")
    for key, spec in schema.items():
        if key not in data:
            if "default" in spec:
                warnings.append(f"missing key '{key}'; loader default {spec['default']!r} applies")
            else:
                warnings.append(f"missing key '{key}' (no documented default)")
            continue
        value = data[key]
        # exact-type match: bool never matches int spec (bool is a subclass,
        # but type() is exact), mirroring the loader's strict typing
        ok = any(type(value) is t for t in spec["types"])
        if not ok:
            warnings.append(
                f"key '{key}' has type {type(value).__name__}, "
                f"expected {[t.__name__ for t in spec['types']]}")
            continue
        if "range" in spec and isinstance(value, int) and not isinstance(value, bool):
            lo, hi = spec["range"]
            if not (lo <= value <= hi):
                warnings.append(
                    f"key '{key}' value {value} out of loader range {lo}-{hi} "
                    f"(loader clamps/defaults)")
    return data, warnings


def main():
    ap = argparse.ArgumentParser(description="Stage 16 PESCM save-file parser/validator")
    ap.add_argument("paths", nargs="+", help=".dat save files or directories containing them")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON report")
    args = ap.parse_args()

    files = []
    for p in args.paths:
        p = Path(p)
        if p.is_dir():
            files += sorted(x for x in p.iterdir()
                            if x.is_file() and x.suffix == ".dat")
        elif p.is_file():
            files.append(p)
        else:
            print(f"skip: {p} not found", file=sys.stderr)
    if not files:
        print("no .dat files found", file=sys.stderr)
        return 1

    report = {}
    rc = 0
    for f in files:
        data, warnings = parse_file(f)
        report[str(f)] = {
            "keys": sorted(data.keys()) if isinstance(data, dict) else None,
            "warnings": warnings,
        }
        if warnings:
            rc = 2
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for fname, r in report.items():
            print(f"== {fname} ==")
            print(f"   keys: {r['keys']}")
            for w in r["warnings"]:
                print(f"   warn: {w}")
            if not r["warnings"]:
                print("   OK: matches native schema")
    return rc


if __name__ == "__main__":
    sys.exit(main())
