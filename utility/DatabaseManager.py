import psycopg2
from AmazonScraper import AmazonScraper, Prodotto
from EpriceScraper import EpriceScraper
import datetime
import GenericScraper
from calendar import monthrange

from beans.ProdottoStatistiche import ProdottoStatistiche


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
                cursor.execute("INSERT INTO " + tablename + " (nome, url, prezzo, data) VALUES(%s, %s, %s, %s)", (prodotto.nome, prodotto.url, prodotto.prezzo, datetime.datetime.now()))


    @staticmethod
    def getProductCount(scraper: GenericScraper):
        query = 'SELECT COUNT(*) FROM (SELECT DISTINCT nome FROM ''' + DatabaseManager.getTable(scraper) + ''') AS R1'''
        with DatabaseManager.__conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()[0][0]

        return rows

    @staticmethod
    def selectProduct(table: GenericScraper, nomeProdotto: str, dataInizio=None, dataFine=None, multiplePriceForDay=False):
        # Inizializzo le date se non ci sono
        if dataInizio is None and dataFine is None:
            dataInizio, dataFine = DatabaseManager.arco30Giorni()
        elif dataInizio is None:
            dataInizio, _ = DatabaseManager.arco30Giorni()
        elif dataFine is None:
            _, dataFine = DatabaseManager.arco30Giorni()

        # print(dataInizio)
        # print(dataFine)

        tablename = DatabaseManager.getTable(table)
        result = list()

        query = DatabaseManager.__getQueryForSelectProduct(tablename, nomeProdotto, dataInizio, dataFine, multiplePriceForDay=multiplePriceForDay)

        with DatabaseManager.__conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

        if nomeProdotto != '':
            # serve per tenere il conto della data che ci si aspetta
            date = None

            for i in range(rows.__len__()):
                # print("Indice: ", i, " max: ", rows.__len__())
                # Leggo tutta la riga
                row = rows[i]
                # Prendo solo la data dalla riga
                # è la data che viene letta dal prodotto
                currDate = row[row.__len__() - 1]

                # Mi salvo il primo giorno disponibile per le misurazioni se non ce l'ho
                if date is None:
                    date = currDate
                    # print("NOONE")
                else:
                    # Se un giorno è stato saltato aggiungo un valore con -1
                    # diff contiene il numero di giorni che mancano
                    # print(date, " - ", currDate)
                    diff = (currDate - date).days
                    # print("DIFF: ", currDate, " - ", date, " = ", diff)
                    if diff >= 1:
                        # print("DIFF >= 1")
                        # print(int(str(currDate - date)[0:1]))

                        # Per ogni giorno che manca lo aggiungo
                        for k in range(diff):
                            # Creo la tupla che conterrà il nuovo valore e inserisco tutti i valori uguali, tranne che per il prezzo
                            # il quale invece sarà -1, e la data che deve essere quella mancante (sono gli ultimi due valori)
                            # (587, 'Star Wars - Millennium Falcon LEGO', 'https://www.amazon.it/dp/B07NDB4Q7S', 155.61, datetime.date(2020, 11, 22))
                            oggetto = tuple()
                            for j in range(row.__len__() - 2):
                                oggetto += (row[j],)

                            # Inserisco il prezzo pari a -1 nella penultima posizione
                            oggetto += (-1,)

                            # Inserisco la data mancante nell'ultima posizione
                            oggetto += (date,)
                            # Incremento il giorno in cui mi trovo di 1
                            date += datetime.timedelta(days=1)

                            # Inserisco l'elemento che mancava nella lista dei risultati
                            result.append(oggetto)

                # Aggiungo il prodotto del giorno analizzato alla lista dei risultati
                result.append(row)
                # Incremento il giorno in cui mi trovo di 1
                date += datetime.timedelta(days=1)

            rows = result

        # for row in rows:
        #     print(row)

        return rows

    '''
        Restituisce il range di tate del mese corrente
    '''
    @staticmethod
    def getDateTuttoIlMese():
        oggi = str(datetime.date.today())
        anno = oggi[0:4]
        mese = oggi[5:7]
        dataInizio = anno + '-' + mese + '-01'
        dataFine = anno + '-' + mese + '-' + str(monthrange(int(anno), int(mese))[1])

        return dataInizio, dataFine

    '''
        Retituisce il range di date degli ultimi 30 giorni
    '''
    @staticmethod
    def arco30Giorni():
        dataFine = datetime.date.today()
        dataInizio = dataFine - datetime.timedelta(31)
        return str(dataInizio), str(dataFine)

    @staticmethod
    def get_prezzi_tutti_i_prodotti(scraper: GenericScraper, data_inizio: str, data_fine: str = str(datetime.date.today())) -> list:
        '''
        :param scraper: Scraper generico che rappresenta l'ecommerce
        :param data_inizio: Data di inizio di cui si vogliono i dati
        :param data_fine: Data di fine di cui si vogliono i dati
        :return: Lista di prodotti con il prezzo minimo, il prezzo massimo e la media
        '''
        query = f"SELECT nome, min(prezzo) as prezzo_minimo, max(prezzo) as prezzo_massimo, cast(avg(prezzo) as decimal(9,2)) as media_prezzo"
        query += f" FROM {DatabaseManager.getTable(scraper)} WHERE prezzo != -1"
        query += f" AND data BETWEEN '{data_inizio}' AND '{data_fine}'"
        query += f" GROUP BY nome ORDER BY nome;"

        with DatabaseManager.__conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

        risultati = [ProdottoStatistiche(elemento[0], elemento[1], elemento[2], elemento[3]) for elemento in rows]
        return risultati

    @staticmethod
    def __getQueryForSelectProduct(tablename: str, nomeProdotto: str, dataInizio: str, dataFine: str, multiplePriceForDay=None):
        # Se si vogliono più prezzi per lo stesso giorno
        if multiplePriceForDay:
            query = """SELECT * FROM """ + tablename + """ WHERE nome='""" + nomeProdotto + """' ORDER BY id"""
        # Se viene passato il nome del prodotto cerca solo quello
        elif nomeProdotto != '':
            query = """
                    SELECT id, nome, url, """ + tablename + """.prezzo, """ + tablename + """.data FROM
                        (SELECT data, MIN(prezzo) as prezzo FROM """ + tablename + """ WHERE prezzo > -1 AND nome = '""" + nomeProdotto + """' GROUP BY data) AS R1
                        INNER JOIN """ + tablename + """ ON """ + tablename + """.nome='""" + nomeProdotto + """'
                        AND """ + tablename + """.data=R1.data
                        AND """ + tablename + """.prezzo=R1.prezzo
                        AND """ + tablename + """.data BETWEEN '""" + dataInizio + """' AND '""" + dataFine + """'
                    ORDER BY data
            """
        # Altrimenti cerca tutti i prodotti
        else:
            query = "SELECT DISTINCT(nome) FROM (SELECT * FROM " + tablename + " ORDER BY id) AS R1;"

        return query

    '''
    SELECT id, nome, url, prodottimediaworld.prezzo, prodottimediaworld.data FROM
        (SELECT data, MIN(prezzo) as prezzo FROM prodottimediaworld WHERE prezzo > -1 AND nome = 'SAMSUNG Galaxy S20 5G Cosmic Gray' GROUP BY data) AS R1
        INNER JOIN prodottimediaworld ON prodottimediaworld.nome='SAMSUNG Galaxy S20 5G Cosmic Gray'
        AND prodottimediaworld.data=R1.data
        AND prodottimediaworld.prezzo > 0
        AND prodottimediaworld.prezzo=R1.prezzo
    ORDER BY data;
    '''


if __name__ == "__main__":
    prodotti = DatabaseManager.get_prezzi_tutti_i_prodotti(AmazonScraper, "2020-11-24", "09-12-2020")
    for prodotto in prodotti:
        print(prodotto)
