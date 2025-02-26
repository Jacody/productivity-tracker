import sys
import matplotlib.pyplot as plt
import numpy as np  # NumPy importieren
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class BarChartApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Balkendiagramm mit Startzeiten und Gesamtstunden")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        # Matplotlib-Figur erstellen
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Kategorien (Wochentage)
        categories = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        start_times = [8.5, 9, 8, 8.1, 9]  # Startzeiten für jede Kategorie
        total_hours = [3, 4, 5, 6, 7]  # Gesamte Stundenzeit für jeden Balken
        x_positions = np.arange(len(categories))  # X-Positionen für die Balken

        # Blauen Balken zeichnen (Hauptwerte)
        bars = self.ax.bar(x_positions, total_hours, bottom=start_times, color='royalblue', width=0.4, label="Main Data")

        # Zusätzlicher roter Balken für Montag (10:00 - 12:00)
        #self.ax.bar(x_positions[0], 2, bottom=10, color='red', width=0.4, label="Extra Block (Monday)")

        # **Totale Stunden als Text über jedem Balken platzieren**
        for bar, hours in zip(bars, total_hours):
            height = bar.get_height() + bar.get_y()  # Höhe des Balkens + Startzeit
            self.ax.text(bar.get_x() + bar.get_width()/2, height, f"{hours}h", 
                         ha='center', va='bottom', fontsize=10, color='black', fontweight='bold')

        # Achsentitel setzen
        self.ax.set_title("Weekly Data with Extra Monday Block")
        self.ax.set_ylabel("Time of the Day")

        # X-Achsenbeschriftung: Kombination aus Wochentag und Startzeit
        x_labels = [f"{day}\n(Start: {start}:00)" for day, start in zip(categories, start_times)]
        self.ax.set_xticks(x_positions)
        self.ax.set_xticklabels(x_labels)

        # Y-Achse von 8:00 bis 20:00 formatieren
        self.ax.set_ylim(8, 20)  # Begrenzung der Y-Achse auf 8:00 - 20:00 Uhr
        self.ax.set_yticks(np.arange(8, 21, 2))  # Tick-Labels alle 2 Stunden
        self.ax.set_yticklabels([f"{h}:00" for h in range(8, 21, 2)])  # Format als Zeit

        # Legende hinzufügen
        self.ax.legend()

        self.canvas.draw()  # Zeichnung aktualisieren

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BarChartApp()
    window.show()
    sys.exit(app.exec_())
