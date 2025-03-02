import os
import csv
import json
import traceback
import pandas as pd
import numpy as np
from utils.seperation_bars import seperation_bar, small_seperation_bar
from utils.logging import log_message

# ===========================
# CONFIGURATION
# ===========================

# File Paths
EXPECTED_DATA_STRUCTURE_PATH = "config/expected_data_structure.json"
TEAM_BASED_MATCH_DATA_PATH = "data/processed/team_based_match_data.json"
TEAM_PERFORMANCE_DATA_PATH_JSON = "outputs/team_data/team_performance_data.json"
TEAM_PERFORMANCE_DATA_PATH_CSV = "outputs/team_data/team_performance_data.csv"

# Load Expected Data Structure
with open(EXPECTED_DATA_STRUCTURE_PATH, "r") as f:
    EXPECTED_DATA_STRUCTURE_DICT = json.load(f)

# ===========================
# CUSTOM METRICS CLASS
# ===========================

class CustomMetrics:
    """
    Define your custom metrics here.
    - Each function should take a pandas DataFrame (df) as input (data for one team).
    - Return a single calculated value.
    - Be decorated with @staticmethod.
    """
    
    @staticmethod
    def consistency_score(df):
        """Computes how consistent a team is across all matches."""
        consistency_scores = []
        for column in df.columns:
            if df[column].dtype in [np.float64, np.int64]:  # Quantitative
                std_dev = df[column].std()
                mean_val = df[column].mean()
                cv = std_dev / mean_val if mean_val != 0 else 1
                consistency_scores.append(1 - min(cv, 1))
            elif df[column].dtype == "O":  # Categorical
                most_common = df[column].value_counts().max()
                consistency_scores.append(most_common / len(df))
            elif df[column].dtype == bool:  # Binary
                major_value_count = max(df[column].sum(), len(df) - df[column].sum())
                consistency_scores.append(major_value_count / len(df))
        return round(np.mean(consistency_scores), 3) if consistency_scores else 0

class CustomMetrics:
    """
    Define your custom metrics here.
    - Each function should take a pandas DataFrame (df) as input (data for one team).
    - Return individual values, not nested dictionaries.
    - Be decorated with @staticmethod.
    """

    @staticmethod
    def consistency_score(df):
        """Computes how consistent a team is across all matches."""
        consistency_scores = []
        for column in df.columns:
            if df[column].dtype in [np.float64, np.int64]:  # Quantitative
                std_dev = df[column].std()
                mean_val = df[column].mean()
                cv = std_dev / mean_val if mean_val != 0 else 1
                consistency_scores.append(1 - min(cv, 1))
            elif df[column].dtype == "O":  # Categorical
                most_common = df[column].value_counts().max()
                consistency_scores.append(most_common / len(df))
            elif df[column].dtype == bool:  # Binary
                major_value_count = max(df[column].sum(), len(df) - df[column].sum())
                consistency_scores.append(major_value_count / len(df))
        return round(np.mean(consistency_scores), 3) if consistency_scores else 0

    @staticmethod
    def auto_coral_mean(df):
        """Computes the mean of autoCoral.L1, autoCoral.L2, autoCoral.L3, autoCoral.L4 per match."""
        auto_coral_vars = ["autoCoral.L1", "autoCoral.L2", "autoCoral.L3", "autoCoral.L4"]
        available_vars = [col for col in auto_coral_vars if col in df.columns]

        if not available_vars:
            return 0  # Default if no valid columns

        df["auto_coral_sum"] = df[available_vars].sum(axis=1, numeric_only=True)
        return round(df["auto_coral_sum"].mean(), 2)

    @staticmethod
    def auto_coral_max(df):
        """Computes the max of autoCoral.L1, autoCoral.L2, autoCoral.L3, autoCoral.L4 per match."""
        auto_coral_vars = ["autoCoral.L1", "autoCoral.L2", "autoCoral.L3", "autoCoral.L4"]
        available_vars = [col for col in auto_coral_vars if col in df.columns]

        if not available_vars:
            return 0  # Default if no valid columns

        df["auto_coral_sum"] = df[available_vars].sum(axis=1, numeric_only=True)
        return int(df["auto_coral_sum"].max())

    @staticmethod
    def tele_coral_mean(df):
        """Computes the mean of teleCoral.L1, teleCoral.L2, teleCoral.L3, teleCoral.L4 per match."""
        tele_coral_vars = ["teleCoral.L1", "teleCoral.L2", "teleCoral.L3", "teleCoral.L4"]
        available_vars = [col for col in tele_coral_vars if col in df.columns]

        if not available_vars:
            return 0  # Default if no valid columns

        df["tele_coral_sum"] = df[available_vars].sum(axis=1, numeric_only=True)
        return round(df["tele_coral_sum"].mean(), 2)

    @staticmethod
    def tele_coral_max(df):
        """Computes the max of teleCoral.L1, teleCoral.L2, teleCoral.L3, teleCoral.L4 per match."""
        tele_coral_vars = ["teleCoral.L1", "teleCoral.L2", "teleCoral.L3", "teleCoral.L4"]
        available_vars = [col for col in tele_coral_vars if col in df.columns]

        if not available_vars:
            return 0  # Default if no valid columns

        df["tele_coral_sum"] = df[available_vars].sum(axis=1, numeric_only=True)
        return int(df["tele_coral_sum"].max())
    
