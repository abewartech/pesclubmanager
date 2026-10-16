"""Stage 24: minimal stub server for PES Club Manager (dead game preservation).

Serves the /asj/*.php API endpoints on localhost. The game client can be
pointed here via the `localhost/asj/trunk/` server table entry (Stage 23)
or a hosts-file override.

Protocol (from static RE):
- POST https://<domain>/asj/<endpoint>.php
- Content-Type: application/x-www-form-urlencoded
- Body: param=<json>&addParam=...
- Request JSON: {"auth_code":"","ms_ver":0,"res_ver":0,"session_id":"",
                 "tutorial":0,"user_code":"","user_id":0}

This is a RESEARCH stub: it logs requests and returns minimal canned
responses. It does not emulate game logic. Enough to observe the boot
sequence and map which endpoints the client actually hits.

Usage:
    python3 scripts/s24_01_stub_server.py [--port 443] [--ssl-cert ...]

Note: the client uses HTTPS. For a real device test you need to either
(a) install a CA and MITM, or (b) patch the client to use http://.
Both are out of scope for this script.
"""

import argparse
import json
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


# Directory for masterdata stub files (Stage 31/32).
# Maps URL path under /masterdata/ to template files.
MASTERDATA_DIR = Path(__file__).parent.parent / "analysis" / "masterdata_stub" / "templates"


# Minimal canned responses per endpoint. The real server is dead;
# these let us observe the client's boot sequence.
# Schema inferred from client key strings (Stage 27).
# Boot sequence: AuthUser -> CheckUpdate -> Login -> top.php (Stage 33).
CANNED = {
    "auth_user.php": {
        "result": 0,
        "session_id": "stub-session-001",
        "auth_code": "stub-auth",
        "user_code": "stub-user",
        "user_id": 1,
    },
    "check_update.php": {
        "result": 0,
        "update_required": 0,
        "latest_ms_ver": 0,
        "latest_res_ver": 0,
    },
    "login.php": {
        "result": 0,
        "session_id": "stub-session-001",
        "tutorial": 0,
    },
    # Stage 34: team data stubs
    "get_team_info.php": {
        "result": 0,
        "team_id": 1001,
        "team_name": "Stub United",
        "formation": "4-4-2",
        "player_size": 3,
        "player_0_id": 1001,
        "player_0_name": "Striker Ronaldo",
        "player_0_position": "CF",
        "player_1_id": 1002,
        "player_1_name": "Defender Puyol",
        "player_1_position": "CB",
        "player_2_id": 1003,
        "player_2_name": "Midfielder Zidane",
        "player_2_position": "AMF",
    },
    # Stage 35: match setup stub (opponent data; sim is client-side)
    "get_match_info.php": {
        "result": 0,
        "match_id": 1,
        "home_team_id": 1001,
        "home_team_name": "Stub United",
        "away_team_id": 1002,
        "away_team_name": "Blue Warriors",
        "away_formation": "4-3-3",
        "away_player_size": 3,
        "away_player_0_id": 2001,
        "away_player_0_name": "Opponent Striker",
        "away_player_0_position": "CF",
        "away_player_1_id": 2002,
        "away_player_1_name": "Opponent Midfielder",
        "away_player_1_position": "CMF",
        "away_player_2_id": 2003,
        "away_player_2_name": "Opponent Defender",
        "away_player_2_position": "CB",
    },
    # Stage 38: training stub
    "do_training.php": {
        "result": 0,
        "training_id": 1,
        "player_id": 1001,
        "exp_gained": 100,
        "level_up": 0,
        "new_shot": 96,
        "new_speed": 91,
    },
    # Stage 39: scouting stub
    "do_scout_player.php": {
        "result": 0,
        "scout_id": 1,
        "player_id": 1004,
        "player_name": "Scouted Talent",
        "rarity": 3,
        "position": "CMF",
    },
    # Stage 40: contract stub
    "do_contract_player.php": {
        "result": 0,
        "contract_id": 1,
        "player_id": 1004,
        "player_name": "Scouted Talent",
        "team_id": 1001,
        "success": 1,
    },
    # Stage 41: item + facility + post-match stubs
    "do_item_purchase.php": {
        "result": 0,
        "item_id": 5001,
        "quantity": 1,
        "remaining_currency": 9990,
    },
    "do_item_use.php": {
        "result": 0,
        "item_id": 5001,
        "effect_applied": 1,
    },
    "do_construct_facility.php": {
        "result": 0,
        "facility_id": 7001,
        "facility_name": "Training Ground",
        "construction_time": 3600,
    },
    "submit_match_result.php": {
        "result": 0,
        "match_id": 1,
        "home_score": 2,
        "away_score": 1,
        "rewards": "exp=50",
    },
    "top.php": {
        "ms_ver": 0,
        "res_ver": 0,
        "session_id": "stub-session-001",
        "server_time": 0,
        "maintenance": 0,
        "first_dialog": 0,
        "use_facebook": 0,
        "news_notice_size": 0,
        "news_news_size": 0,
        "news_friendReq_size": 0,
        "news_friendGift_size": 0,
        "news_asso_size": 0,
        "news_data_size": 0,
        "banner_data_length": 0,
        "purchase_check": 0,
        "online_cup_count": 0,
    },
    "debug_login.php": {
        "result": 0,
        "session_id": "stub-debug-session",
        "user_code": "stub-user",
        "user_id": 1,
    },
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # quieter logging to stdout
        print(f"[{self.command} {self.path}] " + fmt % args)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        if length > 1_048_576:
            self.send_error(413, "request too large")
            return
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        params = urllib.parse.parse_qs(body)
        endpoint = self.path.rsplit("/", 1)[-1].split("?")[0]

        print(f"== POST /asj/{endpoint} ==")
        for k, v in params.items():
            preview = v[0][:200] if v else ""
            print(f"   {k} = {preview}")

        # try to parse the param JSON
        if "param" in params:
            try:
                pj = json.loads(params["param"][0])
                print(f"   param keys: {sorted(pj.keys())}")
            except (json.JSONDecodeError, IndexError):
                print("   param: not JSON")

        resp = CANNED.get(endpoint, {"result": 0})
        data = json.dumps(resp).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        # Masterdata stub: serve template files for /masterdata/* paths
        if "/masterdata/" in self.path:
            # Extract filename from path
            fname = self.path.rsplit("/", 1)[-1].split("?")[0]
            # Try .txt template
            for ext in ["", ".txt"]:
                fpath = MASTERDATA_DIR / (fname + ext)
                if fpath.is_file():
                    data = fpath.read_bytes()
                    print(f"== GET {self.path} -> {fpath.name} ({len(data)} bytes) ==")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
            print(f"== GET {self.path} -> 404 (no template) ==")
            self.send_error(404, "no masterdata template")
            return
        # serve a generic OK for other GET probes
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        data = b'{"result":0}'
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    ap = argparse.ArgumentParser(description="Stage 24 PESCM stub server")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    srv = HTTPServer((args.host, args.port), Handler)
    print(f"stub server on http://{args.host}:{args.port}/asj/ (Ctrl-C to stop)")
    print("Point the client here via hosts override or the localhost server-table entry.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
