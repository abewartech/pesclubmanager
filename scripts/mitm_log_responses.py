from mitmproxy import http
from pathlib import Path
import json, re, time

OUT = Path("/Users/it-admiinistrator/Documents/apps/web-sos-indonesia/others/pesclubmanager/analysis/dynamic_mock_responses")
OUT.mkdir(parents=True, exist_ok=True)

class PescmLogger:
    def request(self, flow: http.HTTPFlow):
        print(f">>> {flow.request.method} {flow.request.pretty_url}")
        req_body = flow.request.get_text(strict=False) or ""
        if req_body:
            try:
                print(req_body[:2000])
            except Exception:
                pass

    def response(self, flow: http.HTTPFlow):
        resp_body = flow.response.get_text(strict=False) or ""
        print(f"<<< {flow.response.status_code} {flow.request.pretty_url} ({len(resp_body)} bytes)")
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", flow.request.host + flow.request.path)[:120]
        if not safe:
            safe = "root"
        out = OUT / f"{safe}_{int(time.time()*1000)}.txt"
        out.write_text(
            "REQUEST:\n"
            + flow.request.method + " " + flow.request.pretty_url + "\n"
            + "Headers: " + json.dumps(dict(flow.request.headers)) + "\n"
            + (flow.request.get_text(strict=False) or "") + "\n\n"
            + "RESPONSE:\n"
            + str(flow.response.status_code) + "\n"
            + "Headers: " + json.dumps(dict(flow.response.headers)) + "\n"
            + (flow.response.get_text(strict=False) or "")
        )
        # If the response is JSON, also save parsed JSON separately.
        ctype = flow.response.headers.get("content-type", "")
        if "json" in ctype.lower():
            try:
                obj = json.loads(resp_body)
                (OUT / f"{safe}_{int(time.time()*1000)}.json").write_text(json.dumps(obj, indent=2, ensure_ascii=False))
            except Exception:
                pass

addons = [PescmLogger()]
