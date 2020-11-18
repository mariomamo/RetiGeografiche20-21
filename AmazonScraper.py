from GenericScraper import GenericScraper
from utility.FileReader import *


class AmazonScraper(GenericScraper):
    # TODO: mettere i path relativi
    extractor_file = 'files/amazon_selector.yml'
    input_file = 'files/amazon_product_list.txt'
    deelay_time = 10

    __user_agents = [
        'Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/60.0.3112.107 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 7.0; SM-G930VC Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/58.0.3029.83 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 6.0.1; SM-G935S Build/MMB29K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 6.0.1; SM-G920V Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 5.1.1; SM-G928X Build/LMY47X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.83 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 6P Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.83 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 7.1.1; G8231 Build/41.2.A.0.219; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69'
    ]

    # TODO: controllare se sono tutti necessari
    # Necessario altrimenti Amazon non risponde
    # Se le richieste di Amazon falliscono senza motivo, provare a cambiare user agent.
    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': __user_agents[__user_agents.__len__()-3],
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'it-IT,en-GB,en-US;q=0.9,en;q=0.8',
    }

    def __init__(self):
        pass

    def get_offers(self) -> list:
        prodotti = readFromFile(self.input_file)
        print("Prodotti:", prodotti)
        product_list = self.scrape(prodotti)
        # print('[AMAZON SCRAPER] result:', type(product_list), 'content:', type(product_list[0]))
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