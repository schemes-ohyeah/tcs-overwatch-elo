import json
from bs4 import BeautifulSoup
from typing import List
from TCS_Objects import Team
from TCS_Scraper import TCS_Scraper

class TCS_Functions():
    @staticmethod
    def scrape_teams() -> List[Team]:
        """
        Using BeautifulSoup scrape data, create Team objects
        (refer to TCS_Objects.py)

        :return: list of Team objects with default None players and sr
        """
        # Get teams
        soup = TCS_Scraper.get_teams()

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

        return teams

    @staticmethod
    def write_teams_tojson(teams: List[Team]) -> None:
        """
        Takes a list of team objects and writes them to a json file

        :param teams: list of Team objects
        :return: void write out to filename teams.json
        """
        with open("teams.json", "w") as out:
            out.write(
                json.dumps(
                    [team.__dict__() for team in teams]
                )
            )