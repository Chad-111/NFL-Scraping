import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from io import StringIO

def get_actual_header(soup):
    # Find the 'thead' element
    thead = soup.find('thead')
    if thead:
        # Find all rows in the thead
        header_rows = thead.find_all('tr')

        # Filter out rows with class 'over_header' (these are the grouping headers)
        actual_header_row = None
        for row in header_rows:
            if 'over_header' not in row.get('class', []):
                actual_header_row = row
                break

        # Now get the actual headers
        if actual_header_row:
            headers = [th.text.strip() for th in actual_header_row.find_all('th')]
            return headers
    return []

# Path to ChromeDriver (update this based on where your chromedriver is located)
CHROME_DRIVER_PATH = './chromedriver.exe'

# Initialize Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run Chrome in headless mode
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.88 Safari/537.36')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-insecure-localhost')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')

service = Service(CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# Define team name mapping from abbreviations to full club names
team_name_mapping = {
    "BAL": "Baltimore Ravens",
    "KAN": "Kansas City Chiefs",
    "BUF": "Buffalo Bills",
    "CLE": "Cleveland Browns",
    "PIT": "Pittsburgh Steelers",
    "IND": "Indianapolis Colts",
    "TEN": "Tennessee Titans",
    "MIA": "Miami Dolphins",
    "LAC": "Los Angeles Chargers",
    "DEN": "Denver Broncos",
    "CIN": "Cincinnati Bengals",
    "JAX": "Jacksonville Jaguars",
    "NYJ": "New York Jets",
    "NWE": "New England Patriots",
    "HOU": "Houston Texans",
    "LVR": "Las Vegas Raiders",
    "DAL": "Dallas Cowboys",
    "WAS": "Washington Commanders",
    "NYG": "New York Giants",
    "PHI": "Philadelphia Eagles",
    "DET": "Detroit Lions",
    "CHI": "Chicago Bears",
    "MIN": "Minnesota Vikings",
    "GNB": "Green Bay Packers",
    "ATL": "Atlanta Falcons",
    "CAR": "Carolina Panthers",
    "NOR": "New Orleans Saints",
    "TAM": "Tampa Bay Buccaneers",
    "ARI": "Arizona Cardinals",
    "LAR": "Los Angeles Rams",
    "SFO": "San Francisco 49ers",
    "SEA": "Seattle Seahawks"
}

# Function to replace team abbreviations in a DataFrame
def replace_team_abbreviations(df):
    for abbr, full_name in team_name_mapping.items():
        df.replace(abbr, full_name, inplace=True)
    return df

def read_html_table(table):
    """Read HTML table and avoid the FutureWarning."""
    html_string = str(table)
    return pd.read_html(StringIO(html_string))[0]

def clean_data(df):
    # Remove rows with class 'over_header' or 'thead' after the first instance
    first_header_found = False

    def filter_unwanted_rows(row):
        nonlocal first_header_found
        # If 'over_header' or 'thead' classes are found in this row
        if any('over_header' in str(item) for item in row) or any('thead' in str(item) for item in row):
            # Skip any additional headers after the first one
            if first_header_found:
                return False
            else:
                first_header_found = True
                return True
        return True

    # Apply the filter to remove unwanted rows
    df = df[df.apply(filter_unwanted_rows, axis=1)]

    # Try to locate the real header (if any) and reset the index after removing over-header rows
    try:
        first_thead_index = df.index[df.apply(lambda row: any('thead' in str(item) for item in row), axis=1)][0]
        df = df.iloc[first_thead_index + 1:]
    except IndexError:
        print("No 'thead' row found, keeping the original data.")
    
    df = df.reset_index(drop=True)

    # Flatten multi-level columns if they exist
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col).strip() for col in df.columns.values]

    return df

# Scrape the main page for the games
main_url = 'https://www.pro-football-reference.com/years/2024/games.htm'
driver.get(main_url)
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Locate the games table
schedule_table = soup.find('table', {'id': 'games'})
rows = schedule_table.find_all('tr')

# Loop through each game row
for game_row in rows:
    boxscore_td = game_row.find('td', attrs={'data-stat': 'boxscore_word'})
    
    # Continue only if the game has 'boxscore' as its boxscore_word, and not 'preview'
    if boxscore_td and boxscore_td.text.strip() == 'boxscore':
        week_th = game_row.find('th', attrs={'data-stat': 'week_num'})  
        winner_td = game_row.find('td', attrs={'data-stat': 'winner'})
        loser_td = game_row.find('td', attrs={'data-stat': 'loser'})
        
        week_number = week_th.text.strip() if week_th else 'Unknown_Week'
        winner_abbr = winner_td.text.strip() if winner_td else 'Unknown_Winner'
        loser_abbr = loser_td.text.strip() if loser_td else 'Unknown_Loser'
        
        winner = team_name_mapping.get(winner_abbr, winner_abbr)
        loser = team_name_mapping.get(loser_abbr, loser_abbr)
        
        boxscore_link = boxscore_td.find('a')['href']
        game_url = f"https://www.pro-football-reference.com{boxscore_link}"

        print(f"Scraping game URL: {game_url}, Week: {week_number}, Winner: {winner}, Loser: {loser}")
        
        driver.get(game_url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        table_names = ['scoring', 'game_info', 'expected_points', 'team_stats', 'player_offense', 'player_defense', 'returns', 'kicking', 'passing_advanced', 'rushing_advanced', 'receiving_advanced', 'defense_advanced', 'home_drives', 'away_drives']
        
        base_dir = 'Game Stats'
        week_dir = os.path.join(base_dir, f'Week {week_number}')
        game_dir = os.path.join(week_dir, f'{winner} vs {loser}')
        os.makedirs(game_dir, exist_ok=True)

        game_tables = {}
        for table_name in table_names:
            div_id = f'all_{table_name}'
            outer_div = soup.find('div', id=div_id)
            if outer_div:
                inner_div = outer_div.find('div', id=f'div_{table_name}')
                if inner_div:
                    table = inner_div.find('table')
                    if table:
                        # Get actual headers, ignoring over-headers
                        headers = get_actual_header(BeautifulSoup(str(table), 'html.parser'))
                        df = read_html_table(table)

                        # Assign correct headers to the DataFrame only if the number of headers matches the number of columns
                        if headers and len(headers) == df.shape[1]:
                            df.columns = headers

                        # Clean the DataFrame by removing over_header and thead rows
                        df = clean_data(df)

                        game_tables[table_name] = df
                        print(f"Scraped {table_name} table for {game_url}")
                    else:
                        print(f"No table found inside div_{table_name} for {game_url}")
                else:
                    print(f"No inner div with id div_{table_name} found for {game_url}")
            else:
                print(f"No outer div with id all_{table_name} found for {game_url}")

        for table_name, df in game_tables.items():
            df = clean_data(df)
            df = replace_team_abbreviations(df)
            file_name = f'{table_name}.csv'
            file_path = os.path.join(game_dir, file_name)
            df.to_csv(file_path, index=False)
            print(f"Saved {table_name} table to {file_path}")

driver.quit()
print(f"Scraping completed for all games with 'boxscore'.")
