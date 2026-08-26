
import json
import random
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the current script's directory to the Python path for local module imports
# This allows importing 's8_01_player_schema' as 'scripts.s8_01_player_schema'
# or directly if the parent directory is already in path.
sys.path.append(str(Path(__file__).resolve().parent))

from s8_01_player_schema import (
    CustomPlayer, POSITION_MAP, VALID_RARITIES, ABILITY_PARAMS, SKILLS,
    INTERNAL_POSITION_KEYS
)

# --- Configuration for player generation ---
NUM_PLAYERS = 1000
OUTPUT_PATH = Path("analysis") / "stage8_player_db" / "player_database.json"

# Base ranges for stats (adjust for more realism)
BASE_ABILITY_MIN = 40
BASE_ABILITY_MAX = 80
RARITY_BONUS_PER_STAR = 5
POSITION_BONUS_PER_APTITUDE = 10

# Position aptitude levels mapping to numeric values
APTITUDE_LEVELS = {
    "N/A": 0, # Not Applicable / Cannot Play
    "D": 1, # Poor
    "C": 2, # Below Average
    "B": 3, # Average
    "A": 4, # Good
    "S": 5, # Excellent
}

# --- Helper functions for stat generation ---

def generate_abilities(rarity: int, primary_position: str) -> Dict[str, int]:
    abilities = {}
    internal_pos = POSITION_MAP.get(primary_position, "")

    for param in ABILITY_PARAMS:
        base_stat = random.randint(BASE_ABILITY_MIN, BASE_ABILITY_MAX)
        
        # Apply rarity bonus
        base_stat += (rarity - 1) * RARITY_BONUS_PER_STAR

        # Apply position-specific bonuses for a more realistic feel
        if internal_pos:
            if internal_pos == "gk" and "gk_decision" in param: # GK specific abilities
                base_stat += random.randint(10, 20)
            elif internal_pos in ["cb", "lsb", "rsb", "dmf"] and ("defense" in param or "body_balance" in param or "intercept" in param): # Defensive abilities
                base_stat += random.randint(5, 15)
            elif internal_pos in ["cf", "st", "lwg", "rwg"] and ("shot" in param or "offense" in param or "dribble" in param or "speed" in param): # Attacking abilities
                base_stat += random.randint(5, 15)
            elif internal_pos in ["cmf", "omf", "rmf", "lmf"] and ("pass" in param or "dribble" in param or "teamwork" in param): # Midfield abilities
                base_stat += random.randint(5, 15)

        abilities[param] = min(99, max(1, base_stat)) # Cap stats between 1 and 99
    return abilities

def generate_positions_aptitude(primary_position: str) -> Dict[str, int]:
    aptitudes = {}
    internal_pos = POSITION_MAP.get(primary_position, "")
    
    for pos_key in INTERNAL_POSITION_KEYS:
        level = 0 # N/A by default
        if pos_key == internal_pos: # Primary position is 'S'
            level = APTITUDE_LEVELS["S"]
        elif (internal_pos in ["cb", "lsb", "rsb"] and pos_key in ["cb", "lsb", "rsb"]) or \
             (internal_pos in ["dmf", "cmf", "omf", "rmf", "lmf"] and pos_key in ["dmf", "cmf", "omf", "rmf", "lmf"]) or \
             (internal_pos in ["cf", "st", "lwg", "rwg"] and pos_key in ["cf", "st", "lwg", "rwg"]): # Similar positions
            if random.random() < 0.7: # 70% chance of being 'A' or 'B'
                 level = random.choice([APTITUDE_LEVELS["A"], APTITUDE_LEVELS["B"]])
            elif random.random() < 0.9: # 20% chance of being 'C'
                 level = APTITUDE_LEVELS["C"]
            else: # 10% chance of 'D' or N/A
                 level = random.choice([APTITUDE_LEVELS["D"], APTITUDE_LEVELS["N/A"]])
        aptitudes[pos_key] = level
    return aptitudes

def generate_active_skills(rarity: int, primary_position: str) -> List[str]:
    num_skills = random.randint(1, min(rarity + 1, 5)) # More skills for higher rarity, up to 5
    if primary_position == "GK": # GK-specific skills
        possible_skills = [s for s in SKILLS if "gk_" in s or "long_throw" in s] + SKILLS
    elif primary_position in ["CF", "SS"]: # Attacker skills
        possible_skills = [s for s in SKILLS if "shoot" in s or "dribble" in s] + SKILLS
    else: # General skills
        possible_skills = SKILLS

    return random.sample(list(set(possible_skills)), k=min(num_skills, len(possible_skills)))

# --- Main generation logic ---

def generate_player_database() -> List[Dict[str, Any]]:
    all_players_normalized = []
    player_names = ["Mbappe", "Haaland", "Messi", "Ronaldo", "Neymar", "Modric", "Kroos", "De Bruyne", "Van Dijk", "Ramos", "Alisson", "Oblak", "Kane", "Lewandowski", "Salah", "Benzema"]
    team_names = ["FC Elite", "United Legends", "Galaxy Stars", "Dynamo Power", "Phoenix FC", "Titanium United"]

    for i in range(NUM_PLAYERS):
        master_id = 100000 + i
        name = random.choice(player_names) + f" {random.randint(1,99)}" # Add random number to names to create variety
        rarity = random.choice(VALID_RARITIES)
        primary_position = random.choice(list(POSITION_MAP.keys()))
        age = random.randint(18, 35)
        height = random.randint(165, 195)
        weight = random.randint(60, 95)
        uniform_number = random.randint(1, 99)
        team_id = random.randint(100, 999) # Random team ID
        country_id = random.randint(1, 200) # Random country ID
        face_id = random.randint(1000, 9999)
        hair_id = random.randint(1000, 9999)
        kit_id = random.randint(1000, 9999)

        abilities = generate_abilities(rarity, primary_position)
        positions_aptitude = generate_positions_aptitude(primary_position)
        active_skills = generate_active_skills(rarity, primary_position)

        player = CustomPlayer(
            master_id=master_id,
            name=name,
            rarity=rarity,
            primary_position=primary_position,
            age=age,
            height=height,
            weight=weight,
            uniform_number=uniform_number,
            team_id=team_id,
            country_id=country_id,
            face_id=face_id,
            hair_id=hair_id,
            kit_id=kit_id,
            abilities=abilities,
            positions_aptitude=positions_aptitude,
            active_skills=active_skills,
        )
        all_players_normalized.append(player.to_normalized_json())
    
    return all_players_normalized

def main():
    print(f"[*] Generating {NUM_PLAYERS} custom players...")
    generated_players = generate_player_database()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps({"players": generated_players}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    print(f"[+] Generated {len(generated_players)} players to {OUTPUT_PATH.relative_to(WORKSPACE)}")

    # Optionally, run the viewer to check the generated data
    # print("[*] Running viewer on generated data...")
    # subprocess.run(["python3", str(WORKSPACE / "scripts" / "s7_01_player_viewer.py"), "--normalized", str(OUTPUT_PATH), "--mapping", str(WORKSPACE / "analysis" / "stage6" / "player_json_key_mapping.json")])

if __name__ == "__main__":
    main()
