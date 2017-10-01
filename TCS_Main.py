from typing import List
import json
from TCS_Objects import Team, Player
from TCS_Functions import TCS_Functions as TCS
from TCS_Scraper import TCS_Scraper

def main() -> None:
    # Uncomment the following line to scrape
    # Warning: takes a while
    #scrape_teams_write_tojson()

    teams = []
    for team in read_teams_from_json():
        players = [Player(player["battle_tag"], player["skill_rating"])
                   for player in team["players"]]
        teams.append(
            Team(
                team["url"],
                team["region"],
                team["name"],
                players,
                team["average_sr"],
                team["elo"]
            )
        )

    for team in teams:
        print(team)

    for match in TCS_Scraper.get_matches():
        print(match)

def scrape_teams_write_tojson() -> None:
    """
    Running this will take half an hour as it scrapes all SR from Overbuff.
    Only run this to update the json file from a web scrape

    :return:
    """
    # Create a list of Team objects by scraping TCS and Overbuff
    teams = TCS.scrape_teams()
    # Save this data to a json file named teams.json
    TCS.write_teams_tojson(teams)

def read_teams_from_json() -> List[Team]:
    """
    Reads the json file and creates a list of Team objects

    :return:
    """
    with open("teams.json", "r") as file:
        data = json.load(file)
    return data

main()