import PySimpleGUI as sg
import os.path
from AmazonScraper import AmazonScraper
from EpriceScraper import EpriceScraper
from MediaworldScraper import MediaworldScraper
from utility.DatabaseManager import DatabaseManager

def generateGraph():
    data_inizio, data_fine = DatabaseManager.arco30Giorni()
    checked_scraper = [AmazonScraper, EpriceScraper, MediaworldScraper]
    # data_inizio, data_fine = None, None

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
            sg.Text(data_inizio, size=(20, 0)),

        ],
        [
            sg.Text("Data Fine:", size=(20, 0)),
            sg.CalendarButton('Choose Date', target=(3, 2), key='endDate', format='%Y-%m-%d'),
            sg.Text(data_fine, size=(20, 0)),

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
        print(event)

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
    print(os.getcwd())
    layout = [[sg.Text("Progetto  Reti geografiche 2020-21")], [sg.Button("Vedi i grafici")], [sg.Button("Genera i grafici")], [sg.Button("Chiudi")]]

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
