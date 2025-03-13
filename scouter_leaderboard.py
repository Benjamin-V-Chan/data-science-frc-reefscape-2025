#!/usr/bin/env python3
import json
from collections import defaultdict

# --- Configuration ---
INPUT_FILE = "data\processed\cleaned_match_data.json"  # Your scouting submissions file
OUTPUT_FILE = "match_alliance_summary.json"  # Output file with aggregated metrics

# --- Load scouting data ---
with open(INPUT_FILE, "r") as f:
    data = json.load(f)

# --- Group entries by match number ---
matches = defaultdict(list)
for entry in data:
    match_number = entry.get("metadata", {}).get("matchNumber")
    if match_number is not None:
        matches[match_number].append(entry)

# --- Process each match ---
result = {}

for match_number, entries in matches.items():
    # Initialize alliance metrics for red and blue
    alliance_metrics = {
        "red": {"teleCoralCount": 0, "autoCoralCount": 0},
        "blue": {"teleCoralCount": 0, "autoCoralCount": 0}
    }
    
    for entry in entries:
        # Determine alliance from robotPosition
        pos = entry.get("metadata", {}).get("robotPosition", "").lower()
        if "red" in pos:
            alliance = "red"
        else:
            alliance = "blue"
        
        vars_dict = entry.get("variables", {})
        # Calculate teleCoralCount for this entry
        tele_sum = 0
        for key in ["teleCoral.L1", "teleCoral.L2", "teleCoral.L3", "teleCoral.L4"]:
            val = vars_dict.get(key, 0)
            # If value is boolean, convert True/False to 1/0
            if isinstance(val, bool):
                val = 1 if val else 0
            tele_sum += val
        
        # Calculate autoCoralCount for this entry
        auto_sum = 0
        for key in ["autoCoral.L1", "autoCoral.L2", "autoCoral.L3", "autoCoral.L4"]:
            val = vars_dict.get(key, 0)
            if isinstance(val, bool):
                val = 1 if val else 0
            auto_sum += val
        
        alliance_metrics[alliance]["teleCoralCount"] += tele_sum
        alliance_metrics[alliance]["autoCoralCount"] += auto_sum
    
    # Save computed metrics under the match number key
    result[match_number] = alliance_metrics

# --- Save the results to a new JSON file ---
with open(OUTPUT_FILE, "w") as f:
    json.dump(result, f, indent=4)

print(f"Aggregated match data saved to {OUTPUT_FILE}")