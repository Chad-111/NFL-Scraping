import os
import pandas as pd

# Define file paths for offensive, defensive, and special team stats directories
offensive_dir = "./Offensive Team Stats"
defensive_dir = "./Defensive Team Stats"
special_dir = "./Special Team Stats"


# Load all offensive CSVs
offensive_files = {
    "downs": "Offensive_Downs.csv",
    "passing": "Offensive_Passing.csv",
    "receiving": "Offensive_Receiving.csv",
    "rushing": "Offensive_Rushing.csv",
    "scoring": "Offensive_Scoring.csv"
}

# Load all defensive CSVs
defensive_files = {
    "downs": "Defensive_Downs.csv",
    "fumbles": "Defensive_Fumbles.csv",
    "passing": "Defensive_Passing.csv",
    "receiving": "Defensive_Receiving.csv",
    "rushing": "Defensive_Rushing.csv",
    "scoring": "Defensive_Scoring.csv",
    "tackles": "Defensive_Tackles.csv"
}

# Load all special teams CSVs
special_files = {
    "goals": "Special_Field_Goals.csv",
    "returns": "Special_Punt_Returns.csv",
    "punts": "Special_Punts.csv",
    "scoring": "Special_Scoring.csv"
}

# Function to load, clean, and rename team names
def load_and_clean_data(filepath):
    df = pd.read_csv(filepath)
    df.dropna(inplace=True)  # Drop rows with missing values
    df['Team'] = df['Team'].str.strip()  # Clean team names
    return df

# Load offensive stats
offensive_data = {}
for category, file_name in offensive_files.items():
    offensive_data[category] = load_and_clean_data(os.path.join(offensive_dir, file_name))

# Load defensive stats
defensive_data = {}
for category, file_name in defensive_files.items():
    defensive_data[category] = load_and_clean_data(os.path.join(defensive_dir, file_name))

# Load special teams stats
special_data = {}
for category, file_name in special_files.items():
    special_data[category] = load_and_clean_data(os.path.join(special_dir, file_name))

# Select key stats for team strength

# Offensive: Total Yards, TDs, Yards per Carry, Pass Yards, Rush Yards
# Defensive: Total Yards Allowed, Sacks, INTs, Rush Defense

# Calculate 3rd and 4th down conversion rates for offense
offensive_data['downs']['3rd Down Conversion Rate'] = (offensive_data['downs']['3rd Md'] / offensive_data['downs']['3rd Att'] * 100).round(2)
offensive_data['downs']['4th Down Conversion Rate'] = (offensive_data['downs']['4th Md'] / offensive_data['downs']['4th Att'] * 100).round(2)

# Optionally, you can add a '%' symbol as well
# offensive_data['downs']['3rd Down Conversion Rate'] = offensive_data['downs']['3rd Down Conversion Rate'].astype(str) + '%'
# offensive_data['downs']['4th Down Conversion Rate'] = offensive_data['downs']['4th Down Conversion Rate'].astype(str) + '%'

offensive_team_strength = pd.DataFrame({
    'Team': offensive_data['rushing']['Team'],
    'Off_Rush_Yds': offensive_data['rushing']['Rush Yds'],
    'Off_YPCar': offensive_data['rushing']['YPC'],
    'Off_YPRec': offensive_data['receiving']['Yds/Rec'],
    'Off_Pass_Yds': offensive_data['passing']['Pass Yds'],
    'Off_Scoring': offensive_data['scoring']['Tot TD'],
    'Off_Completion_Rate': offensive_data['passing']['Cmp %'], 
    'Off_3rd_Down_Conversion_Rate': offensive_data['downs']['3rd Down Conversion Rate'],  # Add 3rd down conversion rate
    'Off_4th_Down_Conversion_Rate': offensive_data['downs']['4th Down Conversion Rate'],  # Add 4th down conversion rate
})

