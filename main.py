from controller import build_dataset, export_dataset, build_player_list

# Run this script to build a csv dataset with the parameters in settings.py

# The function dataset builds a new database (or expands the existing one) and fills it with random matches taken from
# random players.
# It optionally accepts the dataset name. The default name is to be set on the file settings.py

# The function export_dataset writes to a csv the data saved on the json file.
# It accepts:
#   a database object
#   an option
#   (optional) the csv filename
# The option can be one of these strings:
#   both_teams: each sample contains features of the players of both teams and the outcome
#   single_team: each sample contains features of the player of a single team and the outcome

# DA FARE:
# salvare bene i players list


if __name__ == "__main__":
    build_player_list(number_of_players=10000)
    dataset = build_dataset(use_players_list=True)
    export_dataset(dataset, "both_teams")
