import mmap
import threading
from multiprocessing import Process, JoinableQueue
from queue import Queue
from random import random
import time

from threading import Thread

import PySimpleGUI as sg
import os.path
from AmazonScraper import AmazonScraper
from EpriceScraper import EpriceScraper
from MediaworldScraper import MediaworldScraper
from utility.DatabaseManager import DatabaseManager
from grafici import GestoreGrafici
from utility.Ascoltatore import Ascoltatore

# class ProgressBarThread (Thread):
#     window = None
#
#     def __init__(self, window):
#         Thread.__init__(self)
#         self.window = window
#
#     def run(self):
#         print("wewe")
#         while True:
#             event, values = self.window.read()

class ProgressBarListner(Ascoltatore):
    def update(self, operation, *args):
        # Lo stampo solo se è una stringa
        if operation == "prezzi":
            try:
                scraper = args[0][0]
                messaggio = args[0][1]
                if isinstance(messaggio, str):
                    print(scraper, " ---> ", messaggio)
            except Exception as ex:
                print("[ECCEZIONE]: ", ex)
        elif operation == "totprodotti":
            scraper = args[0][0]
            numero_prodotti = args[0][1]
            print(f">>> {scraper} = {numero_prodotti} prodotti")

class ProgressWindow(Ascoltatore):
    window = None
    # __threadlock serve per gestire il lock e non far accavallare le print
    __threadLock = threading.Lock()

    def azzera(self):
        self.text_layout = [
            [
                sg.Text("Amazon", key="-amazonText-", visible=False),
            ],
            [
                sg.Text("Eprice", key="-epriceText-", visible=False),
            ],
            [
                sg.Text("Mediaworld", key="-mediaworldText-", visible=False),
            ]
        ]

        self.progress_layout = [
            [
                sg.ProgressBar(1000, size=(20, 20), key='progbaramazon', visible=False),
            ],
            [
                sg.ProgressBar(1000, size=(20, 20), key='progbareprice', visible=False),
            ],
            [
                sg.ProgressBar(1000, size=(20, 20), key='progbarmediaworld', visible=False)
            ]
        ]

        self.layout = [
            [
                sg.Column(self.text_layout),
                sg.VerticalSeparator(),
                sg.Column(self.progress_layout)
            ],
            [
                sg.Button("Chiudi")
            ]

        ]

    def open(self, checked_scraper: list, datainizio, datafine, multipleprice, missingdata):
        self.azzera()
        self.window = sg.Window("Progress bar grafici", self.layout)
        if checked_scraper.__contains__(AmazonScraper):
            self.window["-amazonText-"].Visible = True
            self.window["progbaramazon"].Visible = True

        if checked_scraper.__contains__(EpriceScraper):
            self.window["-epriceText-"].Visible = True
            self.window["progbareprice"].Visible = True

        if checked_scraper.__contains__(MediaworldScraper):
            self.window["-mediaworldText-"].Visible = True
            self.window["progbarmediaworld"].Visible = True

        self.valori_attuali_progresbar = [0, 0, 0]
        self.valori_massimi_progressbar = [DatabaseManager.getProductCount(AmazonScraper), DatabaseManager.getProductCount(EpriceScraper), DatabaseManager.getProductCount(MediaworldScraper)]

        gestore = GestoreGrafici()
        gestore.addListeners([self])

        self.window["progbaramazon"].MaxValue = self.valori_massimi_progressbar[0]
        self.window["progbareprice"].MaxValue = self.valori_massimi_progressbar[1]
        self.window["progbarmediaworld"].MaxValue = self.valori_massimi_progressbar[2]

        mmap.mmap(0, 65536, 'GlobalSharedMemory')

        for scraper in checked_scraper:
            t = Thread(target=self.startScraping,
                       args=(self.window, scraper, gestore, datainizio, datafine, multipleprice, missingdata))
            t.start()
            # process = Process(target=self.startScraping, args=(self.window, scraper, gestore, datainizio, datafine, multipleprice, missingdata))
            # process.daemon = True
            # process.start()

        while True:
            event, values = self.window.read(timeout=100)
            self.window["progbaramazon"].update_bar(self.valori_attuali_progresbar[0])
            self.window["progbareprice"].update_bar(self.valori_attuali_progresbar[1])
            self.window["progbarmediaworld"].update_bar(self.valori_attuali_progresbar[2])

            # print(f"Amazon {self.valori_attuali_progresbar[0]} - {self.valori_massimi_progressbar[0]}")
            # print(f"Eprice {self.valori_attuali_progresbar[1]} - {self.valori_massimi_progressbar[1]}")
            # print(f"Mediaworld {self.valori_attuali_progresbar[2]} - {self.valori_massimi_progressbar[2]}")

            if event == 'Chiudi' or event == sg.WIN_CLOSED:
                self.window.Close()
                break
            elif event == "Ciao":
                print("OKOK")
            else:
                pass
                #print(event, values)
        #thread = ProgressBarThread(self.window)
        #thread.start()

    def startScraping(self, *args):
        valore = 0
        window, scraper, gestore, datainizio, datafine, multipleprice, missingdata = args
        gestore.ottieniDatiGrafici(scraper, dataInizio=datainizio, dataFine=datafine,
                                                         multiplePriceForDay=multipleprice, discontinuo=missingdata)

    def update(self, operation: str,  *info):
        if (operation == "new_product"):
            scraper, nomeProdotto, date, prezzi, cartellaOutput, discontinuo = info[0]
            # print(f"{nomeProdotto} - {date} - {prezzi} - {cartellaOutput} - {discontinuo}")

            #TODO: Generare grafici qui.
            # A volte funzione e a volte no, BHA
            # gestore = GestoreGrafici()
            # gestore.costruisciGrafico(nomeProdotto, date, prezzi, cartellaOutput, discontinuo)

            # self.create_jobs(info[0], self.report)

            #self.__threadLock.acquire()

            indice = -1
            if scraper == AmazonScraper:
                indice = 0
                # print(f"Amazon {self.valori_attuali_progresbar[indice] + 1} - {self.valori_massimi_progressbar[indice]}")
            if scraper == EpriceScraper:
                indice = 1
                # print(f"Eprice {self.valori_attuali_progresbar[indice] + 1} - {self.valori_massimi_progressbar[indice]}")
            if scraper == MediaworldScraper:
                indice = 2
                # print(f"Mediaworld {self.valori_attuali_progresbar[indice] + 1} - {self.valori_massimi_progressbar[indice]}")

            self.valori_attuali_progresbar[indice] += 1

        elif operation == "fine":
            scraper, message = info[0]

            print(f"fine {scraper} - {AmazonScraper}")

            indice = -1
            if scraper == AmazonScraper:
                indice = 0
            if scraper == EpriceScraper:
                indice = 1
            if scraper == MediaworldScraper:
                indice = 2

            self.valori_attuali_progresbar[indice] = 0
            print(f"azzero {indice}")

            #self.__threadLock.release()

            # self.valori_attuali_progresbar[indice] = self.valori_attuali_progresbar[indice]
            # print(f"{indice}: {self.valori_attuali_progresbar[indice]}")
            # print(f"{operation}: {self.valori_attuali_progresbar[indice]}")