# ===========================
# HELPER FUNCTIONS
# ===========================

def log_teams_with_16_coral(team_data):
    """
    Logs match number and team number of teams that scored exactly 16 coral in a match.

    :param team_data: Dictionary containing match data for each team.
    """
    for team, data in team_data.items():
        matches = data.get("matches", [])
        for match in matches:
            match_number = match.get("metadata", {}).get("matchNumber")
            team_number = match.get("metadata", {}).get("robotTeam")

            # Calculate total coral sum
            coral_vars = ["autoCoral.L1", "autoCoral.L2", "autoCoral.L3", "autoCoral.L4",
                          "teleCoral.L1", "teleCoral.L2", "teleCoral.L3", "teleCoral.L4"]

            coral_sum = sum(match.get("variables", {}).get(var, 0) for var in coral_vars)

            if coral_sum == 16:
                log_message("INFO", f"Match {match_number}, Team {team_number} scored 16 coral.")


def flatten_expected_vars(dictionary, return_dict=None, prefix=""):
    """Flattens only variable names but keeps their properties intact."""
    if return_dict is None:
        return_dict = {}

    for key, value in dictionary.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict) and "statistical_data_type" not in value:
            flatten_expected_vars(value, return_dict, full_key)
        else:
            return_dict[full_key] = value

    return return_dict

FLATTENED_EXPECTED_VARIABLES = flatten_expected_vars(EXPECTED_DATA_STRUCTURE_DICT.get("variables", {}))

