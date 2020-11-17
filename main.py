from AmazonScraper import AmazonScraper
from EpriceScraper import EpriceScraper
from MediaworldScraper import MediaworldScraper
from utility.DatabaseManager import DatabaseManager


if __name__ == "__main__":
    databaseManager = DatabaseManager()
    scrapers = [AmazonScraper(), EpriceScraper(), MediaworldScraper()]
    #scrapers = [MediaworldScraper()]
    for scraper in scrapers:
        # TODO: Mettere più Thread
        scrapertype = type(scraper)
        prodotti = scraper.get_offers()
        databaseManager.insert(prodotti, scrapertype)


