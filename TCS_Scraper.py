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
    def scrape_future_match(url, teams) -> (int, int):
        """
        Returns two team ids in the matchup

        :param url:
        :param teams:
        :return:
        """
        soup = Scraper.get_soup(url)
        team_1url = soup.find("div", {"id" : "player1Container"}).find("a")
        team_1url = team_1url.get("href") if team_1url else None
        team_2url = soup.find("div", {"id" : "player2Container"}).find("a")
        team_2url = team_2url.get("href") if team_2url else None

        if team_1url and team_2url:
            team_1id = int(team_1url.split("/")[-1])
            team_2id = int(team_2url.split("/")[-1])
            return team_1id, team_2id
        return None, None

    @staticmethod
    def scrape_match(url, teams) -> (int, List[List[int]], int):
        """
        Returns the team ids and list of results relative to team 1 where
        results is a list of ints in index 0
        [1] -> win
        [0] -> draw
        [-1] -> loss
        and the map in index 1

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
                        # Top row will be all <th> instead of <td>. Skip this row
                        continue
                    map = cols[1].text.strip()
                    winner = cols[2].text.strip()
                    if winner == team_1.name:
                        results.append([1, map])
                        print(team_1.name + " wins " + map + " against " + team_2.name)
                    elif winner == team_2.name:
                        results.append([-1, map])
                        print(team_2.name + " wins " + map + " against " + team_1.name)
                    else:
                        results.append([0, map])
                        print(team_1.name + " draws " + team_2.name + " on " + map)
        else:
            team_1id = team_2id = None

        return team_1id, results, team_2id

    @staticmethod
    def scrape_matches(end_round: int, start_round: int=1, future=False) -> List[str]:
        """
        Gets a list of all matches by visiting each region's individual page

        :return: string list of match urls
        """
        base_url = "https://compete.tespa.org/tournament/75/phase/1/group/"
        matches = []
        # for each group (region)
        for x in range(1, 5):
            print("Looking for matches in group", x)
            url = base_url + str(x)
            soup = Scraper.get_soup(url)
            # for each round up to the specific round in parameter, inclusive
            for x in range(start_round, end_round + 1):
                print("Looking for matches in round", x)
                round_soup = soup.find("div", {"id" : "collapseRound" + str(x)})
                matchups = round_soup.find_all("table",
                                               {"class" : "table margin-top margin-bottom panel"})

                if future:
                    # If future round do not verify if it has taken place
                    for matchup in matchups:
                        match_url = matchup.find("a").get("href")
                        matches.append(match_url)
                else:
                    # Otherwise, make sure the game has been played by making
                    # sure the total score is more than 0
                    for matchup in matchups:
                        # Check that something has happened in this matchup
                        # eg no forfeit or empty score
                        scores = matchup.find_all("div", {"class" : "pull-right"})
                        score1 = scores[0].text.strip()
                        score1 = int(score1) if score1.isdigit() else 0
                        score2 = scores[1].text.strip()
                        score2 = int(score2) if score2.isdigit() else 0
                        if score1 + score2 > 0:
                            match_url = matchup.find("a").get("href")
                            matches.append(match_url)

        return matches