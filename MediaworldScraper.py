import math
import time
from GenericScraper import GenericScraper
import requests
from utility.FileUtility import *
from random import randrange
from utility.FileUtility import *


class MediaworldScraper(GenericScraper):
    __prePathMario = "D:/Mario/Reti geografiche/RetiGeografiche20-21/"
    __prePathMarioPC2 = "C:/Users/Mario/Desktop/Mario/Progetti/RetiGeografiche20-21/"
    __prePAth = __prePathMarioPC2

    extractor_file = __prePAth + 'files/mediaworld_selector.yml'
    input_file = __prePAth + 'files/mediaworld_product_list.txt'

    # extractor_file = 'C:/Users/Mario/Desktop/Mario/Progetti/RetiGeografiche20-21/files/mediaworld_selector.yml'
    # input_file = 'C:/Users/Mario/Desktop/Mario/Progetti/RetiGeografiche20-21/files/mediaworld_product_list.txt'
    deelay_time = 5
    __maximum_404_try = 3
    maximum_request = 3
    __current_agent = 0
    # __try_404 deve partire da 1 altrimenti la prima volta aspetta 0 secondi
    __try_404 = 1
    __404_sleep_time = 60

    ERRORE_NON_DISPONIBILE = "non disponibile"

    def __init__(self):
        # TODO: controllare se sono tutti necessari
        self.headers = {
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            #'user-agent': self.user_agents[randrange(self.user_agents.__len__())],
            'user-agent': self.user_agents[self.__current_agent],
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://www.mediaworld.it',

        }

    '''Prendo i prezzi'''
    def get_offers(self) -> list:
        prodotti = readFromFile(self.input_file)
        # print("Prodotti:", prodotti)
        product_list = self.scrape(prodotti)

        # print('[MEDIAWORLD SCRAPER] result:', type(product_list), 'content:', type(product_list[0]))
        # print(product_list)
        return product_list

    '''Definisco i valori per i prezzi di MediaWorld'''
    def getPrice(self, val: dict):
        # Chiamo la superclasse
        price = super(MediaworldScraper, self).getPrice(val)
        # Se la superclasse non riesce a leggere il risultato provo a leggerlo così
        if price is None and val['price_deal'] is not None and val['price_deal'].__len__() > 0:
            price = val['price_deal']

        return price

    def isAvailable(self, val: dict) -> bool:
        available = True

        # Se c'è il valore per vedere se il prezzo è disponibile
        if 'price_not_available' in val:
            # Se c'è del testo in 'price_not_available' vuol dire che il prodotto non è disponibile
            if val['price_not_available'] is not None and self.ERRORE_NON_DISPONIBILE in val['price_not_available']:
                available = False

        # print(f"{val['price_not_available']}")
        return available

    '''Restituendo False la richiesta non continua e viene assegnato come valore al prodotto -1'''
    def onRedirect(self):
        # print('è stato eseguito un redirect, mi fermo')
        return False

    '''Se MediaWorld non risponde aspetto fino a 2 volte, prima 60 e poi 120 secondi e riprovo'''
    def waitRequest(self, numeroRichiesta: int):
        # Dopo 3 errori 404 aspetta un minuto e riprova
        # Aspetta fino a un minuto per massimo 3 volte
        # 403/404 try parte da 1
        print("MEDIAWORLD WAIT REQUEST: TENTATIVO ", numeroRichiesta, " - 404 ERROR: ", self.__try_404)
        # se si possono fare ancora richieste
        if numeroRichiesta < self.maximum_request:
            time.sleep(self.deelay_time)
        # Se si ottengono 3 risposte 403/404 consecutive si aspetta un pò e si riprova fino __maximum_404_try volte
        elif numeroRichiesta == self.maximum_request and self.__try_404 < self.__maximum_404_try:
            # Le richieste effettuate vengono azzerate, altrimenti il metodo di GenericScraper termina dopo 3 errori 403/404
            self.richieste_effettuate = 0
            print("MEDIAWORLD: ASPETTO {} SECONDI".format(self.__404_sleep_time * self.__try_404))
            time.sleep(self.__404_sleep_time * self.__try_404)
            self.__try_404 += 1
        # Se dopo __maximum_try_404 volte non si riesce, si fallisce
        else:
            self.__try_404 = 1

    '''Azzero la variabile __try_404 se la richiesta è andata a buon fine'''
    def requestOk(self):
        self.__try_404 = 1

    def __change_user_agent(self):
        self.__current_agent += 1
        self.__current_agent = int(math.fmod(self.__current_agent, self.headers.__len__()))
        print(self.headers['user-agent'], " - ", self.__current_agent, " - ", self.headers.__len__())
        self.headers['user-agent'] = self.user_agents[self.__current_agent]

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
        return "mediaworld"