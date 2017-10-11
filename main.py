from flask import Flask, render_template, request, jsonify
from TCS_Functions import TCS_Functions as TCS
from TCS_Objects import Team, Match
from typing import List

app = Flask(__name__)
GLOBAL_teams = TCS.read_teams_from_json(reset=False)
GLOBAL_matches = TCS.read_matches_from_json()
GLOBAL_future_matches = TCS.read_matches_from_json(future=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/matches")
def matches_json():
    """
    Returns a json for all matches. Currently not publicly findable.
    :return:
    """
    global GLOBAL_matches

    matches = [GLOBAL_matches[key] for key in GLOBAL_matches]
    return jsonify([match.__dict__() for match in matches])


@app.route("/rankings/<region>")
@app.route("/rankings")
def rankings_page(region=None):
    """
    Lists all teams in order by rank, optionally by region
    :param region: west north south east
    :return:
    """
    global GLOBAL_teams

    teams = [GLOBAL_teams[key] for key in GLOBAL_teams]
    # If a region is specified, filter filter teams only by the region
    if region:
        teams = [team for team in teams if team.region == region]

    # Sort by elo
    teams.sort(key=lambda x: x.elo, reverse=True)

    # If ?json=[anything] return json page rather than html
    if request.args.get("json"):
        return jsonify([team.__dict__() for team in teams])

    # Set json link to be displayed in html
    if region is None:
        json_link = "/rankings?json=true"
        region = "nationwide"
    else:
        json_link = "/rankings/" + region + "?json=true"
    return render_template("rankings.html",
                           teams=teams,
                           region=region,
                           json_link=json_link)


@app.route("/search")
def search_page():
    """
    Searches by team name, university, or player within team
    :return:
    """
    global GLOBAL_teams

    query = request.args.get("query").lower()
    teams = [GLOBAL_teams[key] for key in GLOBAL_teams]
    results = []

    for team in teams:
        name = team.name.lower()
        university = team.university.lower()
        # TODO Ability to search by abbreviation
        abbreviation = ""
        search = " ".join([name, university, abbreviation])
        if query in search:
            # Search for name, university, TODO Abbreviation
            results.append(team)
        else:
            # Search for battle tag in team
            for player in team.players:
                if query in player.battle_tag.lower():
                    results.append(team)

    return render_template("search.html",
                           query=query,
                           results=results)


@app.route("/team/<team_id>")
def team_page(team_id):
    """
    Displays known team data such as players, match history, and future
    matches. Pending feature to show summary of map choices (maps
    chosen when team loses) and best maps (just based on wins)

    :param team_id:
    :return:
    """
    global GLOBAL_teams, GLOBAL_matches, GLOBAL_future_matches

    team = GLOBAL_teams[int(team_id)]
    matches = [
        GLOBAL_matches[match_id] for match_id in team.matches
    ]

    my_matches = []
    # Init elo trend as team.average_sr as first item, will add more later
    elo_trend = [team.average_sr]
    # Refer to find_match_data doc to see what is returned in data
    for match in matches:
        data = find_match_data(team, match, elo_trend)
        my_matches.append(data)

    future_matches = [
        GLOBAL_future_matches[match_id] for match_id in team.future_matches
    ]
    my_future_matches = []
    # Refer to find_future_match_data to see what is returned in data
    for future_match in future_matches:
        data = find_future_match_data(team, future_match)
        my_future_matches.append(data)

    return render_template("team.html",
                           team=team,
                           elo_trend=elo_trend,
                           matches=my_matches,
                           future_matches=my_future_matches)


def find_match_data(team: Team, match: Match, elo_trend: List[int]):
    """
    Match data is stored in the perspective of "team 1" as defined by Tespa.
    Since the match page is to show in perspective of the requested team,
    data is rearranged if necessary to be in that team's perspective.

    :param team:
    :param match:
    :param elo_trend:
    :return: Dict ->
        results: list of str map and int -1 / 0 / 1 indicating loss, tie, win
        elos: list of float pre-calculated Elo values from each map
        opponent_elo: float opponent team starting Elo
        opponent: Team
        opponent_id: int
        url: str tespa url of the match
        win_chance: float calculated win chance from starting Elos
    """
    global GLOBAL_teams

    data = {}
    if match.team_1id == team.id:
        data["results"] = match.results
        data["elos"] = match.team_1elos
        data["opponent_elo"] = match.team_2elos[0]
        data["opponent"] = GLOBAL_teams[match.team_2id].name
        data["opponent_id"] = match.team_2id
    elif match.team_2id == team.id:
        # Matches store win result relative to team 1. Flip if this is team 2
        data["results"] = [[-result[0], result[1]] for result in match.results]
        data["elos"] = match.team_2elos
        data["opponent_elo"] = match.team_1elos[0]
        data["opponent"] = GLOBAL_teams[match.team_1id].name
        data["opponent_id"] = match.team_1id
    else:
        print("something is wrong with team match finding")
    # TODO Display url to frontend
    data["url"] = match.url
    elo_trend.extend(data["elos"][1:])

    # Probably to win based on math from here
    data["win_chance"] = Match.calculate_win_chance(
        data["elos"][0], data["opponent_elo"]
    )

    return data


def find_future_match_data(team: Team, future_match: Match):
    """
    Refer to find_match_data doc for details about perspective

    :param team:
    :param future_match:
    :return: Dict ->
        elo: float current team's elo
        opponent_elo: float
        opponent: Team
        opponent_id: int
        win_chance: float calculated win chance from most recent Elos
    """
    global GLOBAL_teams

    data = {}
    if future_match.team_1id == team.id:
        data["elo"] = future_match.team_1elos[0]
        data["opponent_elo"] = future_match.team_2elos[0]
        data["opponent"] = GLOBAL_teams[future_match.team_2id].name
        data["opponent_id"] = future_match.team_2id
    elif future_match.team_2id == team.id:
        data["elo"] = future_match.team_2elos[0]
        data["opponent_elo"] = future_match.team_1elos[0]
        data["opponent"] = GLOBAL_teams[future_match.team_1id].name
        data["opponent_id"] = future_match.team_1id
    else:
        print("something is wrong with the future match finding")
    data["win_chance"] = Match.calculate_win_chance(
        data["elo"], data["opponent_elo"]
    )

    return data


if __name__ == "__main__":
    app.run()
