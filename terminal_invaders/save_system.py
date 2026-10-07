import json
import os

SAVE_FILE = "savegame.json"

def load_game_data():
    if not os.path.exists(SAVE_FILE):
        return {
            "total_credits": 0,
            "permanent_upgrades": {
                "max_health": 0,
                "fire_rate_boost": 0,
                "starting_xp": 0
            }
        }
    try:
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"total_credits": 0, "permanent_upgrades": {}}

def save_game_data(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_credits(amount):
    data = load_game_data()
    data["total_credits"] += amount
    save_game_data(data)

def buy_upgrade(upgrade_key, cost):
    data = load_game_data()
    if data["total_credits"] >= cost:
        data["total_credits"] -= cost
        # Initialize permanent_upgrades if missing
        if "permanent_upgrades" not in data:
            data["permanent_upgrades"] = {}

        current_val = data["permanent_upgrades"].get(upgrade_key, 0)
        data["permanent_upgrades"][upgrade_key] = current_val + 1
        save_game_data(data)
        return True
    return False
