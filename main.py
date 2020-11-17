from AmazonScraper import AmazonScraper
from EpriceScraper import EpriceScraper
from MediaworldScraper import MediaworldScraper
from utility.DatabaseManager import DatabaseManager
from multiprocessing import Process


def startscrape(scraper, **kwargs):
    print("Scraper ", scraper, " inizializzato")
    scrapertype = type(scraper)
    prodotti = scraper.get_offers()
    DatabaseManager.insert(prodotti, scrapertype)
    print("Scraping di ", scrapertype, " eseguito correttamente")


if __name__ == "__main__":
    scrapers = [AmazonScraper(), EpriceScraper(), MediaworldScraper()]
    #scrapers = [AmazonScraper()]
    for scraper in scrapers:
        p = Process(target=startscrape, args=(scraper,))
        p.start()


