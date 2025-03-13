import os
import json
import math
from collections import defaultdict
import tbapy



# CONFIGURATION
SUMMARY_FILE = "outputs\scouter_leaderboard\blue_alliance_data.json" # Aggregated metrics from scouting data
SCOUTING_FILE = "data\processed\cleaned_match_data.json" # Raw scouting entries
PENALTIES_FILE = "outputs\scouter_leaderboard\scouter_penalties.json" # Output file for raw penalty counts
RELATIVE_FILE = "outputs\scouter_leaderboard\scouter_penalties_relative.json" # Output file for relative percentages & confidence intervals

# TBA config
TBA_KEY = os.getenv("TBA_KEY")
if not TBA_KEY:
    print("Please set the TBA_KEY environment variable.")
    exit(1)

tba = tbapy.TBA(TBA_KEY)
event_key = "2025caph"
year = 2025



# LOAD DATA

# Load aggregated alliance metrics from scouting data
with open(SUMMARY_FILE, "r") as f:
    alliance_summary = json.load(f)

# Load raw scouting data
with open(SCOUTING_FILE, "r") as f:
    scouting_data = json.load(f)



# MAIN SCRIPT

#TODO: Make logging better and more detailed (include specific error info and maybe have it save to a .txt within folder dedicated to script logs (for recording keeping (and should have timestamps and run speed and stuff too)))

# Group scouting entries by match number and alliance
# Essentially mapping each match number to a dictionary with keys "red" and "blue"
# These values are the sets of scouter names that submitted entries for that alliance.
match_alliance_scouters = defaultdict(lambda: {"red": set(), "blue": set()})
for entry in scouting_data:
    metadata = entry.get("metadata", {})
    match_num = metadata.get("matchNumber")
    if match_num is None:
        continue
    pos = metadata.get("robotPosition", "").lower()
    scouter = metadata.get("scouterName", "Unknown")
    if "red" in pos:
        match_alliance_scouters[match_num]["red"].add(scouter)
    else:
        match_alliance_scouters[match_num]["blue"].add(scouter)

# Initialize penalty tracker for each scouter
penalties = defaultdict(int)

# Iterate over each match number in the aggregated summary
for match_num_key, our_alliance in alliance_summary.items():
    try:
        match_num = int(match_num_key)
    except Exception:
        match_num = match_num_key

    print(f"Processing match {match_num}...")
    
    # Retrieve TBA match data for specific match number
    try:
        tba_match = tba.match(year=year, event=event_key, number=match_num)
    except Exception as e:
        print(f"Error retrieving TBA match data for match {match_num}: {e}")
        continue

    # Extract TBA alliance data from score_breakdown
    tba_score = tba_match.get("score_breakdown", {})
    tba_blue = tba_score.get("blue", {})
    tba_red  = tba_score.get("red", {})

    # Retrieve aggregated values for each alliance from the scouting summary
    our_blue_auto = our_alliance.get("blue", {}).get("autoCoralCount", 0)
    our_blue_tele = our_alliance.get("blue", {}).get("teleCoralCount", 0)
    our_red_auto  = our_alliance.get("red", {}).get("autoCoralCount", 0)
    our_red_tele  = our_alliance.get("red", {}).get("teleCoralCount", 0)

    # TBA values: note that teleCoral data is under "teleopCoralCount"
    tba_blue_auto = tba_blue.get("autoCoralCount")
    tba_blue_tele = tba_blue.get("teleopCoralCount")
    tba_red_auto  = tba_red.get("autoCoralCount")
    tba_red_tele  = tba_red.get("teleopCoralCount")

    # For each alliance, compare our values with TBA values.
    # For every mismatch (if the TBA value is provided), add one penalty point for each scouter in that alliance (respective to opportunistic attribute counts. aka if more opportunities to fail, will keep in mind in calculation)
    if tba_blue_auto is not None and our_blue_auto != tba_blue_auto:
        for scouter in match_alliance_scouters.get(match_num, {}).get("blue", []):
            penalties[scouter] += 1
        print(f"Mismatch in match {match_num} BLUE autoCoralCount: scouting = {our_blue_auto}, TBA = {tba_blue_auto}")

    if tba_blue_tele is not None and our_blue_tele != tba_blue_tele:
        for scouter in match_alliance_scouters.get(match_num, {}).get("blue", []):
            penalties[scouter] += 1
        print(f"Mismatch in match {match_num} BLUE teleCoralCount: scouting = {our_blue_tele}, TBA = {tba_blue_tele}")

    if tba_red_auto is not None and our_red_auto != tba_red_auto:
        for scouter in match_alliance_scouters.get(match_num, {}).get("red", []):
            penalties[scouter] += 1
        print(f"Mismatch in match {match_num} RED autoCoralCount: scouting = {our_red_auto}, TBA = {tba_red_auto}")

    if tba_red_tele is not None and our_red_tele != tba_red_tele:
        for scouter in match_alliance_scouters.get(match_num, {}).get("red", []):
            penalties[scouter] += 1
        print(f"Mismatch in match {match_num} RED teleCoralCount: scouting = {our_red_tele}, TBA = {tba_red_tele}")

# Save raw penalty counts to JSON file
with open(PENALTIES_FILE, "w") as f:
    json.dump(penalties, f, indent=4)
print(f"Scouter penalties saved to {PENALTIES_FILE}")

# Compute total number of scouting entries per scouter
total_entries = defaultdict(int)
for entry in scouting_data:
    scouter = entry.get("metadata", {}).get("scouterName", "Unknown")
    total_entries[scouter] += 1

# Compute relative penalty percentages and 95% confidence intervals (alpha = 0.05)
# Since each entry contributes 2 metrics (teleCoralCount and autoCoralCount), maximum possible errors = count * 2.
relative_penalties = {}
for scouter, count in total_entries.items():
    penalty_count = penalties.get(scouter, 0)
    max_possible = count * 2  # 2 opportunities per entry
    
    # Proportion of errors and Standard error using binomial proportion calculations (adv stats!)
    p = penalty_count / max_possible if max_possible > 0 else 0
    se = math.sqrt(p * (1 - p) / max_possible) if max_possible > 0 else 0
    
    # 95% confidence interval (alpha = 0.05) using normal approximation (Z = 1.96)
    ci_lower = max(0, p - 1.96 * se)
    ci_upper = min(1, p + 1.96 * se)
    relative_penalties[scouter] = {
        "total_entries": count,
        "max_possible": max_possible,
        "penalties": penalty_count,
        "penalty_percent": p * 100,
        "ci_lower_percent": ci_lower * 100,
        "ci_upper_percent": ci_upper * 100
    }

# Save relative penalty data with confidence intervals to JSON file
with open(RELATIVE_FILE, "w") as f:
    json.dump(relative_penalties, f, indent=4)
print(f"Scouter relative penalties with confidence intervals saved to {RELATIVE_FILE}")