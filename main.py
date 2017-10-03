from flask import Flask, render_template, request, jsonify
from TCS_Functions import TCS_Functions as TCS

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/matches")
def matches():
    matches = TCS.read_matches_from_json()
    matches = [matches[key] for key in matches]
    return jsonify([match.__dict__() for match in matches])

@app.route("/rankings/<region>")
@app.route("/rankings")
def rankings(region=None):
    teams = TCS.read_teams_from_json(reset=False)
    teams = [teams[key] for key in teams]
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
    query = request.args.get("query")
    return "Your query for \"" + query + "\" returned 0 results, mostly because " \
                                       "the search algorithm hasn't been implemented yet."

@app.route("/team/<id>")
def team(id):
    teams = TCS.read_teams_from_json(reset=False)
    matches = TCS.read_matches_from_json()
    team = teams[int(id)]
    matches = [matches[match_id] for match_id in team.matches]
    my_matches = []
    opponent = None
    for match in matches:
        data = {}
        if match.team_1id == team.id:
            data["results"] = match.results
            data["elos"] = match.team_1elos
            opponent = teams[match.team_2id].name
        elif match.team_2id == team.id:
            # Matches store win result relative to team 1. Flip if this is team 2
            data["results"] = [[-result[0], result[1]] for result in match.results]
            data["elos"] = match.team_2elos
            opponent = teams[match.team_1id].name
        else:
            print("something is wrong with team match finding")
        data["url"] = match.url
        my_matches.append(data)

    return render_template("team.html",
                           team=team,
                           matches=my_matches,
                           opponent=opponent)

if __name__ == "__main__":
    app.run()