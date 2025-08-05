import json

def save_selected_assets(selected_floor, selected_wall):
    with open("selection_data.json", "w") as f:
        json.dump({
            "floor": selected_floor,
            "wall": selected_wall
        }, f)

def load_selected_assets():
    try:
        with open("selection_data.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"floor": None, "wall": None}