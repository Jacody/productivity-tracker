import csv
import os
import sys
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Konfiguration und Hilfsfunktionen
class Config:
    """Klasse für alle Konfigurationseinstellungen und allgemeine Hilfsfunktionen"""
    
    # Aktualisierungsintervall in Millisekunden (36 Sekunden)
    REFRESH_INTERVAL = 36000
    
    @staticmethod
    def get_current_week_dates():
        """Berechnet Daten für die aktuelle Woche (Montag bis Freitag)"""
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
        
        return week_dates
    
    @staticmethod
    def get_base_dir():
        """Findet das Basisverzeichnis der Anwendung"""
        base_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
        print("Base Directory:", base_dir)
        return base_dir
    
    @staticmethod
    def time_to_decimal(time_str):
        """Hilfsfunktion zur Umwandlung von Zeitstrings in Dezimalstunden"""
        try:
            if time_str.strip() in ['', 'False']:
                return 0.0
            parts = list(map(int, time_str.split(':')))
            return parts[0] + parts[1]/60 + (parts[2] if len(parts)>2 else 0)/3600
        except:
            return 0.0


# Datenverarbeitung
class DataProcessor:
    """Klasse für alle Datenverarbeitungsfunktionen"""
    
    @staticmethod
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
    
    @staticmethod
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
    
    @staticmethod
    def sum_actual_times(data_dict):
        """Sums up all actual times for each data element and converts to an array of hours."""
        total_actual_times = []
        for index in sorted(data_dict.keys()):  # Sort keys to maintain order
            total_time = sum(int(row["Actual Time"]) for row in data_dict[index] if str(row["Actual Time"]).isdigit())
            total_actual_times.append(round(total_time / 3600, 2))  # Convert seconds to hours
        return total_actual_times
    
    @staticmethod
    def extract_start_times(data_dict):
        """Extracts the first start time from each dataset."""
        start_times = [' ', ' ', ' ', ' ', ' ']  
        
        # Durchlaufe alle geladenen CSV-Daten
        for index, data in data_dict.items():
            if data:  # Stelle sicher, dass die Datei Daten enthält
                for row in data:
                    if row["Start"] != "False":
                        # Zeit ohne Sekunden speichern (HH:MM)
                        start_time = datetime.strptime(row["Start"], "%H:%M:%S").strftime("%H:%M")
                        start_times[index - 1] = start_time  # Speichere die Zeit an der richtigen Stelle
                        break  # Schleife für diese Datei beenden, sobald eine Startzeit gefunden wurde
        
        return start_times


# Datensammlung und -verarbeitung
class DataManager:
    """Klasse für das Sammeln und Verwalten aller Daten"""
    
    def __init__(self):
        self.week_dates = Config.get_current_week_dates()
        self.base_dir = Config.get_base_dir()
        self.data_dict = {}
        
    def load_all_data(self, verbose=True):
        """Lädt alle CSV-Dateien für die aktuelle Woche"""
        self.data_dict = {}  # Reset data dictionary for refresh
        
        for index, (day, date) in enumerate(self.week_dates.items(), start=1):
            file_path = os.path.join(self.base_dir, "data", f"{date}.csv")
            if os.path.exists(file_path):
                if verbose:
                    print(f"Loading CSV file for {day}: {file_path}")
                self.data_dict[index] = DataProcessor.read_csv(file_path)
                if verbose:
                    DataProcessor.print_csv_nicely(self.data_dict[index], file_path)
            else:
                if verbose:
                    print(f"File does not exist: {file_path}")
        
        # Calculate metrics
        self.total_actual_times = DataProcessor.sum_actual_times(self.data_dict)
        self.start_times = DataProcessor.extract_start_times(self.data_dict)
        
        if verbose:
            print("Total actual times per dataset:", self.total_actual_times)
        
        return self.data_dict, self.total_actual_times, self.start_times


