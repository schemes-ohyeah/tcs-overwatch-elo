from typing import List
from bs4 import BeautifulSoup
import requests
requests.packages.urllib3.disable_warnings()

def get_soup(url, soupMethod="html.parser"):
    r = requests.get(url, timeout=20, verify=False)
    raw_html = r.text
    return BeautifulSoup(raw_html, soupMethod)

class TCS_Scraper():
    @staticmethod
    def scrape_teams():
        """
        Gets HTML from the following url listing all teams

        :return: BeautifulSoup response
        """
        return get_soup("https://compete.tespa.org/tournament/75/phase/1")

    @staticmethod
    def scrape_players(url) ->List[str]:
        """
        Takes a team url and gets all battle tags
        excluding team coordinator and substitutes

        :param url: team url
        :return: String list of battle tags
        """
        scraped_players = []
        soup = get_soup(url, "lxml")

        table = soup.find("table")
        rows = table.find_all("tr")[:-1]

        for row in rows:
            role = row.find("i")
            if role:
                if role.get("title") == "Player":
                    handle = row.find("td", {"class": "text-break"}).text
                    scraped_players.append(handle)
        return scraped_players

    @staticmethod
    def scrape_match(url):
        """
        Returns the team urls and the number of won / loss
        :param url:
        :return:
        """
        soup = get_soup(url)
        team_1 = soup.find("div", {"id" : "player1Container"}).find("a")
        team_1 = team_1.get("href") if team_1 else None
        team_2 = soup.find("div", {"id" : "player2Container"}).find("a")
        team_2 = team_2.get("href") if team_2 else None

        if team_1 and team_2:
            t1_score = soup.find("input", {"id" : "team1_score"})
            t1_score = int(t1_score.get("value")) if t1_score.get("value") else 0
            t2_score = soup.find("input", {"id" : "team2_score"})
            t2_score = int(t2_score.get("value")) if t2_score.get("value") else 0
        else:
            t1_score = t2_score = 0

        total_games = t1_score + t2_score

        t1_lose = total_games - t1_score

        return team_1, t1_score, t1_lose, team_2

    @staticmethod
    def scrape_matches() -> List[str]:
        """
        Gets a list of all matches by visiting each region's individual page

        :return: string list of match urls
        """
        base_url = "https://compete.tespa.org/tournament/75/phase/1/group/"
        matches = []
        for x in range(1, 5):
            url = base_url + str(x)
            soup = get_soup(url)
            links = soup.find_all("a")
            for link in links:
                match_url = link.get("href")
                if "match" in match_url:
                    matches.append(match_url)

        # URLs are duplicated for each cell due to how the UI is laid out
        return matches[::2]