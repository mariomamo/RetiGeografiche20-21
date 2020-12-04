from AmazonScraper import AmazonScraper
from EpriceScraper import EpriceScraper
from MediaworldScraper import MediaworldScraper
from utility.DatabaseManager import DatabaseManager
from multiprocessing import Process, Queue
import time
from multiprocessing import JoinableQueue


def startscrape(jobs, report):
    while True:
        scraper = jobs.get()
        print("Scraper ", scraper, " inizializzato")
        scrapertype = type(scraper)
        prodotti = scraper.get_offers()
        print("Scraping di ", scrapertype, " eseguito correttamente")
        report.put((prodotti, scrapertype))
        jobs.task_done()


def create_process(jobs, report):
    for _ in range(3):
        process = Process(target=startscrape, args=(jobs, report))
        process.daemon = True
        process.start()

def create_jobs(scrapers, jobs):
    for scraper in scrapers:
        jobs.put(scraper)


def waitForComplete(jobs, report):
    jobs.join()

    while not report.empty():
        tupla = report.get_nowait()
        DatabaseManager.insert(tupla[0], tupla[1])


if __name__ == "__main__":
    scrapers = [AmazonScraper(), EpriceScraper(), MediaworldScraper()]
    # scrapers = [EpriceScraper()]

    report = Queue()
    jobs = JoinableQueue()

    create_process(jobs, report)

    create_jobs(scrapers, jobs)
    time.sleep(2)
    waitForComplete(jobs, report)


