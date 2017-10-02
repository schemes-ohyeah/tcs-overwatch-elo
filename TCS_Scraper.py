from typing import List, Dict
from Scraper import Scraper

class TCS_Scraper(Scraper):
    @staticmethod
    def scrape_teams():
        """
        Gets HTML from the following url listing all teams

        :return: BeautifulSoup response
        """
        return Scraper.get_soup("https://compete.tespa.org/tournament/75/phase/1")

    @staticmethod
    def scrape_players(url) ->List[str]:
        """
        Takes a team url and gets all battle tags
        excluding team coordinator and substitutes

        :param url: team url
        :return: String list of battle tags
        """
        scraped_players = []
        soup = Scraper.get_soup(url, "lxml")

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
    def scrape_match(url, teams) -> (int, List[int], int):
        """
        Returns the team ids and list of results relative to team 1 where
        results is a list of ints
        [1] -> win
        [0] -> draw
        [-1] -> loss

        :param url:
        :return: team_1id, results,  team_2id
        """
        soup = Scraper.get_soup(url)
        team_1url = soup.find("div", {"id" : "player1Container"}).find("a")
        team_1url = team_1url.get("href") if team_1url else None
        team_2url = soup.find("div", {"id" : "player2Container"}).find("a")
        team_2url = team_2url.get("href") if team_2url else None

        results = []
        if team_1url and team_2url:
            # Get the team id and find the team object from the dict of teams
            team_1id = int(team_1url.split("/")[-1])
            team_2id = int(team_2url.split("/")[-1])
            team_1 = teams[team_1id]
            team_2 = teams[team_2id]

            # Table is a list of maps and their results in order
            result_table = soup.find("table", {"class" : "table panel-body table-bordered"})
            if result_table:
                for row in result_table.find_all("tr"):
                    cols = row.find_all("td")
                    if not cols:
                        continue
                    map = cols[1].text.strip()
                    winner = cols[2].text.strip()
                    if winner == team_1.name:
                        results.append(1)
                        print(team_1.name + " wins " + map + " against " + team_2.name)
                    elif winner == team_2.name:
                        results.append(-1)
                        print(team_2.name + " wins " + map + " against " + team_1.name)
                    else:
                        results.append(0)
                        print(team_1.name + " draws " + team_2.name + " on " + map)
        else:
            team_1id = team_2id = None

        return team_1id, results, team_2id

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
            soup = Scraper.get_soup(url)
            matchups = soup.find_all("div", {"data-toggle":"tooltip"})
            for matchup in matchups:
                print(matchup)
                scores = matchup.find_all("div", {"class":"pull-right"})
                test = 0
                for score in scores:
                    if score.text.strip() == "0" or score.text.strip() == "F":
                        test += 1
                match_url = matchup.find("a").get("href")
                if test != 2:
                    matches.append(match_url)

        # URLs are duplicated for each cell due to how the UI is laid out
        return matches[::2]