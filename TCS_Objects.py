from TCS_Scraper import TCS_Scraper
from typing import List
from Overbuff_Scraper import Overbuff_Scraper as Overbuff

class Player():
    def __init__(self, battle_tag: str, skill_rating: int=None):
        """
        If web scraping from TCS, sr will be None so we scrape from Overbuff.
        Otherwise are are reading from a json file and scraping is unnecessary.

        :param battle_tag:
        :param skill_rating:
        """
        self.battle_tag = battle_tag
        self.skill_rating = skill_rating \
            if skill_rating is not None \
            else Overbuff.get_sr(battle_tag)

    def __str__(self):
        if self.skill_rating > 0:
            return self.battle_tag + " (" + str(self.skill_rating) + " SR)"
        return self.battle_tag + " (Unranked)"

    def __dict__(self):
        dict = {
            "battle_tag" : self.battle_tag,
            "skill_rating" : self.skill_rating
        }
        return dict

class Team():
    def __init__(self, url: str, region: str, name: str,
                 players: List[Player]=None, average_sr: float=None,
                 elo: float=None):
        """
        If web scraping from TCS, playerlist will be None so we go to the
        individual team page and scrape from there.
        If that is the case, average_sr will also be none and will be calculated
        from the player list.
        Otherwise are are reading from a json file and scraping is unnecessary.

        :param url:
        :param region: west, south, north, east
        :param name: team name
        :param players: list of Player objects
        :param average_sr:
        """
        self.id = int(url.split("/")[-1])
        self.url = url
        self.region = region
        self.name = name
        self.players = players
        self.average_sr = average_sr
        self.elo = elo

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
               + "elo: " + str(self.elo) + "\n" \
               + "players: " + "\n" + players

    def __dict__(self):
        dict = {
            "url" : self.url,
            "region" : self.region,
            "name" : self.name,
            "players" : [player.__dict__() for player in self.players],
            "average_sr" : self.average_sr,
            "elo" : self.elo
        }
        return dict

    def scrape_player_list(self):
        """
        Takes the team url and looks up the battle tags, ignoring team
        coordinators and substitutes

        :return: void
        """
        scraped_players = TCS_Scraper.scrape_players(self.url)

        player_list = []
        for battle_tag in scraped_players:
            player_list.append(Player(battle_tag))
        self.players = player_list

    def calculate_average(self):
        """
        Takes list of players and averages their SR, ignoring unranked people.
        If there are more than 6 players, only take the top 6.

        :return:
        """
        team_list = []
        # Get the sr of all players on team
        for player in self.players:
            sr = player.skill_rating
            if sr > 0:
                team_list.append(sr)
            # Unranked people are listed as -1 SR, do not consider in average

        # If entire team is unranked
        if not team_list:
            return -1

        # If for some reason there are more than 6 players,
        # only use the top 6 ranked players, assume rest are substitutes
        if len(team_list) > 6:
            team_list.sort(reverse=True)
            team_list = team_list[:6]
        team_sr = sum(team_list) / len(team_list)
        self.average_sr = team_sr
        self.elo = team_sr

    @staticmethod
    def calculate_elo(my_elo: float, opponent_elo: float, result: int):
        """
        Elo update based on the math stuff I found here:
        https://metinmediamath.wordpress.com/2013/11/27/how-to-calculate-the-elo-rating-including-example/


        :param opponent_elo:
        :param result: 1: win, 0: draw, -1: lose
        :return: void
        """
        # Transformed rank
        R_1 = pow(10, my_elo / 400)
        R_2 = pow(10, opponent_elo / 400)

        # Expected score
        E_1 = R_1 / (R_1 + R_2)
        E_2 = R_2 / (R_1 + R_2)

        # If win
        if result == 1:
            S_1 = 1
            S_2 = 0
        # If draw
        elif result == 0:
            S_1 = S_2 = 0.5
        # If lose
        elif result == -1:
            S_1 = 0
            S_2 = 1
        else:
            print("Incorrect result inputted")
            S_1 = S_2 = -1

        # "Arbitrary" weight factor indicating how much
        # a match should shift elo
        K = 50

        r_1prime = my_elo + K * (S_1 - E_1)
        r_2prime = opponent_elo + K * (S_2 - E_2)

        return r_1prime, r_2prime