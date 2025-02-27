import csv
import os
from tabulate import tabulate
import sys
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta
import numpy as np 

# Get today's date (or set manually for testing)
#today = datetime(2025, 2, 6)  # Fixed date for testing
today = datetime.today()
# Get current ISO calendar week
year, week, weekday = today.isocalendar()

# Calculate Monday of the current week
monday = today - timedelta(days=weekday - 1)

# Generate dates for Monday to Friday in "DD-MM-YY" format
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
week_dates = {day: (monday + timedelta(days=i)).strftime("%d-%m-%y") for i, day in enumerate(days)}

# Define base directory
base_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
print("Base Directory:", base_dir)

# Dictionary to store data files
data_dict = {}

# Function to read CSV file
def read_csv(file_path):
    """Reads a CSV file and returns the data as a list of dictionaries."""
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data = [row for row in reader]

        # Entferne alle Zeilen am Anfang, die nicht 1,1,1 sind
        while data and (int(data[0]["Mode"]) != 1 or int(data[0]["Status"]) != 1 or int(data[0]["Work"]) != 1):
            data.pop(0)

        #add last row for live timer
        current_time = datetime.now().strftime("%H:%M:%S")
        new_row = {"Mode": "0", "Status": "0", "Work": "0", "Time": current_time }
        data.append(new_row)

        # Add extra columns if not present in CSV
        for row in data:
            row["Start"] = row["Time"] if int(row["Mode"]) == 1 and int(row["Status"]) == 1 and int(row["Work"]) == 1 else "False"

        # Assign "Stop" time from the next row
        for i in range(len(data) - 1):
            if data[i]["Start"] != "False":
                data[i]["Stop"] = data[i + 1]["Time"]

        # Calculate "Actual Time"
        for row in data:
            try:
                if row["Start"] != "False":
                    start_time = datetime.strptime(row["Start"], "%H:%M:%S")
                    stop_time = datetime.strptime(row["Stop"], "%H:%M:%S")
                    actual_time = (stop_time - start_time).total_seconds()
                    row["Actual Time"] = int(actual_time)
                else:
                    row["Actual Time"] = 0
            except Exception:
                row["Actual Time"] = 0
        return data
    
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
# Function to sum up actual times for each data element
def sum_actual_times(data_dict):
    """Sums up all actual times for each data element and converts to an array of hours."""
    total_actual_times = []
    for index in sorted(data_dict.keys()):  # Sort keys to maintain order
        total_time = sum(int(row["Actual Time"]) for row in data_dict[index] if str(row["Actual Time"]).isdigit())
        total_actual_times.append(round(total_time / 3600, 2))  # Convert seconds to hours
    return total_actual_times

# Function to print CSV data nicely
def print_csv_nicely(data, file_path):
    """Prints the CSV data in a formatted table."""
    if not data:
        print(f"No data found for {file_path}")
        return
    
    headers = list(data[0].keys())  # Extract column names
    rows = [list(row.values()) for row in data]  # Extract row values

    print(f"Data from {file_path}:")
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print("\n" + "=" * 50 + "\n")  # Separator for better readability

# Process each CSV file and store it in data_dict
for index, (day, date) in enumerate(week_dates.items(), start=1):
    file_path = os.path.join(base_dir, "data", f"{date}.csv")
    if os.path.exists(file_path):
        print(f"Loading CSV file for {day}: {file_path}")
        data_dict[index] = read_csv(file_path)  # Store data in dictionary with numeric key
    
        print_csv_nicely(data_dict[index], file_path) #Print nicely formatted output
    else:
        print(f"File does not exist: {file_path}")
# Calculate and print total actual times
total_actual_times = sum_actual_times(data_dict)
print("Total actual times per dataset:", total_actual_times)

# Array für die ersten Startzeiten (ohne Sekunden)
start_times = [' ', ' ', ' ', ' ', ' ']  


# Startzeiten laden Durchlaufe alle geladenen CSV-Daten
for index, data in data_dict.items():
    if data:  # Stelle sicher, dass die Datei Daten enthält
        for row in data:
            if row["Start"] != "False":
                # Zeit ohne Sekunden speichern (HH:MM)
                start_time = datetime.strptime(row["Start"], "%H:%M:%S").strftime("%H:%M")
                start_times[index - 1] = start_time  # Speichere die Zeit an der richtigen Stelle
                break  # Schleife für diese Datei beenden, sobald eine Startzeit gefunden wurde



print("Erste Startzeiten aus jeder CSV-Datei (ohne Sekunden):", start_times)



