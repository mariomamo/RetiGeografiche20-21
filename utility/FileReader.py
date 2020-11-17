from beans.Prodotto import Prodotto
SEPARATOR = "|%!|"


def readFromFile(filepath: str):
    lista_prodotti = []
    with open(filepath, 'r') as file:
        lines = file.readlines()
        for line in lines:
            params = line.split(SEPARATOR)
            lista_prodotti.append(Prodotto(nome=params[1][0: params[1].__len__()], url=params[0]))

        return lista_prodotti
