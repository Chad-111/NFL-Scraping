import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

# Define the mapping from short names to full club names
team_name_mapping = {
    "49ers": "San Francisco 49ers",
    "Commanders": "Washington Commanders",
    "Ravens": "Baltimore Ravens",
    "Seahawks": "Seattle Seahawks",
    "Bills": "Buffalo Bills",
    "Bengals": "Cincinnati Bengals",
    "Saints": "New Orleans Saints",
    "Vikings": "Minnesota Vikings",
    "Packers": "Green Bay Packers",
    "Buccaneers": "Tampa Bay Buccaneers",
    "Cardinals": "Arizona Cardinals",
    "Colts": "Indianapolis Colts",
    "Chiefs": "Kansas City Chiefs",
    "Cowboys": "Dallas Cowboys",
    "Bears": "Chicago Bears",
    "Falcons": "Atlanta Falcons",
    "Lions": "Detroit Lions",
    "Texans": "Houston Texans",
    "Jaguars": "Jacksonville Jaguars",
    "Raiders": "Las Vegas Raiders",
    "Broncos": "Denver Broncos",
    "Rams": "Los Angeles Rams",
    "Jets": "New York Jets",
    "Steelers": "Pittsburgh Steelers",
    "Giants": "New York Giants",
    "Eagles": "Philadelphia Eagles",
    "Panthers": "Carolina Panthers",
    "Titans": "Tennessee Titans",
    "Browns": "Cleveland Browns",
    "Chargers": "Los Angeles Chargers",
    "Patriots": "New England Patriots",
    "Dolphins": "Miami Dolphins"
}

# Define the folders for each category
folders = {
    "Top 25 Players": ["Passing_Yards", "Rushing_Yards", "Reciving_Receptions", "Defensive_Forced_Fumbles", "Defensive_Combine_Tackles", "Defensive_Interceptions", "Kicking_Field_Goals_Made", "Punting_Average_Yards", "Punt_Returns_Average_Yards"],
    "Offensive Team Stats": ["Offensive_Passing", "Offensive_Rushing", "Offensive_Receiving", "Offensive_Scoring", "Offensive_Downs"],
    "Defensive Team Stats": ["Defensive_Passing", "Defensive_Rushing", "Defensive_Receiving", "Defensive_Scoring", "Defensive_Tackles", "Defensive_Downs", "Defensive_Fumbles", "Defensive_Interceptions"],
    "Special Team Stats": ["Special_Field_Goals", "Special_Scoring", "Special_Punts", "Special_Punt_Returns"]
}

# Create the folders if they do not exist
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Function to process and clean the special field goals data with simplified column names
def process_special_field_goals(df):
    def split_attempts_made(column, simplified_name):
        attempts_made = df[column].str.split('_', expand=True)
        attempts_made.columns = [f"{simplified_name}_Attempts", f"{simplified_name}_Made"]
        attempts_made = attempts_made.fillna('0').astype(int)  # Fill missing values and convert to integers
        return attempts_made

    # Define ranges and simplified column names
    fg_ranges = {
        '1-19 > A-M': 'FG_1_19',
        '20-29 > A-M': 'FG_20_29',
        '30-39 > A-M': 'FG_30_39',
        '40-49 > A-M': 'FG_40_49',
        '50-59 > A-M': 'FG_50_59',
        '60+ > A-M': 'FG_60'
    }
    
    for column, simplified_name in fg_ranges.items():
        attempts_made = split_attempts_made(column, simplified_name)
        df = pd.concat([df, attempts_made], axis=1)
    
    # Drop the original combined columns
    df = df.drop(columns=fg_ranges.keys())
    
    # Optionally: Compute percentages for each range with simplified column names
    for simplified_name in fg_ranges.values():
        attempts_col = f"{simplified_name}_Attempts"
        made_col = f"{simplified_name}_Made"
        percentage_col = f"{simplified_name}_Percentage"
        # Replace the percentage calculation with a check for 0 attempts
        df[percentage_col] = (df[made_col] / df[attempts_col] * 100).fillna(-1).round(2)
        df.loc[df[attempts_col] == 0, percentage_col] = 0  # Replace -1.0 with 0 where no attempts were made
        
    return df

