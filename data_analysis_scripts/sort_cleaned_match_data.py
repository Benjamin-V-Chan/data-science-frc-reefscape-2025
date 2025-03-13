import json

# Load the JSON data from file
with open('data\processed\cleaned_match_data.json', 'r') as f:
    data = json.load(f)

# Sort the list by the matchNumber field in ascending order
sorted_data = sorted(data, key=lambda item: item['metadata']['matchNumber'])

# Write the sorted JSON data to a new file
with open('data\processed\sorted_cleaned_match_data.json', 'w') as f:
    json.dump(sorted_data, f, indent=4)

print("JSON data has been sorted by ascending matchNumber and saved to 'sorted_match_data.json'.")
