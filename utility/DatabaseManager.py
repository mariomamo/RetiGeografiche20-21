import psycopg2
from AmazonScraper import AmazonScraper
from EpriceScraper import EpriceScraper
from MediaworldScraper import MediaworldScraper
from datetime import datetime
import GenericScraper


class DatabaseManager:
    __conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="ProdottiEcommerce",
            user="root",
            password="root")
    __conn.autocommit = True

    @staticmethod
    def getTable(scrapertype):
        if scrapertype == AmazonScraper:
            return "prodottiamazon"
        elif scrapertype == EpriceScraper:
            return "prodottieprice"
        else:
            return "prodottimediaworld"


    @staticmethod
    def insert(prodotti, scrapertype):
        #sql = "INSERT INTO 'ProdottiAmazon' (Nome, URL, Prezzo) VALUES({}, {}, {}".format()
        tablename = DatabaseManager.getTable(scrapertype)

        with DatabaseManager.__conn.cursor() as cursor:
            for prodotto in prodotti:
                cursor.execute("INSERT INTO "+tablename+" (nome, url, prezzo, data) VALUES(%s, %s, %s, %s)", (prodotto.nome, prodotto.url, prodotto.prezzo, datetime.now()))

    @staticmethod
    def selectProduct(table: GenericScraper, nomeProdotto: str):
        tablename = DatabaseManager.getTable(table)
        query = "SELECT * FROM " + tablename + " WHERE nome LIKE '" + nomeProdotto + "%' ORDER BY id"

        with DatabaseManager.__conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

        return rows