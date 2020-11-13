import psycopg2
import GenericScraper
from AmazonScraper import AmazonScraper
from utility.DatabaseManager import DatabaseManager


if __name__ == "__main__":
    databaseManager = DatabaseManager()
    scrapers = [AmazonScraper()]
    for scraper in scrapers:
        prodotti = scraper.get_offers()
        for prodotto in prodotti:
            #print(prodotto.nome + " - " + prodotto.prezzo + " - " + prodotto.url)
            databaseManager.insert(prodotto)


