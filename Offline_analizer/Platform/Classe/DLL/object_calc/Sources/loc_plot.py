import matplotlib.pyplot as plt
import numpy as np

def plot_points(file_path):
    # Einlesen der Daten aus der Datei als Strings
    data = np.loadtxt(file_path, delimiter=',', dtype=str)
    radial_distance = data[:, 0].astype(float)
    azimuth_angle = data[:, 1].astype(float)
    point_ids = data[:, 2]  # Annahme: Die ID ist in der dritten Spalte der Daten enthalten
    colors = data[:, 3]  # Annahme: Die Farbe ist in der vierten Spalte der Daten enthalten

    # Konvertierung von radialen in kartesische Koordinaten
    x = radial_distance * np.cos((azimuth_angle))
    y = radial_distance * np.sin((azimuth_angle))

    # Erstelle eine Figur und eine Achse
    fig, ax = plt.subplots()

    # Plotten der Punkte mit IDs und Farben
    for i in range(len(x)):
        ax.scatter(y[i], x[i], marker='^', color=colors[i])
        ax.text(y[i], x[i], str(int(point_ids[i])), ha='center', va='bottom')

    # Achsenbeschriftungen
    ax.set_xlabel('lateral axis')
    ax.set_ylabel('longitudinal axis')

    # Achsenlimits
    ax.set_xlim(10, -10)
    ax.set_ylim(0, 30)

    # Nullpunkt in der Mitte der y-Achse
    #ax.spines['left'].set_position('center')
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_position('zero')
    ax.spines['top'].set_color('none')

    # Achsenticks anpassen
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # Diagrammtitel
    ax.set_title('Location Plot')

    # Anzeigen des Diagramms
    plt.show()

# Beispielaufruf der Funktion mit einer Datei namens data.txt
file_path = '../build/Release/data.txt'
plot_points(file_path)