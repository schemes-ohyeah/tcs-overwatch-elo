from TCS_Functions import TCS_Functions as TCS

def main() -> None:
    # Uncomment the following line to scrape
    # Warning: takes a while
    # scrape_teams_write_tojson()

    teams = TCS.read_teams_from_json(reset=True)
    matches = TCS.calculate_matches(teams)
    future_matches = None#TCS.predict_matches(teams)
    TCS.write_tojson(teams, "teams.json")
    TCS.write_tojson(matches, "matches.json")
    TCS.write_tojson(future_matches, "future_matches.json")

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

main()