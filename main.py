from controller import build_dataset, export_dataset, build_players_list

# Run this script to build a csv dataset with the parameters in settings.py

# The function build_dataset() builds a new database (or expands the existing one) and fills it with random matches
# taken either from random players (obtained on the fly) or from a players list file (by setting the argument
# use_players_list to True), which can be created automatically using the function build_players_list().

# The function build_players_list() fills a file whose name can be set on settings.py with random players. This file is
# then used (optionally) while building the dataset to reduce the time needed to get a random player each time (which
# adds up over time) and make it impossible to get the same player from time to time, which happens.

# It optionally accepts the dataset name. The default name is to be set on the file settings.py

# The function export_dataset writes to a csv the data saved on the json file.
# It accepts:
#   a database object
#   an option
#   (optional) the csv filename
# The option can be one of these strings:
#   both_teams: each sample contains features of the players of both teams and the outcome
#   single_team: each sample contains features of the player of a single team and the outcome


if __name__ == "__main__":
    build_players_list(number_of_players=10000)
    dataset = build_dataset(use_players_list=True)
    export_dataset(dataset, "both_teams")
