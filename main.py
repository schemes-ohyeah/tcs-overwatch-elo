from flask import Flask, render_template, request, jsonify
from TCS_Functions import TCS_Functions as TCS

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/rankings/<region>")
@app.route("/rankings")
def rankings(region=None):
    teams = TCS.read_teams_from_json(reset_elo=False)
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

@app.route("/team/<id>")
def team(id):
    teams = TCS.read_teams_from_json(reset_elo=False)
    team = teams[int(id)]
    return render_template("team.html", team=team)

@app.route("/search")
def search():
    query = request.args.get("query")
    return "Your query for \"" + query + "\" returned 0 results, mostly beacuse " \
                                       "the search algorithm hasn't been implemented yet."

if __name__ == "__main__":
    app.run()