import tbapy
import json
import os

TBA_KEY = os.getenv("TBA_KEY")

tba = tbapy.TBA(TBA_KEY)
event_key = "2025caph"
year = 2025

match_num = 5

tba_match = tba.match(year=year, event=event_key, number=match_num)

with open(f'outputs\scouter_leaderboard\match_{match_num}_single_match_data_tba.json', "w") as f:
    json.dump(tba_match, f, indent=4)