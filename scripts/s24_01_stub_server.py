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
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer


# Minimal canned responses per endpoint. The real server is dead;
# these let us observe the client's boot sequence.
# Schema inferred from client key strings (Stage 27).
CANNED = {
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
        # serve a generic OK for GET probes
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
