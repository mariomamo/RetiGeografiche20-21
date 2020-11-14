import psycopg2
from AmazonScraper import AmazonScraper
from EpriceScraper import EpriceScraper
from MediaworldScraper import MediaworldScraper
from datetime import datetime

class DatabaseManager:

    __conn = None

    def __init__(self):
        self.__conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="ProdottiEcommerce",
            user="root",
            password="root")
        self.__conn.autocommit = True

        print("CONN: ", self.__conn)

    def getTable(self, scrapertype):
        if scrapertype == AmazonScraper:
            return "prodottiamazon"
        elif scrapertype == EpriceScraper:
            return "prodottieprice"
        else:
            return "prodottimediaworld"




    def insert(self, prodotti, scrapertype):
        #sql = "INSERT INTO 'ProdottiAmazon' (Nome, URL, Prezzo) VALUES({}, {}, {}".format()
        tablename = self.getTable(scrapertype)

        with self.__conn.cursor() as cursor:
            for prodotto in prodotti:
                cursor.execute("INSERT INTO "+tablename+" (nome, url, prezzo, data) VALUES(%s, %s, %s, %s)", (prodotto.nome, prodotto.url, prodotto.prezzo, datetime.now()))


