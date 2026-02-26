import matplotlib.pyplot as plt
import numpy as np

def plot_points(file_path, file_title):
    # Einlesen der Daten aus der Datei als Strings
    data = np.loadtxt(file_path, delimiter=',', dtype=str)
    radial_distance = data[:, 0].astype(float)  # First column contains the radial distance of each location
    azimuth_angle = data[:, 1].astype(float)  # Secong column contains the azimuth angle of each location
    elevation_angle = data[:, 2].astype(float)  # Third column contains the elevation angle of each location
    point_ids = data[:, 3]  # Fourth column contains the location ID
    colors = data[:, 4]  # Fifth column contains the color
    three_dimensions = data[:, 5]  # Sixth column contains the indicator for the dimensions

    # Konvertierung von radialen in kartesische Koordinaten
    x = radial_distance * np.cos(elevation_angle) * np.cos(azimuth_angle)
    y = radial_distance * np.cos(elevation_angle) * np.sin(azimuth_angle)
    z = radial_distance * np.sin(elevation_angle)

    # Erstelle eine Figur und eine Achse
    fig, ax = plt.subplots()

    # Plotten der Punkte mit IDs und Farben
    for i in range(len(x)):
        ax.scatter(y[i], x[i], marker='o', color=colors[i], s=13)  # 's' parameter controls the size of the points
        ax.text(y[i], x[i], str(int(point_ids[i])), ha='center', va='bottom')

    # Achsenbeschriftungen
    ax.set_xlabel('lateral axis')
    ax.set_ylabel('longitudinal axis')

    # Achsenlimits
    ax.set_xlim(15, -15)
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
    ax.set_title(file_title)

    # In Case at least one location generated is with the sensor in parking mode (3D points) we want an additional plot in 3D
    if np.any(three_dimensions.astype(int) == 1):
        fig_3d = plt.figure()
        ax_3d = fig_3d.add_subplot(111, projection='3d')

        # Set the labels for the axes
        ax_3d.set_xlabel('lateral axis')
        ax_3d.set_ylabel('longitudinal axis')
        ax_3d.set_zlabel('vertical axis')
        
        # Set the axial limits
        ax_3d.set_xlim(10, -10)
        ax_3d.set_ylim(10, 30)
        ax_3d.set_zlim(-2, 4)

        ax_3d.set_title(file_title + ' Parking')

        # Add grid lines for better visualization
        ax_3d.grid(True)
        
        # Add color bar to indicate the height (z-axis) with a fixed scale
        # Also use three_dimensions.astype(int) == 1 to only show the color bar for the 3D points
        sc = ax_3d.scatter(y[three_dimensions.astype(int) == 1], 
                           x[three_dimensions.astype(int) == 1], 
                           z[three_dimensions.astype(int) == 1], 
                           c=z[three_dimensions.astype(int) == 1], 
                           cmap='inferno', vmin=-0.5, vmax=1.5)
        fig_3d.colorbar(sc, ax=ax_3d, label='Height (z-axis)')
    
    # Anzeigen des Diagramms
    plt.show()

# Beispielaufruf der Funktion mit einer Datei namens data.txt
file_path = '../build/Release/data.txt'
file_title = '1objXloc'
plot_points(file_path,file_title)
file_path = '../build/Release/data_RoadObj.txt'
file_title = 'RoadObj'
plot_points(file_path,file_title)