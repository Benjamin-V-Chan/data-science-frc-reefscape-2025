import os
import json
import traceback
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import parallel_coordinates
from utils.logging import log_message

# ===========================
# CONFIGURATION SECTION
# ===========================

TEAM_PERFORMANCE_DATA_PATH_JSON = "outputs/team_data/team_performance_data.json"
VISUALIZATIONS_DIR = "outputs/visualizations"

# Bar Chart Configuration
BAR_CHART_CONFIG = {
    "distribution a": {"variable_metrics": ["var1_mean"], "visualizations": ["bar_chart"]},
    "distribution b": {
        "variable_metrics": ["var2_mean", "var2_max", "var3_percent_True"],
        "visualizations": ["stacked_bar_chart", "grouped_bar_chart", "parallel_coordinates_plot"]
    }
}

# Boxplot Configuration
BOXPLOT_CONFIG = {
    "Boxplot for Variable 1": ["var1"],
    "Boxplot for Variable 2 and 3": ["var2"]
}

# ===========================
# HELPER FUNCTIONS
# ===========================

def load_team_performance_data():
    """Loads the team performance JSON data."""
    if not os.path.exists(TEAM_PERFORMANCE_DATA_PATH_JSON):
        log_message("ERROR", f"Team performance data file not found: {TEAM_PERFORMANCE_DATA_PATH_JSON}")
        return None

    with open(TEAM_PERFORMANCE_DATA_PATH_JSON, "r") as infile:
        return json.load(infile)

def ensure_directory_exists(directory):
    """Ensures that a directory exists."""
    os.makedirs(directory, exist_ok=True)

def extract_metric_data(team_data, metric_list):
    """
    Extracts relevant metrics from the team data.

    :param team_data: The dictionary containing team statistics.
    :param metric_list: List of metric names to extract.
    :return: A DataFrame containing the extracted metrics.
    """
    extracted_data = []

    for team, stats in team_data.items():
        row = {"team": team}
        for metric in metric_list:
            row[metric] = stats.get(metric, 0)  # Default to 0 if metric is missing
        extracted_data.append(row)

    return pd.DataFrame(extracted_data)

# ===========================
# BAR CHART VISUALIZATION FUNCTIONS
# ===========================

def generate_bar_chart(df, title, save_path):
    """Generates a simple bar chart for a single metric comparison."""
    metric = df.columns[1]  # Assuming "team" is the first column
    df.set_index("team")[metric].plot(kind="bar", figsize=(10, 5), color="skyblue", edgecolor="black")

    plt.title(title)
    plt.xlabel("Teams")
    plt.ylabel(metric)
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    log_message("INFO", f"Bar Chart saved: {save_path}")

def generate_grouped_bar_chart(df, title, save_path):
    """Generates a grouped bar chart comparing teams for each variable metric."""
    df.set_index("team").plot(kind="bar", figsize=(12, 6), colormap="viridis")

    plt.title(title)
    plt.xlabel("Teams")
    plt.ylabel("Values")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Metrics")
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    log_message("INFO", f"Grouped Bar Chart saved: {save_path}")

def generate_stacked_bar_chart(df, title, save_path):
    """Generates a stacked bar chart comparing teams across multiple metrics."""
    df.set_index("team").plot(kind="bar", stacked=True, figsize=(12, 6), colormap="plasma")

    plt.title(title)
    plt.xlabel("Teams")
    plt.ylabel("Values")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Metrics")
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    log_message("INFO", f"Stacked Bar Chart saved: {save_path}")

def generate_parallel_coordinates_plot(df, title, save_path):
    """Generates a parallel coordinates plot to compare multiple metrics per team."""
    df_normalized = df.copy()
    df_normalized[df.columns[1:]] = df_normalized[df.columns[1:]].apply(lambda x: (x - x.min()) / (x.max() - x.min()))

    plt.figure(figsize=(12, 6))
    parallel_coordinates(df_normalized, class_column="team", colormap=plt.get_cmap("tab10"), linewidth=2)

    plt.title(title)
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Metrics")
    plt.ylabel("Normalized Values (0-1)")
    plt.legend(title="Teams", bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    log_message("INFO", f"Parallel Coordinates Plot saved: {save_path}")

# ===========================
# BOXPLOT VISUALIZATION FUNCTION
# ===========================

def generate_boxplot(team_data, variable, save_path):
    """
    Generates a boxplot for a single variable across teams.

    :param team_data: Dictionary containing team performance data.
    :param variable: Variable name for the boxplot.
    :param save_path: Path to save the plot.
    """
    df = extract_metric_data(team_data, [variable])

    if df.empty:
        log_message("WARNING", f"No valid data for {variable}, skipping boxplot.")
        return

    plt.figure(figsize=(10, 6))
    df.boxplot(column=variable, by="team", grid=False)

    plt.title(f"Boxplot for {variable} across Teams")
    plt.xlabel("Teams")
    plt.ylabel(variable.replace("_", " ").title())
    plt.xticks(rotation=45, ha="right")

    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    log_message("INFO", f"Boxplot saved: {save_path}")

# ===========================
# MAIN FUNCTION
# ===========================

def main():
    log_message("INFO", "Script 04: Visualizations Started")

    try:
        team_performance_data = load_team_performance_data()
        if team_performance_data is None:
            raise ValueError("No team performance data available.")

        ensure_directory_exists(VISUALIZATIONS_DIR)

        # Process bar charts
        for title, config in BAR_CHART_CONFIG.items():
            variable_metrics = config["variable_metrics"]
            visualizations = config["visualizations"]

            log_message("INFO", f"Processing {title}: {variable_metrics}")

            df = extract_metric_data(team_performance_data, variable_metrics)
            if df.empty:
                log_message("WARNING", f"No data found for {title}. Skipping...")
                continue

            for vis in visualizations:
                save_path = os.path.join(VISUALIZATIONS_DIR, f"{title}_{vis}.png")

                if vis == "bar_chart" and len(variable_metrics) == 1:
                    generate_bar_chart(df, title, save_path)
                elif vis == "grouped_bar_chart" and len(variable_metrics) > 1:
                    generate_grouped_bar_chart(df, title, save_path)
                elif vis == "stacked_bar_chart" and len(variable_metrics) > 1:
                    generate_stacked_bar_chart(df, title, save_path)
                elif vis == "parallel_coordinates_plot" and len(variable_metrics) > 1:
                    generate_parallel_coordinates_plot(df, title, save_path)

        # Process boxplots
        for title, variables in BOXPLOT_CONFIG.items():
            for variable in variables:
                log_message("INFO", f"Generating boxplot for {variable}")
                save_path = os.path.join(VISUALIZATIONS_DIR, f"{variable}_boxplot.png")
                generate_boxplot(team_performance_data, variable, save_path)

        log_message("INFO", "Script 04: Completed Successfully")

    except Exception as e:
        log_message("ERROR", f"Unexpected error: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
