from bs4 import BeautifulSoup
import requests
import pandas as pd

clubs = {"Legia Warszawa":"/legia-warschau/startseite/verein/255/saison_id/2019"} # to be continued

class TransfermarktTeamCollector:
    """
    Transfermarkt Ekstraklasa Scrapper
    """
    def __init__(self, url):
        """
        Transfermarkt.com team's data scrapper
        :param url: team's url we want to scrap
        """

        # We need to behave as we are browsing site instead of scraping it
        headers = {'User-Agent':
                       'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

        self.pageTree = requests.get(url, headers=headers)

        if self.pageTree.status_code != 200: raise Exception("Page has not been scrapped correctly!")

        self.pageSoup = BeautifulSoup(self.pageTree.content, 'html.parser')

        return

    def create_players_table(self):

        players = self.pageSoup.findAll('tr', {'class': ['even', 'odd']})
        players_names = [(p.find('a', {"class": "spielprofil_tooltip"})).text for p in players]
        players_values = [(p.find('td', {"class": "rechts hauptlink"})).text for p in players]
        players_birthdate = [(p.findAll('td', {"class": "zentriert"}))[1].text for p in players]
        players = pd.DataFrame({"name": players_names,
                                "market-value": players_values,
                                "birthdate":players_birthdate})

        return players

def main():

    page = 'https://www.transfermarkt.pl'

    TMcollector = TransfermarktTeamCollector(page + clubs["Legia Warszawa"])
    players = TMcollector.create_players_table()
    print(players)


if __name__ == "__main__":
    main()