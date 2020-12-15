import os
import threading
import time
import datetime
from pathlib import Path
import matplotlib.pylab as pl
import GenericScraper
from AmazonScraper import AmazonScraper
from EpriceScraper import EpriceScraper
from MediaworldScraper import MediaworldScraper
import multiprocessing
from threading import Thread

from beans.ProdottoReport import ProdottoReport
from beans.ProdottoStatistiche import ProdottoStatistiche
from utility.Ascoltabile import Ascoltabile
from utility.Ascoltatore import Ascoltatore
from utility.DatabaseManager import DatabaseManager


# class GraphicGeneratorAscoltatore(Ascoltatore):
#     # __threadlock serve per gestire il lock e non far accavallare le print
#    __threadLock = threading.Lock()
#     __threadLock = threading.Lock()
#     __prodotti = dict()
#     __alreadyPrintedTot = False
#
#     def update(self, operation, *args):
#         # Lo stampo solo se è una stringa
#         if operation == "prezzi":
#             try:
#                 scraper = args[0][0]
#                 messaggio = args[0][1]
#                 if isinstance(messaggio, str):
#                     self.__threadLock.acquire()
#                     print(scraper, " ---> ", messaggio)
#                     self.__threadLock.release()
#             except Exception as ex:
#                 print("[ECCEZIONE]: ", ex)
#         elif operation == "totprodotti":
#             scraper = args[0][0]
#             numero_prodotti = args[0][1]
#             self.aggiungiProdotto(scraper, numero_prodotti)
#
#             if self.__prodotti.__len__() == 3:
#                 self.__threadLock.acquire()
#                 if not self.__alreadyPrintedTot:
#                     print(f"Prodotti totali: {self.getTotaleProdotti()}")
#                     self.__alreadyPrintedTot = True
#                 self.__threadLock.release()


class GraphicGeneratorAscoltatore(Ascoltatore):

    def update(self, operation, *args):
        # Lo stampo solo se è una stringa
        if operation == "prezzi":
            try:
                scraper = args[0][0]
                messaggio = args[0][1]
                if isinstance(messaggio, str):
                    print(scraper, " ---> ", messaggio)
            except Exception as ex:
                print("[ECCEZIONE]: ", ex)
        elif operation == "totprodotti":
            scraper = args[0][0]
            numero_prodotti = args[0][1]
            print(f">>> {scraper} = {numero_prodotti} prodotti")


