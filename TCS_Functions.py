import json, pickle
from typing import Dict, List
from TCS_Objects import Team, Player, Match
from TCS_Scraper import TCS_Scraper

CURRENT_ROUND = 10


def get_swiss_ids(teams: Dict[int, Team]) -> None:
    soup = TCS_Scraper.get_soup("https://compete.tespa.org/tournament/90/phase/1")
    table = soup.find("table", {"class" : "table table-hover table-bordered"})
    rows = table.find_all("tr")[1:]

    swiss_teams = {}

    for row in rows:
        tag = row.find("a")

        name = tag.text.strip()
        url = tag.get("href")
        id = int(url.split("/")[-1])
        swiss_teams[name] = id

    id_pair = {}
    for team_id in teams:
        team = teams[team_id]
        if team.name in swiss_teams:
            id_pair[swiss_teams[team.name]] = team.id
            print("\tfound", team.name)
        else:
            print(team.name, "not found")

    with open("static/swiss_ids.pkl", "wb") as f:
        pickle.dump(id_pair, f, pickle.HIGHEST_PROTOCOL)


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


def calculate_matches(
        match_urls: List[str], teams: Dict[int, Team], lut: Dict[int, int]=None) \
        -> Dict[int, Match]:
    """
    Goes through all matches and calculates new elo for teams with each
    map causing a new elo shift, rather than an overall bo3 / bo5

    :param match_urls:
    :param teams:
    :param lut: look up table for swiss ids
    :return:
    """
    matches = {}
    for match in match_urls:
        print("Scraping", match)
        team_1id, results, team_2id \
            = TCS_Scraper.scrape_match(match, teams, lut=lut)
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


def predict_matches(match_urls: List[str], teams: Dict[int, Team], lut=None) -> Dict[int, Match]:
    matches = {}
    for match in match_urls:
        print("Scraping", match)
        team_1id, team_2id = TCS_Scraper.scrape_future_match(match, teams, lut)
        # If there are not 2 teams in this match, skip
        # if not (team_1id and team_2id):
        #     continue
        team_1 = teams[team_1id] if team_1id in teams else None
        team_2 = teams[team_2id] if team_2id in teams else None

        if not team_2:
            new_match = Match(
                match,
                team_1id,
                team_2id,
                [team_1.elo],
                [0]
            )
        else:
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

        if team_2:
            team_2.future_matches.append(new_match.id)

    return matches

def write_doom_tojson(data, filename: str) -> None:
    with open("static/json/" + filename, "w") as out:
        out.write(
            json.dumps(
                [[subdatum.__dict__() for subdatum in datum] for datum in data]
            )
        )

def write_tojson(data, filename: str) -> None:
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


def read_teams_from_json(reset: bool=False, swiss: bool=False) -> Dict[int, Team]:
    """
    Reads the json file and creates a list of Team objects

    :return:
    """
    filename = "static/json/"
    with open(filename + "teams.json", "r") as file:
        data1 = json.load(file)

    teams1 = []
    for team in data1:
        players = [Player(player["battle_tag"], player["skill_rating"])
                   for player in team["players"]]
        teams1.append(
            Team(
                team["url"],
                team["region"],
                team["name"],
                team["university"],
                players,
                team["average_sr"],
                team["elo"] if swiss else 1500,#team["average_sr"],
                None if reset else team["matches"],
                None
            ))

    team_dict = {}
    for team in teams1:
        team_dict[team.id] = team

    if reset:
        return team_dict

    with open(filename + "teams_stage2.json") as file:
        data2 = json.load(file)

    teams2 = []
    for team in data2:
        players = [Player(player["battle_tag"], player["skill_rating"])
                   for player in team["players"]]
        new_team = Team(
            team["url"],
            team["region"],
            team["name"],
            team["university"],
            players,
            team["average_sr"],
            team["elo"],
            team["matches"],
            team["future_matches"]
        )

        regional_matches = team_dict[new_team.id].matches
        regional_matches.extend(new_team.matches)
        new_team.matches = regional_matches

        teams2.append(new_team)

    team_dict = {}
    for team in teams2:
        team_dict[team.id] = team
    return team_dict


def read_matches_from_json(filename: str) -> Dict[int, Match]:
    base = "static/json/"
    with open(base + filename, "r") as file:
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

def read_doom_matches_from_json(filename: str) -> List[List[Match]]:
    base = "static/json/"
    with open (base + filename, "r") as file:
        data = json.load(file)
    doom_matches = []
    for path in data:
        doom_path = []
        for match in path:
            doom_path.append(
                Match(
                    match["url"],
                    match["team_1id"],
                    match["team_2id"],
                    match["team_1elos"],
                    match["team_2elos"],
                    match["results"]
                )
            )
        doom_matches.append(doom_path)
    return doom_matches