import os
import shutil

def reset_folders(config, base_path="."):
    """
    Resets the directory structure based on the provided config dictionary.
    Deletes all files and subdirectories except for specified files and folders.

    Parameters:
        config (dict): Dictionary defining folder structure and files/folders to keep.
        base_path (str): Base directory for the operation.
    """
    for folder, content in config.items():
        folder_path = os.path.join(base_path, folder)

        if isinstance(content, dict):  # It's a folder
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)  # Create missing folders
            else:
                keep_files, keep_folders = extract_keep_items(content)

                print(f"\nProcessing Folder: {folder_path}")
                print(f"Keeping Files: {keep_files}")
                print(f"Keeping Folders: {keep_folders}")

                # Process files FIRST before clearing folder
                clear_folder(folder_path, keep_files, keep_folders)

            # Recursively process subdirectories AFTER preserving files
            reset_folders(content, folder_path)
        elif content is None:  # It's a file
            os.makedirs(os.path.dirname(folder_path), exist_ok=True)

def extract_keep_items(content):
    """Extracts files and folders that should be preserved."""
    keep_files = set()
    keep_folders = set()

    for key, value in content.items():
        if value is None:  # If value is None, it means it's a file
            keep_files.add(key)
        else:  # Otherwise, it's a folder
            keep_folders.add(key)

    return keep_files, keep_folders

def clear_folder(folder_path, keep_files, keep_folders):
    """Clears all files and subdirectories in a folder except specified items."""
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        print(f"Checking: {item_path} (is file: {os.path.isfile(item_path)}, is dir: {os.path.isdir(item_path)})")

        if item in keep_files or item in keep_folders:
            print(f"Skipping: {item}")
            continue

        if os.path.isfile(item_path):
            print(f"Deleting file: {item_path}")
            os.remove(item_path)
        elif os.path.isdir(item_path):
            print(f"Deleting folder: {item_path}")
            shutil.rmtree(item_path)

if __name__ == "__main__":
    
    config = {
        "data": {
            "processed": {},  
            "raw": {
                "raw_match_data.json": None
            }
        },
        "outputs": {
            "statistics": {},
            "team_data": {},
            "visualizations": {},
            "scouter_leaderboard": {}
        },
        "config": {
            "data_generation_config_default_values_config.json": None,
            "expected_data_structure.json": None
        }
    }

    import json
    print("Config being used:", json.dumps(config, indent=4))

    reset_folders(config)
