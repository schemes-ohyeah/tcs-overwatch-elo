import pickle
import TCS_Functions as TCS
from TCS_Scraper import TCS_Scraper
from typing import Dict

def main() -> None:
    # Uncomment the following line to scrape
    # Warning: takes a while
    # scrape_teams_write_tojson()

    teams = TCS.read_teams_from_json(reset=True, swiss=True)

    # Updates regional_matches.json
    # update_regionals(teams)

    # Looks up team ids from national swiss and matches them to team ids
    # from regional bracket, caching to a pickle
    # TCS.get_swiss_ids(teams)

    swiss_ids = read_swiss_ids()

    # NYU
    swiss_ids[18451] = 15360
    print(teams[15360].name, "changed to NYU Ultraviolets")
    teams[15360].name = "NYU Ultraviolets"

    # UIC
    swiss_ids[18450] = 15341
    print(teams[15341].name, "changed to We're Boosted")
    teams[15341].name = "We're Boosted"

    update_swiss(teams, swiss_ids)

    update_doom(teams, swiss_ids, curr_round=4)

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

def read_swiss_ids() -> Dict[int, int]:
    with open("static/swiss_ids.pkl", "rb") as f:
        return pickle.load(f)

def update_regionals(teams) -> None:
    match_urls = TCS_Scraper.scrape_regional_matches(end_round=10)
    regional_matches = TCS.calculate_matches(match_urls, teams)
    TCS.write_tojson(teams, "teams.json")
    TCS.write_tojson(regional_matches, "regional_matches.json")

def update_swiss(teams, swiss_ids) -> None:
    match_urls = TCS_Scraper.scrape_swiss_matches()
    swiss_matches = TCS.calculate_matches(match_urls, teams, lut=swiss_ids)
    TCS.write_tojson(swiss_matches, "swiss_matches.json")
    TCS.write_tojson(teams, "teams_stage2.json")

def update_doom(teams, swiss_ids, curr_round: int) -> None:
    doom_matches_urls = TCS_Scraper.scrape_doom_matches()

    match_urls = []
    for url_list in doom_matches_urls:
        match_urls.extend(url_list)
    future_matches = TCS.predict_matches(match_urls, teams, lut=swiss_ids)

    # Get completed doom rounds
    match_urls = []
    for x in range(curr_round):
        match_urls.extend(doom_matches_urls[x])
    doom_matches = TCS.calculate_matches(match_urls, teams, lut=swiss_ids)
    TCS.write_tojson(doom_matches, "doom_matches.json")
    TCS.write_tojson(teams, "teams_stage2.json")

    # Get scheduled doom rounds
    doom_matches = []
    # for url_list in doom_matches_urls:
    for x in range(curr_round, len(doom_matches_urls)):
        doom_path = []
        for url in doom_matches_urls[x]:
            url_id = int(url.split("/")[-1])
            doom_path.append(future_matches[url_id])
        doom_matches.append(doom_path)

    TCS.write_doom_tojson(doom_matches, "doom_matches.json")
    TCS.write_tojson(future_matches, "future_matches.json")
    TCS.write_tojson(teams, "teams_stage2.json")

main()