# Calculate 3rd and 4th down stop rates
defensive_data['downs']['3rd Down Stop Rate'] = (defensive_data['downs']['3rd Att'] - defensive_data['downs']['3rd Md']) / defensive_data['downs']['3rd Att']
defensive_data['downs']['4th Down Stop Rate'] = (defensive_data['downs']['4th Att'] - defensive_data['downs']['4th Md']) / defensive_data['downs']['4th Att']

defensive_team_strength = pd.DataFrame({
    'Team': defensive_data['rushing']['Team'],
    'Def_Rush_Yds_Allowed': defensive_data['rushing']['Rush Yds'],
    'Def_YPCar_Allowed': defensive_data['rushing']['YPC'],
    'Def_Pass_Yds_Allowed': defensive_data['passing']['Yds'],
    'Def_INT': defensive_data['passing']['INT'],
    'Def_Yds/Rec_Allowed': defensive_data['receiving']['Yds/Rec'],
    'Def_Sacks': defensive_data['tackles']['Sck'],
    'Def_3rd_Down_Stop_Rate': defensive_data['downs']['3rd Down Stop Rate'],  # 3rd down stop rate
    'Def_4th_Down_Stop_Rate': defensive_data['downs']['4th Down Stop Rate'],  # 4th down stop rate
})

# Convert 3rd and 4th Down Stop Rates to percentages and round to 2 decimal places
defensive_team_strength['Def_3rd_Down_Stop_Rate'] = (defensive_team_strength['Def_3rd_Down_Stop_Rate'] * 100).round(2)
defensive_team_strength['Def_4th_Down_Stop_Rate'] = (defensive_team_strength['Def_4th_Down_Stop_Rate'] * 100).round(2)

# defensive_team_strength['Def_3rd_Down_Stop_Rate'] = defensive_team_strength['Def_3rd_Down_Stop_Rate'].astype(str) + '%'
# defensive_team_strength['Def_4th_Down_Stop_Rate'] = defensive_team_strength['Def_4th_Down_Stop_Rate'].astype(str) + '%'


# Load the special teams stats
special_team_strength = pd.DataFrame({
    'Team': special_data['goals']['Team'],
    'FG_Made': special_data['goals']['FGM'],
    'FG_Attempted': special_data['goals']['Att'],
    'FG_30_39_Attempts': special_data['goals']['FG_30_39_Attempts'],
    'FG_40_49_Attempts': special_data['goals']['FG_40_49_Attempts'],
    'FG_50_59_Attempts': special_data['goals']['FG_50_59_Attempts'],
    'FG_60_Attempts': special_data['goals']['FG_60_Attempts'],
    'FG_30+': special_data['goals']['FG_30_39_Percentage'],
    'FG_40+': special_data['goals']['FG_40_49_Percentage'],
    'FG_50+': special_data['goals']['FG_50_59_Percentage'],
    'FG_60+': special_data['goals']['FG_60_Percentage'],
    'Longest_FG': special_data['goals']['Lng'],
    'Punts': special_data['punts']['Punts'],
    'Punt_Avg': special_data['punts']['Avg'],
    'XP_Made': special_data['scoring']['XPM'],
    'XP_%': special_data['scoring']['XP Pct'],
})

# Add a binary column indicating if the team has attempted field goals from the specific yardage range
special_team_strength['FG_30_Attempted_Flag'] = special_team_strength['FG_30_39_Attempts'].notna().astype(int)
special_team_strength['FG_40_Attempted_Flag'] = special_team_strength['FG_40_49_Attempts'].notna().astype(int)
special_team_strength['FG_50_Attempted_Flag'] = special_team_strength['FG_50_59_Attempts'].notna().astype(int)
special_team_strength['FG_60_Attempted_Flag'] = special_team_strength['FG_60_Attempts'].notna().astype(int)

# Merge the updated special team stats with other team strength data
team_strength = pd.merge(offensive_team_strength, defensive_team_strength, on='Team')
team_strength = pd.merge(team_strength, special_team_strength, on='Team')

# Save the updated team strength data to CSV
team_strength.to_csv("Team_Strength.csv", index=False)

print("Updated Team Strength data has been saved to Team_Strength.csv")

