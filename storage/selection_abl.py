import json

SELECTION_FILE = "storage/selection_data.json"

def save_selected_assets(selected_floor, selected_wall):
    with open(SELECTION_FILE, "w") as f:
        json.dump({
            "floor": selected_floor,
            "wall": selected_wall
        }, f)

def load_selected_assets():
    try:
        with open(SELECTION_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"floor": None, "wall": None}