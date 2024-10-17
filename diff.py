import pandas as pd

# Example loading data
df_schedule = pd.read_csv('NFL_Finished_Games.csv')  # Your merged schedule with stats
team_strength = pd.read_csv('Team_Strength.csv')  # Your team strength data

# Clean column names by stripping any leading/trailing spaces
df_schedule.columns = df_schedule.columns.str.strip()
team_strength.columns = team_strength.columns.str.strip()

# Merge Winner (home team) with team_strength
df_home = pd.merge(df_schedule, team_strength, how='left', left_on='Winner', right_on='Team')

# Merge Loser (away team) with team_strength
df_away = pd.merge(df_schedule, team_strength, how='left', left_on='Loser', right_on='Team', suffixes=('_home', '_away'))

# Now you have `df_home` and `df_away`, which have home and away team data merged.
# Drop redundant columns from the second merge (like 'Team_away' or 'Week_away')
df_games = df_away.drop(columns=['Team_away'])

# List of features for which we'll calculate the home-away difference
features_to_diff = [
    'Off_Rush_Yds', 'Off_YPCar', 'Off_YPRec', 'Off_Pass_Yds', 'Off_Scoring',
    'Off_Completion_Rate', 'Off_3rd_Down_Conversion_Rate', 'Off_4th_Down_Conversion_Rate',
    'Def_Rush_Yds_Allowed', 'Def_YPCar_Allowed', 'Def_Pass_Yds_Allowed', 'Def_INT',
    'Def_Yds/Rec_Allowed', 'Def_Sacks', 'Def_3rd_Down_Stop_Rate', 'Def_4th_Down_Stop_Rate',
    'FG_Made', 'FG_Attempted', 'XP_Made', 'XP_%', 'FG_30+', 'FG_40+', 'FG_50+', 'FG_60+'
]

# Function to calculate differences between home and away teams and round to 2 decimal places
def calculate_feature_differences(df_games):
    for feature in features_to_diff:
        home_col = f'{feature}_home'
        away_col = f'{feature}_away'
        diff_col = f'{feature}_Diff'
        
        # Calculate the difference and round to 2 decimal places
        df_games[diff_col] = (df_games[home_col] - df_games[away_col]).round(2)
    
    return df_games

# Calculate the differences between home and away team strengths
df_games = calculate_feature_differences(df_games)

# Save the updated DataFrame to a CSV
df_games.to_csv("NFL_Games_With_Feature_Differences.csv", index=False)

print("Feature differences have been calculated and saved to NFL_Games_With_Feature_Differences.csv")
