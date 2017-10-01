from bs4 import BeautifulSoup
import requests
requests.packages.urllib3.disable_warnings()

class TCS_Functions():
    @classmethod
    def soup(self):
        with open("teams_page.html", "rb") as teams_page:
            soup = BeautifulSoup(teams_page.read(), "html.parser")

        tables = soup.find_all("table", {"class" : "table table-hover table-bordered"})

        for table in tables:
            rows = table.find_all("tr")[1:]

            for row in rows:
                url = row.find("a")
                url = url.get("href")
                self.get_tag(url)

    @classmethod
    def get_tag(self, url):
        r = requests.get(url, timeout=20, verify=False)

        raw_html = r.text
        soup = BeautifulSoup(raw_html, "html.parser")

        table = soup.find("table")
        rows = table.find_all("tr")[:-1]

        for row in rows:
            role = row.find("i")
            if role.get("title") == "Player":
                handle = row.find("td", {"class" : "text-break"})
                print(handle.text)