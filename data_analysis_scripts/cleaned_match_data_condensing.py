import tbapy
import json
import os

with open('data\processed\sorted_cleaned_match_data.json', "r") as infile:
    raw_data = json.load(infile)

data = {}

for entry in raw_data:
    match_num = entry['metadata']['matchNumber']
    
    if match_num not in data:
        data[match_num] = {'red': {},
                           'blue': {}
                           }
        
    position = entry['metadata']['robotPosition']
    
    if 'red' in position:
        alliance = 'red'
    else:
        alliance = 'blue'
    
    climb = entry['variables']['climb']
    if climb == 'failed':
        data[match_num][alliance][position] = 'none'
    else:
         data[match_num][alliance][position] = climb

with open(f'outputs\scouter_leaderboard\cleaned_match_data_from_scouters.json', "w") as f:
    json.dump(data, f, indent=4)

TBA_KEY = os.getenv("TBA_KEY")

tba = tbapy.TBA(TBA_KEY)
event_key = "2025caph"
year = 2025

match_num = 10

colors = ['red', 'blue']
robots = ['endGameRobot1', 'endGameRobot2', 'endGameRobot3']

data = {}

for match in range(1, match_num + 1):

    tba_match = tba.match(year=year, event=event_key, number=match)

    data[str(match)] = {}
    
    for color in colors:
        
        data[str(match)][color] = {}
        
        for robot in robots:
            data[str(match)][color][robot] = tba_match['score_breakdown'][color][robot]

with open('outputs\scouter_leaderboard\multiple_match_data_tba.json', "w") as f:
    json.dump(data, f, indent=4)