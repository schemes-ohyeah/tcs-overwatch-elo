from TCS_Functions import TCS_Functions as TCS
from TCS_Scraper import TCS_Scraper

def main() -> None:
    # Uncomment the following line to scrape
    # Warning: takes a while
    #scrape_teams_write_tojson()

    teams = TCS.read_teams_from_json(reset_elo=True)
    TCS.calculate_matches(teams)
    TCS.write_teams_tojson(teams)
    for team in teams:
        print(teams[team])

def scrape_teams_write_tojson() -> None:
    """
    Running this will take half an hour as it scrapes all SR from Overbuff.
    Only run this to update the json file from a web scrape

    :return:
    """
    # Create a dictionary  of Team objects by scraping TCS and Overbuff
    teams = TCS.get_teams()
    # Save this data to a json file named teams.json
    TCS.write_teams_tojson(teams)

main()