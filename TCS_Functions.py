import json
from typing import Dict
from TCS_Objects import Team, Player
from TCS_Scraper import TCS_Scraper

class TCS_Functions():
    @staticmethod
    def get_teams() -> Dict[int, Team]:
        """
        Using BeautifulSoup scrape data, create Team objects
        (refer to TCS_Objects.py)

        :return: list of Team objects with default None players and sr
        """
        # Get teams
        soup = TCS_Scraper.scrape_teams()

        # Get each region table
        regions = soup.find_all("table", {"class" : "table table-hover table-bordered"})

        regions_teams = []

        for region in regions:
            rows = region.find_all("tr")[1:]
            region_list = []

            # find the url and team name for each team in this region
            for row in rows:
                tag = row.find("a")
                name = tag.text.strip()
                url = tag.get("href")
                region_list.append([name, url])

            # append this region's list of names and url
            regions_teams.append(region_list)

        NAME = 0
        URL = 1
        teams = []

        # Using this list, create Team objects
        REGION_NAMES = ["west", "south", "north", "east"]
        for x in range(len(REGION_NAMES)):
            for team in regions_teams[x]:
                teams.append(
                    Team(
                        team[URL],
                        REGION_NAMES[x],
                        team[NAME],
                    )
                )

        team_dict = {}
        for team in teams:
            team_dict[team.id] = team

        return team_dict

    @staticmethod
    def calculate_matches(teams: Dict[int, Team]) -> None:
        """
        Goes through all matches and calculates new elo for teams with each
        map causing a new elo shift, rather than an overall bo3 / bo5

        :param teams:
        :return:
        """
        matches = TCS_Scraper.scrape_matches()
        for match in matches:
            print("Scraping", match)
            team_1id, results, team_2id \
                = TCS_Scraper.scrape_match(match, teams)
            if not results:
                continue
            team_1 = teams[team_1id]
            team_2 = teams[team_2id]

            for result in results:
                e1p, e2p = Team.calculate_elo(team_1.elo, team_2.elo, result)
                print(team_1.name, str(e1p - team_1.elo))
                print(team_2.name, str(e2p - team_2.elo))
                team_1.elo = e1p
                team_2.elo = e2p

    @staticmethod
    def write_teams_tojson(teams: Dict[int, Team]) -> None:
        """
        Takes a list of team objects and writes them to a json file

        :param teams: list of Team objects
        :return: void write out to filename teams.json
        """
        with open("teams.json", "w") as out:
            out.write(
                json.dumps(
                    [teams[team].__dict__() for team in teams]
                )
            )

    @staticmethod
    def read_teams_from_json(reset_elo: bool=False) ->Dict[int, Team]:
        """
        Reads the json file and creates a list of Team objects

        :return:
        """
        with open("teams.json", "r") as file:
            data = json.load(file)

        teams = []
        for team in data:
            players = [Player(player["battle_tag"], player["skill_rating"])
                       for player in team["players"]]
            teams.append(
                Team(
                    team["url"],
                    team["region"],
                    team["name"],
                    players,
                    team["average_sr"],
                    team["average_sr"] if reset_elo else team["elo"]
                )
            )

        team_dict = {}
        for team in teams:
            team_dict[team.id] = team

        return team_dict