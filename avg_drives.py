from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
import time
import re

# Set up Selenium WebDriver
service = Service(executable_path="./chromedriver.exe")  # Update with your actual path
driver = webdriver.Chrome(service=service)

# Open the webpage
url = "https://www.pro-football-reference.com/years/2024/#all_drives"
driver.get(url)

# Let the page load
time.sleep(3)  # Adjust sleep time for the page to fully load

# Find the table by its ID
drive_table = driver.find_element(By.ID, "drives")

# Extract the table HTML content
html_content = drive_table.get_attribute('outerHTML')

# Use pandas to read the table
df_drives = pd.read_html(html_content)[0]

# Flatten multi-index columns
df_drives.columns = [' '.join(col).strip() for col in df_drives.columns.values]

# Clean the data:
# Drop empty rows or irrelevant rows (like 'League Total')
df_drives_clean = df_drives.dropna()

# Rename columns
df_drives_clean.columns = ['Rank', 'Team', 'Games', 'Drives', 'Total_Plays', 'Score_Percent', 'Turnover_Percent', 
                           'Avg_Drive_Plays', 'Avg_Drive_Yards', 'Avg_Drive_Start', 'Avg_Drive_Time', 'Avg_Drive_Points']

# Remove rows where 'Rank' is NaN (League Total or any unwanted summary rows)
df_drives_clean = df_drives_clean.dropna(subset=['Rank'])

# Convert data types to numeric where needed
df_drives_clean['Rank'] = pd.to_numeric(df_drives_clean['Rank'], errors='coerce', downcast='integer')
df_drives_clean['Games'] = pd.to_numeric(df_drives_clean['Games'], errors='coerce', downcast='integer')
df_drives_clean['Total_Plays'] = pd.to_numeric(df_drives_clean['Total_Plays'], errors='coerce', downcast='integer')
df_drives_clean['Score_Percent'] = pd.to_numeric(df_drives_clean['Score_Percent'], errors='coerce')
df_drives_clean['Turnover_Percent'] = pd.to_numeric(df_drives_clean['Turnover_Percent'], errors='coerce')
df_drives_clean['Avg_Drive_Plays'] = pd.to_numeric(df_drives_clean['Avg_Drive_Plays'], errors='coerce')
df_drives_clean['Avg_Drive_Yards'] = pd.to_numeric(df_drives_clean['Avg_Drive_Yards'], errors='coerce')
df_drives_clean['Avg_Drive_Points'] = pd.to_numeric(df_drives_clean['Avg_Drive_Points'], errors='coerce')


# Function to convert Avg_Drive_Time to seconds
def convert_time_to_seconds(time_str):
    minutes, seconds = map(int, time_str.split(':'))
    return minutes * 60 + seconds

# Function to convert Avg_Drive_Start to yards from opponent's end zone
def convert_drive_start(drive_start_str):
    # Split the string into "Own"/"Opp" and yard value
    match = re.match(r"(Own|Opp) (\d+\.?\d*)", drive_start_str)
    if match:
        position, yards = match.groups()
        yards = float(yards)
        if position == 'Own':
            # Convert own side to distance from opponent's end zone
            return 100 - yards
        elif position == 'Opp':
            return yards
    return None  # For any unexpected values


# Apply the conversion functions
df_drives_clean['Avg_Drive_Time'] = df_drives_clean['Avg_Drive_Time'].apply(convert_time_to_seconds)
df_drives_clean['Avg_Drive_Start'] = df_drives_clean['Avg_Drive_Start'].apply(convert_drive_start)

# Save the updated table to CSV
df_drives_clean.to_csv("Drive_Averages.csv", index=False)

print("Drive Averages have been processed, cleaned and saved to Drive_Averages.csv")

# Close the WebDriver
driver.quit()
