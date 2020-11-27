from beans.Prodotto import Prodotto
import os

SEPARATOR = "|%!|"


def readFromFile(filepath: str):
    lista_prodotti = []
    with open(filepath, 'r') as file:
        lines = file.readlines()
        for line in lines:
            # Rimuovo lo '\n' alla fine di ogni riga
            line = line.strip("\n")
            params = line.split(SEPARATOR)
            lista_prodotti.append(Prodotto(nome=params[1][0: params[1].__len__()], url=params[0]))

        return lista_prodotti


def deleteFromFile(filepath: str, urlProdotto):
    prodotti = []

    with open(filepath, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip("\n")
            param = line.split(SEPARATOR)[0]
            if param != urlProdotto:
                prodotti.append(line)

    elementi = 0
    with open(filepath, "w") as f:
        for prodotto in prodotti:
            f.write(prodotto)
            elementi += 1
            if elementi != prodotti.__len__():
                f.write("\n")
