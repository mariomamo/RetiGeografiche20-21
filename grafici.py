import threading
import time
from pathlib import Path
import matplotlib.pylab as pl
from utility.DatabaseManager import DatabaseManager
import GenericScraper
from AmazonScraper import AmazonScraper
from EpriceScraper import EpriceScraper
from MediaworldScraper import MediaworldScraper
import multiprocessing
from utility.Ascoltatore import Ascoltatore
from utility.Ascoltabile import Ascoltabile
from threading import Thread


# class GraphicGeneratorAscoltatore(Ascoltatore):
#     # __threadlock serve per gestire il lock e non far accavallare le print
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

        for prodotto in tuttiIProdotti:
            # nomeProdotto = prodotto[1][0:prodotto[1].__len__() - 1]
            nomeProdotto = prodotto[1].strip("\n")
            # print(nomeProdotto)
            datiRitorno.append(self.ottieniGrafico(scraper, nomeProdotto, dataInizio=dataInizio, dataFine=dataFine,
                                multiplePriceForDay=multiplePriceForDay, discontinuo=discontinuo, costruisciGrafico=False))

        self.notify("prezzi", DatabaseManager.getTable(scraper), ">>>>>> Generazione grafici completata <<<<<<")
        return datiRitorno

    def ottieniGrafici(self, scraper: GenericScraper, dataInizio=None, dataFine=None, multiplePriceForDay=False, discontinuo=True):
        tuttiIProdotti = DatabaseManager.selectProduct(scraper, "")

        #TODO: Utilizzarlo fuori, è meglio
        # numeroProdotti = DatabaseManager.getProductCount(scraper)
        # self.notify("totprodotti", DatabaseManager.getTable(scraper), numeroProdotti)

        for prodotto in tuttiIProdotti:
            # nomeProdotto = prodotto[1][0:prodotto[1].__len__() - 1]
            nomeProdotto = prodotto[1].strip("\n")
            # print(nomeProdotto)
            self.ottieniGrafico(scraper, nomeProdotto, dataInizio=dataInizio, dataFine=dataFine,
                                   multiplePriceForDay=multiplePriceForDay, discontinuo=discontinuo)

        self.notify("prezzi", DatabaseManager.getTable(scraper), ">>>>>> Generazione grafici completata <<<<<<")


    def ottieniGrafico(self, scraper: GenericScraper, nomeProdotto: str, dataInizio=None, dataFine=None, multiplePriceForDay=False, discontinuo=True, costruisciGrafico = True):
        nomeProdotto = nomeProdotto.replace("'", "''")

        prodotti = DatabaseManager.selectProduct(scraper, nomeProdotto, dataInizio=dataInizio, dataFine=dataFine, multiplePriceForDay=multiplePriceForDay)
        prezzi = self.__ottieniPrezzi(prodotti)
        date = self.__ottieniData(prodotti)

        # print(prezzi)
        # print(date)

        # for prodotto in prodotti:
        #     print(prodotto)

        cartellaOutput = DatabaseManager.getTable(scraper)

        nomeProdotto = nomeProdotto.replace("\"", "pollici")
        nomeProdotto = nomeProdotto.replace("''", "'")
        nomeProdotto = nomeProdotto.replace(":", " ")
        nomeProdotto = nomeProdotto.replace("/", "-")
        # nomeProdotto = nomeProdotto.replace("+", "")
        # nomeProdotto = nomeProdotto.replace(".", r".")

        # Creo la cartella se non esiste
        Path(cartellaOutput).mkdir(parents=True, exist_ok=True)
        # print(cartellaOutput + '/' + nomeProdotto)

        if self.__listeners is not None:
            self.notify("prezzi", DatabaseManager.getTable(scraper), nomeProdotto)

        if costruisciGrafico:
            self.costruisciGrafico(nomeProdotto, date, prezzi, cartellaOutput, discontinuo=discontinuo)
        else:
            return nomeProdotto, date, prezzi, cartellaOutput, discontinuo



    def costruisciGrafico(self, nomeProdotto: str, date: list, prezzi: list, cartellaOutput: str, discontinuo=False):
        if discontinuo:
            prezzi = self.rimuoviValoriInutili(prezzi)

        pl.title(nomeProdotto)
        pl.plot(date, prezzi, "r-")
        pl.plot(date, prezzi, "ro")
        pl.ylabel('Prezzi')
        pl.xlabel('Giorni')
        pl.grid()
        # pl.xticks(rotation=75)
        pl.savefig(cartellaOutput + '/' + nomeProdotto + ".png")
        # pl.show()
        pl.close()

    '''Rimuove i valori pari a -1'''

    def rimuoviValoriInutili(self, prezzi: list) -> list:
        for i in range(prezzi.__len__()):
            if prezzi[i] == -1:
                prezzi[i] = None

        return prezzi

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
    gestore.addListeners([GraphicGeneratorAscoltatore()])
    scraper = [AmazonScraper, EpriceScraper, MediaworldScraper]
    # scraper = [MediaworldScraper]

    processes = []

    # COSI' NON CONDIVIDONO LA MEMORIA, E QUINDI OGNI LISTENER HA UNA SUA MEMORIA
    for i in range(scraper.__len__()):
        process = multiprocessing.Process(target=worker, args=(scraper[i], gestore))
        processes.append(process)
        process.start()

    # wairForProcess(processes)
    # gestore.ottieniGrafico(AmazonScraper, "Samsung Galaxy S20+ 5g Tim Cosmic Gray 8gb/128gb Dual Sim", multiplePriceForDay=False)

    # VERAMENTE CONCORRENTE
    # thread = []
    # for i in range(3):
    #     t = GraphicGeneratorThread(gestore, scraper[i])
    #     thread.append(t)
    #     t.start()
    #
    # for process in thread:
    #     process.join()
