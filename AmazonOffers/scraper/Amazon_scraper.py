from AmazonOffers.scraper.Generic_scraper import Generic_scraper
import requests
from selectorlib import Extractor
import time


class Amazon_scraper(Generic_scraper):
    __single_extractor = 'C:\\Users\\Mario\\Desktop\\Mario\\Progetti\\RetiGeografiche20-21\\AmazonOffers\\amazon_scraper\\amazon_single_selectors.yml'
    __multiple_extractor = 'C:\\Users\\Mario\\Desktop\\Mario\\Progetti\\RetiGeografiche20-21\\AmazonOffers\\amazon_scraper\\amazon_multiple_selectors.yml'
    __deelay_time = 10

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

    def get_offers(self, links: list, selector: str = 'single') -> list:
        product_list = self.__scrape(links, selector)
        # print('[AMAZON SCRAPER] result:', type(product_list), 'content:', type(product_list[0]))
        # print(product_list)
        return product_list

    def __scrape(self, params: list, selector: str = 'single') -> list:

        if selector == 'multiple':
            extractor = Extractor.from_yaml_file(self.__multiple_extractor)
        else:
            extractor = Extractor.from_yaml_file(self.__single_extractor)

        result = []

        # params è una lista di liste. Le liste all'interno contengono il nome del prodotto
        # e le caratteristiche (Ram, memoria, ecc)
        for i in range(params.__len__()):
            # param rappresenta il singolo prodotto desiderato (quello letto dal file di input)
            # Ex. google pixel 4a xl |%!| 6Gb |%!| 64GB |%!| https://...
            param = params[i]
            link = param[param.__len__()-1]     # ottengo il link al prodotto

            # Eseguo la richiesta per prelevare i dati
            request = requests.get(link, headers=self.__headers)

            print('status: ', request.status_code)

            # Controllo errori
            if request.status_code > 500:
                if "To discuss automated access to Amazon data please contact" in request.text:
                    print("Page %s was blocked by Amazon. Please try using better proxies\n" % link)
                else:
                    print("Page %s must have been blocked by Amazon as the status code was %d" % (
                        link, request.status_code))
                return []

            # val rappresenta i prodotti letti dalla pagina (per i prodotti multipli è un dizionario)
            #print('REQUEST: ', request.text)
            val = extractor.extract(request.text)
            # print('val: ', val)

            if selector == 'multiple':
                if val is not None:
                    # products_list è una lista di dizionari, ogni dizionario fa riferimento ad un prodotto
                    # Ex. [{'image': '', 'name':'', ...}, {}, ...]

                    products_list = val['products']
                    # print(products_list)
                    # print('type :', type(products_list))
                    if products_list is not None:
                        print('OK', link)
                        result.extend(self.__filter_products(products_list, params[i]))
                    else:
                        print('PRODUCT LIST NONE', link)
                else:
                    print('VAL NONE', link)
            else:
                # In questo caso 'val' è un dizionario
                result.extend(self.__filter_products(val, params[i]))

            # print(type(val))
            # Qui dovrei avvisare il main e passargli i valori
            if i < params.__len__() - 1: time.sleep(self.__deelay_time)

        return result

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

    # def __scrape(self, links: list, selector: str = 'single') -> list:
    #
    #     if selector == 'multiple':
    #         extractor = Extractor.from_yaml_file(self.__multiple_extractor)
    #     else:
    #         extractor = Extractor.from_yaml_file(self.__single_extractor)
    #
    #     result = []
    #
    #     for i in range(links.__len__()):
    #         link = links[i]
    #         request = requests.get(link, headers=self.__headers)
    #
    #         print('status: ', request.status_code)
    #
    #         if request.status_code > 500:
    #             if "To discuss automated access to Amazon data please contact" in request.text:
    #                 print("Page %s was blocked by Amazon. Please try using better proxies\n" % link)
    #             else:
    #                 print("Page %s must have been blocked by Amazon as the status code was %d" % (
    #                     link, request.status_code))
    #             return []
    #
    #         val = extractor.extract(request.text)
    #
    #         if selector == 'multiple':
    #             products_list = val['products']
    #             if val is not None and products_list is not None:
    #                 print('OK', link)
    #                 result.extend(products_list)
    #             else:
    #                 print('NONE', link)
    #         else:
    #             result.append(val)
    #
    #         # print(type(val))
    #         if i < links.__len__() - 1: time.sleep(self.__deelay_time)
    #
    #     return result