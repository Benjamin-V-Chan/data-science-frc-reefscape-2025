import json
import os

# File paths
EXPECTED_DATA_STRUCTURE_FILE = "config/expected_data_structure.json"
INPUT_FILE = "data/raw/raw_data.json"
OUTPUT_COMBINED_FILE = "data/raw/combined_data.json"
OUTPUT_VOIDED_FILE = "data/raw/voided_entries.json"

def load_json(filepath):
    """Loads JSON data from a file."""
    with open(filepath, "r") as file:
        return json.load(file)

def save_json(filepath, data):
    """Saves JSON data to a file."""
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

def get_metadata_fields(expected_structure):
    """Extracts required metadata fields from expected data structure."""
    return set(expected_structure.get("metadata", {}).keys())

def match_entries(match_data, super_data, metadata_fields):
    """Matches entries between matchApp and superApp based on metadata fields."""
    combined_data = []
    voided_entries = []

    # Create a lookup dictionary for superApp data using only expected metadata fields
    super_lookup = {
        tuple(entry["metadata"].get(field, None) for field in metadata_fields): entry
        for entry in super_data
    }

    for match_entry in match_data:
        key = tuple(match_entry["metadata"].get(field, None) for field in metadata_fields)

        if key in super_lookup:
            # Merge the data
            combined_entry = {
                "metadata": {field: match_entry["metadata"].get(field, None) for field in metadata_fields},
                "matchData": match_entry,
                "superData": super_lookup[key]
            }
            combined_data.append(combined_entry)
        else:
            # Log as voided if no matching superApp entry is found
            voided_entries.append({"entry": match_entry, "reason": "No matching superApp entry found"})

    # Check for unmatched superApp entries
    for key, super_entry in super_lookup.items():
        if key not in {tuple(entry["metadata"].get(field, None) for field in metadata_fields) for entry in match_data}:
            voided_entries.append({"entry": super_entry, "reason": "No matching matchApp entry found"})

    return combined_data, voided_entries

def main():
    # Load data
    data = load_json(INPUT_FILE)
    expected_structure = load_json(EXPECTED_DATA_STRUCTURE_FILE)

    match_data = data.get("matchApp", [])
    super_data = data.get("superApp", [])

    # Get required metadata fields from the expected data structure
    metadata_fields = get_metadata_fields(expected_structure)

    # Match entries and identify voided entries
    combined_data, voided_entries = match_entries(match_data, super_data, metadata_fields)

    # Save output files
    save_json(OUTPUT_COMBINED_FILE, combined_data)
    save_json(OUTPUT_VOIDED_FILE, voided_entries)

if __name__ == "__main__":
    main()