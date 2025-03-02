# advanced-frc-data-science-template

An advanced template for FRC teams to use as their data science systems. Easy implementation into current FRC team systems.

### Features
   - Advanced print logging systems with error location detection
   - Robust scripts that will clean and validate data
   - Customizable Data Analysis Scripts that you can build off of
   - Customizable data generation scripts to generate/simulate a dataset to test
   - Robust, Monte Carlo Simulation-based data generation system
   - Highly versatile and customizable expected data structure JSON, allowing for a wide range of input data structures
   - Versatility and easy integration with any team's current data science systems

### Steps

1. **Download libraries**
   - Use `pip install -r requirements.txt`
   - Pip install local -e.

2. **Edit JSONs to personalize data science system**
   - Replace example data structure `expected_data_structure.json` to match your data's expected data structure
      - Ensure format is correct else it will not work (robust and built-in error logging in 01_data_structure_validation script to help and give feedback)
      - Pay attention to structure of pre-filled example data structure
   - Replace data generation configuration settings in `data_generation_config.json` to match your needs for data generation/simulation
      - Ensure format is correct else it will not work (robust and built-in error logging in 01_data_structure_validation script to help and give feedback)
      - Pay attention to structure of pre-filled example data generation configuration settings. Reference a copy of it when customizing simulation parameters
      - This config file will be used to generate/simulate a detailed and fully built-out dataset to test the data analysis system with
   - If you do not wish to generate/simulate a dataset, you can set the `running_data_generation` key to `false`

3. **Prepare Raw Data [SKIP IF YOU WILL BE GENERATING/SIMULATING A DATASET]**:
   - Place raw JSON file in `data/raw` and rename to `raw_match_data.json`

4. **Run Scripts in Order**:
   - `python data_generation_scripts/02_data_structure_validation.py`
   - Data Generation Scripts [SKIP IF YOU WILL *NOT* BE GENERATING/SIMULATING A DATASET]
      - `python data_generation_scripts/01_data_generation_config_json_creation.py`
      - `python data_generation_scripts/02_data_generation_config_validation.py`
   - Data Analysis Scripts
      - `python data_analysis_scripts/01_clear_files.py`
      - `python data_analysis_scripts/02_data_cleaning_and_preprocessing.py`
      - `python data_analysis_scripts/03_team_based_match_data_restructuring.py`
      - `python data_analysis_scripts/04_data_analysis_and_statistics_aggregation.py`
      - `python data_analysis_scripts/05_visualizations.py`

4. **View Results**:
   - Cleaned Match Data in `data/processed`.
   - Cleaned Team-based match data in `data/processed`.
   - Team statistics data in `outputs/team_data`.
   - Scouter Error Leaderboard in `outputs/statistics`.
   - Team Comparison Stats in `outputs/statistics`.
   - Advanced Team Comparison Stats in `outputs/team_data`.
   - Team Statistical Analysis in `outputs/team_data`.
   - Visualizations in `outputs/visualizations`.
