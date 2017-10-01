from typing import List

class Player():
    def __init__(self, battle_tag: str):
        self.battle_tag = battle_tag
        self.sr = Overbuff.get_sr(battle_tag)

class Team():
    def __init__(self, url: str, region: str, name: str, players: List[Player]):
        self.url = url
        self.region = region
        self.name = name
        self.players = players,
        self.average_sr = 0

    def calculate_average(self):
        team_list = []
        for player in self.players:
            sr = player.sr
            team_list.append(sr)
        team_list.sort(reverse=True)
        team_list = team_list[:6]
        team_sr = sum(team_list) / 6
        self.average_sr = team_sr