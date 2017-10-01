from TCS_Scraper import TCS_Scraper
from typing import List
import requests
requests.packages.urllib3.disable_warnings()

from Overbuff_Scraper import Overbuff_Scraper as Overbuff

class Player():
    def __init__(self, battle_tag: str, skill_rating: int=None):
        self.battle_tag = battle_tag
        self.skill_rating = skill_rating \
            if skill_rating is not None \
            else Overbuff.get_sr(battle_tag)

    def __str__(self):
        return self.battle_tag + " (" + self.skill_rating + " SR)"

    def __dict__(self):
        dict = {
            "battle_tag" : self.battle_tag,
            "skill_rating" : self.skill_rating
        }
        return dict

class Team():
    def __init__(self, url: str, region: str, name: str,
                 players: List[Player]=None, average_sr: float=None):
        self.url = url
        self.region = region
        self.name = name
        self.players = players
        self.average_sr = average_sr

        if players is None:
            self.scrape_player_list()
        if average_sr is None:
            self.calculate_average()

    def __str__(self):
        players = ""
        for player in self.players:
            players += "\t" + str(player) + "\n"

        return self.name + " <" + self.url + ">\n" \
               + "region: " + self.region + "\n" \
               + "average_sr: " + str(self.average_sr) + "\n" \
               + "players: " + "\n" + players

    def __dict__(self):
        dict = {
            "url" : self.url,
            "region" : self.region,
            "name" : self.name,
            "players" : [player.__dict__() for player in self.players],
            "average_sr" : self.average_sr
        }
        return dict

    def scrape_player_list(self):
        scraped_players = TCS_Scraper.get_players(self.url)

        player_list = []
        for battle_tag in scraped_players:
            player_list.append(Player(battle_tag))
        self.players = player_list

    def calculate_average(self):
        team_list = []
        # Get the sr of all players on team
        for player in self.players:
            sr = player.skill_rating
            team_list.append(sr)

        # If for some reason there are more than 6 players,
        # only use the top 6 ranked players in the average
        team_list.sort(reverse=True)
        team_list = team_list[:6]
        team_sr = sum(team_list) / 6
        self.average_sr = team_sr