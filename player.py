import math
import shutil
import statistics

from riotwatcher import LolWatcher
import settings


class Match(object):
    api_key = settings.api_key
    region = settings.region

    def __init__(self, id):
        self.id = id
        self.info = None

    # I let the user choose when he wants to get the info, this is to avoid unnecessary api calls
    def get_infos(self):
        try:
            self.info = LolWatcher(self.api_key).match.by_id(self.region, self.id)
        finally:
            return self.info

    def has_info(self):
        return self.info or self.get_infos()


class Player(object):
    api_key = settings.api_key
    matches_to_get = settings.matches
    queue = settings.queue
    region = settings.region

    def __init__(self, name=None, puuid=None):
        if puuid:
            infos = LolWatcher(self.api_key).summoner.by_puuid(self.region, puuid)
        elif name:
            infos = LolWatcher(self.api_key).summoner.by_name(self.region, name)
        else:
            print("Expected either a puuid or a nickname")
            exit(1)

        self.name = infos["name"]
        self.puuid = infos["puuid"]
        self.match_history = None

    def get_match_history(self, created_before=None):
        # The subsequent code converts unix time in ms to s
        if created_before and created_before > 9999999999:
            created_before = math.ceil(created_before / 1000)

        matches_ids = LolWatcher(self.api_key).match.matchlist_by_puuid(
            region=self.region,
            puuid=self.puuid,
            count=self.matches_to_get,
            end_time=created_before,
            queue=self.queue
        )

        if len(matches_ids) != self.matches_to_get:
            return None

        self.match_history = [Match(id) for id in matches_ids]
        return self.match_history

    def has_match_history(self):
        return self.match_history or self.get_match_history()

    def get_useful_infos_from_match_history(self):
        # This method requires that the player has a valid match history
        if not self.match_history or len(self.match_history) != self.matches_to_get:
            return None

        # For each game we need to get these info
        games_won = 0
        games_lost = 0
        avg_bounty_level = []
        avg_gold_per_second = []
        avg_kill_participation = []
        avg_max_living_time_over_game_duration = []

        for match in self.match_history:
            # get_infos also returns the info. If there's no info, there was an error
            if not match.get_infos():
                return None

            game_duration = match.info["info"]["gameDuration"]
            blue_team_kills = match.info["info"]["teams"][0]["objectives"]["champion"]["kills"]
            red_team_kills = match.info["info"]["teams"][1]["objectives"]["champion"]["kills"]

            if blue_team_kills == 0: blue_team_kills = 1
            if red_team_kills == 0: red_team_kills = 1

            # We are only interested about the info of the current player
            match_participants = match.info["info"]["participants"]
            current_player = [participant for participant in match_participants if participant["puuid"] == self.puuid]
            current_player = current_player[0]

            if current_player["win"]:
                games_won += 1
            else:
                games_lost += 1

            p_team_kills = blue_team_kills if current_player["teamId"] == 100 else red_team_kills

            avg_bounty_level += [current_player["bountyLevel"]]
            avg_gold_per_second += [current_player["goldEarned"] / game_duration]
            avg_kill_participation += [(current_player["kills"] + current_player["assists"]) / p_team_kills]
            avg_max_living_time_over_game_duration += [current_player["longestTimeSpentLiving"] / game_duration]

        # Checking data
        if games_won + games_lost != self.matches_to_get:
            return None

        # Calculating averages and adding them to data
        try:
            return [
                games_won,
                games_lost,
                statistics.mean(avg_bounty_level),
                statistics.mean(avg_gold_per_second),
                statistics.mean(avg_kill_participation),
                statistics.mean(avg_max_living_time_over_game_duration)
            ]
        except statistics.StatisticsError:
            return None


class PlayersList:
    def __init__(self):
        self.filename = settings.players_list_filename
        self.__tmp_filename = f"{settings.players_list_filename}.tmp"

        try:
            self.__players_list = set(puuid.strip("\n\r") for puuid in open(self.filename))
        except FileNotFoundError:
            self.__players_list = set()

    def __save(self):
        with open(self.__tmp_filename, "w") as file:
            file.write("\n".join(self.__players_list))
        shutil.move(self.__tmp_filename, self.filename)

    def players_count(self):
        return len(self.__players_list)

    def add(self, *puuids: str):
        self.__players_list.update(puuids)
        self.__save()

    def pop(self):
        player = self.__players_list.pop()
        self.__save()
        return player
