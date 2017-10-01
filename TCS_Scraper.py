from bs4 import BeautifulSoup
import requests
requests.packages.urllib3.disable_warnings()

class TCS_Scraper():
    @staticmethod
    def get_teams():
        """
        Gets HTML from the following url listing all teams

        :return: BeautifulSoup response
        """
        url = "https://compete.tespa.org/tournament/75/phase/1"
        r = requests.get(url, timeout=20, verify=False)

        raw_html = r.text
        soup = BeautifulSoup(raw_html, "html.parser")

        return soup

    @staticmethod
    def get_players(url):
        """
        Takes a team url and gets all battle tags
        excluding team coordinator and substitutes

        :param url: team url
        :return: String list of battle tags
        """
        scraped_players = []
        url = url
        r = requests.get(url, timeout=20, verify=False)

        raw_html = r.text
        soup = BeautifulSoup(raw_html, "lxml")

        table = soup.find("table")
        rows = table.find_all("tr")[:-1]

        for row in rows:
            role = row.find("i")
            if role:
                if role.get("title") == "Player":
                    handle = row.find("td", {"class": "text-break"}).text
                    scraped_players.append(handle)
        return scraped_players