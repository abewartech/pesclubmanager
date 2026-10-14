"""Stage 9: generate a self-contained offline HTML viewer for the player DB.

Reads the Stage 5 normalized players and the Stage 6 JSON-key mapping,
then emits a single HTML file (no CDN, no server, no build step) with:
  - searchable / sortable player table
  - per-player detail with native evidence badges per field
  - schema explorer for the 105-key mapping, including the 8 unknown keys
    and the 60 native-only offset fields

Read-only: never modifies the input artifacts.
"""

import argparse
import html
import json
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_PLAYERS = WORKSPACE / "analysis" / "stage5_player_json" / "normalized_players.json"
DEFAULT_MAPPING = WORKSPACE / "analysis" / "stage6" / "player_json_key_mapping.json"
DEFAULT_OUT = WORKSPACE / "analysis" / "stage9_player_view" / "player_db_viewer.html"

CONF_CLASS = {"HIGH": "high", "MEDIUM": "med", "UNKNOWN": "unk", "LOW": "low"}


def esc(value):
    return html.escape(str(value), quote=True)


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def field_rows(player):
    """Flatten player sections into (section, key, value, evidence) rows."""
    rows = []
    evidence = player.get("native_evidence", {}) or {}
    for section, fields in player.items():
        if section in ("native_evidence", "provenance", "raw_unmapped"):
            continue
        if not isinstance(fields, dict):
            continue
        for key, value in fields.items():
            ev = evidence.get(key, {}) if isinstance(evidence, dict) else {}
            rows.append((section, key, value, ev))
    return rows


