import json
from typing import Dict
from TCS_Objects import Team, Player, Match
from TCS_Scraper import TCS_Scraper

CURRENT_ROUND  = 2

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
                        team[NAME]
                    )
                )

        team_dict = {}
        for team in teams:
            team_dict[team.id] = team

        return team_dict

    @staticmethod
    def calculate_matches(teams: Dict[int, Team]) -> Dict[int, Match]:
        """
        Goes through all matches and calculates new elo for teams with each
        map causing a new elo shift, rather than an overall bo3 / bo5

        :param teams:
        :return:
        """
        match_urls = TCS_Scraper.scrape_matches(end_round=CURRENT_ROUND)
        matches = {}
        for match in match_urls:
            print("Scraping", match)
            team_1id, results, team_2id \
                = TCS_Scraper.scrape_match(match, teams)
            # If nothing happened on this match page, skip it
            if not results:
                continue
            team_1 = teams[team_1id]
            team_2 = teams[team_2id]

            team_1elos = [team_1.elo]
            team_2elos = [team_2.elo]
            for result in results:
                # Calculate new elo for each team
                e1p, e2p = Team.calculate_elo(team_1.elo, team_2.elo, result[0])

                # Print elo changes for each team
                print(team_1.name, str(e1p - team_1.elo))
                print(team_2.name, str(e2p - team_2.elo))

                # Store the elo changes
                team_1elos.append(e1p)
                team_2elos.append(e2p)

                # Set new elo values
                team_1.elo = e1p
                team_2.elo = e2p

            # Create a new match object and append it to the list of matches
            new_match = Match(
                match,
                team_1id,
                team_2id,
                team_1elos,
                team_2elos,
                results
            )
            matches[new_match.id] = new_match

            # Add match id to each team object
            team_1.matches.append(new_match.id)
            team_2.matches.append(new_match.id)

        return matches

    @staticmethod
    def predict_matches(teams: Dict[int, Team]):
        match_urls = TCS_Scraper.scrape_matches(
            start_round=CURRENT_ROUND + 1,
            end_round=CURRENT_ROUND + 2,
            future=True
        )
        matches = {}
        for match in match_urls:
            print("Scraping", match)
            team_1id, team_2id = TCS_Scraper.scrape_future_match(match, teams)
            # If there are not 2 teams in this match, skip
            if not (team_1id and team_2id):
                continue
            team_1 = teams[team_1id]
            team_2 = teams[team_2id]
            new_match = Match(
                match,
                team_1id,
                team_2id,
                [team_1.elo],
                [team_2.elo],
            )
            matches[new_match.id] = new_match

            # Add future match ids to each team object
            team_1.future_matches.append(new_match.id)
            team_2.future_matches.append(new_match.id)

        return matches

    @staticmethod
    def write_tojson(data, filename) -> None:
        """
        Takes a dict of objects and writes them to a json file

        :param data:
        :param filename:
        :return:
        """
        with open("static/json/" + filename, "w") as out:
            out.write(
                json.dumps(
                    [data[datum].__dict__() for datum in data]
                )
            )

    @staticmethod
    def read_teams_from_json(reset: bool=False) -> Dict[int, Team]:
        """
        Reads the json file and creates a list of Team objects

        :return:
        """
        with open("static/json/teams.json", "r") as file:
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
                    None,
                    players,
                    team["average_sr"],
                    team["average_sr"] if reset else team["elo"],
                    None if reset else team["matches"],
                    None if reset else team["future_matches"]
                )
            )

        team_dict = {}
        for team in teams:
            team_dict[team.id] = team

        return team_dict

    @staticmethod
    def read_matches_from_json(future=False) -> Dict[int, Match]:
        filename = "static/json/"
        if future:
            filename += "future_matches.json"
        else:
            filename += "matches.json"
        with open(filename, "r") as file:
            data = json.load(file)

        matches = []
        for match in data:
            matches.append(
                Match(
                    match["url"],
                    match["team_1id"],
                    match["team_2id"],
                    match["team_1elos"],
                    match["team_2elos"],
                    match["results"],
                )
            )
        match_dict = {}
        for match in matches:
            match_dict[match.id] = match

        return match_dict