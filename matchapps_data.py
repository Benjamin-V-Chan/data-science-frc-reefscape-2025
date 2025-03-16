import json
import os

EXPECTED_DATA_STRUCTURE_FILE = "config/expected_data_structure.json"
INPUT_FILE = "data/raw/lar_data_raw.json"
OUTPUT_COMBINED_FILE = "data/raw/matchapps_data.json"


def load_json(filepath):
    """Loads JSON data from a file."""
    with open(filepath, "r") as file:
        return json.load(file)


def save_json(filepath, data):
    """Saves JSON data to a file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)


# Load JSON data
data = load_json(INPUT_FILE)

# Extract "matchApp" data
new_data = data.get("matchApp", [])

# Print JSON (Optional)
print(json.dumps(new_data, indent=4))

# Save extracted data to the new file
save_json(OUTPUT_COMBINED_FILE, new_data)
