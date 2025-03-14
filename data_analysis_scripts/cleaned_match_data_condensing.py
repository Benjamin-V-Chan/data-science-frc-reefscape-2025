import json

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
