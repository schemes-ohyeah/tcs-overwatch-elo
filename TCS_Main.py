import json
from TCS_Functions import TCS_Functions as TCS

teams = TCS.scrape_teams()
with open("teams.json", "w") as out:
    out.write(
        json.dumps(
            [team.__dict__() for team in teams]
        )
    )