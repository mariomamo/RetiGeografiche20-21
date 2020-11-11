import GenericScraper
from AmazonScraper import AmazonScraper

if __name__ == "__main__":
    scrapers = [AmazonScraper()]
    for scraper in scrapers:
        prodotti = scraper.get_offers()
        for prodotto in prodotti:
            print(prodotto.nome + " - " + prodotto.prezzo + " - " + prodotto.url)
