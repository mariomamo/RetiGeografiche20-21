import traceback

import PySimpleGUI as sg
import os.path
from AmazonScraper import AmazonScraper
from EpriceScraper import EpriceScraper
from MediaworldScraper import MediaworldScraper
from utility.DatabaseManager import DatabaseManager
from grafici import GestoreGrafici
from utility.Ascoltatore import Ascoltatore
import webbrowser
from beans.ProdottoReport import ProdottoReport

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


# class ProgressBarListner(Ascoltatore):
#     def update(self, operation, *args):
#         # Lo stampo solo se è una stringa
#         if operation == "prezzi":
#             try:
#                 scraper = args[0][0]
#                 messaggio = args[0][1]
#                 if isinstance(messaggio, str):
#                     print(scraper, " ---> ", messaggio)
#             except Exception as ex:
#                 print("[ECCEZIONE]: ", ex)
#         elif operation == "totprodotti":
#             scraper = args[0][0]
#             numero_prodotti = args[0][1]
#             print(f">>> {scraper} = {numero_prodotti} prodotti")


class ProgressWindow():
    window = None

    # def long_function_thread(self, window, checked_scraper, datainizio, datafine, multipleprice, missingdata):
    #     progressbarlistner = ProgressBarListner()
    #     for scraper in checked_scraper:
    #         gestore = GestoreGrafici()
    #         gestore.addListeners([progressbarlistner])
    #         datiProdottiScraper = gestore.ottieniDatiGrafici(scraper, dataInizio=datainizio, dataFine=datafine, multiplePriceForDay=multipleprice, discontinuo=missingdata)


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

        #ascoltatore = ProgressBarListner()
        #Thread(target=self.long_function_thread, args=(self.window, checked_scraper, datainizio, datafine, multipleprice, missingdata), daemon=True).start()
        gestore = GestoreGrafici()
        #progressbarlistner = ProgressBarListner()

        while True:
            if len(checked_scraper) > 0:
                i = 0
                event, values = self.window.read(timeout=100)
                scraper = checked_scraper.pop()
                print(scraper)
                #gestore.addListeners([progressbarlistner])
                datiProdottiScraper = gestore.ottieniDatiGrafici(scraper, dataInizio=datainizio, dataFine=datafine, multiplePriceForDay=multipleprice, discontinuo=missingdata)

                for dati in datiProdottiScraper:
                    #print(*dati)
                    folder = os.path.join(os.path.dirname(__file__), os.pardir)
                    gestore.ottieniGrafico(scraper, dati[0], datainizio, datafine, multipleprice, missingdata, folder)
                    #AGGIORNA
                    print(i)
                    i += 1
                    tot = (1000/len(datiProdottiScraper)) * i
                    if scraper == AmazonScraper:
                        self.window['progbaramazon'].update_bar(tot)
                    elif scraper == EpriceScraper:
                        self.window['progbareprice'].update_bar(tot)
                    elif scraper == MediaworldScraper:
                        self.window['progbarmediaworld'].update_bar(tot)

            else:
                event, values = self.window.read()

            if event == 'Chiudi' or event == sg.WIN_CLOSED:
                self.window.close()
                break
            else:
                print(event, values)
        generateGraph()

        #thread = ProgressBarThread(self.window)
        #thread.start()



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
            sg.Radio("Tutti", "misurazioni", default=True, enable_events=True, key='mistutti'),
            sg.Radio("Minore", "misurazioni", enable_events=True, key='mismin'),

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
    current_scraper = None

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
        [
          sg.Text("Seleziona il prodotto per ottenere il report", key="-REPORT-", size=(75, 5))
        ],
            back_row
    ]

    # For now will only show the name of the file that was chosen
    image_viewer_column = [
        [
            sg.Text("Seleziona il prodotto da visualizzare sulla sinistra")
        ],
        [
            sg.Text(size=(78, 1), key="-TOUT-")
        ],
        [
            sg.Image(key="-IMAGE-", size=(640, 480))
        ],
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
            current_scraper = AmazonScraper
            fnames, curfolder = getImagesFromFolder("prodottiamazon")
            window["-CURFOLDER-"].update(curfolder)
            window["-FILE LIST-"].update(fnames)
        elif event == "Eprice":
            current_scraper = EpriceScraper
            fnames, curfolder = getImagesFromFolder("prodottieprice")
            window["-CURFOLDER-"].update(curfolder)
            window["-FILE LIST-"].update(fnames)
        elif event == "Mediaworld":
            current_scraper = MediaworldScraper
            fnames, curfolder = getImagesFromFolder("prodottimediaworld")
            window["-CURFOLDER-"].update(curfolder)
            window["-FILE LIST-"].update(fnames)
        elif event == "-FILE LIST-":  # A file was chosen from the listbox
            try:
                filename = os.path.join(
                    window["-CURFOLDER-"].DisplayText, values["-FILE LIST-"][0]
                )

                print(filename)

                window["-IMAGE-"].update(filename=filename)
                nomeprodotto = values["-FILE LIST-"][0]
                nomeprodotto = nomeprodotto[:-4]
                window["-TOUT-"].update(nomeprodotto)
                save_file_name = "report_" + DatabaseManager.getTable(current_scraper) + ".txt"
                print(save_file_name)
                save_dir = os.path.join(os.path.dirname(__file__), os.pardir, save_file_name)

                GestoreGrafici.controlla_reale_sconto(current_scraper, directory=save_dir)
                path = os.path.join(save_dir)
                stats = GestoreGrafici.load_sconto_info(nomeprodotto, path)
                # print(f"stats: {stats}")
                if stats is not None:
                    # TODO: Aggiungere report per gli altri e-commerce
                    window["-REPORT-"].update(f"Report per: {stats.nome}:\n"
                                              f"Prezzo black friday: {stats.prezzo_bf}€\n"
                                              f"Prezzo minimo dopo il Black friday: {stats.prezzo_dopo}€\n"
                                              f"Differenza: {stats.differenza_prezzo}€, differenza percentuale: {stats.percentuale_sconto}%\n"
                                              f"E' uno scono fake? {stats.is_sconto_fake}")
                else:
                    window["-REPORT-"].update(f"Report non disponibile")
            except Exception as ex:
                traceback.print_exc()


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
        [sg.Image(key="-LOGOIMAGE-", size=(640, 350), filename="../immagini/github.png", enable_events=True)],
    ]

    github_viewer_column = [
        [sg.Image(key="-GITHUBIMAGE-", size=(640, 350), filename="../immagini/github.png", enable_events=True)],
    ]

    doc_viewer_column = [
        [sg.Image(key="-DOCIMAGE-", size=(640, 350), filename="../immagini/documenti.png", enable_events=True)],
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
        elif event == "-DOCIMAGE-":
            webbrowser.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstleyVEVO', new=2)
        elif event == "-GITHUBIMAGE-":
            webbrowser.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstleyVEVO', new=2)
        elif event == "-LOGOIMAGE-":
            webbrowser.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstleyVEVO', new=2)


if __name__ == '__main__':
    start()
