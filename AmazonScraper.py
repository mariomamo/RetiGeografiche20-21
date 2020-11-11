from GenericScraper import GenericScraper
from utility.FileReader import *
from selectorlib import Extractor
from beans.Prodotto import  Prodotto
import requests
import time

class AmazonScraper(GenericScraper):
    # TODO: mettere i path relativi
    __extractor_file = 'D:\\Mario\\Reti geografiche\\RetiGeografiche20-21\\files\\amazon_selector.yml'
    __input_file = 'D:\\Mario\\Reti geografiche\\RetiGeografiche20-21\\files\\amazon_product_list.txt'
    __deelay_time = 10

    # TODO: controllare se sono tutti necessari
    # Necessario altrimenti Amazon non risponde
    __headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    def __init__(self):
        pass

    def get_offers(self) -> list:
        urls = readFromFile(self.__input_file)
        product_list = self.__scrape(urls)
        # print('[AMAZON SCRAPER] result:', type(product_list), 'content:', type(product_list[0]))
        # print(product_list)
        return product_list

    # TODO: Integrazione con il bot Telegram
    # urls è una lista di url
    def __scrape(self, urls: list) -> list:
        i = 0
        prodotti = []
        # params è una lista di prodotti
        for url in urls:
            # Eseguo la richiesta per prelevare i dati
            # request contiene la risposta
            request = requests.get(url, headers=self.__headers)

            print('status: ', request.status_code)

            # Controllo errori
            # TODO: se l'errore è 500 la richiesta viene fatta dopo un pò
            if request.status_code > 500:
                if "To discuss automated access to Amazon data please contact" in request.text:
                    print("Page %s was blocked by Amazon. Please try using better proxies\n" % url)
                else:
                    print("Page %s must have been blocked by Amazon as the status code was %d" % (url, request.status_code))
                return []

            # Crea l'estrattore per fare webscrape
            extractor = Extractor.from_yaml_file(self.__extractor_file)

            # val rappresenta i prodotti letti dalla pagina (per i prodotti multipli è un dizionario)
            # print('REQUEST: ', request.text)
            val = extractor.extract(request.text)
            prodotti.append(Prodotto(val['name'], val['price'], url))

            # print(type(val))
            # Qui dovrei avvisare il main e passargli i valori
            if i < urls.__len__() - 1: time.sleep(self.__deelay_time)
            i += 1

        return prodotti

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