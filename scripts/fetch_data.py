import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Define the URL and output file path
URL = "https://www.basketball-reference.com/leagues/NBA_2023_per_game.html"
OUTPUT_DIR = "nba_mvp_dashboard/data/"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "nba_2023_per_game_stats.csv")

def fetch_and_save_data():
    """
    Fetches player statistics from Basketball-Reference.com,
    parses the main table, and saves it as a CSV file.
    """
    try:
        print(f"Fetching data from {URL}...")
        response = requests.get(URL, timeout=10) # Added timeout
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        print("Data fetched successfully.")

        print("Parsing HTML content...")
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the table by its ID
        table = soup.find("table", id="per_game_stats")

        if table is None:
            print("Error: Could not find the table with id 'per_game_stats'.")
            return

        print("Table found. Converting to pandas DataFrame...")
        # pandas.read_html returns a list of DataFrames. We expect only one table with this ID.
        df_list = pd.read_html(str(table))
        if not df_list:
            print("Error: pandas could not parse the HTML table.")
            return
        
        df = df_list[0]
        print("DataFrame created successfully.")

        # Create the directory if it doesn't exist
        if not os.path.exists(OUTPUT_DIR):
            print(f"Creating directory: {OUTPUT_DIR}")
            os.makedirs(OUTPUT_DIR)

        print(f"Saving DataFrame to {OUTPUT_FILE}...")
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Data saved successfully to {OUTPUT_FILE}")

    except requests.exceptions.RequestException as e:
        print(f"Error during requests to {URL}: {e}")
    except pd.errors.EmptyDataError as e:
        print(f"Error: No data found when trying to parse the table: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    fetch_and_save_data()
