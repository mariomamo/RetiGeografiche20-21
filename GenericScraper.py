from abc import ABCMeta, abstractmethod
import time
import requests
from selectorlib import Extractor
import re


class GenericScraper:
    __metaclass__ = ABCMeta
    headers = {}
    maximum_request = 3
    extractor_file = ''
    input_file = ''
    deelay_time = 10

    @abstractmethod
    def get_offers(self) -> dict: raise Exception("NotImplementedException")

    def scrape(self, prodotti: list) -> list:
        i = 0
        result = []

        # params è una lista di prodotti
        for prodotto in prodotti:
            # Eseguo la richiesta per prelevare i dati
            # request contiene la risposta
            try:
                request = requests.get(prodotto.url, headers=self.headers)
            except:
                print("ERRORE RICHIESTA")

            print('status: ', request.status_code, " - ", prodotto.url)

            # Controllo errori
            # TODO: se l'errore è 500 la richiesta viene fatta dopo un pò
            richieste = 0
            while request.status_code != 200 and richieste < self.maximum_request:
                richieste += 1
                time.sleep(3)
                try:
                    request = requests.get(prodotto.url, headers=self.headers)
                    print("TENTATIVO ", richieste)
                except:
                    print("ERRORE RICHIESTA")

            if request.status_code == 200:
                # Crea l'estrattore per fare webscrape
                extractor = Extractor.from_yaml_file(self.extractor_file)

                # val rappresenta i prodotti letti dalla pagina (per i prodotti multipli è un dizionario)
                # print('REQUEST: ', request.text)
                val = extractor.extract(request.text)

                # Se c'è il prezzo
                price = None
                if val['price'] is not None and val['price'].__len__() > 0:
                    price = val['price']
                elif val['price_deal'] is not None and val['price_deal'].__len__() > 0:
                    price = val['price_deal']

                # Rimuovo eventuali caratteri diversi dai numeri che possono esserci all'interno, compreso il simbolo €
                price = self.fixPrice(price)
                print("PRICE: ", price)

                # NON DOVREBBE PIU' ESSERE NECESSARIO
                # formatto la stringa per convertirla in float
                # if '.' in price and ',' in price:
                #     price = price.replace('.', '').replace(',', '.')
                # else:
                #     price = price.replace(',', '.')

                try:
                    prodotto.prezzo = float(price)
                except:
                    print("Eccezzzion MANNAAAAGG")

                # Qui dovrei avvisare il main e passargli i valori
                if i < prodotti.__len__() - 1: time.sleep(self.deelay_time)
                i += 1

                result.append(prodotto)

        return result

    def fixPrice(self, price: str):
        # return re.sub('[^0-9]', '', price)
        if price is None:
            return -1

        print("price: ", price)

        # Prendo tutti i numeri che sono nella stringa, facendo lo split con la ','
        # Restituisce un array contenente tutti i numeri
        # Esempio:
        # Input: 1.497,59, Output: ['1', '497', '59']
        # Input: 1189, Output: ['1189', '00']
        # Eventuali caratteri che non sono numeri vengono scartati
        temp = re.findall(r"[-+]?\d*\\,\d+|\d+", price)

        # print("TEMP: ", temp)

        # Se contiene solo due elementi restituisce il primo e il secondo divisi dal punto
        if temp.__len__() == 2:
            return temp[0] + "." + temp[1]
        elif temp.__len__() == 3:
            # Altrimenti restituisce il primo e il secondo concatenati e aggiunge un punto tra la
            # concatenazione di questi due e il terzo
            return temp[0] + temp[1] + "." + temp[2]

        # VECCHIO METODO
        # if val['price'] is not None and val['price'].__len__() > 0:
        #     price = val['price']
        #     # Rimuovo il simbolo dell'euro
        #     print("PRICE: " + price)
        #     if price[price.__len__() - 1] == '€':
        #         price = price[0: price.__len__() - 2]
        #
        #     print("PREZZO: ", price)
        # elif val['price_deal'] is not None and val['price_deal'].__len__() > 0:
        #     price = val['price_deal']
        #     # Rimuovo il simbolo dell'euro
        #     if price[price.__len__() - 1] == '€':
        #         price = price[0: price.__len__() - 2]
        #
        #     print("PREZZO: ", price)
        # else:
        #     print("NULLONE")
        #     price = '-1'
