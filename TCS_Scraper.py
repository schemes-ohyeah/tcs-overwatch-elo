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

        return soup