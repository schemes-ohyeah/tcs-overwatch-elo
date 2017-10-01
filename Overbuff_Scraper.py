from Scraper import Scraper

class Overbuff_Scraper(Scraper):
    @staticmethod
    def get_sr(battle_tag):
        """
        Takes in a battle tag and runs a query on overbuff to scrape SR

        :param battle_tag:
        :return: SR or -1 if unranked
        """
        user, id = battle_tag.split("#")
        url = "https://www.overbuff.com/players/pc/{0}-{1}".format(user, id)
        soup = super().get_soup(url)

        sr = soup.find("span", {"class": "color-stat-rating"})

        return int(sr.text) if sr else -1