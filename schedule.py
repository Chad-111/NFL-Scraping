import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# Function to handle upcoming games by setting points to 'N/A'
def handle_upcoming_games(df):
    df['Winner_Points'] = df.apply(lambda x: 'N/A' if x['game_status'] == 'upcoming' else x['Winner_Points'], axis=1)
    df['Loser_Points'] = df.apply(lambda x: 'N/A' if x['game_status'] == 'upcoming' else x['Loser_Points'], axis=1)
    return df

# Function to validate and format columns
def validate_and_format_columns(df):
    # 1. Check if 'Week' is an integer
    if 'Week' in df.columns:
        df['Week'] = pd.to_numeric(df['Week'], errors='coerce')  # Convert to numeric and coerce errors to NaN
        if df['Week'].isnull().any():
            print("Warning: Some 'Week' values could not be converted to integers.")
        else:
            print("All 'Week' values are valid integers.")
    
    # 2. Check if 'Date' is in 'YYYY-MM-DD' format
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')  # Convert to datetime
        if df['Date'].isnull().any():
            print("Warning: Some 'Date' values could not be converted to the correct date format.")
        else:
            print("All 'Date' values are valid and in 'YYYY-MM-DD' format.")
    
    # 3. Check if 'Time' is in the correct format (e.g., '8:20PM')
    if 'Time' in df.columns:
        try:
            df['Time'] = pd.to_datetime(df['Time'], format='%I:%M%p', errors='coerce').dt.time  # Convert to time
            if df['Time'].isnull().any():
                print("Warning: Some 'Time' values could not be converted to the correct time format.")
            else:
                print("All 'Time' values are valid and in 'HH:MM AM/PM' format.")
        except Exception as e:
            print(f"Error while converting 'Time': {e}")

    return df

# URL for the NFL schedule
url = "https://www.pro-football-reference.com/years/2024/games.htm"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Locate the schedule table by its ID
schedule_table = soup.find('table', {'id': 'games'})

# Read the HTML table into a DataFrame
df_schedule = pd.read_html(str(schedule_table))[0]

# Clean the schedule to remove header rows that are repeated within the data
df_schedule = df_schedule[df_schedule['Week'] != 'Week']

# Reset the index after dropping the unnecessary rows
df_schedule.reset_index(drop=True, inplace=True)

# Convert 'Date' to datetime format to easily filter upcoming games
df_schedule['Date'] = pd.to_datetime(df_schedule['Date'], errors='coerce')

# Clean and prepare the data by filtering necessary columns
df_schedule_played = df_schedule[['Week', 'Day', 'Date', 'Time', 'Winner/tie', 'Loser/tie', 'PtsW', 'PtsL']].copy()
df_schedule_played.columns = ['Week', 'Day', 'Date', 'Time', 'Winner', 'Loser', 'Winner_Points', 'Loser_Points']

# Validate and format columns for 'Week', 'Date', and 'Time'
df_schedule_played = validate_and_format_columns(df_schedule_played)

# Get today's date
today = datetime.today().date()

# Separate the games into finished and upcoming based on the Date
finished_games = df_schedule_played[df_schedule_played['Date'].dt.date < today].copy()
upcoming_games = df_schedule_played[df_schedule_played['Date'].dt.date >= today].copy()

# For upcoming games, reformat columns and rename 'Winner' and 'Loser' to 'Visitor' and 'Home'
upcoming_games = upcoming_games[['Week', 'Day', 'Date', 'Time', 'Winner', 'Loser']]
upcoming_games.columns = ['Week', 'Day', 'Date', 'Time', 'Visitor', 'Home']

# Add a 'game_status' column to indicate whether the game is completed or upcoming
finished_games['game_status'] = 'completed'
upcoming_games['game_status'] = 'upcoming'

# Apply the function to handle upcoming games (set points to 'N/A' for upcoming games)
upcoming_games = handle_upcoming_games(upcoming_games)

# Drop the 'game_status' column for saving
upcoming_games = upcoming_games.drop(columns=['game_status'])
finished_games = finished_games.drop(columns=['game_status'])

# Save finished and upcoming games to separate CSV files
finished_games.to_csv("Finished_Games.csv", index=False)
upcoming_games.to_csv("Upcoming_Games.csv", index=False)

print("Finished games have been saved to Finished_Games.csv")
print("Upcoming games have been saved to Upcoming_Games.csv")
