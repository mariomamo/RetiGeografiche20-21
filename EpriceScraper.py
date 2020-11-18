from GenericScraper import GenericScraper
from utility.FileReader import *


class EpriceScraper(GenericScraper):
    # TODO: mettere i path relativi
    extractor_file = 'files/eprice_selector.yml'
    input_file = 'files/eprice_product_list.txt'
    # Incredibile, e-price si fa floodare
    deelay_time = 0

    # TODO: controllare se sono tutti necessari
    # Necessario altrimenti Amazon non risponde
    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.eprice.it/',
    }

    def __init__(self):
        pass

    def get_offers(self) -> list:
        prodotti = readFromFile(self.input_file)
        #print("Prodotti:", prodotti)
        product_list = self.scrape(prodotti)
        # print('[E-PRICE SCRAPER] result:', type(product_list), 'content:', type(product_list[0]))
        # print(product_list)
        return product_list

    # Filtra i prodotti corretti in base al nome e alle caratteristiche
    def __filter_products(self, products_list, params) -> list:
        result = []

        # Scansiono tutta la lista di prodotti
        for i in range(products_list.__len__()):
            num_params_ok = 0
            # Per ogni parametro nella lista di parametri
            for param in params:
                # product è un dizionario contenente i dati del prodotto
                product = products_list[i]

                # Se nel nome del prodotto ci sono tutti i parametri aggiungilo alla lista
                if param in product['name'].lower():
                    num_params_ok += 1
                if num_params_ok == params.__len__() - 1:
                    result.append(product)
                    break

        return result