from pathlib import Path
import matplotlib.pylab as pl
from utility.DatabaseManager import DatabaseManager
import GenericScraper
from AmazonScraper import AmazonScraper
from EpriceScraper import EpriceScraper
from MediaworldScraper import MediaworldScraper
import multiprocessing
from utility.Listener import Listener
from utility.Ascoltatore import  Ascoltatore


class MyListener(Listener):

    def update(self, *args):
        # Lo stampo solo se è una stringa
        try:
            scraper = args[0][0]
            messaggio = args[0][1]
            if isinstance(messaggio, str):
                print(scraper, " ---> ", messaggio)
        except Exception as ex:
            print("[ECCEZIONE]: ", ex)


class GestoreGrafici(Ascoltatore):

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

    def ottieniGrafici(self, scraper: GenericScraper, dataInizio=None, dataFine=None, multiplePriceForDay=False, discontinuo=True):
        tuttiIProdotti = DatabaseManager.selectProduct(scraper, "")
        for prodotto in tuttiIProdotti:
            # nomeProdotto = prodotto[1][0:prodotto[1].__len__() - 1]
            nomeProdotto = prodotto[1].strip("\n")
            # print(nomeProdotto)
            self.ottieniGrafico(scraper, nomeProdotto, dataInizio=dataInizio, dataFine=dataFine,
                                   multiplePriceForDay=multiplePriceForDay, discontinuo=discontinuo)

        self.notify(DatabaseManager.getTable(scraper), ">>>>>> Generazione grafici completata <<<<<<")


    def ottieniGrafico(self, scraper: GenericScraper, nomeProdotto: str, dataInizio=None, dataFine=None, multiplePriceForDay=False, discontinuo=True) -> None:
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

        self.costruisciGrafico(nomeProdotto, date, prezzi, cartellaOutput, discontinuo=discontinuo)

        if self.__listeners is not None:
            self.notify(DatabaseManager.getTable(scraper), nomeProdotto)

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

    def addListeners(self, listeners: list = Listener):
        self.__listeners.extend(listeners)
        print(self.__listeners)

    def removeListener(self, listener: Listener):
        self.__listeners.remove(listener)

    def notify(self, *args):
        for listener in self.__listeners:
            listener.update(args)


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


if __name__ == '__main__':
    gestore = GestoreGrafici()
    gestore.addListeners([MyListener()])
    scraper = [AmazonScraper, EpriceScraper, MediaworldScraper]
    # scraper = [MediaworldScraper]

    processes = []
    for i in range(scraper.__len__()):
        process = multiprocessing.Process(target=worker, args=(scraper[i], gestore))
        processes.append(process)
        process.start()

    wairForProcess(processes)
    # gestore = GestoreGrafici()
    # gestore.ottieniGrafico(AmazonScraper, "Samsung Galaxy S20+ 5g Tim Cosmic Gray 8gb/128gb Dual Sim", multiplePriceForDay=False)