class GestoreGrafici(Ascoltabile):

    DEFAULT_OUTPUT_FILE = "report.txt"

    def __init__(self):
        self.__listeners = []

    def __ottieniPrezzi(self, prodotti: list) -> list:
        prezzi = list()
        for prodotto in prodotti:
            prezzi.append(prodotto[3])

        return prezzi

    def __ottieniData(self, prodotti: list) -> list:
        date = list()
        last_month = "0"
        for prodotto in prodotti:
            data = prodotto[prodotto.__len__() - 1]
            if last_month == data.strftime("%m"):
                data = data.strftime('%d')
            else:
                last_month = data.strftime("%m")
                data = data.strftime('%d/%m')
            date.append(data)

        return date

    def ottieniDatiGrafici(self, scraper: GenericScraper, dataInizio=None, dataFine=None, multiplePriceForDay=False, discontinuo=True):
        tuttiIProdotti = DatabaseManager.selectProduct(scraper, "")

        # TODO: Utilizzarlo fuori, è meglio
        # numeroProdotti = DatabaseManager.getProductCount(scraper)
        # self.notify("totprodotti", DatabaseManager.getTable(scraper), numeroProdotti)
        datiRitorno = []

        cicli = 0
        for prodotto in tuttiIProdotti:
            cicli += 1
            # nomeProdotto = prodotto[1][0:prodotto[1].__len__() - 1]
            nomeProdotto = prodotto[0].strip("\n")
            # print(nomeProdotto)
            prod = self.ottieniGrafico(scraper, nomeProdotto, dataInizio=dataInizio, dataFine=dataFine,
                                                 multiplePriceForDay=multiplePriceForDay, discontinuo=discontinuo,
                                                 costruisciGrafico=False)
            # print("PROD: ", nomeProdotto)
            self.notify("new_product", scraper, *prod)
            datiRitorno.append(prod)

        print(f"{scraper} - FINITONEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE - {cicli} cicli")

        self.notify("fine", scraper, ">>>>>> Generazione grafici completata <<<<<<")
        return datiRitorno

    def ottieniGrafici(self, scraper: GenericScraper, dataInizio=None, dataFine=None, multiplePriceForDay=False, discontinuo=True):
        tuttiIProdotti = DatabaseManager.selectProduct(scraper, "")

        #TODO: Utilizzarlo fuori, è meglio
        # numeroProdotti = DatabaseManager.getProductCount(scraper)
        # self.notify("totprodotti", DatabaseManager.getTable(scraper), numeroProdotti)

        for prodotto in tuttiIProdotti:
            # nomeProdotto = prodotto[1][0:prodotto[1].__len__() - 1]
            nomeProdotto = prodotto[0].strip("\n")
            # print(nomeProdotto)
            self.ottieniGrafico(scraper, nomeProdotto, dataInizio=dataInizio, dataFine=dataFine,
                                   multiplePriceForDay=multiplePriceForDay, discontinuo=discontinuo)

        self.notify("fine", DatabaseManager.getTable(scraper), ">>>>>> Generazione grafici completata <<<<<<")

    def ottieniGrafico(self, scraper: GenericScraper, nomeProdotto: str, dataInizio=None, dataFine=None,
                       multiplePriceForDay=False, discontinuo=True, costruisciGrafico = True, folder=None):

        if folder is not None:
            cartella_output = os.path.join(folder, DatabaseManager.getTable(scraper))
        else:
            cartella_output = DatabaseManager.getTable(scraper)

        # Solo per cercare nel db
        nomeProdotto = nomeProdotto.replace("'", "''")

        prodotti = DatabaseManager.selectProduct(scraper, nomeProdotto, dataInizio=dataInizio, dataFine=dataFine, multiplePriceForDay=multiplePriceForDay)
        prezzi = self.__ottieniPrezzi(prodotti)
        date = self.__ottieniData(prodotti)

        # print(prezzi)
        # print(date)

        # for prodotto in prodotti:
        #     print(prodotto)

        nomeProdotto = self.normalizza_nome_prodotto(nomeProdotto)

        # Creo la cartella se non esiste
        Path(cartella_output).mkdir(parents=True, exist_ok=True)
        # print(cartellaOutput + '/' + nomeProdotto)

        if self.__listeners is not None:
            self.notify("prezzi", DatabaseManager.getTable(scraper), nomeProdotto)

        if costruisciGrafico:
            self.costruisciGrafico(nomeProdotto, date, prezzi, cartella_output, discontinuo=discontinuo)
        else:
            return nomeProdotto, date, prezzi, cartella_output, discontinuo

    @staticmethod
    def normalizza_nome_prodotto(nomeProdotto):
        nomeProdotto = nomeProdotto.replace("\"", " pollici")
        nomeProdotto = nomeProdotto.replace("''", "'")
        nomeProdotto = nomeProdotto.replace(":", " ")
        nomeProdotto = nomeProdotto.replace("/", "-")
        # nomeProdotto = nomeProdotto.replace("+", "")
        # nomeProdotto = nomeProdotto.replace(".", r".")

        return nomeProdotto

    def costruisciGrafico(self, nomeProdotto: str, date: list, prezzi: list, cartellaOutput: str, discontinuo=False):
        if discontinuo:
            prezzi = self.rimuoviValoriInutili(prezzi)

        pl.title(nomeProdotto)
        pl.plot(date, prezzi, "r-")
        pl.plot(date, prezzi, "ro")
        pl.ylabel('Prezzi')
        pl.xlabel('Giorni')
        pl.grid()
        pl.xticks(rotation=75)
        pl.savefig(cartellaOutput + '/' + nomeProdotto + ".png")
        # pl.show()
        pl.close()

    '''Rimuove i valori pari a -1'''

    def rimuoviValoriInutili(self, prezzi: list) -> list:
        for i in range(prezzi.__len__()):
            if prezzi[i] == -1:
                prezzi[i] = None

        return prezzi

    @staticmethod
    def controlla_reale_sconto(scraper, directory=DEFAULT_OUTPUT_FILE):
        prodotti_black_friday = DatabaseManager.get_prezzi_tutti_i_prodotti(scraper, "2020-11-19", "2020-11-20")
        prodotti_dopo = DatabaseManager.get_prezzi_tutti_i_prodotti(scraper, "2020-11-24")
        lista_nomi = [prodotto.nome for prodotto in prodotti_black_friday]
        risultati = []

        if directory is None:
            directory = GestoreGrafici.DEFAULT_OUTPUT_FILE

        for prodotto in prodotti_dopo:
            if prodotto.nome in lista_nomi:
                # Il prodotto era disponibile nel black friday
                risultati.append(prodotto)

        soglia_percentuale = 2

        with open(directory, "w", encoding="UTF-8") as file:
            for prod_dopo, prod_bf in zip(risultati, prodotti_black_friday):
                differenza = round(prod_dopo.prezzo_minimo - prod_bf.prezzo_minimo, 2)
                percentuale_sconto_oggi = round((differenza * 100) / prod_bf.prezzo_minimo, 2)
                # print(f"diff: {differenza}\n"
                #       f"\tprod_bf: {prod_bf.prezzo_minimo} - prod_dopo: {prod_bf.prezzo_minimo}\n"
                #       f"\t{differenza * 100} / {prod_dopo.prezzo_minimo} = {(differenza * 100) / prod_dopo.prezzo_minimo}")

                if percentuale_sconto_oggi <= soglia_percentuale:
                    # È uno sconto fake
                    # print(percentuale_sconto_oggi)
                    prod_dopo.is_fake_sconto = True

                stringa = f"{GestoreGrafici.normalizza_nome_prodotto(prod_dopo.nome)}\t{prod_bf.prezzo_minimo}\t{prod_dopo.prezzo_minimo}"
                stringa += f"\t{percentuale_sconto_oggi}"
                stringa += f"\t{differenza}"
                stringa += f"\t{prod_dopo.is_fake_sconto}"
                # print(stringa)
                file.write(stringa + '\n')

    @staticmethod
    def load_sconto_info(nome_prodotto: str, nome_file=DEFAULT_OUTPUT_FILE) -> ProdottoReport:
        # Il confronto viene fatto tutto su lower per evitare errori di typo
        nome_prodotto = nome_prodotto.lower()

        # print(f"file: {nome_file}")

        try:
            with open(nome_file, "r", encoding="UTF-8") as file:
                for line in file.readlines():
                    # In posizione 0 c'è il nome del prodotto
                    # print(line.replace("\n", "").split("\t"))
                    valori_prodotto = line.replace("\n", "").split("\t")
                    if valori_prodotto[0].lower() == nome_prodotto:
                        # Il penultimo valore manca nella lista quindi deve essere 0
                        valore = False
                        if valori_prodotto[5].lower() == "true":
                            valore = True

                        prodotto = ProdottoReport(valori_prodotto[0], float(valori_prodotto[1]),
                                                  float(valori_prodotto[2]),
                                                  float(valori_prodotto[3]),
                                                  float(valori_prodotto[4]),
                                                  valore)
                        return prodotto
        except Exception as ex:
            print(ex)

        # return ProdottoReport(*["" for i in range(6)])

    def addListeners(self, listeners: list = Ascoltatore):
        self.__listeners.extend(listeners)
        print(self.__listeners)

    def removeListener(self, listener: Ascoltatore):
        self.__listeners.remove(listener)

    def notify(self, operation, *args):
        for listener in self.__listeners:
            listener.update(operation, args)


