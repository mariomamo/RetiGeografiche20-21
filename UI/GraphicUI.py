import PySimpleGUI as sg
import os.path
from AmazonScraper import AmazonScraper
from EpriceScraper import EpriceScraper
from MediaworldScraper import MediaworldScraper
from utility.DatabaseManager import DatabaseManager
from grafici import GestoreGrafici
from utility.Ascoltatore import Ascoltatore

class MyAscoltatore(Ascoltatore):

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
            print(f"Scraper:  {args[0][0]}, totale prodotti: {args[0][1]}")

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
            data_inizio, data_fine = DatabaseManager.tuttoIlMese()
            window['-STARTDATETEXT-'].update(data_inizio)
            window['-ENDDATETEXT-'].update(data_fine)
        elif event == "date31day":
            data_inizio, data_fine = DatabaseManager.arco30Giorni()
            window['-STARTDATETEXT-'].update(data_inizio)
            window['-ENDDATETEXT-'].update(data_fine)
        elif event == "Genera":
            startdate = window['-STARTDATETEXT-'].DisplayText
            enddate = window['-ENDDATETEXT-'].DisplayText
            multipleprice = values["mistutti"]
            missingdata = values["missyes"]
            if startdate == "Tutte" and enddate == "Tutte":
                startdate = None
                enddate = None

            for scraper in checked_scraper:
                lis = MyAscoltatore()
                gestore = GestoreGrafici()
                gestore.addListeners([lis])
                gestore.ottieniGrafici(scraper, dataInizio=startdate, dataFine=enddate, multiplePriceForDay=multipleprice, discontinuo=missingdata)

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
