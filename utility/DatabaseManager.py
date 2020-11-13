import psycopg2
from beans.Prodotto import Prodotto
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

    def insert(self, prodotto):
        #sql = "INSERT INTO 'ProdottiAmazon' (Nome, URL, Prezzo) VALUES({}, {}, {}".format()
        with self.__conn.cursor() as cursor:
            cursor.execute("INSERT INTO \"ProdottiAmazon\" (nome, url, prezzo, data) VALUES(%s, %s, %s, %s)", (prodotto.nome, prodotto.url, 200, datetime.now()))


