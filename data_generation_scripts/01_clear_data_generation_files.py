from utils.seperation_bars import *
import os

# ===========================
# CONFIGURATION SECTION
# ===========================

data_generation_config_json_path = 'config/data_generation_config.json'
generated_raw_match_data_json_path = 'data/raw/generated_raw_match_data.json'

# ===========================
# MAIN SCRIPT SECTION
# ===========================

seperation_bar()
print("Script 01: Clear Data Generation Files\n")

try:
    if os.path.exists(data_generation_config_json_path):
        os.remove(data_generation_config_json_path)
        print(f"[INFO] Data Generation Config JSON Deleted at '{data_generation_config_json_path}'")
    else:
        print(f"[INFO] File '{data_generation_config_json_path}' does not exist. Skipping.")

    if os.path.exists(generated_raw_match_data_json_path):
        os.remove(generated_raw_match_data_json_path)
        print(f"[INFO] Generated Raw Match Data JSON Deleted at '{generated_raw_match_data_json_path}'")
    else:
        print(f"[INFO] File '{generated_raw_match_data_json_path}' does not exist. Skipping.")

    print("\n[INFO] Script 01: Completed successfully.")

except Exception as e:
    print(f"\n[ERROR] An error occurred: {e}")
    print("\nScript 01: Failed.")

seperation_bar()
