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
    # Stage 34: team data stubs (refined Stage 43)
    "get_team_info.php": {
        "result": 0,
        "team_id": 1001,
        "team_name": "Stub United",
        "team_short_name": "STU",
        "formation": "4-4-2",
        "formation_value": 442,
        "team_player_list": 3,
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
    # Stage 38: training stub (refined Stage 43)
    "do_training.php": {
        "result": 0,
        "training_id": 1,
        "training_pt": 100,
        "player_id": 1001,
        "exp_gained": 100,
        "level_up": 0,
        "new_shot": 96,
        "new_speed": 91,
    },
    # Stage 39: scouting stub (refined Stage 43)
    "do_scout_player.php": {
        "result": 0,
        "scout_id": 1,
        "scout_point": 500,
        "scout_ticket_num": 2,
        "player_id": 1004,
        "player_name": "Scouted Talent",
        "player_rare": 3,
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
        "result": 0,
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
    # Stage 44: achievement, facility, item stubs
    "do_achievement_completion.php": {
        "result": 0,
        "achievement_id": 1,
        "completed": 1,
    },
    "do_receive_achievement_reward.php": {
        "result": 0,
        "reward_id": 1,
        "received": 1,
    },
    "get_achievement_list.php": {
        "result": 0,
        "achievement_size": 2,
        "achievement_0_id": 1,
        "achievement_0_name": "First Win",
        "achievement_1_id": 2,
        "achievement_1_name": "Score 10 Goals",
    },
    "do_cancel_facility.php": {
        "result": 0,
        "facility_id": 7001,
        "cancelled": 1,
    },
    "do_completion_facility.php": {
        "result": 0,
        "facility_id": 7001,
        "completed": 1,
    },
    "do_shorten_facility.php": {
        "result": 0,
        "facility_id": 7001,
        "time_reduced": 1800,
    },
    "do_item_exchange.php": {
        "result": 0,
        "from_item_id": 5001,
        "to_item_id": 5002,
        "quantity": 1,
    },
    "do_item_use_legend.php": {
        "result": 0,
        "item_id": 5003,
        "effect_applied": 1,
    },
    # Stage 45: scout operations
    "check_scout_list_expand.php": {
        "result": 0,
        "can_expand": 1,
        "cost": 100,
    },
    "do_scout_list_expand.php": {
        "result": 0,
        "new_capacity": 50,
    },
    "do_scout_list_favorite.php": {
        "result": 0,
        "scout_id": 1,
        "favorited": 1,
    },
    "do_scout_multiple_chance.php": {
        "result": 0,
        "chance_id": 1,
        "available": 1,
    },
    "do_select_scout_multiple.php": {
        "result": 0,
        "selected_id": 1,
    },
    "do_sell_scout_player.php": {
        "result": 0,
        "player_id": 1004,
        "sold_price": 500,
    },
    "do_obtain_scout_player.php": {
        "result": 0,
        "player_id": 1004,
        "obtained": 1,
    },
    "do_obtain_youth_player.php": {
        "result": 0,
        "player_id": 1005,
        "player_name": "Youth Prospect",
        "obtained": 1,
    },
    # Stage 46: auction + player ops
    "do_bid_auction.php": {
        "result": 0,
        "auction_id": 1,
        "bid_amount": 1000,
        "is_highest": 1,
    },
    "do_favorite_auction.php": {
        "result": 0,
        "auction_id": 1,
        "favorited": 1,
    },
    "get_auction_list.php": {
        "result": 0,
        "auction_size": 2,
        "auction_0_id": 1,
        "auction_0_player": "Star Player",
        "auction_1_id": 2,
        "auction_1_player": "Rising Star",
    },
    "get_auction_detail.php": {
        "result": 0,
        "auction_id": 1,
        "current_bid": 1000,
        "time_left": 3600,
    },
    "do_change_player_info.php": {
        "result": 0,
        "player_id": 1001,
        "updated": 1,
    },
    "do_limit_over.php": {
        "result": 0,
        "player_id": 1001,
        "new_limit": 99,
    },
    "do_quality_training.php": {
        "result": 0,
        "player_id": 1001,
        "quality_up": 1,
    },
    "do_choice_quality.php": {
        "result": 0,
        "choice_id": 1,
        "selected": 1,
    },
    # Stage 47: social + association
    "check_social_id.php": {
        "result": 0,
        "social_id": "stub123",
        "valid": 1,
    },
    "check_taboo_word.php": {
        "result": 0,
        "word": "test",
        "is_taboo": 0,
    },
    "get_friend_list.php": {
        "result": 0,
        "friend_size": 2,
        "friend_0_id": 2001,
        "friend_0_name": "Friend One",
        "friend_1_id": 2002,
        "friend_1_name": "Friend Two",
    },
    "do_send_friend_request.php": {
        "result": 0,
        "target_id": 2001,
        "sent": 1,
    },
    "do_accept_friend.php": {
        "result": 0,
        "friend_id": 2001,
        "accepted": 1,
    },
    "association_cup_save_my_team_info.php": {
        "result": 0,
        "saved": 1,
    },
    "get_all_star_team_info.php": {
        "result": 0,
        "team_id": 9001,
        "team_name": "All Stars",
    },
    "get_legend_team_info.php": {
        "result": 0,
        "team_id": 9002,
        "team_name": "Legends",
    },
    "get_reserve_team_info.php": {
        "result": 0,
        "reserve_size": 5,
    },
    # Stage 48: coach/youth/team ops
    "do_change_all_star_player_info.php": {
        "result": 0,
        "updated": 1,
    },
    "do_speedup_facility.php": {
        "result": 0,
        "facility_id": 7001,
        "sped_up": 1,
    },
    "do_trade_scout.php": {
        "result": 0,
        "trade_id": 1,
        "completed": 1,
    },
    "do_trans_coach.php": {
        "result": 0,
        "coach_id": 1,
        "transferred": 1,
    },
    "do_trans_level_up_coach.php": {
        "result": 0,
        "coach_id": 1,
        "new_level": 2,
    },
    "do_trans_limit_over_coach.php": {
        "result": 0,
        "coach_id": 1,
        "limit_up": 1,
    },
    "do_trans_open_coach.php": {
        "result": 0,
        "coach_id": 1,
        "opened": 1,
    },
    "do_update_team_info.php": {
        "result": 0,
        "team_id": 1001,
        "updated": 1,
    },
    "do_youth_acquisition.php": {
        "result": 0,
        "player_id": 1006,
        "acquired": 1,
    },
    "do_youth_remove_player.php": {
        "result": 0,
        "player_id": 1006,
        "removed": 1,
    },
    "do_youth_scout.php": {
        "result": 0,
        "scout_id": 2,
        "player_found": 1,
    },
    "do_youth_training.php": {
        "result": 0,
        "player_id": 1006,
        "trained": 1,
    },
    # Stage 49: friend/agent/auction/facility
    "friend_accept.php": {
        "result": 0,
        "accepted": 1,
    },
    "friend_append_info.php": {
        "result": 0,
        "info_updated": 1,
    },
    "friend_delete.php": {
        "result": 0,
        "deleted": 1,
    },
    "friend_request_delete.php": {
        "result": 0,
        "deleted": 1,
    },
    "friend_search.php": {
        "result": 0,
        "found_size": 1,
        "found_0_id": 3001,
        "found_0_name": "Search Result",
    },
    "friend_send_gift.php": {
        "result": 0,
        "gift_sent": 1,
    },
    "get_agent_offer.php": {
        "result": 0,
        "offer_size": 1,
        "offer_0_id": 1,
    },
    "get_auction_result.php": {
        "result": 0,
        "won": 0,
        "final_bid": 1000,
    },
    "get_bgm_data.php": {
        "result": 0,
        "bgm_id": 1,
    },
    "get_ceo_rewards.php": {
        "result": 0,
        "reward_size": 1,
    },
    "get_contract_player_info.php": {
        "result": 0,
        "player_id": 1004,
        "contract_days": 30,
    },
    "get_facility_list.php": {
        "result": 0,
        "facility_size": 2,
        "facility_0_id": 7001,
        "facility_0_name": "Training Ground",
    },
    # Stage 50: misc get ops
    "get_favorite_auction_list.php": {
        "result": 0,
        "fav_size": 1,
    },
    "get_limit_over_coach_list.php": {
        "result": 0,
        "coach_size": 1,
    },
    "get_locale_info.php": {
        "result": 0,
        "locale": "en",
        "country": "ID",
    },
    "get_managers_score_info.php": {
        "result": 0,
        "score": 1000,
        "rank": 5,
    },
    "get_menu_data.php": {
        "result": 0,
        "menu_version": 1,
    },
    "get_present_player.php": {
        "result": 0,
        "player_id": 1007,
        "player_name": "Gift Player",
    },
    "get_quality_set_list.php": {
        "result": 0,
        "set_size": 1,
    },
    "get_quality_training_base_list.php": {
        "result": 0,
        "base_size": 1,
    },
    "get_quality_training_coach_list.php": {
        "result": 0,
        "coach_size": 1,
    },
    "get_replay_data.php": {
        "result": 0,
        "replay_id": 1,
        "has_data": 0,
    },
    "get_running_commentary_data.php": {
        "result": 0,
        "commentary_size": 0,
    },
    "get_scout.php": {
        "result": 0,
        "scout_id": 1,
        "scout_name": "Head Scout",
    },
    "get_scout_high_rarity_list.php": {
        "result": 0,
        "scout_size": 1,
    },
    # Stage 51: final batch - all 120 ops covered
    "facebook_request.php": {
        "result": 0,
        "fb_connected": 0,
    },
    "get_shop_item_info.php": {
        "result": 0,
        "shop_size": 3,
    },
    "get_subscription_bg_data.php": {
        "result": 0,
        "has_subscription": 0,
    },
    "get_youth_list.php": {
        "result": 0,
        "youth_size": 2,
    },
    "get_youth_player_list.php": {
        "result": 0,
        "player_size": 2,
    },
    "load_reserve_team.php": {
        "result": 0,
        "loaded": 1,
    },
    "main.php": {
        "result": 0,
        "ok": 1,
    },
    "payment_limit.php": {
        "result": 0,
        "limit": 10000,
        "used": 0,
    },
    "purchase_token.php": {
        "result": 0,
        "token_added": 10,
    },
    "receive_gift.php": {
        "result": 0,
        "gift_id": 1,
        "received": 1,
    },
    "register_user.php": {
        "result": 0,
        "user_id": 1,
        "registered": 1,
    },
    "request_data.php": {
        "result": 0,
        "data": "",
    },
    "save_all_star_team.php": {
        "result": 0,
        "saved": 1,
    },
    "save_legend_team.php": {
        "result": 0,
        "saved": 1,
    },
    "save_reserve_team.php": {
        "result": 0,
        "saved": 1,
    },
    "select_agent_offer.php": {
        "result": 0,
        "selected": 1,
    },
    "select_present_player.php": {
        "result": 0,
        "player_id": 1007,
        "selected": 1,
    },
    "send_message.php": {
        "result": 0,
        "sent": 1,
    },
    "server_data.php": {
        "result": 0,
        "server_time": 0,
    },
    "set_language.php": {
        "result": 0,
        "language": "en",
    },
    "set_player_name_language.php": {
        "result": 0,
        "set": 1,
    },
    "set_youth_training.php": {
        "result": 0,
        "set": 1,
    },
    "use_item_auto.php": {
        "result": 0,
        "used": 1,
    },
    "use_item_auto_legend.php": {
        "result": 0,
        "used": 1,
    },
    "association14_do_player_rental.php": {
        "result": 0,
        "rented": 1,
    },
    "association19_get_rental_player_list.php": {
        "result": 0,
        "rental_size": 1,
    },
    "association6_do_chat.php": {
        "result": 0,
        "sent": 1,
    },
    "cup11_save_cup_team.php": {
        "result": 0,
        "saved": 1,
    },
    "cup_live11_save_cup_team.php": {
        "result": 0,
        "saved": 1,
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
