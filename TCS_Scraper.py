from bs4 import BeautifulSoup
import requests
requests.packages.urllib3.disable_warnings()

def get_teams():
    url = "https://compete.tespa.org/tournament/75/phase/1"
    r = requests.get(url, timeout=20, verify=False)

    raw_html = r.text
    soup = BeautifulSoup(raw_html, "html.parser")

    # "wb" because page.read() gives us bytes so we write bytes
    with open("teams_page.html", "w") as teams_page:
        teams_page.write(str(soup.prettify()))

def get_sr(battle_tag):
    user, id = battle_tag.split("#")
    url = "https://www.overbuff.com/players/pc/{0}-{1}".format(user, id)
    print(url)
    r = requests.get(url, timeout=20, verify=False)

    raw_html = r.text
    soup = BeautifulSoup(raw_html, "html.parser")

    sr = soup.find("span", {"class" : "color-stat-rating"})

    return sr.text

# def get_players():

get_teams()