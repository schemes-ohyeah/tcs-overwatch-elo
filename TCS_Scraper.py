import urllib.request

class TCS_Scraper():
    @staticmethod
    def get_teams():
        url = "https://compete.tespa.org/tournament/75/phase/1"
        page = urllib.request.urlopen(url)
        # "wb" because page.read() gives us bytes so we write bytes
        with open("teams_page.html", "wb") as teams_page:
            content = page.read()
            teams_page.write(content)

TCS_Scraper.get_teams()