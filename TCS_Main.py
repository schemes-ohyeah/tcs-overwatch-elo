from TCS_Functions import TCS_Functions as TCS

teams = TCS.scrape_teams()
for team in teams:
    print(team)