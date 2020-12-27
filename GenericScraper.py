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
    richieste_effettuate = 0
    request = None

    user_agents = [
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

    @abstractmethod
    def get_offers(self) -> dict: raise Exception("NotImplementedException")

    def scrape(self, prodotti: list) -> list:
        i = 0
        result = []

        # params è una lista di prodotti
        for prodotto in prodotti:
            # Eseguo la richiesta per prelevare i dati
            # request contiene la risposta
            self.request = self.makeRequest(prodotto.url)

            # Se viene eseguito qualche redirect strano chiama la funzione onRedirect
            if self.request is not None and prodotto.url != self.request.url:
                # Se onRedirect restituisce True si continua la richiesta
                if self.onRedirect():
                    result = self.continuaRichiesta(prodotto, i, prodotti, result)
                else:
                    # Altrimenti si imposta come valore del prodotto -1 e si continua con un nuovo prodotto
                    prodotto.prezzo = -1
                    result.append(prodotto)
                    print(f"[{self.getScraperName().upper()} - REDIRECT ERROR]: {prodotto.nome}, {prodotto.url}, {prodotto.prezzo}", sep='')
            else:
                result = self.continuaRichiesta(prodotto, i, prodotti, result)

        return result

    def continuaRichiesta(self, prodotto, i, prodotti, result):
        # print('status: ', self.request.status_code, " - ", prodotto.url)

        # Controllo errori
        # TODO: se l'errore è 500 la richiesta viene fatta dopo un pò
        while self.request.status_code != 200 and self.richieste_effettuate < self.maximum_request:
            self.richieste_effettuate += 1
            self.waitRequest(self.richieste_effettuate)
            self.request = self.makeRequest(prodotto.url)

        if self.request is not None and self.request.status_code == 200:
            # La richiesta è andata bene
            self.requestOk()
            # Crea l'estrattore per fare webscrape
            extractor = Extractor.from_yaml_file(self.extractor_file)

            # val rappresenta i prodotti letti dalla pagina (per i prodotti multipli è un dizionario)
            # print('REQUEST: ', request.text)
            val = extractor.extract(self.request.text)

            # Controllo se il prodotto è disponibile
            available = self.isAvailable(val)

            # Se il prodotto è disponibile
            if available:
                # Leggo il prezzo letto
                price = self.getPrice(val)

                # Rimuovo eventuali caratteri diversi dai numeri che possono esserci all'interno, compreso il simbolo €
                price = self.fixPrice(price)

                try:
                    prodotto.prezzo = float(price)
                except:
                    print("Eccezzzion MANNAAAAGG")
            else:
                # Se il prodotto non è disponibile
                prodotto.prezzo = -1
                # print(f"{prodotto.nome} NON DISPONIBILE: {prodotto.prezzo}")

            print(f"[{self.getScraperName().upper()}", end="")
            if available:
                print(" - DISPONIBILE] ", end="")
            else:
                print(" - NON DISPONIBILE] ", end="")

            print(f"{prodotto.nome} - {prodotto.url} = € {prodotto.prezzo} ")

            # Qui dovrei avvisare il main e passargli i valori
            if i < prodotti.__len__() - 1: time.sleep(self.deelay_time)
            i += 1

            result.append(prodotto)

        return result

    @abstractmethod
    def getScraperName(self):
        return "generic scraper"

    def getPrice(self, val: dict):
        price = None
        if val['price'] is not None and val['price'].__len__() > 0:
            price = val['price']

        return price

    def isAvailable(self, val: dict) -> bool:
        available = True

        # Se c'è il valore per vedere se il prezzo è disponibile
        if 'price_not_available' in val:
            # Se c'è del testo in 'price_not_available' vuol dire che il prodotto non è disponibile
            if val['price_not_available'] is not None and val['price_not_available'].__len__() > 0:
                available = False

        return available

    def waitRequest(self, numeroRichiesta: int):
        time.sleep(3)
        if numeroRichiesta is not None:
            print("TENTATIVO ", numeroRichiesta)

    def makeRequest(self, url: str):
        # request = requests.get(url, headers=self.headers)
        try:
            return requests.get(url, headers=self.headers)
        except:
            print(f"Errore richiesta per {url}")
            return None

    def onRedirect(self):
        return True

    '''Viene chiamato quando la richiesta è andata a buon fine'''
    def requestOk(self):
        pass

    def fixPrice(self, price: str):
        # return re.sub('[^0-9]', '', price)
        if price is None:
            return -1

        # print("price: ", price)

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