def generateGraph():
    data_inizio, data_fine = DatabaseManager.arco30Giorni()
    checked_scraper = [AmazonScraper, EpriceScraper, MediaworldScraper]

    option_rows = [
        [
            sg.Text("Seleziona l'e-commerce", size=(20, 0)),
            sg.Checkbox("Amazon", default=True, enable_events=True, key='ecommamazon'),
            sg.Checkbox("Eprice", default=True, enable_events=True, key='ecommeprice'),
            sg.Checkbox("Mediaworld", default=True, enable_events=True, key='ecommmediaworld'),
        ],
        [
            sg.Text("Range di date", size=(20, 0)),
            sg.Button("Tutti", key="datetutti"),
            sg.Button("Mese corrente", key="datemese"),
            sg.Button("Ultimi 31 giorni", key="date31day"),

        ],
        [
            sg.Text("Data inizio:", size=(20, 0)),
            sg.CalendarButton('Choose Date', target=(2, 2), key='startDate', format='%Y-%m-%d'),
            sg.Text(data_inizio, size=(20, 0), key="-STARTDATETEXT-"),

        ],
        [
            sg.Text("Data Fine:", size=(20, 0)),
            sg.CalendarButton('Choose Date', target=(3, 2), key='endDate', format='%Y-%m-%d'),
            sg.Text(data_fine, size=(20, 0), key="-ENDDATETEXT-"),

        ],
        [
            sg.Text("Misurazioni multiple", size=(20, 0)),
            sg.Radio("Tutti", "misurazioni", enable_events=True, key='mistutti'),
            sg.Radio("Minore", "misurazioni", default=True, enable_events=True, key='mismin'),

        ],

        [
            sg.Text("Date mancanti", size=(20, 0)),
            sg.Radio("Si", "datemancanti", default=True, enable_events=True, key='missyes'),
            sg.Radio("No", "datemancanti", enable_events=True, key='missno'),
        ],
        [
            sg.Button("Genera"),
            sg.Button("Indietro"),
        ]
    ]

    window = sg.Window("Generatore grafici", option_rows)

    while True:
        event, values = window.read()

        if event == "Indietro":
            window.close()
            start()
            break
        elif event == sg.WIN_CLOSED:
            window.close()
            break
        elif event == "ecommamazon":
            if AmazonScraper in checked_scraper:
                checked_scraper.remove(AmazonScraper)
            else:
                checked_scraper.append(AmazonScraper)
        elif event == "ecommeprice":
            if EpriceScraper in checked_scraper:
                checked_scraper.remove(EpriceScraper)
            else:
                checked_scraper.append(EpriceScraper)
        elif event == "ecommmediaworld":
            if MediaworldScraper in checked_scraper:
                checked_scraper.remove(MediaworldScraper)
            else:
                checked_scraper.append(MediaworldScraper)
        elif event == "datetutti":
            window['-STARTDATETEXT-'].update("Tutte")
            window['-ENDDATETEXT-'].update("Tutte")
        elif event == "datemese":
            data_inizio, data_fine = DatabaseManager.getDateTuttoIlMese()
            window['-STARTDATETEXT-'].update(data_inizio)
            window['-ENDDATETEXT-'].update(data_fine)
        elif event == "date31day":
            data_inizio, data_fine = DatabaseManager.arco30Giorni()
            window['-STARTDATETEXT-'].update(data_inizio)
            window['-ENDDATETEXT-'].update(data_fine)
        elif event == "Genera":
            data_inizio = window['-STARTDATETEXT-'].DisplayText
            data_fine = window['-ENDDATETEXT-'].DisplayText
            multipleprice = values["mistutti"]
            missingdata = values["missyes"]
            if data_inizio == "Tutte" and data_fine == "Tutte":
                data_inizio = None
                data_fine = None

            window.close()
            p = ProgressWindow()
            p.open(checked_scraper, data_inizio, data_fine, multipleprice, missingdata)

            break

    generateGraph()


