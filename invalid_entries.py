import json
from collections import defaultdict

# File paths
INPUT_FILE = "data/raw/backup.json"  # Replace with actual path
OUTPUT_FILE_CLEANED = "data/raw/cleaned_backup.json"
OUTPUT_FILE_INVALID = "data/raw/invalid_entries.json"

# Expected robot positions per match
EXPECTED_POSITIONS = {"red_1", "red_2", "red_3", "blue_1", "blue_2", "blue_3"}

def is_valid_entry(entry):
    """Checks if an entry has all required metadata keys."""
    required_keys = {"scouterName", "matchNumber", "robotTeam", "robotPosition"}
    if "metadata" not in entry:
        return False, "Missing metadata"
    metadata = entry["metadata"]
    
    missing_keys = [key for key in required_keys if key not in metadata]
    if missing_keys:
        return False, f"Missing metadata keys: {', '.join(missing_keys)}"
    
    return True, None

def validate_matches(data):
    """Filters out invalid entries and returns cleaned data & invalid data with reasons."""
    match_dict = defaultdict(list)

    # Organize entries by match number
    for entry in data:
        is_valid, reason = is_valid_entry(entry)
        if is_valid:
            match_dict[entry["metadata"]["matchNumber"]].append(entry)
        else:
            entry["removal_reason"] = reason

    cleaned_data = []
    invalid_data = []

    for match_number, entries in match_dict.items():
        teams = set()
        positions = set()
        match_valid = True
        removal_reasons = []

        if len(entries) != 6:
            match_valid = False
            removal_reasons.append(f"Match {match_number} does not have exactly 6 teams (found {len(entries)})")

        for entry in entries:
            metadata = entry["metadata"]
            team = metadata["robotTeam"]
            position = metadata["robotPosition"]

            if team in teams:
                match_valid = False
                removal_reasons.append(f"Duplicate team {team} in match {match_number}")

            if position in positions:
                match_valid = False
                removal_reasons.append(f"Duplicate position {position} in match {match_number}")

            teams.add(team)
            positions.add(position)

        if match_valid:
            cleaned_data.extend(entries)
        else:
            for entry in entries:
                entry["removal_reason"] = "; ".join(removal_reasons)
                invalid_data.append(entry)

    return cleaned_data, invalid_data

def main():
    # Load the data
    with open(INPUT_FILE, "r") as infile:
        data = json.load(infile)["matchApp"]  # Extract match data

    # Validate and clean data
    cleaned_data, invalid_data = validate_matches(data)

    # Save cleaned data
    with open(OUTPUT_FILE_CLEANED, "w") as outfile:
        json.dump({"matchApp": cleaned_data}, outfile, indent=4)

    # Save invalid data with reasons
    with open(OUTPUT_FILE_INVALID, "w") as outfile:
        json.dump({"invalidEntries": invalid_data}, outfile, indent=4)

if __name__ == "__main__":
    main()
