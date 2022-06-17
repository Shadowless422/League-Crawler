import datetime
import os
import platform
import random
import statistics
import time

from dataset import MatchesDataset
from player import Player, Match, PlayersList
import settings


def export_dataset(database: MatchesDataset, features: str = "both_teams", filename: str = settings.csv_filename):
    """
    This function exports the dataset to a csv file. The csv won't have an header.

    :param database:
    :param features:
    :param filename:
    :return:
    """
    options = ["both_teams", "single_team"]
    if features not in options:
        raise Exception("Invalid option")

    if features == options[0]:
        return database.export_to_csv_both_teams(filename)  # "both_teams"
    return database.export_to_csv_single_team(filename)  # "single_team"


def get_match_info(match: Match):
    """
    This function returns useful data about a given match and each participant of it.

    :param match: the match from which to get the info
    :return: a dictionary containing the data related to each team and a bool that is True if the blue team won. None if there was an error.
    """
    if not match.has_info():
        return None

    # First, we need to check if every participant has a valid match_history
    participants = match.info["info"]["participants"]
    creation_date = match.info["info"]["gameCreation"]

    participants_as_players = []
    for participant in participants:
        player = Player(puuid=participant["puuid"])

        # get_match_history returns None if the match_history contains more or less games than requested
        if not player.get_match_history(created_before=creation_date):
            return None

        participants_as_players += [player]

    # Setting up variables
    blue_team_won = match.info["info"]["teams"][0]["win"]
    blue_team_data = []
    red_team_data = []

    for player_number, player in enumerate(participants_as_players):
        if not (participant_data := player.get_useful_infos_from_match_history()):
            return None

        # Players from 0 to 4 are on blue team, those from 5 to 9 are on red team
        if player_number < 5:
            blue_team_data += participant_data
        else:
            red_team_data += participant_data

    return dict(blue=blue_team_data, red=red_team_data, blue_won=blue_team_won)


def get_new_match(player: Player, dataset: MatchesDataset):
    """
    This function returns a match from the player's match history which is not already present in the dataset.

    :param player: the player from which to take the match history
    :param dataset: the dataset to look at when checking if the match is eligible
    :return: a match which is not already present in the dataset. None if there was an error or if all matches are
    already in the dataset
    """
    if not player.has_match_history():
        return None

    # Creating a list of matches that are not already present in the database
    new_matches = [match for match in player.match_history if not dataset.contains_match(match.id)]
    if not new_matches:
        return None

    # We need only the first match of that list
    return new_matches[0]


def get_new_player(player: Player):
    """
    This function returns a player taken from the given player's match history.

    :param player: the player from which to take the match history
    :return: the player taken from the player match history. The player passed as input if there was an error.
    """
    if not player.has_match_history():
        return player

    random_match = random.choice(player.match_history)

    if not random_match.has_info():
        return player

    puuids = random_match.info["metadata"]["participants"]
    puuids.remove(player.puuid)

    return Player(puuid=random.choice(puuids))


class Info:
    def __init__(self):
        self.before = time.time()
        self.delta_times = []
        self.avg_time = None

    def update(self):
        # Edit time variables
        self.delta_times += [time.time() - self.before]
        self.delta_times = self.delta_times[-10:]
        self.avg_time = round(statistics.mean(self.delta_times))

        # Resetting before
        self.before = time.time()
        return self

    def display(self, target_matches, saved_matches):
        # Setting the right 'clear_screen' cmd basing on the current platform
        clear_screen = "cls" if platform.system() == "Windows" else "clear"
        os.system(clear_screen)

        print(f"Target matches: {target_matches}")
        print(f"Matches in database: {saved_matches}")

        if self.avg_time:
            print(f"Average time needed for each match: {str(datetime.timedelta(seconds=self.avg_time))}")
            eta = (target_matches - saved_matches) * self.avg_time
            print(f"ETA: {str(datetime.timedelta(seconds=eta))}")


def build_dataset(database_name: str = settings.db_filename, use_players_list: bool = False):
    """
    This function builds a dataset (or expands it if it does already exist) and fills it with data about random matches.
    At the end, the dataset will contain a number of matches equal to the relative setting in settings.py

    :param database_name:
    :param use_players_list: if true, the function will use the players list to get a new player instead of randomly
           getting one each iteration (and so wasting a lot of api calls)
    :return:
    """
    dataset = MatchesDataset(database_name)
    player = Player(name=settings.name)
    players_list = PlayersList() if use_players_list else None

    # Setting up time variables
    info = Info()

    # MAIN LOOP
    while dataset.matches_count() < settings.target_matches:
        # Printing info
        info.display(target_matches=settings.target_matches, saved_matches=dataset.matches_count())

        # Getting a new player
        if players_list:
            try:
                player = Player(puuid=players_list.pop())
            except KeyError:
                print(f"Not enough players in players list to get all matches requested."
                      f"Only {dataset.matches_count()} matches retrieved out of {settings.target_matches}")
                return
        else:
            player = get_new_player(player)

        # Getting a new match from the player's match history. If something goes wrong (i.e. the database already
        # contains all matches on the player's match history), it returns None
        match = get_new_match(player, dataset)
        if not match:
            continue

        # This function will iterate through all participants and extract the useful datas from each one of them
        data = get_match_info(match)
        if not data:
            continue

        dataset.add_match(match.id, data)

        # Updating info since the iteration went through with no problems
        info.update()


def build_player_list(number_of_players: int = settings.target_matches):
    """
    This function builds a players list file (or expands the existing one) and fills it with puuids of different players
    to be used inside the build_dataset function.

    :param number_of_players: the minimum number of players to get. Default: the number of target matches on settings.py
    :return: None
    """
    player = Player(name=settings.name)
    players_list = PlayersList()

    while players_list.players_count() < number_of_players:
        print(f"Players to get: {number_of_players}\n"
              f"Players retrieved: {players_list.players_count()}")

        # Getting a new player, if the set is empty, it searches a new player from the match history of the current one
        try:
            player = Player(puuid=players_list.pop())
        except KeyError:
            player = get_new_player(player)

        if not player.has_match_history():
            continue

        for match in player.match_history:
            if not match.has_info():
                continue

            players_list.add(*match.info["metadata"]["participants"])