def getImagesFromFolder(type: str):
    folder = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    folder = os.path.join(folder, type)
    try:
        # Get list of files in folder
        file_list = os.listdir(folder)
    except:
        file_list = []

    fnames = [
        f
        for f in file_list
        if os.path.isfile(os.path.join(folder, f))
           and f.lower().endswith(".png")
    ]
    return fnames, folder


def showgraph():
    back_row = [
        sg.Button("Indietro"),
        sg.Button("Chiudi"),
    ]

    file_list_column = [
        [
            sg.Text("Seleziona una categoria"),
        ],
        [
            sg.Text(size=(78, 1), key="-CURFOLDER-")
        ],
        [
            sg.Button("Amazon"),
            sg.Button("Eprice"),
            sg.Button("Mediaworld"),
        ],
        [
            sg.Listbox(
                values=[], enable_events=True, size=(75, 20), key="-FILE LIST-"
            )
        ],
        back_row
    ]

    # For now will only show the name of the file that was chosen
    image_viewer_column = [
        [sg.Text("Seleziona il prodotto da visualizzare sulla sinistra")],
        [sg.Text(size=(78, 1), key="-TOUT-")],
        [sg.Image(key="-IMAGE-", size=(640, 480))],
    ]

    # ----- Full layout -----
    layout = [
        [
            sg.Column(file_list_column),
            sg.VSeperator(),
            sg.Column(image_viewer_column),
        ],
    ]

    window = sg.Window("Visualizzazione grafici", layout)

    # Run the Event Loop
    while True:
        event, values = window.read()
        if event == "Chiudi" or event == sg.WIN_CLOSED:
            window.close()
            break
        elif event == "Indietro":
            window.close()
            start()
            break
        # Folder name was filled in, make a list of files in the folder
        elif event == "Amazon":
            fnames, curfolder = getImagesFromFolder("prodottiamazon")
            window["-CURFOLDER-"].update(curfolder)
            window["-FILE LIST-"].update(fnames)
        elif event == "Eprice":
            fnames, curfolder = getImagesFromFolder("prodottieprice")
            window["-CURFOLDER-"].update(curfolder)
            window["-FILE LIST-"].update(fnames)
        elif event == "Mediaworld":
            fnames, curfolder = getImagesFromFolder("prodottimediaworld")
            window["-CURFOLDER-"].update(curfolder)
            window["-FILE LIST-"].update(fnames)
        elif event == "-FILE LIST-":  # A file was chosen from the listbox
            try:
                filename = os.path.join(
                    window["-CURFOLDER-"].DisplayText, values["-FILE LIST-"][0]
                )
                window["-TOUT-"].update(values["-FILE LIST-"][0])
                window["-IMAGE-"].update(filename=filename)
            except:
                pass

