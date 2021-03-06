from GenericScraper import GenericScraper
from utility.FileUtility import *
from random import randrange


class AmazonScraper(GenericScraper):
    __prePathMario = "D:/Mario/Reti geografiche/RetiGeografiche20-21/"
    __prePathMarioPC2 = "C:/Users/Mario/Desktop/Mario/Progetti/RetiGeografiche20-21/"
    __prePAth = __prePathMario

    # TODO: mettere i path relativi
    extractor_file = __prePAth + 'files/amazon_selector.yml'
    input_file = __prePAth + 'files/amazon_product_list.txt'

    # extractor_file = 'C:/Users/Mario/Desktop/Mario/Progetti/RetiGeografiche20-21/files/amazon_selector.yml'
    # input_file = 'C:/Users/Mario/Desktop/Mario/Progetti/RetiGeografiche20-21/files/amazon_product_list.txt'
    deelay_time = 10

    def __init__(self):
        # TODO: controllare se sono tutti necessari
        # Necessario altrimenti Amazon non risponde
        # Se le richieste di Amazon falliscono senza motivo, provare a cambiare user agent.
        self.headers = {
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': self.user_agents[randrange(self.user_agents.__len__())],
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://www.amazon.com/',
            'accept-language': 'it-IT,en-GB,en-US;q=0.9,en;q=0.8',
        }
        pass

    def get_offers(self) -> list:
        prodotti = readFromFile(self.input_file)
        # print("Prodotti:", prodotti)
        product_list = self.scrape(prodotti)
        # print('[AMAZON SCRAPER] result:', type(product_list), 'content:', type(product_list[0]))
        # print(product_list)
        return product_list

    def getPrice(self, val: dict):
        # Chiamo la superclasse
        price = super(AmazonScraper, self).getPrice(val)
        # Se la superclasse non riesce a leggere il risultato provo a leggerlo così
        if price is None and val['price_deal'] is not None and val['price_deal'].__len__() > 0:
            price = val['price_deal']
        elif val['price_promo'] is not None and val['price_promo'].__len__() > 0:
            price = val['price_promo']

        return price

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

    def getScraperName(self):
        return "amazon"

    # def fixPrice(self, price: str):
    #     print("OKOK")
    #     return 100