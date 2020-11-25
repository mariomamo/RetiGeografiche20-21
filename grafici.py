from pathlib import Path
import matplotlib.pylab as pl
from utility.DatabaseManager import DatabaseManager
import GenericScraper
from AmazonScraper import AmazonScraper
from EpriceScraper import EpriceScraper
from MediaworldScraper import MediaworldScraper
import multiprocessing


class GestoreGrafici:

    @staticmethod
    def __ottieniPrezzi(prodotti: list) -> list:
        prezzi = list()
        for prodotto in prodotti:
            prezzi.append(prodotto[3])

        return prezzi

    @staticmethod
    def __ottieniData(prodotti: list) -> list:
        date = list()
        for prodotto in prodotti:
            data = prodotto[prodotto.__len__() - 1]
            data = data.strftime('%m/%d')
            date.append(data)

        return date

    @staticmethod
    def ottieniGrafico(scraper: GenericScraper, nomeProdotto: str) -> None:
        nomeProdotto = nomeProdotto.replace("'", "''")

        prodotti = DatabaseManager.selectProduct(scraper, nomeProdotto)
        prezzi = GestoreGrafici.__ottieniPrezzi(prodotti)
        date = GestoreGrafici.__ottieniData(prodotti)

        # print(prezzi)
        # print(date)

        # for prodotto in prodotti:
        #     print(prodotto)

        cartellaOutput = DatabaseManager.getTable(scraper)

        nomeProdotto = nomeProdotto.replace("\"", "pollici")
        nomeProdotto = nomeProdotto.replace("''", "'")
        nomeProdotto = nomeProdotto.replace(":", " ")
        #nomeProdotto = nomeProdotto.replace("+", "")
        #nomeProdotto = nomeProdotto.replace(".", r".")

        # Creo la cartella se non esiste
        Path(cartellaOutput).mkdir(parents=True, exist_ok=True)
        # print(cartellaOutput + '/' + nomeProdotto)

        pl.title(nomeProdotto)
        pl.plot(date, prezzi, "r-")
        pl.plot(date, prezzi, "ro")
        pl.ylabel('Prezzi')
        pl.xlabel('Giorni')
        pl.savefig(cartellaOutput + '/' + nomeProdotto + ".png")
        #pl.show()
        pl.close()


def worker(scraper: GenericScraper) -> None:
    tuttiIProdotti = DatabaseManager.selectProduct(scraper, "")
    for prodotto in tuttiIProdotti:
        # nomeProdotto = prodotto[1][0:prodotto[1].__len__() - 1]
        nomeProdotto = prodotto[1].strip("\n")
        print(nomeProdotto)
        GestoreGrafici.ottieniGrafico(scraper, nomeProdotto)


def wairForProcess(processes: list) -> None:
    for processo in processes:
        processo.join()


if __name__ == '__main__':
    scraper = [AmazonScraper, EpriceScraper, MediaworldScraper]
    #scraper = [MediaworldScraper]
    processes = []
    for i in range(scraper.__len__()):
        process = multiprocessing.Process(target=worker, args=(scraper[i],))
        processes.append(process)
        process.start()

    wairForProcess(processes)
    # GestoreGrafici.ottieniGrafico(MediaworldScraper, "PS4 PRO 1TB")
    # GestoreGrafici.ottieniGrafico(MediaworldScraper, "PS5 1TB + Horizon Zero Dawn + Uncharted 4")