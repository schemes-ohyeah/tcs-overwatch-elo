from bs4 import BeautifulSoup
import requests
requests.packages.urllib3.disable_warnings()

class Scraper():
    @staticmethod
    def get_soup(url, soupMethod="html.parser"):
        r = requests.get(url, timeout=20, verify=False)
        raw_html = r.text
        return BeautifulSoup(raw_html, soupMethod)