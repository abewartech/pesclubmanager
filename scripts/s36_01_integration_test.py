"""Stage 36: integration test simulating the client boot flow.

Hits the stub server endpoints in the order the client is expected
to call them:
  1. auth_user.php (AuthUser)
  2. check_update.php (CheckUpdate)
  3. login.php (Login)
  4. top.php (top menu data)
  5. get_team_info.php (GetTeamInfo)
  6. get_match_info.php (match setup)
  7. /masterdata/players (roster download)

Validates HTTP 200 and expected JSON keys for each step.
Run against a live stub server:
  python3 scripts/s36_01_integration_test.py [--port 8080]
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request


STEPS = [
    ("auth_user.php", {"session_id", "user_id"}),
    ("check_update.php", {"update_required"}),
    ("login.php", {"session_id"}),
    ("top.php", {"ms_ver", "res_ver"}),
    ("get_team_info.php", {"team_id", "team_name"}),
    ("get_match_info.php", {"match_id", "home_team_id", "away_team_id"}),
]


def post(base, endpoint, payload=None):
    data = urllib.parse.urlencode(
        {"param": json.dumps(payload or {})}
    ).encode()
    req = urllib.request.Request(
        f"{base}/asj/{endpoint}", data=data, method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status, json.loads(r.read())


def get(base, path):
    with urllib.request.urlopen(f"{base}{path}", timeout=10) as r:
        return r.status, r.read()[:200]


def main():
    ap = argparse.ArgumentParser(description="Stage 36 integration test")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    base = f"http://{args.host}:{args.port}"

    failed = 0
    for endpoint, required_keys in STEPS:
        try:
            status, body = post(base, endpoint)
            keys = set(body.keys())
            missing = required_keys - keys
            if status == 200 and not missing:
                print(f"PASS {endpoint}")
            else:
                print(f"FAIL {endpoint}: status={status} missing={missing}")
                failed += 1
        except Exception as e:
            print(f"FAIL {endpoint}: {e}")
            failed += 1

    # masterdata
    try:
        status, _ = get(base, "/asj/masterdata/players")
        print(f"{'PASS' if status == 200 else 'FAIL'} /masterdata/players")
        if status != 200:
            failed += 1
    except Exception as e:
        print(f"FAIL /masterdata/players: {e}")
        failed += 1

    print(f"\n{len(STEPS) + 1 - failed}/{len(STEPS) + 1} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
