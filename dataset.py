import csv
import json
import os
import shutil


class MatchesDataset(object):
    def __init__(self, filename):
        self.filename = filename
        self.__tmp_filename = f"{filename}.tmp"

        try:
            with open(filename) as json_file:
                self.__db = json.load(json_file)
        except FileNotFoundError:
            self.__db = {}

    def __save(self):
        with open(self.__tmp_filename, "w") as json_file:
            json.dump(
                self.__db,
                json_file,
                indent=4,
                separators=(',', ': ')
            )
        shutil.move(self.__tmp_filename, self.filename)

    def add_match(self, match_id: str, data: dict):
        self.__db[match_id] = data
        self.__save()

    def remove_matches(self, *matches_id: str):
        for match_id in matches_id:
            del self.__db.pop[match_id]
        self.__save()

    def matches_count(self):
        return len(self.__db)

    def contains_match(self, match_id: str):
        return match_id in self.__db

    def export_to_csv_both_teams(self, csv_filename: str):
        # If the script is running on Windows, we need to set newline as an empty string, or the csv writer make
        # an extra line each time it writes a row
        new_line = "" if os.name == "nt" else None

        with open(csv_filename, "w", newline=new_line) as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for match, data in self.__db.items():
                result = [1] if data["blue_won"] else [0]
                csv_writer.writerow(data["blue"] + data["red"] + result)

    def export_to_csv_single_team(self, csv_filename: str):
        new_line = "" if os.name == "nt" else None

        with open(csv_filename, "w", newline=new_line) as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for match, data in self.__db.items():
                if data["blue_won"]:
                    blue_result = [1]
                    red_result = [0]
                else:
                    blue_result = [0]
                    red_result = [1]
                csv_writer.writerow(data["blue"] + blue_result)
                csv_writer.writerow(data["red"] + red_result)
