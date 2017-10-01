from bs4 import BeautifulSoup
from TCS_Objects import *

class TCS_Functions():
    @staticmethod
    def soup():
        with open("teams_page.html", "rb") as teams_page:
            soup = BeautifulSoup(teams_page.read(), "html.parser")

        """
        regions_html = soup.find_all("div", class_="panel panel-default")

        regions_teams = {}
        for region_table in regions_html:
            region_name = region_table.h1.contents[0].lower()
            region_list = []
            for row in region_table.tr:
                team_link = row.find("a")
                print(team_link)
            # regions_teams[region_name] = region_list
        
        """

        tables = soup.find_all("table", {"class" : "table table-hover table-bordered"})

        for table in tables:
            rows = table.find_all("tr")[1:]

            for row in rows:
                url = row.find("a")
                print(url.get("href"))
