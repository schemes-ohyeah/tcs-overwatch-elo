from typing import List
import json
from TCS_Objects import Team, Player
from TCS_Functions import TCS_Functions as TCS

def main() -> None:
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
                team["average_sr"]
            )
        )

    for team in teams:
        print(team)

def scrape_teams_write_tojson() -> None:
    # Create a list of Team objects by scraping TCS and Overbuff
    teams = TCS.scrape_teams()
    # Save this data to a json file named teams.json
    TCS.write_teams_tojson(teams)

def read_teams_from_json() -> List[Team]:
    with open("teams.json", "r") as file:
        data = json.load(file)
    return data

main()