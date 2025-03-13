#!/usr/bin/env python3
import os
import json
from collections import defaultdict
import tbapy

# --- Configuration ---
# File names (adjust if necessary)
SUMMARY_FILE = "match_alliance_summary.json"   # Aggregated metrics per match from scouting data
SCOUTING_FILE = "data\processed\cleaned_match_data.json"        # Raw scouting data entries
PENALTIES_FILE = "scouter_penalties.json"        # Output file for scouter penalty counts
RELATIVE_FILE = "scouter_penalties_relative.json" # Output file for relative penalty percentages

# TBA configuration (set your TBA key in your environment)
TBA_KEY = os.getenv("TBA_KEY")
if not TBA_KEY:
    print("Please set the TBA_KEY environment variable.")
    exit(1)

tba = tbapy.TBA(TBA_KEY)
event_key = "2025caph"  # Adjust as needed
year = 2025             # Adjust as needed

# --- Load the aggregated alliance metrics from scouting data ---
with open(SUMMARY_FILE, "r") as f:
    alliance_summary = json.load(f)

# --- Load the raw scouting data ---
with open(SCOUTING_FILE, "r") as f:
    scouting_data = json.load(f)

# --- Group scouting entries by match number and alliance ---
# This dictionary will map each match number to a dict with keys "red" and "blue"
# whose values are sets of scouter names that provided entries for that alliance.
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

# --- Initialize penalty tracker for each scouter ---
penalties = defaultdict(int)

# --- Iterate over each match number in the aggregated summary ---
for match_num_key, our_alliance in alliance_summary.items():
    try:
        # Ensure the match number is an integer
        match_num = int(match_num_key)
    except Exception:
        match_num = match_num_key

    print(f"Processing match {match_num}...")
    # Retrieve TBA match data for this match number using tbapy
    try:
        tba_match = tba.match(year=year, event=event_key, number=match_num)
    except Exception as e:
        print(f"Error retrieving TBA match data for match {match_num}: {e}")
        continue

    # Extract TBA alliance data from the score_breakdown
    tba_score = tba_match.get("score_breakdown", {})
    tba_blue = tba_score.get("blue", {})
    tba_red  = tba_score.get("red", {})

    # Get our aggregated values for each alliance
    our_blue_auto = our_alliance.get("blue", {}).get("autoCoralCount", 0)
    our_blue_tele = our_alliance.get("blue", {}).get("teleCoralCount", 0)
    our_red_auto  = our_alliance.get("red", {}).get("autoCoralCount", 0)
    our_red_tele  = our_alliance.get("red", {}).get("teleCoralCount", 0)

    # TBA data: assume autoCoralCount is directly provided,
    # and teleCoral data is under "teleopCoralCount".
    tba_blue_auto = tba_blue.get("autoCoralCount")
    tba_blue_tele = tba_blue.get("teleopCoralCount")
    tba_red_auto  = tba_red.get("autoCoralCount")
    tba_red_tele  = tba_red.get("teleopCoralCount")

    # For each alliance, compare our values to TBA's.
    # For every mismatch (if the TBA value exists), add one penalty point for each scouter in that alliance.
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

# --- Save the raw penalty leaderboard to a JSON file ---
with open(PENALTIES_FILE, "w") as f:
    json.dump(penalties, f, indent=4)

print(f"Scouter penalties saved to {PENALTIES_FILE}")

# --- Compute total number of scouting entries per scouter ---
total_entries = defaultdict(int)
for entry in scouting_data:
    scouter = entry.get("metadata", {}).get("scouterName", "Unknown")
    total_entries[scouter] += 1

# --- Create relative percentages for each scouter ---
# For each scouter, penalty percent = (penalty count / total entries) * 100.
relative_penalties = {}
for scouter, count in total_entries.items():
    penalty_count = penalties.get(scouter, 0)
    percent = (penalty_count / count) * 100 if count > 0 else 0
    relative_penalties[scouter] = {
        "total_entries": count,
        "penalties": penalty_count,
        "penalty_percent": percent
    }

# --- Save the relative penalty leaderboard to a JSON file ---
with open(RELATIVE_FILE, "w") as f:
    json.dump(relative_penalties, f, indent=4)

print(f"Scouter relative penalties saved to {RELATIVE_FILE}")
