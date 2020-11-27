import PySimpleGUI as sg
import os.path


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

    window = sg.Window("Image Viewer", layout)

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
    layout = [[sg.Text("Progetto  Reti geografiche 2020-21")], [sg.Button("Vedi i grafici")], [sg.Button("Chiudi")]]

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


if __name__ == '__main__':
    start()
