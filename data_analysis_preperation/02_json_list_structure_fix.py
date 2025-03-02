import json
import os
import traceback

def fix_json_structure(filepath):
    """
    Fixes improperly formatted JSON files where multiple root objects exist
    without being enclosed in a list.
    """
    with open(filepath, "r") as infile:
        content = infile.read().strip()
        
        # Ensure the content is formatted as a JSON array
        if not content.startswith("["):
            content = "[" + content.replace("}\n{", "},{") + "]"
        
        try:
            json_data = json.loads(content)
            return json_data
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON Fix Failed: {e}")
            return None

def save_fixed_json(filepath, output_path):
    """Reads, fixes, and saves the reformatted JSON."""
    try:
        fixed_json = fix_json_structure(filepath)
        if fixed_json is None:
            raise ValueError("Failed to fix JSON file.")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as outfile:
            json.dump(fixed_json, outfile, indent=4)
        print(f"[INFO] Fixed JSON saved to {output_path}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    INPUT_JSON_PATH = "data/raw/raw_match_data.json"  # Input JSON file
    OUTPUT_JSON_PATH = "data/raw/fixed_match_data.json"  # Output fixed JSON file
    
    save_fixed_json(INPUT_JSON_PATH, OUTPUT_JSON_PATH)
