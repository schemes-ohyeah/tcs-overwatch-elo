from Overbuff_Scraper import Overbuff_Scraper as Overbuff
from bs4 import BeautifulSoup
import requests
requests.packages.urllib3.disable_warnings()

class Player():
    def __init__(self, battle_tag: str):
        self.battle_tag = battle_tag
        self.sr = Overbuff.get_sr(battle_tag)

    def __str__(self):
        return self.battle_tag + " (" + self.sr + " SR)"

class Team():
    def __init__(self, url: str, region: str, name: str):
        self.url = url
        self.region = region
        self.name = name
        self.players = [],
        self.average_sr = 0

        self.scrape_player_list()
        self.calculate_average()

    def __str__(self):
        players = ""
        for player in self.players:
            players += "\t" + str(player) + "\n"

        return self.name + "<" + self.url + ">\n" \
               + "region: " + self.region + "\n" \
               + "average_sr: " + str(self.average_sr) + "\n" \
               + "players: " + "\n" + players

    def scrape_player_list(self):
        # TODO Sean will fill something here
        scraped_players = []
        # Sean just do the thing above here so it's a list of battle tags

        url = self.url
        r = requests.get(url, timeout=20, verify=False)

        raw_html = r.text
        soup = BeautifulSoup(raw_html, "html.parser")

        table = soup.find("table")
        rows = table.find_all("tr")[:-1]

        for row in rows:
            role = row.find("i")
            if role.get("title") == "Player":
                handle = row.find("td", {"class": "text-break"}).text
                scraped_players.append(handle)

        player_list = []
        for battle_tag in scraped_players:
            player_list.append(Player(battle_tag))
        self.players = player_list

    def calculate_average(self):
        team_list = []
        for player in self.players:
            sr = player.sr
            team_list.append(sr)
        team_list.sort(reverse=True)
        team_list = team_list[:6]
        team_sr = sum(team_list) / 6
        self.average_sr = team_sr