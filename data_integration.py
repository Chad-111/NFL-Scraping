import pandas as pd

# Step 1: Load the updated Finished and Upcoming games CSV files and the team strength dataset
finished_games_df = pd.read_csv('Finished_Games.csv')
upcoming_games_df = pd.read_csv('Upcoming_Games.csv')
team_strength_df = pd.read_csv('Team_Strength.csv')

# Step 2: Merge team strength with the finished and upcoming games

# Merge for finished games using Winner and Loser
finished_merged_home = pd.merge(finished_games_df, team_strength_df, left_on='Winner', right_on='Team', suffixes=('', '_home'), how='left')
finished_merged_full = pd.merge(finished_merged_home, team_strength_df, left_on='Loser', right_on='Team', suffixes=('_home', '_away'), how='left')

# Merge for upcoming games using Home and Visitor
upcoming_merged_home = pd.merge(upcoming_games_df, team_strength_df, left_on='Home', right_on='Team', suffixes=('', '_home'), how='left')
upcoming_merged_full = pd.merge(upcoming_merged_home, team_strength_df, left_on='Visitor', right_on='Team', suffixes=('_home', '_away'), how='left')

# Step 3: Save the finished games and upcoming games to separate CSV files
finished_merged_full.to_csv('NFL_Finished_Games.csv', index=False)
upcoming_merged_full.to_csv('NFL_Upcoming_Games.csv', index=False)

# Optional: Combine the finished and upcoming merged data into one DataFrame if needed
merged_data_full = pd.concat([finished_merged_full, upcoming_merged_full], ignore_index=True)

# Step 4: Clean the merged data by dropping duplicate team columns
merged_data_full.drop(columns=['Team_home', 'Team_away'], inplace=True)

# Step 5: Handle missing values for upcoming games (where stats will be N/A)
merged_data_full.fillna('N/A', inplace=True)

# Optional: Save the combined dataset if needed
merged_data_full.to_csv('NFL_Integrated_Data_2024.csv', index=False)

print("Data integration complete. The merged datasets have been saved as 'NFL_Finished_Games.csv' and 'NFL_Upcoming_Games.csv'.")
