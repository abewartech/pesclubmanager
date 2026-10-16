"""Stage 42: accurate mock client simulating the real game client.

Unlike the integration test (which just hits endpoints), this mock:
- Maintains session state across requests (auth_code, session_id, user_id)
- Sends proper param JSON per Stage 23 format
- Follows request dependencies (team_id from GetTeamInfo → match setup)
- Logs full request/response for schema refinement
- Simulates a complete game session: boot → team → scout → contract
  → training → match → post-match

Usage:
  python3 scripts/s42_01_mock_client.py [--port 8080] [--log FILE]
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request


class MockClient:
    def __init__(self, base, log=None):
        self.base = base
        self.log = log
        # Client state (mirrors what the real client tracks)
        self.auth_code = ""
        self.session_id = ""
        self.user_code = ""
        self.user_id = 0
        self.ms_ver = 0
        self.res_ver = 0
        self.team_id = 0

    def _log(self, msg):
        print(msg)
        if self.log:
            self.log.write(msg + "\n")

    def request(self, endpoint, extra_params=None):
        """Send a request like the real client does."""
        param = {
            "auth_code": self.auth_code,
            "ms_ver": self.ms_ver,
            "res_ver": self.res_ver,
            "session_id": self.session_id,
            "tutorial": 0,
            "user_code": self.user_code,
            "user_id": self.user_id,
        }
        if extra_params:
            param.update(extra_params)

        body = urllib.parse.urlencode({"param": json.dumps(param)}).encode()
        url = f"{self.base}/asj/{endpoint}"
        self._log(f">>> POST {endpoint}")
        self._log(f"    param keys: {sorted(param.keys())}")

        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                resp = json.loads(r.read())
                self._log(f"<<< {r.status} keys: {sorted(resp.keys())}")
                return resp
        except Exception as e:
            self._log(f"<<< ERROR: {e}")
            return None

    def boot(self):
        """Boot sequence: AuthUser -> CheckUpdate -> Login -> top."""
        self._log("== BOOT ==")
        r = self.request("auth_user.php")
        if r and r.get("result") == 0:
            self.session_id = r.get("session_id", "")
            self.auth_code = r.get("auth_code", "")
            self.user_code = r.get("user_code", "")
            self.user_id = r.get("user_id", 0)

        r = self.request("check_update.php")
        # client would download masterdata here if update_required

        r = self.request("login.php")
        r = self.request("top.php")
        return True

    def team_flow(self):
        """Get team info."""
        self._log("== TEAM ==")
        r = self.request("get_team_info.php")
        if r and r.get("team_id"):
            self.team_id = r["team_id"]
        return r

    def progression_flow(self):
        """Scout -> contract -> training."""
        self._log("== PROGRESSION ==")
        r = self.request("do_scout_player.php")
        scouted_id = r.get("player_id") if r else 0

        r = self.request("do_contract_player.php",
                         {"player_id": scouted_id} if scouted_id else None)

        r = self.request("do_training.php",
                         {"player_id": 1001})
        return True

    def match_flow(self):
        """Match setup -> (client simulates) -> submit result."""
        self._log("== MATCH ==")
        r = self.request("get_match_info.php",
                         {"team_id": self.team_id} if self.team_id else None)
        # Real client would run the match sim here (client-side)
        self._log("    [client simulates match locally]")
        r = self.request("submit_match_result.php",
                         {"match_id": 1, "home_score": 2, "away_score": 1})
        return True

    def run_session(self):
        """Run a complete mock game session."""
        self._log("# Mock client session start")
        self.boot()
        self.team_flow()
        self.progression_flow()
        self.match_flow()
        self._log("# Mock client session end")
        self._log(f"# Final state: session={self.session_id[:20]}... "
                  f"user={self.user_id} team={self.team_id}")


def main():
    ap = argparse.ArgumentParser(description="Stage 42 mock client")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--log", default=None, help="log file path")
    args = ap.parse_args()

    log = open(args.log, "w") if args.log else None
    try:
        client = MockClient(f"http://{args.host}:{args.port}", log)
        client.run_session()
    finally:
        if log:
            log.close()


if __name__ == "__main__":
    main()
