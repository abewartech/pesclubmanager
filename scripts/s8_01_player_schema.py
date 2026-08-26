
import dataclasses
from typing import Dict, List, Optional, Any

# --- Position Mapping ---
# User-facing positions to internal game aptitude keys (from Stage 6 analysis)
POSITION_MAP = {
    "GK": "gk",
    "CB": "cb",
    "RB": "rsb",  # Right Back
    "LB": "lsb",  # Left Back
    "DMF": "dmf",
    "CMF": "cmf",
    "AMF": "omf",  # Attacking Midfielder
    "RMF": "rmf",
    "LMF": "lmf",
    "CF": "cf",   # Center Forward / Striker
    "SS": "st",    # Second Striker (often similar to CF)
}
INTERNAL_POSITION_KEYS = sorted(list(set(POSITION_MAP.values())))

# --- Rarity ---
RARITY_LABELS = {
    1: "★",
    2: "★★",
    3: "★★★",
    4: "★★★★",
    5: "★★★★★",
}
VALID_RARITIES = list(RARITY_LABELS.keys())

# --- Ability Parameters (from Stage 6 mapping) ---
ABILITY_PARAMS = [
    "param_agility", "param_ball_spin_control", "param_body_balance",
    "param_defense_decision", "param_dribble", "param_gk_decision",
    "param_heading", "param_intercept", "param_jump", "param_kick_power",
    "param_long_pass", "param_offense_decision", "param_place_kicking",
    "param_r_foot_acc", "param_r_foot_frequency", "param_saving",
    "param_short_pass", "param_shot", "param_speed", "param_stamina",
    "param_teamwork", "param_trap"
]

# --- Skills (from Stage 6 mapping) ---
SKILLS = [
    "skill_acrobatic_shoot", "skill_back_spin_lob", "skill_captaincy",
    "skill_chasing", "skill_combative_spirit", "skill_control_curve",
    "skill_flip_flap", "skill_gk_long_throw", "skill_knuckle_shoot",
    "skill_long_throw", "skill_low_pant_kick", "skill_man_mark",
    "skill_one_touch_pass", "skill_one_touch_shoot", "skill_out_spin_kick",
    "skill_pin_point_cross", "skill_pivot_foot_touch", "skill_quick_touch",
    "skill_roulette", "skill_scissors", "skill_sombrero", "skill_super_sub"
]

# --- Player Field Offsets (from Stage 4/6 analysis - in-memory, not file offsets) ---
FIELD_OFFSETS = {
    "master_id": {"offset": "0x1d0", "width": "u64"},
    "name": {"offset": "0x38", "width": "pointer"},
    "rarity": {"offset": "0x1c0", "width": "u32"},
    "age": {"offset": "0x18/0x1c", "width": "u64/u8"}, # Bitfield
    "original_team_id": {"offset": "0xdc", "width": "u32"},
    "serial_id": {"offset": "0x1c8", "width": "u64"},
    "uniform_number": {"offset": "0x1ac", "width": "u32"},
    "salary": {"offset": "0x1e8", "width": "u32"},
    "contract_period": {"offset": "0x1e0", "width": "u32"},
    "market_value": {"offset": "0x1a0", "width": "u64"},
    "sell_price": {"offset": "0x1a8", "width": "u32"},
    "motivation_value": {"offset": "0x20c", "width": "u8"},
    "appearance_id": {"offset": "0x1b0", "width": "u32"}, # Example appearance ID
}

# --- Player Data Model (for custom database generation) ---
@dataclasses.dataclass
class CustomPlayer:
    master_id: int
    name: str
    rarity: int # 1-5 stars
    primary_position: str # GK, CB, RB, etc.
    age: int
    height: int # cm
    weight: int # kg
    uniform_number: int
    team_id: int # Placeholder for a custom team ID
    country_id: int # Placeholder for a country ID

    # Abilities (all 22 params)
    abilities: Dict[str, int]

    # Positions aptitude (all 13 internal game keys)
    # 0 = N/A, 1 = D, 2 = C, 3 = B, 4 = A, 5 = S
    positions_aptitude: Dict[str, int]

    # Skills (list of active skill keys)
    active_skills: List[str]

    # Appearance IDs (references to PAK assets if applicable)
    face_id: int = 0 # Placeholder for a specific face model/texture
    hair_id: int = 0 # Placeholder for a specific hair model/texture
    kit_id: int = 0 # Placeholder for a specific kit/uniform


    # --- Helper to convert to normalized JSON format (Stage 5 compatible) ---
    def to_normalized_json(self) -> Dict[str, Any]:
        normalized = {
            "identity": {
                "master_id": self.master_id,
                "serial_id": self.master_id, # Using master_id as serial for simplicity
            },
            "profile": {
                "name": self.name,
                "rarity": self.rarity,
                "age": self.age,
                "position": POSITION_MAP.get(self.primary_position, ""),
                # height and weight are not in native schema, adding to raw_unmapped or custom
                "height": self.height, 
                "weight": self.weight,
            },
            "team": {
                "original_team_id": self.team_id,
                # "nationality" : self.country_id (if we add country_id)
            },
            "contract": {
                "salary": 1000 * self.rarity * self.age, # Example formula
                "contract_period": 12, # Default
                "market_value": 5000 * self.rarity * self.age,
                "sell_price": 2500 * self.rarity * self.age,
                "motivation_value": 75, # Default
            },
            "abilities": self.abilities,
            "skills": {}, # Will be populated by active_skills
            "positions": self.positions_aptitude,
            "records": { # Minimal placeholder records
                "record_goal_total": 0,
                "record_match_total": 0,
            },
            "raw_unmapped": {
                 # Placeholder for any unmapped fields, or for height/weight if we don't put them in profile
            },
            "native_evidence": {}, # Not generating native evidence for custom data
            "provenance": {
                "source": "custom_generator",
                "generator_version": "1.0",
            },
            "appearance": { # Custom appearance section
                "face_id": self.face_id,
                "hair_id": self.hair_id,
                "kit_id": self.kit_id,
            }
        }

        # Populate skills from active_skills list
        for skill_key in self.active_skills:
            if skill_key in SKILLS: # Ensure it's a valid skill
                normalized["skills"][skill_key] = 1 # Set to 1 if player has the skill

        return normalized

