from bs4 import BeautifulSoup
import requests
requests.packages.urllib3.disable_warnings()

class TCS_Scraper():
    @staticmethod
    def get_teams():
        url = "https://compete.tespa.org/tournament/75/phase/1"
        r = requests.get(url, timeout=20, verify=False)

        raw_html = r.text
        soup = BeautifulSoup(raw_html, "html.parser")

        # "wb" because page.read() gives us bytes so we write bytes
        with open("teams_page.html", "w") as teams_page:
            teams_page.write(str(soup.prettify()))

TCS_Scraper.get_teams()
