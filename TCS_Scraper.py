from bs4 import BeautifulSoup
import requests
requests.packages.urllib3.disable_warnings()

def get_soup(url, soupMethod="html.parser"):
    r = requests.get(url, timeout=20, verify=False)
    raw_html = r.text
    return BeautifulSoup(raw_html, soupMethod)

class TCS_Scraper():
    @staticmethod
    def get_teams():
        """
        Gets HTML from the following url listing all teams

        :return: BeautifulSoup response
        """
        return get_soup("https://compete.tespa.org/tournament/75/phase/1")

    @staticmethod
    def get_players(url):
        """
        Takes a team url and gets all battle tags
        excluding team coordinator and substitutes

        :param url: team url
        :return: String list of battle tags
        """
        scraped_players = []
        soup = get_soup(url, "lxml")

        table = soup.find("table")
        rows = table.find_all("tr")[:-1]

        for row in rows:
            role = row.find("i")
            if role:
                if role.get("title") == "Player":
                    handle = row.find("td", {"class": "text-break"}).text
                    scraped_players.append(handle)
        return scraped_players

    @staticmethod
    def get_matches():
        base_url = "https://compete.tespa.org/tournament/75/phase/1/group/"
        matches = []
        for x in range(1, 5):
            url = base_url + str(x)
            soup = get_soup(url)
            links = soup.find_all("a")
            for link in links:
                match_url = link.get("href")
                if "match" in match_url:
                    matches.append(match_url)
        return matches