import tbapy
import os
import json
from utils.seperation_bars import seperation_bar, small_seperation_bar

tba = tbapy.TBA(os.getenv('TBA_KEY'))

print(tba.team_events('frc4201'))

event_key = '2025caph' # (Hueneme Port Event Code)

event_info = tba.event_insights(event_key)

seperation_bar()
print(json.dumps(event_info, indent=4))

seperation_bar()

# # EVENT INFO PER TEAM?

# teams = ['frc4201', 'frc4']

# for team in teams:
#     small_seperation_bar(team.upper())
    
#     print(json.dumps())

# PER MATCH DATA?

match_data = tba.match(year=2025, event=event_key, number=32)
print(json.dumps(match_data, indent=4))

with open("outputs/data_test.json", "w") as f:
    json.dump(match_data, f, indent=4)