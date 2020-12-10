from grafici import GestoreGrafici
import sys

nome_file = "report.txt"
try:
    nome_file = sys.argv[1]
except Exception as ex:
    pass

gestore = GestoreGrafici()
gestore.controlla_reale_sconto(nome_file)
