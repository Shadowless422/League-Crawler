import os
from dotenv import load_dotenv

# Settings
csv_filename = "outputs/export.csv"
db_filename = "outputs/db.json"
matches = 20
name = "Shadowless422"
players_list_filename = "outputs/players.txt"
queue = 400
region = "euw1"
target_matches = 5000

# Loading API key
load_dotenv()
api_key = os.getenv("API_KEY")

