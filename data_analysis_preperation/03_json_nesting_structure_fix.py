import json

# Load the expected data structure to identify valid keys
with open("config/expected_data_structure.json", "r") as f:
    expected_structure = json.load(f)

metadata_keys = set(expected_structure["metadata"].keys())
variable_keys = set(expected_structure["variables"].keys())

# Load the input JSON data
with open("data/raw/matchapps_data.json", "r") as f:
    input_data = json.load(f)

# Process each entry in the input data
formatted_data = []
for entry in input_data:
    formatted_entry = {"metadata": {}, "variables": {}}

    # Extract metadata fields
    for key in metadata_keys:
        if key in entry["metadata"]:
            formatted_entry["metadata"][key] = entry["metadata"][key]

    # Extract variable fields and group them under "variables"
    for key in variable_keys:
        if key in entry:
            formatted_entry["variables"][key] = entry[key]

    # Preserve `_id` if needed
    if "_id" in entry:
        formatted_entry["_id"] = entry["_id"]

    formatted_data.append(formatted_entry)

# Save the transformed data to a new JSON file
with open("data/raw/formatted_match_data.json", "w") as f:
    json.dump(formatted_data, f, indent=4)

print("Conversion complete! The formatted data is saved in 'formatted_match_data.json'.")
