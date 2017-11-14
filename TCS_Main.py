import pickle
from TCS_Functions import TCS_Functions as TCS
from TCS_Scraper import TCS_Scraper

def main() -> None:
    # Uncomment the following line to scrape
    # Warning: takes a while
    # scrape_teams_write_tojson()

    teams = TCS.read_teams_from_json(reset=True)
    TCS.write_tojson(teams, "teams.json")

    # Looks up team ids from national swiss and matches them to team ids
    # from regional bracket, caching to a pickle
    # TCS.get_swiss_ids(teams)

    # Updates regional_matches.json - this should not be touched since
    # this section of the tourney is over
    # update_regionals(teams)

    swiss_ids = read_swiss_ids()
    # NYU
    swiss_ids[18451] = 15360
    print(teams[15360].name, "changed to NYU Ultraviolets")
    teams[15360].name = "NYU Ultraviolets"

    # UIC
    swiss_ids[18450] = 15341
    print(teams[15341].name, "changed to We're Boosted")
    teams[15341].name = "We're Boosted"

    match_urls = TCS_Scraper.scrape_swiss_matches()
    swiss_matches = TCS.calculate_matches(match_urls, teams, lut=swiss_ids)
    TCS.write_tojson(swiss_matches, "swiss_matches.json")

    # match_urls = TCS_Scraper.scrape_matches(
    #     start_round=11,
    #     end_round=14,
    #     future=True
    # )
    # future_matches = None#TCS.predict_matches(teams)
    # TCS.write_tojson(future_matches, "future_matches.json")

def scrape_teams_write_tojson() -> None:
    """
    Running this will take half an hour as it scrapes all SR from Overbuff.
    Only run this to update the json file from a web scrape

    :return:
    """
    # Create a dictionary of Team objects by scraping TCS and Overbuff
    teams = TCS.get_teams()
    # Save this data to a json file named teams.json
    TCS.write_tojson(teams, "teams.json")

def read_swiss_ids() -> None:
    with open("static/swiss_ids.pkl", "rb") as f:
        return pickle.load(f)

def update_regionals(teams) -> None:
    match_urls = TCS_Scraper.scrape_regional_matches(end_round=10)
    regional_matches = TCS.calculate_matches(match_urls, teams)
    TCS.write_tojson(regional_matches, "regional_matches.json")

main()