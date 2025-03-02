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
        """
        Originale Funktion (umbenannt für Rückwärtskompatibilität)
        Sums up all actual times for each data element and converts to an array of hours.
        """
        return DataProcessor.sum_actual_times_original(data_dict)
    
    @staticmethod
    def sum_actual_times_original(data_dict):
        """
        Originale Funktion für Rückwärtskompatibilität
        Sums up all actual times for each data element and converts to an array of hours.
        """
        total_actual_times = []
        for index in sorted(data_dict.keys()):  # Sort keys to maintain order
            total_time = sum(int(row["Actual Time"]) for row in data_dict[index] if str(row["Actual Time"]).isdigit())
            total_actual_times.append(round(total_time / 3600, 2))  # Convert seconds to hours
        return total_actual_times
    
    @staticmethod
    def sum_actual_times_extended(data_dict):
        """
        Erweiterte Funktion zur Berechnung von Task-Zeiten
        Sums up all actual times for each data element and calculates task and subtask totals.
        
        Returns:
        - total_actual_times: List of total hours per day
        - task_totals: Dictionary with total seconds per task
        - subtask_totals: Dictionary with total seconds per subtask combination
        """
        total_actual_times = []
        task_totals = {}
        subtask_totals = {}
        
        for index in sorted(data_dict.keys()):  # Sort keys to maintain order
            # Summe der Zeiten für den Tag berechnen (wie bisher)
            total_time = sum(int(row["Actual Time"]) for row in data_dict[index] if str(row["Actual Time"]).isdigit())
            total_actual_times.append(round(total_time / 3600, 2))  # Convert seconds to hours
            
            # Tasks und Subtasks in diesem Datensatz analysieren
            for row in data_dict[index]:
                if (str(row["Actual Time"]).isdigit() and 
                    "Task" in row and "Subtask" in row and 
                    row["Start"] != "False"):
                    
                    actual_time = int(row["Actual Time"])
                    task = row.get("Task", "").strip()
                    subtask = row.get("Subtask", "").strip()
                    
                    # Subtask Key erstellen (Task + Subtask Kombination)
                    task_subtask_key = f"{task}:{subtask}" if task and subtask else task or "(Keine Aufgabe)"
                    
                    # Task Zähler aktualisieren
                    if task:
                        task_totals[task] = task_totals.get(task, 0) + actual_time
                    
                    # Task + Subtask Kombination zählen
                    subtask_totals[task_subtask_key] = subtask_totals.get(task_subtask_key, 0) + actual_time
        
        return total_actual_times, task_totals, subtask_totals
    
    @staticmethod
    def print_task_statistics(task_totals, subtask_totals):
        """Druckt eine formatierte Übersicht der Task- und Subtask-Zeiten"""
        print("\n==== Aufgaben-Statistik ====\n")
        
        # Sortiere nach der aufgewendeten Zeit (absteigend)
        sorted_tasks = sorted(task_totals.items(), key=lambda x: x[1], reverse=True)
        
        print("Gesamtzeit pro Aufgabe:")
        print("======================")
        task_rows = []
        for task, seconds in sorted_tasks:
            hours = seconds / 3600
            minutes = (seconds % 3600) / 60
            task_rows.append([task, f"{int(hours)}h {int(minutes)}m", seconds])
        
        print(tabulate(task_rows, headers=["Aufgabe", "Zeit", "Sekunden"], tablefmt="grid"))
        
        # Sortiere nach der aufgewendeten Zeit (absteigend)
        sorted_subtasks = sorted(subtask_totals.items(), key=lambda x: x[1], reverse=True)
        
        print("\nGesamtzeit pro Aufgabe + Unteraufgabe:")
        print("====================================")
        subtask_rows = []
        for task_subtask, seconds in sorted_subtasks:
            hours = seconds / 3600
            minutes = (seconds % 3600) / 60
            task, *subtask_parts = task_subtask.split(":", 1)
            subtask = subtask_parts[0] if subtask_parts else "-"
            subtask_rows.append([task, subtask, f"{int(hours)}h {int(minutes)}m", seconds])
        
        print(tabulate(subtask_rows, headers=["Aufgabe", "Unteraufgabe", "Zeit", "Sekunden"], tablefmt="grid"))
        print("\n" + "=" * 50 + "\n")
    
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
        self.task_totals = {}
        self.subtask_totals = {}
        
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
        
        # Bisherige Berechnung für Rückwärtskompatibilität
        self.total_actual_times = DataProcessor.sum_actual_times_original(self.data_dict)
        self.start_times = DataProcessor.extract_start_times(self.data_dict)
        
        # Neue Berechnung für Task-Statistiken
        _, self.task_totals, self.subtask_totals = DataProcessor.sum_actual_times_extended(self.data_dict)
        
        if verbose:
            print("Total actual times per dataset:", self.total_actual_times)
            # Ausgabe der Task-Statistiken
            DataProcessor.print_task_statistics(self.task_totals, self.subtask_totals)
        
        # Nur ursprüngliche Rückgabewerte für Rückwärtskompatibilität zurückgeben
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
        #self.last_update_time = datetime.now()

    def setup_ui(self):
        """Initialisiert die UI-Komponenten"""
        layout = QVBoxLayout(self)
        self.setWindowTitle("Arbeitszeit Visualisierung")

        # Matplotlib Canvas vorbereiten
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        
        # Nur den Chart anzeigen, keine Info-Panels
        layout.addWidget(self.canvas)

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
        #self.last_update_time = datetime.now()
        
        print("Aktualisierung abgeschlossen.")

    def draw_chart(self):
        """Zeichnet ein modernes, ansprechenderes Balkendiagramm"""
        self.ax.clear()
        categories = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
        x_pos = np.arange(len(categories))
        bar_width = 0.6  # Breitere Balken für ein moderneres Aussehen
        
        # Farben für ein modernes Farbschema
        main_color = '#3498db'  # Blau
        highlight_color = '#2ecc71'  # Grün für erreichte Stundenziele
        background_color = '#f8f9fa'  # Heller Hintergrund
        grid_color = '#A0A0A0'  # Hellgraue Rasterlinien
        text_color = '#2c3e50'  # Dunkelblau/Grau für Text
        
        # Hintergrund einstellen
        self.figure.patch.set_facecolor(background_color)
        self.ax.set_facecolor(background_color)
        
        # Ziel-Arbeitsstunden (z.B. 8 Stunden pro Tag)
        target_hours = 8.0
        
        # Balken für jeden Tag zeichnen
        for day_idx in range(1, 6):  # Index 1-5 für Montag-Freitag
            if day_idx in self.data_dict:
                day_data = self.data_dict[day_idx]
                last_valid_bar = None
                daily_total = 0.0 if day_idx-1 >= len(self.total_actual_times) else self.total_actual_times[day_idx-1]
                
                # Farbe basierend auf Zielerfüllung bestimmen
                bar_color = highlight_color if daily_total >= target_hours else main_color
                
                # Alle Arbeitsintervalle des Tages verarbeiten
                for i, row in enumerate(day_data[:-1]):  # Letzte Zeile ignorieren
                    if row["Start"] != "False" and row["Actual Time"] > 0:
                        start = Config.time_to_decimal(row["Start"])
                        duration = row["Actual Time"] / 3600
                        
                        # Balken mit abgerundeten Ecken (keine direkte Unterstützung in matplotlib,
                        # aber mit Alpha-Transparenz und Schatten kann ein moderner Look erzeugt werden)
                        bar = self.ax.bar(
                            x_pos[day_idx-1], 
                            duration,
                            bottom=start,
                            width=bar_width,
                            color=bar_color,
                            alpha=0.85,
                            edgecolor='none',
                            zorder=3
                        )
                        
                        last_valid_bar = bar
                
                # Gesamtzeit über letztem Balken anzeigen mit modernerem Stil
                if last_valid_bar and day_idx-1 < len(self.total_actual_times):
                    total_time = self.total_actual_times[day_idx-1]
                    bar_top = last_valid_bar[0].get_height() + last_valid_bar[0].get_y()
                    
                    # Hintergrundblase für die Stundenanzahl
                    # Stundenanzahl als einfache schwarze Zahl
                    self.ax.text(
                        x_pos[day_idx-1], 
                        bar_top + 0.8, 
                        f"{total_time:.1f}h",
                        ha='center', 
                        va='center',
                        fontsize=10,
                        fontweight='normal',
                        color='black',  # Schwarze Zahl
                        zorder=4
                    )

        # Horizontale Linien für Arbeitszeiten (9-17 Uhr) hervorheben
        self.ax.axhspan(9, 17, color='#f1f8ff', alpha=0.5, zorder=1)
        
        # Diagrammformatierung
        self.ax.set_ylim(7, 20)
        self.ax.set_yticks(np.arange(8, 21, 1))
        self.ax.set_yticklabels([f"{h}:00" for h in range(8, 21)], fontsize=9, color=text_color)
        self.ax.set_xticks(x_pos)
        
        # Formatierte X-Achsenbeschriftungen mit Wochentag und Startzeit
        formatted_labels = []
        for day, time in zip(categories, self.start_times):
            if time.strip() not in ['', ' ']:
                formatted_labels.append(f"{day}\n{time}")
            else:
                formatted_labels.append(day)
        
        self.ax.set_xticklabels(formatted_labels, fontsize=10, color=text_color)
        
        # Dunklere Rasterlinien
        self.ax.grid(True, axis='y', linestyle='-', alpha=0.4, color=grid_color, zorder=0)
        
        # Wochensumme anzeigen
        week_total = sum(self.total_actual_times)
        week_goal = target_hours * 5  # 5 Arbeitstage
        percentage = (week_total / week_goal) * 100 if week_goal > 0 else 0
        
        """# Wochensumme als Titel
        status_color = highlight_color if percentage >= 100 else (main_color if percentage >= 85 else '#e74c3c')
        self.ax.set_title(
            f"Weekly Tracking: {week_total:.1f}h von {week_goal}h ({percentage:.0f}%)", 
            fontsize=12, 
            fontweight='bold',
            color=status_color,
            pad=15
        )"""
        
        # Achsenlinien entfernen für ein cleaneres Aussehen
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color(grid_color)
        self.ax.spines['bottom'].set_color(grid_color)
        
        # Heutigen Tag hervorheben
        today = datetime.today().weekday()  # 0 = Montag, 4 = Freitag
        if 0 <= today <= 4:  # Nur Wochentage markieren
            self.ax.get_xticklabels()[today].set_color(highlight_color)
            self.ax.get_xticklabels()[today].set_fontweight('extra bold')
        
        """# Aktualisierungszeitstempel dezent anzeigen
        update_time = self.last_update_time.strftime("%H:%M:%S")
        self.figure.text(
            0.99, 0.01, 
            f"Aktualisiert: {update_time}", 
            ha='right', 
            va='bottom',
            fontsize=7,
            color='#aab8c2',
            style='italic'
        )
        """
        # Layout optimieren
        self.figure.tight_layout(pad=2.0)
        self.canvas.draw()
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