#start_times = [8.5, 9, 8, 8.1, 9]  # Startzeiten für jede Kategorie
total_hours = [3, 4, 5, 6, 7]  # Gesamte Stundenzeit für jeden Balken


class BarChartApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Balkendiagramm mit mehreren Balken für Montag")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        # Matplotlib-Figur erstellen
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # CSV-Daten laden
        self.data = read_csv(file_path)  # Hier wird data geladen

        # Kategorien (Wochentage)
        categories = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        #start_times = [8.5, 9, 8, 8.1, 9]  # Startzeiten für jede Kategorie
        x_positions = np.arange(len(categories))  # X-Positionen für die Balken

        # Werte für die blauen Balken (Hauptwerte)
        values = [9, 11, 14, 16]  # Beispielstunden

        # Blauen Balken zeichnen
        #self.ax.bar(x_positions, values, color='royalblue', width=0.4, label="Main Data")

        def time_to_decimal(time_str):
            time_parts = list(map(int, time_str.split(":")))
            
            if len(time_parts) == 3:  # Falls das Format HH:MM:SS ist
                hours, minutes, seconds = time_parts
            elif len(time_parts) == 2:  # Falls das Format HH:MM ist
                hours, minutes = time_parts
                seconds = 0
            else:
                raise ValueError(f"Ungültiges Zeitformat: {time_str}")

            return hours + minutes / 60 + seconds / 3600
        
        # Zusätzlicher roter Balken für Montag (10:00 - 12:00)
        #self.ax.bar(x_positions[0], 2, bottom=10, color='red', width=0.4, label="Hacken")
        #self.ax.bar(x_positions[1], 2700/3600, bottom=8.5, color='royalblue', width=0.4, label="Hacken")
        
        #Balken zeichnen
        values = [9, 11, 14, 16]  # Werte, die über den letzten Balken stehen sollen

        for j in range(1, len(data_dict) + 1):  # Start bei 1, weil data_dict[0] nicht existiert
            if data_dict[j] is not None and len(data_dict[j]) > 1:  # Sicherstellen, dass Daten existieren
                last_valid_index = None
                
                for i in range(len(data_dict[j]) - 1):  # Nicht auf die letzte Zeile zugreifen!
                    if data_dict[j][i]["Start"] != "False" and data_dict[j][i]["Actual Time"] > 0:
                        last_valid_index = i  # Speichert den Index des letzten gültigen Balkens
                        
                        self.ax.bar(x_positions[j-1], data_dict[j][i]["Actual Time"] / 3600, 
                                    bottom=time_to_decimal(str(data_dict[j][i]["Start"])), 
                                    color='royalblue', width=0.4)
                
                # Falls ein gültiger letzter Balken existiert, platziere den Text darüber
                if last_valid_index is not None and j <= len(total_actual_times):
                    last_bar_height = data_dict[j][last_valid_index]["Actual Time"] / 3600
                    last_bar_bottom = time_to_decimal(str(data_dict[j][last_valid_index]["Start"]))
                    last_bar_top = last_bar_bottom + last_bar_height

                    self.ax.text(x_positions[j-1], last_bar_top + 0.2,  # Direkt über dem letzten Balken
                                str(total_actual_times[j-1]), 
                                ha='center', fontsize=10, fontweight='normal', color='black')

        '''
        # **Totale Stunden als Text über jedem Balken platzieren**
        for bar, hours in zip(bars, total_hours):
            height = bar.get_height() + bar.get_y()  # Höhe des Balkens + Startzeit
            self.ax.text(bar.get_x() + bar.get_width()/2, height, f"{hours}h", 
                         ha='center', va='bottom', fontsize=10, color='black', fontweight='bold'
        '''

        # Achsentitel setzen
        self.ax.set_title("Weekly Data with Extra Monday Block")
        self.ax.set_ylabel("Time of the Day")

        # X-Achsenbeschriftung: Kombination aus Wochentag und Startzeit
        x_labels = [f"{day}\n {start}" for day, start in zip(categories, start_times)]
        self.ax.set_xticks(x_positions)
        self.ax.set_xticklabels(x_labels)

        # Y-Achse von 8:00 bis 20:00 formatieren
        self.ax.set_ylim(8, 20)  # Begrenzung der Y-Achse auf 8:00 - 20:00 Uhr
        self.ax.set_yticks(np.arange(8, 21, 1))  # Tick-Labels alle 2 Stunden
        self.ax.set_yticklabels([f"{h}:00" for h in range(8, 21, 1)])  # Format als Zeit

        # Legende hinzufügen
        #self.ax.legend()

        self.canvas.draw()  # Zeichnung aktualisieren


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BarChartApp()
    window.show()
    sys.exit(app.exec_())
