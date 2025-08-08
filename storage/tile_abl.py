import json

TILES_FILE = "storage/tile_data.json"

# Load tiles from file
def load_tiles():
    with open(TILES_FILE, "r") as f:
        return json.load(f)

# Save changes to file
def save_tiles(tiles):
    with open(TILES_FILE, "w") as f:
        json.dump(tiles, f, indent=4)