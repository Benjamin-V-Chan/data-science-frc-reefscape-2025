import tbapy
import json
import os

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

with open('outputs\scouter_leaderboard\multiple_atch_data_tba.json', "w") as f:
    json.dump(data, f, indent=4)