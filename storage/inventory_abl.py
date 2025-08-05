import json
import os

INVENTORY_FILE = "storage/inventory_data.json"

# Default structure
default_inventory = {
    "item": [],
    "floor": [],
    "wall": []
}

# Load inventory from file
def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        return default_inventory
    with open(INVENTORY_FILE, "r") as f:
        return json.load(f)

# Save inventory to file
def save_inventory(inventory):
    with open(INVENTORY_FILE, "w") as f:
        json.dump(inventory, f, indent=4)