# GUI Klasse - jetzt als QWidget statt QMainWindow für bessere Integration
class BarChartApp(QWidget):
    def __init__(self, data_dict, total_actual_times, start_times):
        super().__init__()
        self.data_dict = data_dict
        self.start_times = start_times
        self.total_actual_times = total_actual_times
        
        self.setup_ui()
        self.setup_timer()
        self.draw_chart()
        
        # Status-Label für letzte Aktualisierung
        self.last_update_time = datetime.now()
        self.update_status_label()

    def setup_ui(self):
        """Initialisiert die UI-Komponenten"""
        layout = QVBoxLayout(self)
        self.setWindowTitle("Arbeitszeit Visualisierung")

        # Chart und Info in horizontal layout
        chart_info_layout = QHBoxLayout()

        # Matplotlib Canvas vorbereiten
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        
        # Info-Panel erstellen
        info_panel = QVBoxLayout()
        self.labels = {
            'avg_start': QLabel("Durchschnittsstartzeit: Wird berechnet..."),
            'total_hours': QLabel("Gesamtstunden: Wird berechnet..."),
            'last_update': QLabel("Letzte Aktualisierung: -")
        }
        
        for label in self.labels.values():
            info_panel.addWidget(label)

        # Layouts zusammenfügen
        chart_info_layout.addWidget(self.canvas, 75)  # 75% Platz für Diagramm
        chart_info_layout.addLayout(info_panel, 25)   # 25% für Info-Panel
        
        layout.addLayout(chart_info_layout)

    def setup_timer(self):
        """Richtet den Timer für die automatische Aktualisierung ein"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(Config.REFRESH_INTERVAL)  # Aktualisiere alle 36 Sekunden
        print(f"Auto-refresh aktiviert: Alle {Config.REFRESH_INTERVAL/1000} Sekunden")

    def refresh_data(self):
        """Aktualisiert die Daten und die Anzeige"""
        print("Daten werden aktualisiert...")
        
        # Daten neu laden (ohne ausführliche Ausgabe)
        data_manager = DataManager()
        self.data_dict, self.total_actual_times, self.start_times = data_manager.load_all_data(verbose=False)
        
        # Chart neu zeichnen
        self.draw_chart()
        
        # Update time
        self.last_update_time = datetime.now()
        self.update_status_label()
        
        print("Aktualisierung abgeschlossen.")

    def update_status_label(self):
        """Aktualisiert das Status-Label mit der letzten Aktualisierungszeit"""
        update_time_str = self.last_update_time.strftime("%H:%M:%S")
        self.labels['last_update'].setText(f"Letzte Aktualisierung: {update_time_str}")

    def draw_chart(self):
        """Zeichnet das eigentliche Balkendiagramm"""
        self.ax.clear()
        categories = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        x_pos = np.arange(len(categories))
        bar_width = 0.4

        # Balken für jeden Tag zeichnen
        for day_idx in range(1, 6):  # Index 1-5 für Montag-Freitag
            if day_idx in self.data_dict:
                day_data = self.data_dict[day_idx]
                last_valid_bar = None
                
                # Alle Arbeitsintervalle des Tages verarbeiten
                for i, row in enumerate(day_data[:-1]):  # Letzte Zeile ignorieren
                    if row["Start"] != "False" and row["Actual Time"] > 0:
                        start = Config.time_to_decimal(row["Start"])
                        duration = row["Actual Time"] / 3600
                        last_valid_bar = self.ax.bar(
                            x_pos[day_idx-1], 
                            duration,
                            bottom=start,
                            width=bar_width,
                            color='royalblue',
                            alpha=0.7
                        )
                
                # Gesamtzeit über letztem Balken anzeigen
                if last_valid_bar and (day_idx-1) < len(self.total_actual_times):
                    total_time = self.total_actual_times[day_idx-1]
                    bar_top = last_valid_bar[0].get_height() + last_valid_bar[0].get_y()
                    self.ax.text(
                        x_pos[day_idx-1], 
                        bar_top + 0.1, 
                        f"{total_time:.2f}h",
                        ha='center', 
                        va='bottom',
                        fontsize=9
                    )

        # Diagrammformatierung
        self.ax.set_ylim(7, 20)
        self.ax.set_yticks(np.arange(8, 21, 1))
        self.ax.set_yticklabels([f"{h}:00" for h in range(8, 21)])
        self.ax.set_xticks(x_pos)
        self.ax.set_xticklabels([f"{day}\n{time}" for day, time in zip(categories, self.start_times)])
        #self.ax.set_title("Arbeitszeiten der Woche")
        self.ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Statistiken aktualisieren
        self.update_statistics()
        self.canvas.draw()

    def update_statistics(self):
        """Aktualisiert die Statistik-Labels mit korrekter Zeitumrechnung"""
        # Nur gültige Startzeiten berücksichtigen (Leerstrings filtern)
        valid_times = [Config.time_to_decimal(t) for t in self.start_times if t.strip()]
        
        if valid_times:
            # Durchschnittsberechnung
            avg_start_decimal = np.mean(valid_times)
            
            # Korrekte Umrechnung in Stunden:Minuten
            hours = int(avg_start_decimal)
            minutes = int((avg_start_decimal - hours) * 60)
            avg_start_str = f"{hours:02d}:{minutes:02d}"
            
            # Summenberechnung
            total_hours = sum(self.total_actual_times)
            
            self.labels['avg_start'].setText(
                f"Durchschnittliche Startzeit: {avg_start_str}"
            )
            self.labels['total_hours'].setText(
                f"Gesamte Arbeitszeit: {total_hours:.2f} Stunden"
            )
        else:
            self.labels['avg_start'].setText("Durchschnittliche Startzeit: N/A")
            self.labels['total_hours'].setText("Gesamte Arbeitszeit: 0.0 Stunden")


# Hauptprogramm (nur ausführen, wenn die Datei direkt gestartet wird)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Daten-Manager initialisieren
    data_manager = DataManager()
    data_dict, total_actual_times, start_times = data_manager.load_all_data()
    
    # GUI starten
    window = BarChartApp(data_dict, total_actual_times, start_times)
    window.show()
    sys.exit(app.exec_())