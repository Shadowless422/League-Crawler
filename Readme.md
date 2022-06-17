# LoL Crawler
This is a data collector script based on [RiotWatcher](https://github.com/pseudonym117/Riot-Watcher) to build a dataset containing specific data about each participant of a match. Those data are meant to feed an ML implementation to try to predict the outcome of a match starting from those data.

# Getting Started
## About the data collected
The data is retrieved directly from Riot APIs using [RiotWatcher](https://github.com/pseudonym117/Riot-Watcher), a really useful wrapper written in Python that implements a naive rate limiter, which is needed since the free API Key that Riot provides is limited to 20 requests per 1 minute and 100 requests per 2 minutes ([source](https://developer.riotgames.com/docs/portal)). All data is therefore of public domain and so it can be accessed by anyone.

## Requirements
[Python Dotenv Library](https://pypi.org/project/python-dotenv) is needed to load the environment variables (in this case the API key).

[RiotWatcher](https://github.com/pseudonym117/Riot-Watcher) is needed to do the API calls.
```
pip install -r requirements.txt
```

## Setting up the API key
To being able to use this script you must get an API key from [Riot Games](https://developer.riotgames.com/). To use it you need to put it in a file called ".env" on the script folder this way:
```
API_KEY="RGAPI-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
```


## Building the dataset
To build the .json dataset you need to run the function "build_dataset()". If you want to build a players list beforehand, run the function "build_players_list()" and set the argument "use_players_list" to True.


## Exporting the dataset to .csv
To export the data inside the .json database use the function "export_dataset()".

### CSV details
The .csv file won't have an header. Each row contains all the data about one or both teams, the last element being the result. 

If each row contains data about both teams, the data about the blue team is on the first half. The result is 1 if the blue team won, 0 if not.

If each row contains data about a single team, the odd rows will contain  the data about the blue team, the even rows will contain the data about the red team of each match (i.e.: same match, row 1 blue team data, row 2 red team data).

# Disclaimer
This project isn't endorsed by Riot Games and doesn't reflect the views or 38 opinions of Riot Games or anyone officially involved in producing or 39 managing League of Legends. League of Legends and Riot Games are 40 trademarks or registered trademarks of Riot Games, Inc. League of Legends 41 © Riot Games, Inc.