def build_html(players, mapping):
    mappings = mapping.get("mappings", [])
    summary = mapping.get("summary", {})
    unknown_keys = mapping.get("unknown_json_keys", [])

    players_json = json.dumps(players, ensure_ascii=False)
    mappings_json = json.dumps(mappings, ensure_ascii=False)

    conf_counts = summary.get("confidence_counts", {})

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PESCM Player DB Viewer (offline)</title>
<style>
:root {{ --bg:#111418; --panel:#1a1f26; --line:#2a323d; --txt:#dfe6ee; --dim:#8b96a3; }}
body {{ background:var(--bg); color:var(--txt); font-family:system-ui,sans-serif; margin:0; }}
header {{ padding:14px 20px; border-bottom:1px solid var(--line); }}
header h1 {{ margin:0; font-size:18px; }}
header p {{ margin:4px 0 0; color:var(--dim); font-size:13px; }}
nav {{ display:flex; gap:8px; padding:10px 20px; border-bottom:1px solid var(--line); }}
nav button {{ background:var(--panel); color:var(--txt); border:1px solid var(--line); padding:8px 14px; cursor:pointer; border-radius:6px; }}
nav button.active {{ background:#2c6bed; border-color:#2c6bed; }}
main {{ padding:16px 20px; max-width:1200px; }}
.tab {{ display:none; }} .tab.active {{ display:block; }}
input[type=search], select {{ background:var(--panel); color:var(--txt); border:1px solid var(--line); padding:8px 10px; border-radius:6px; margin:0 8px 12px 0; }}
table {{ width:100%; border-collapse:collapse; font-size:14px; }}
th, td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); }}
th {{ cursor:pointer; color:var(--dim); user-select:none; }}
tr:hover td {{ background:#1e242d; }}
.badge {{ display:inline-block; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:bold; }}
.high {{ background:#123f22; color:#4ade80; }} .med {{ background:#42320f; color:#fbbf24; }}
.unk {{ background:#43161a; color:#f87171; }} .low {{ background:#3a2b12; color:#fb923c; }}
.detail {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:14px 16px; margin-top:12px; }}
.detail h3 {{ margin:14px 0 6px; font-size:14px; color:var(--dim); text-transform:uppercase; }}
.ev {{ font-size:12px; color:var(--dim); }}
code {{ background:#0d1014; padding:1px 6px; border-radius:4px; font-size:12px; }}
.stats {{ display:flex; gap:16px; margin-bottom:12px; font-size:13px; color:var(--dim); }}
.stats b {{ color:var(--txt); }}
a {{ color:#7aa2ff; }}
</style>
</head>
<body>
<header>
<h1>PES Club Manager — Offline Player DB Viewer</h1>
<p>Read-only view over Stage 5 normalized players + Stage 6 decoder schema. No network calls.</p>
</header>
<nav>
<button data-tab="players" class="active">Players</button>
<button data-tab="schema">Schema mapping</button>
<button data-tab="unknown">Unknown keys ({len(unknown_keys)})</button>
</nav>
<main>
<div class="tab active" id="tab-players">
  <div class="stats">
    <span>Players: <b id="stat-players"></b></span>
    <span>JSON keys mapped: <b>{summary.get("mapped_json_key_count", "?")}/{summary.get("json_key_count", "?")}</b></span>
    <span>HIGH <b>{conf_counts.get("HIGH", 0)}</b> · MEDIUM <b>{conf_counts.get("MEDIUM", 0)}</b> · UNKNOWN <b>{conf_counts.get("UNKNOWN", 0)}</b></span>
  </div>
  <input type="search" id="q" placeholder="Search name / serial_id / master_id…">
  <table id="ptable"><thead><tr>
    <th data-k="name">Name</th><th data-k="serial_id">Serial</th><th data-k="master_id">Master</th>
    <th data-k="position">Pos</th><th data-k="age">Age</th><th data-k="team">Team</th>
  </tr></thead><tbody></tbody></table>
  <div class="detail" id="pdetail" style="display:none"></div>
</div>
<div class="tab" id="tab-schema">
  <input type="search" id="sq" placeholder="Filter json_key / field…">
  <select id="sconf"><option value="">all confidence</option><option>HIGH</option><option>MEDIUM</option><option>UNKNOWN</option><option>LOW</option></select>
  <table id="stable"><thead><tr>
    <th>json_key</th><th>field</th><th>confidence</th><th>offsets</th><th>setters</th>
  </tr></thead><tbody></tbody></table>
</div>
<div class="tab" id="tab-unknown">
  <p style="color:var(--dim)">JSON keys seen in <code>PrepareDataFromJson</code> with no native field correlation yet. Preserved as-is — no semantics invented.</p>
  <table><thead><tr><th>json_key</th><th>instr address</th><th>literal address</th></tr></thead>
  <tbody id="urows"></tbody></table>
</div>
</main>
<script>
const PLAYERS = {players_json};
const MAPPINGS = {mappings_json};
const confClass = {{HIGH:"high", MEDIUM:"med", UNKNOWN:"unk", LOW:"low"}};
const $ = id => document.getElementById(id);

// tabs
document.querySelectorAll("nav button").forEach(b => b.onclick = () => {{
  document.querySelectorAll("nav button").forEach(x => x.classList.remove("active"));
  document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
  b.classList.add("active"); $("tab-"+b.dataset.tab).classList.add("active");
}});

// players table
function flat(p) {{
  return {{
    name: p.profile?.name ?? "", serial_id: p.identity?.serial_id ?? "",
    master_id: p.identity?.master_id ?? "", position: Object.keys(p.positions||{{}})[0] ?? "",
    age: p.profile?.age ?? "", team: p.team?.original_team_id ?? "", _p: p
  }};
}}
let rows = PLAYERS.map(flat);
$("stat-players").textContent = rows.length;
function renderPlayers() {{
  const q = $("q").value.toLowerCase();
  const tb = document.querySelector("#ptable tbody"); tb.innerHTML = "";
  rows.filter(r => !q || (r.name+r.serial_id+r.master_id).toLowerCase().includes(q))
    .forEach(r => {{
      const tr = document.createElement("tr");
      ["name","serial_id","master_id","position","age","team"].forEach(k => {{
        const td = document.createElement("td"); td.textContent = r[k]; tr.appendChild(td);
      }});
      tr.onclick = () => showDetail(r._p);
      tb.appendChild(tr);
    }});
}}
function showDetail(p) {{
  const d = $("pdetail"); d.style.display = "block";
  let htm = `<h2 style="margin:0">${{esc(p.profile?.name ?? "?")}} <span class="ev">#${{esc(p.identity?.serial_id ?? "?")}}</span></h2>`;
  const ev = p.native_evidence || {{}};
  for (const [sec, fields] of Object.entries(p)) {{
    if (["native_evidence","provenance","raw_unmapped"].includes(sec) || typeof fields !== "object") continue;
    htm += `<h3>${{esc(sec)}}</h3><table>`;
    for (const [k, v] of Object.entries(fields)) {{
      const e = ev[k] || {{}};
      const c = e.confidence || "";
      htm += `<tr><td><code>${{esc(k)}}</code></td><td>${{esc(typeof v === "object" ? JSON.stringify(v) : v)}}</td>` +
        `<td>${{c ? `<span class="badge ${{confClass[c]||""}}">${{esc(c)}}</span>` : ""}}` +
        `${{e.field_candidate ? ` <span class="ev">${{esc(e.field_candidate)}}</span>` : ""}}` +
        `${{(e.offsets||[]).length ? ` <span class="ev">${{e.offsets.map(o=>"<code>"+esc(o)+"</code>").join(" ")}}</span>` : ""}}</td></tr>`;
    }}
    htm += "</table>";
  }}
  if (p.raw_unmapped && Object.keys(p.raw_unmapped).length) {{
    htm += `<h3>raw_unmapped (preserved)</h3><table>` +
      Object.entries(p.raw_unmapped).map(([k,v]) => `<tr><td><code>${{esc(k)}}</code></td><td>${{esc(v)}}</td></tr>`).join("") + "</table>";
  }}
  d.innerHTML = htm;
  d.scrollIntoView({{behavior:"smooth", block:"nearest"}});
}}
function esc(s) {{ return String(s).replace(/[&<>"]/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[c])); }}
$("q").oninput = renderPlayers;
renderPlayers();

// schema table
function renderSchema() {{
  const q = $("sq").value.toLowerCase(), cf = $("sconf").value;
  const tb = document.querySelector("#stable tbody"); tb.innerHTML = "";
  MAPPINGS.filter(m => (!cf || m.confidence === cf) &&
      (!q || (m.json_key + (m.field_candidate||"")).toLowerCase().includes(q)))
    .forEach(m => {{
      const tr = document.createElement("tr");
      tr.innerHTML = `<td><code>${{esc(m.json_key)}}</code></td><td>${{esc(m.field_candidate||"—")}}</td>` +
        `<td><span class="badge ${{confClass[m.confidence]||""}}">${{esc(m.confidence||"?")}}</span></td>` +
        `<td>${{(m.offsets||[]).map(o=>"<code>"+esc(o)+"</code>").join(" ")}}</td>` +
        `<td class="ev">${{esc((m.setter_functions||[]).join(", "))}}</td>`;
      tb.appendChild(tr);
    }});
}}
$("sq").oninput = renderSchema; $("sconf").onchange = renderSchema;
renderSchema();

// unknown keys
$("urows").innerHTML = {json.dumps([{"k": u["json_key"], "i": (u.get("prepare_data_from_json_evidence") or [{}])[0].get("instruction_address",""), "l": (u.get("prepare_data_from_json_evidence") or [{}])[0].get("literal_address","")} for u in unknown_keys], ensure_ascii=False)}.map(u =>
  `<tr><td><code>${{esc(u.k)}}</code></td><td><code>${{esc(u.i)}}</code></td><td><code>${{esc(u.l)}}</code></td></tr>`).join("");
</script>
</body>
</html>"""


def main():
    ap = argparse.ArgumentParser(description="Generate offline HTML player DB viewer (Stage 9)")
    ap.add_argument("--players", default=str(DEFAULT_PLAYERS))
    ap.add_argument("--mapping", default=str(DEFAULT_MAPPING))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    players_doc = load_json(args.players)
    players = players_doc.get("players", [])
    if not isinstance(players, list):
        raise SystemExit(f"No players list in {args.players}")
    mapping = load_json(args.mapping)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_html(players, mapping), encoding="utf-8")
    print(f"wrote {out} ({len(players)} players, {len(mapping.get('mappings', []))} mapped keys)")


if __name__ == "__main__":
    main()
