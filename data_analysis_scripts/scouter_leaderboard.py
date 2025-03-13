import os
import json
import math
import time
from collections import defaultdict
import tbapy



# CONFIGURATION

SCOUTING_FILE = "data\processed\cleaned_match_data.json"  # Raw scouting entries
SUMMARY_FILE = "outputs\scouter_leaderboard\summary_alliance_data.json"  # Aggregated metrics from scouting data
PENALTIES_FILE = "outputs\scouter_leaderboard\scouter_penalties.json"  # Output file for raw penalty counts
RELATIVE_FILE = "outputs\scouter_leaderboard\scouter_penalties_relative.json"  # Output file for relative percentages & confidence intervals

# TBA configuration
TBA_KEY = os.getenv("TBA_KEY")
if not TBA_KEY:
    print("Please set the TBA_KEY environment variable.")
    exit(1)

tba = tbapy.TBA(TBA_KEY)
event_key = "2025caph"
year = 2025

start_time = time.time()



# ALLIANCE SUMMARY GENERATION

print("Generating alliance summary from scouting data...")
with open(SCOUTING_FILE, "r") as f:
    scouting_data = json.load(f)

# We'll produce a dictionary keyed by match number (as a string) with sub-dictionaries for "blue" and "red".
# Each alliance's dictionary contains:
#   "teleCoralCount": sum(teleCoral.L1 + teleCoral.L2 + teleCoral.L3 + teleCoral.L4) for that alliance in that match,
#   "autoCoralCount": sum(autoCoral.L1 + autoCoral.L2 + autoCoral.L3 + autoCoral.L4) for that alliance in that match.
alliance_summary = {}

for entry in scouting_data:
    metadata = entry.get("metadata", {})
    match_num = metadata.get("matchNumber")
    if match_num is None:
        continue
    match_key = str(match_num)
    pos = metadata.get("robotPosition", "").lower()
    alliance = "red" if "red" in pos else "blue"
    vars_dict = entry.get("variables", {})

    # Calculate teleCoralCount for this entry
    tele_count = 0
    for key in ["teleCoral.L1", "teleCoral.L2", "teleCoral.L3", "teleCoral.L4"]:
        val = vars_dict.get(key, 0)
        if isinstance(val, bool):
            val = 1 if val else 0
        tele_count += val

    # Calculate autoCoralCount for this entry
    auto_count = 0
    for key in ["autoCoral.L1", "autoCoral.L2", "autoCoral.L3", "autoCoral.L4"]:
        val = vars_dict.get(key, 0)
        if isinstance(val, bool):
            val = 1 if val else 0
        auto_count += val

    if match_key not in alliance_summary:
        alliance_summary[match_key] = {
            "blue": {"teleCoralCount": 0, "autoCoralCount": 0},
            "red": {"teleCoralCount": 0, "autoCoralCount": 0}
        }
    alliance_summary[match_key][alliance]["teleCoralCount"] += tele_count
    alliance_summary[match_key][alliance]["autoCoralCount"] += auto_count

with open(SUMMARY_FILE, "w") as f:
    json.dump(alliance_summary, f, indent=4)
print(f"Alliance summary saved to {SUMMARY_FILE}")



# CROSS-REFERNCING WITH TBA DATA AND PENALTY COMPUTATIONS

# Group scouting entries by match number and alliance (to know which scouters contributed)
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

for match_num_key, our_alliance in alliance_summary.items():
    try:
        match_num = int(match_num_key)
    except Exception:
        match_num = match_num_key

    print(f"Processing match {match_num}...")
    try:
        tba_match = tba.match(year=year, event=event_key, number=match_num)
    except Exception as e:
        print(f"Error retrieving TBA match data for match {match_num}: {e}")
        continue

    # Extract TBA alliance data from score_breakdown
    tba_score = tba_match.get("score_breakdown", {})
    tba_blue = tba_score.get("blue", {})
    tba_red = tba_score.get("red", {})

    our_blue_auto = our_alliance.get("blue", {}).get("autoCoralCount", 0)
    our_blue_tele = our_alliance.get("blue", {}).get("teleCoralCount", 0)
    our_red_auto = our_alliance.get("red", {}).get("autoCoralCount", 0)
    our_red_tele = our_alliance.get("red", {}).get("teleCoralCount", 0)

    # Note: TBA provides teleCoral data under "teleopCoralCount"
    tba_blue_auto = tba_blue.get("autoCoralCount")
    tba_blue_tele = tba_blue.get("teleopCoralCount")
    tba_red_auto = tba_red.get("autoCoralCount")
    tba_red_tele = tba_red.get("teleopCoralCount")

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

with open(PENALTIES_FILE, "w") as f:
    json.dump(penalties, f, indent=4)
print(f"Scouter penalties saved to {PENALTIES_FILE}")



# RELATIVE PENALTY AND 95% CONFIDENCE INTERVAL CALCULATIONS

# Count total number of scouting entries per scouter
total_entries = defaultdict(int)
for entry in scouting_data:
    scouter = entry.get("metadata", {}).get("scouterName", "Unknown")
    total_entries[scouter] += 1

# Since each entry contributes 2 metrics (teleCoralCount and autoCoralCount),
# maximum possible errors = number_of_entries * 2.
relative_penalties = {}
for scouter, count in total_entries.items():
    penalty_count = penalties.get(scouter, 0)
    max_possible = count * 2
    p = penalty_count / max_possible if max_possible > 0 else 0
    se = math.sqrt(p * (1 - p) / max_possible) if max_possible > 0 else 0
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

with open(RELATIVE_FILE, "w") as f:
    json.dump(relative_penalties, f, indent=4)
print(f"Scouter relative penalties with confidence intervals saved to {RELATIVE_FILE}")

end_time = time.time()
print(f"Script run completed in {end_time - start_time:.2f} seconds.")