def convert_to_serializable(obj):
    """Converts NumPy and Pandas types to standard Python types for JSON serialization."""
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        return float(obj) if not np.isnan(obj) else None
    if isinstance(obj, (bool, np.bool_)):
        return int(obj)  # Convert bool to 0/1 for CSV readability
    if isinstance(obj, (pd.Series, pd.DataFrame)):
        return obj.to_dict()
    if isinstance(obj, dict):
        return {str(k): convert_to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return '"' + ", ".join(map(str, obj)) + '"'  # Ensure CSV stores as a single cell
    return obj

def determine_statistical_type(variable_name):
    """Returns the statistical data type (quantitative, categorical, binary) based on the expected structure."""
    return FLATTENED_EXPECTED_VARIABLES.get(variable_name, {}).get("statistical_data_type", "unknown")

def calculate_team_performance_data(team_data):
    """
    Computes performance metrics and applies custom metrics per team.

    :param team_data: Dictionary containing match data for each team.
    :return: A dictionary with aggregated team statistics.
    """
    all_team_performance_data = {}

    for team, data in team_data.items():
        matches = data.get("matches", [])
        if not matches:
            all_team_performance_data[team] = {"number_of_matches": 0}
            continue

        flat_data = [{k: v for k, v in flatten_expected_vars(match["variables"]).items()} for match in matches]
        df = pd.DataFrame(flat_data)
        df.dropna(axis=1, how="all", inplace=True)

        team_performance = {"number_of_matches": len(df)}

        # Store raw match values
        for column in df.columns:
            team_performance[f"{column}_values"] = convert_to_serializable(df[column].tolist())

        # Compute statistics
        for column in df.columns:
            stat_type = determine_statistical_type(column)

            if stat_type == "quantitative":
                df[column] = pd.to_numeric(df[column], errors='coerce')

                team_performance[f"{column}_mean"] = convert_to_serializable(df[column].mean())
                team_performance[f"{column}_std_dev"] = convert_to_serializable(df[column].std())
                team_performance[f"{column}_range"] = convert_to_serializable(df[column].max() - df[column].min())
                team_performance[f"{column}_median"] = convert_to_serializable(df[column].median())
                team_performance[f"{column}_max"] = convert_to_serializable(df[column].max())
                team_performance[f"{column}_min"] = convert_to_serializable(df[column].min())

                # # First and Third Quartile
                team_performance[f"{column}_q1"] = convert_to_serializable(df[column].quantile(0.25))
                team_performance[f"{column}_q3"] = convert_to_serializable(df[column].quantile(0.75))
                team_performance[f"{column}_iqr"] = convert_to_serializable(df[column].quantile(0.75) - df[column].quantile(0.25))

        # Apply Custom Metrics
        for metric_name in dir(CustomMetrics):
            if not metric_name.startswith("_") and callable(getattr(CustomMetrics, metric_name)):
                team_performance[metric_name] = getattr(CustomMetrics, metric_name)(df)

        all_team_performance_data[str(team)] = team_performance  # Ensure team key is a string

    return all_team_performance_data


# ===========================
# MAIN SCRIPT
# ===========================

def main():
    seperation_bar()
    log_message("INFO", "Script 03: Data Analysis & Statistics Aggregation Started")

    try:
        small_seperation_bar("LOAD DATA")
        log_message("INFO", "Loading team-based match data.")

        with open(TEAM_BASED_MATCH_DATA_PATH, 'r') as infile:
            team_data = json.load(infile)

        team_performance_data = calculate_team_performance_data(team_data)

        small_seperation_bar("SAVE DATA")
        
        small_seperation_bar("LOG TEAMS WITH 16 CORAL")
        log_teams_with_16_coral(team_data)
        
        # Save JSON
        log_message("INFO", f"Saving JSON team performance data to: {TEAM_PERFORMANCE_DATA_PATH_JSON}")
        os.makedirs(os.path.dirname(TEAM_PERFORMANCE_DATA_PATH_JSON), exist_ok=True)
        with open(TEAM_PERFORMANCE_DATA_PATH_JSON, 'w') as json_file:
            json.dump(convert_to_serializable(team_performance_data), json_file, indent=4)

        # Save CSV
        log_message("INFO", f"Saving CSV team performance data to: {TEAM_PERFORMANCE_DATA_PATH_CSV}")
        os.makedirs(os.path.dirname(TEAM_PERFORMANCE_DATA_PATH_CSV), exist_ok=True)

        with open(TEAM_PERFORMANCE_DATA_PATH_CSV, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)

            all_headers = sorted({key for team in team_performance_data.values() for key in team.keys()})
            all_headers.insert(0, "team")
            csv_writer.writerow(all_headers)

            for team, metrics in team_performance_data.items():
                row = [team] + [convert_to_serializable(metrics.get(k, "")) for k in all_headers[1:]]
                csv_writer.writerow(row)

        small_seperation_bar("SUMMARY")
        log_message("INFO", f"Total teams processed: {len(team_performance_data)}")

        log_message("INFO", "Script 03: Completed Successfully")

    except Exception as e:
        log_message("ERROR", f"An unexpected error occurred: {e}")
        print(traceback.format_exc())

    seperation_bar()


if __name__ == "__main__":
    main()