# Scrape table function
def scrape_table(url, name):
    print(f"Scraping {name} from {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table')
    if table:
        headers = []
        rows = []
        header_row = table.find_all('th')
        for header in header_row:
            headers.append(header.get_text().strip())
        
        for row in table.find_all('tr')[1:]:
            columns = row.find_all('td')
            row_data = []
            for col in columns:
                # Extract team name if found in div
                club_fullname = col.find('div', class_='d3-o-club-fullname')
                if club_fullname:
                    team_name = club_fullname.get_text().strip()
                    full_team_name = team_name_mapping.get(team_name, team_name)
                    row_data.append(full_team_name)
                else:
                    text = col.get_text(separator=" ").strip()
                    row_data.append(text)
            rows.append(row_data)

        if headers and rows:
            df = pd.DataFrame(rows, columns=headers)
            return df
    return None

# Validate data function
def validate_data(df, file_name):
    print(f"\n--- Validating data for {file_name} ---")
    if df.isnull().values.any():
        print(f"Warning: Missing data (NaN) found in {file_name}!")
        nan_summary = df.isnull().sum()
        print(nan_summary[nan_summary > 0])

    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            invalid_data = df[df[col] == -1.0]
            if not invalid_data.empty:
                print(f"Warning: Invalid data (-1.0) found in column {col} in {file_name}!")
                print(invalid_data[['Team', col]])

    columns_to_check = ['FG_Attempted', 'XP_Made', 'Punts']
    for col in columns_to_check:
        if col in df.columns:
            zero_data = df[df[col] == 0]
            if not zero_data.empty:
                print(f"Warning: Zero values found in column {col} in {file_name}, which may be unexpected!")
                print(zero_data[['Team', col]])

# Process, validate, and save the data into the correct folder
def process_and_validate(url, file_name):
    df = scrape_table(url, file_name)
    if df is not None:
        if file_name == "Special_Field_Goals":
            df = process_special_field_goals(df)  # Clean special field goals data

        # Determine the folder based on file_name
        folder_name = None
        for folder, stats in folders.items():
            if file_name in stats:
                folder_name = folder
                break
        
        if folder_name:
            # Save the file into the correct folder
            csv_path = f'./{folder_name}/{file_name}.csv'
            df.to_csv(csv_path, index=False)
            print(f"Data scraped and saved to {csv_path}")
            
            # Read back the CSV to perform validation
            df_reloaded = pd.read_csv(csv_path)
            validate_data(df_reloaded, file_name)
        else:
            print(f"Error: Could not find a folder for {file_name}")


# URL Dictionary
url_dict = {
    "Passing_Yards": "https://www.nfl.com/stats/player-stats/category/passing/2024/reg/all/passingyards/desc",
    "Rushing_Yards": "https://www.nfl.com/stats/player-stats/category/rushing/2024/reg/all/rushingyards/desc",
    "Reciving_Receptions": "https://www.nfl.com/stats/player-stats/category/receiving/2024/reg/all/receivingreceptions/desc",
    "Defensive_Forced_Fumbles": "https://www.nfl.com/stats/player-stats/category/fumbles/2024/reg/all/defensiveforcedfumble/desc",
    "Defensive_Combine_Tackles": "https://www.nfl.com/stats/player-stats/category/tackles/2024/reg/all/defensivecombinetackles/desc",
    "Defensive_Interceptions": "https://www.nfl.com/stats/player-stats/category/interceptions/2024/reg/all/defensiveinterceptions/desc",
    "Kicking_Field_Goals_Made": "https://www.nfl.com/stats/player-stats/category/field-goals/2024/reg/all/kickingfgmade/desc",
    "Punting_Average_Yards": "https://www.nfl.com/stats/player-stats/category/punts/2024/reg/all/puntingaverageyards/desc",
    "Punt_Returns_Average_Yards": "https://www.nfl.com/stats/player-stats/category/punt-returns/2024/reg/all/puntreturnsaverageyards/desc",
    "Offensive_Passing": "https://www.nfl.com/stats/team-stats/offense/passing/2024/reg/all",
    "Offensive_Rushing": "https://www.nfl.com/stats/team-stats/offense/rushing/2024/reg/all",
    "Offensive_Receiving": "https://www.nfl.com/stats/team-stats/offense/receiving/2024/reg/all",
    "Offensive_Scoring": "https://www.nfl.com/stats/team-stats/offense/scoring/2024/reg/all",
    "Offensive_Downs": "https://www.nfl.com/stats/team-stats/offense/downs/2024/reg/all",
    "Defensive_Passing": "https://www.nfl.com/stats/team-stats/defense/passing/2024/reg/all",
    "Defensive_Rushing": "https://www.nfl.com/stats/team-stats/defense/rushing/2024/reg/all",
    "Defensive_Receiving": "https://www.nfl.com/stats/team-stats/defense/receiving/2024/reg/all",
    "Defensive_Scoring": "https://www.nfl.com/stats/team-stats/defense/scoring/2024/reg/all",
    "Defensive_Tackles": "https://www.nfl.com/stats/team-stats/defense/tackles/2024/reg/all",
    "Defensive_Downs": "https://www.nfl.com/stats/team-stats/defense/downs/2024/reg/all",
    "Defensive_Fumbles": "https://www.nfl.com/stats/team-stats/defense/fumbles/2024/reg/all",
    "Defensive_Interceptions": "https://www.nfl.com/stats/team-stats/defense/interceptions/2024/reg/all",
    "Special_Field_Goals": "https://www.nfl.com/stats/team-stats/special-teams/field-goals/2024/reg/all",
    "Special_Scoring": "https://www.nfl.com/stats/team-stats/special-teams/scoring/2024/reg/all",
    "Special_Punts": "https://www.nfl.com/stats/team-stats/special-teams/punts/2024/reg/all",
    "Special_Punt_Returns": "https://www.nfl.com/stats/team-stats/special-teams/punt-returns/2024/reg/all"
}

# Iterate over the URL dictionary to scrape, validate, and save each stat
for stat_name, stat_url in url_dict.items():
    process_and_validate(stat_url, stat_name)