from flask import Flask, render_template, request, jsonify
from TCS_Functions import TCS_Functions as TCS
from TCS_Objects import Match

app = Flask(__name__)
GLOBAL_teams = TCS.read_teams_from_json(reset=False)
GLOBAL_matches = TCS.read_matches_from_json()
GLOBAL_future_matches = TCS.read_matches_from_json(future=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/matches")
def matches():
    global GLOBAL_matches
    matches = [GLOBAL_matches[key] for key in GLOBAL_matches]
    return jsonify([match.__dict__() for match in matches])

@app.route("/rankings/<region>")
@app.route("/rankings")
def rankings(region=None):
    global GLOBAL_teams
    teams = [GLOBAL_teams[key] for key in GLOBAL_teams]
    if region:
        teams = [team for team in teams if team.region == region]
    teams.sort(key=lambda x: x.elo, reverse=True)
    if request.args.get("json"):
        return jsonify([team.__dict__() for team in teams])
    if region is None:
        json_link = "/rankings?json=true"
    else:
        json_link = "/rankings/" + region + "?json=true"
    if region is None:
        region = "nationwide"
    return render_template("rankings.html",
                           teams=teams,
                           region=region,
                           json_link=json_link)

@app.route("/search")
def search():
    global GLOBAL_teams
    query = request.args.get("query").lower()
    teams = [GLOBAL_teams[key] for key in GLOBAL_teams]
    results = []
    for team in teams:
        if query in team.name.lower():
            results.append(team)
        if query in team.university.lower():
            results.append(team)
        for player in team.players:
            if query in player.battle_tag.lower():
                results.append(team)

    return render_template("search.html",
                           query=query,
                           results=results)

@app.route("/team/<id>")
def team(id):
    global GLOBAL_teams, GLOBAL_matches, GLOBAL_future_matches
    team = GLOBAL_teams[int(id)]
    matches = [GLOBAL_matches[match_id] for match_id in team.matches]
    my_matches = []
    elo_trend = [team.average_sr]
    for match in matches:
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
        data["url"] = match.url
        elo_trend.extend(data["elos"][1:])

        # Probably to win based on math from here
        data["win_chance"] = Match.calculate_win_chance(data["elos"][0], data["opponent_elo"])

        my_matches.append(data)

    my_future_matches = []
    for match_id in team.future_matches:
        future_match = GLOBAL_future_matches[match_id]
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
        data["win_chance"] = Match.calculate_win_chance(data["elo"], data["opponent_elo"])
        my_future_matches.append(data)

    return render_template("team.html",
                           team=team,
                           elo_trend=elo_trend,
                           matches=my_matches,
                           future_matches=my_future_matches)

if __name__ == "__main__":
    app.run()