def worker(scraper: GenericScraper, gestore: GestoreGrafici) -> None:
    gestore.ottieniGrafici(scraper)
    # tuttiIProdotti = DatabaseManager.selectProduct(scraper, "")
    # for prodotto in tuttiIProdotti:
    #     # nomeProdotto = prodotto[1][0:prodotto[1].__len__() - 1]
    #     nomeProdotto = prodotto[1].strip("\n")
    #     # print(nomeProdotto)
    #     gestore.ottieniGrafico(scraper, nomeProdotto, multiplePriceForDay=False)


def wairForProcess(processes: list) -> None:
    for processo in processes:
        processo.join()


class GraphicGeneratorThread (Thread):

    def __init__(self, gestore: GestoreGrafici, scraper: GenericScraper):
        Thread.__init__(self)
        self.__gestore = gestore
        self.__scraper = scraper

    def run(self):
        self.__gestore.ottieniGrafici(self.__scraper)


if __name__ == '__main__':
    gestore = GestoreGrafici()
    gestore.controlla_reale_sconto()
    gestore.addListeners([GraphicGeneratorAscoltatore()])
    scraper = [AmazonScraper, EpriceScraper, MediaworldScraper]
    # scraper = [AmazonScraper]

    processes = []
    #
    # # COSI' NON CONDIVIDONO LA MEMORIA, E QUINDI OGNI LISTENER HA UNA SUA MEMORIA
    for i in range(scraper.__len__()):
        process = multiprocessing.Process(target=worker, args=(scraper[i], gestore))
        processes.append(process)
        process.start()

    wairForProcess(processes)
    # gestore.ottieniGrafico(AmazonScraper, "Samsung Galaxy S20+ 5g Tim Cosmic Gray 8gb/128gb Dual Sim", multiplePriceForDay=False)

    # VERAMENTE CONCORRENTE
    # COSÌ CONDIVIDONO LA MEMORIA E IL LISTENER HA MEMORIA COMUNE
    # thread = []
    # for i in range(3):
    #     t = GraphicGeneratorThread(gestore, scraper[i])
    #     thread.append(t)
    #     t.start()
    #
    # for process in thread:
    #     process.join()

    # print(GestoreGrafici.load_sconto_info("Apple iPhone 12 bianco (64GB)"))
    # GestoreGrafici.controlla_reale_sconto()