def start():
    button_column = [
        [
            sg.Text("Progetto  Reti geografiche 2020-21")
        ],
        [
            sg.Button("Vedi i grafici")
        ],
        [
            sg.Button("Genera i grafici")
        ],
        [
            sg.Button("Chiudi")
        ]
    ]

    logo_viewer_column = [
        [sg.Image(key="-LOGOIMAGE-", size=(640, 350), filename="../prodottiamazon/God of war.png")],
    ]

    github_viewer_column = [
        [sg.Image(key="-GITHUBIMAGE-", size=(640, 350), filename="../immagini/github.png")],
    ]

    doc_viewer_column = [
        [sg.Image(key="-DOCIMAGE-", size=(640, 350), filename="../prodottiamazon/God of war.png")],
    ]

    layout = [
        [
            sg.Column(button_column, size=(651, 350)),
            sg.VSeperator(),
            sg.Column(logo_viewer_column),
        ],
        [
            sg.HSeparator()
        ],
        [
            sg.Column(github_viewer_column),
            sg.VSeperator(),
            sg.Column(doc_viewer_column),
        ],
    ]


    # Create the window
    window = sg.Window("Progetto Reti geografiche", layout)

    # Create an event loop
    while True:
        event, values = window.read()
        # End program if user closes window or
        # presses the OK button
        if event == "Chiudi" or event == sg.WIN_CLOSED:
            window.close()
            break
        elif event == "Vedi i grafici":
            window.close()
            showgraph()
            break
        elif event == "Genera i grafici":
            window.close()
            generateGraph()
            break


if __name__ == '__main__':
    start()
