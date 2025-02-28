import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Importiere die drei Programme
from tracker import MainApp  # Gesichtserkennung (Produktivitäts-Tracker)
from todo_manager import TodoApp  # To-Do-Manager
# Importiere die BarChartApp-Klasse aus csv_reader
from csv_reader import DataManager, BarChartApp  # CSV-Visualisierung

# Wrappen der MainApp als QWidget für Integration
class ProductivityTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.main_app = MainApp()  # Produktivitäts-Tracker GUI
        self.layout.addWidget(self.main_app)
        self.setLayout(self.layout)

# Wrappen der BarChartApp als QWidget für Integration
class CsvVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        
        # Daten-Manager initialisieren und Daten laden
        data_manager = DataManager()
        data_dict, total_actual_times, start_times = data_manager.load_all_data(verbose=False)
        
        # BarChartApp erstellen und dem Layout hinzufügen
        self.chart_app = BarChartApp(data_dict, total_actual_times, start_times)
        self.layout.addWidget(self.chart_app)
        
        self.setLayout(self.layout)

# Haupt-App mit vertikalem Layout für alle drei Programme
class CombinedApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Productivity-Tracker")
        self.setGeometry(100, 100, 1200, 900)  # Etwas höher für mehr Platz

        # Zentrales Widget mit vertikalem Layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Titel-Label
        """title_label = QLabel("Produktivitäts-Suite")
        title_font = QFont("Arial", 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)"""
        
        # Oberen Teil (ursprüngliches horizontales Split-Layout) erstellen
        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.addWidget(ProductivityTracker())  # Produktivitäts-Tracker
        
        # Todo-App-Widget erstellen
        todo_app = TodoApp()
        
        # Splitter-Verhältnis einstellen (50/50)
        top_splitter.addWidget(todo_app)
        top_splitter.setSizes([500, 500])
        
        # Trennlinie zwischen oberem und unterem Bereich
        separator = QLabel()
        separator.setStyleSheet("background-color: #cccccc; min-height: 2px; max-height: 2px;")
        
        # CSV-Visualisierung im unteren Bereich hinzufügen
        csv_widget = CsvVisualizer()
        
        # Elemente zum Layout hinzufügen
        main_layout.addWidget(top_splitter, 1)  # 2 = doppelte Gewichtung für den oberen Teil
        main_layout.addWidget(separator)
        main_layout.addWidget(csv_widget, 2)   # 1 = einfache Gewichtung für die Visualisierung
        
        # Datumsanzeige hinzufügen
        date_label = QLabel(f"Datum: {self.get_current_date()}")
        date_label.setAlignment(Qt.AlignRight)
        main_layout.addWidget(date_label)
        
        self.setCentralWidget(central_widget)
    
    def get_current_date(self):
        """Gibt das aktuelle Datum im deutschen Format zurück"""
        from datetime import datetime
        return datetime.now().strftime("%d.%m.%Y")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = CombinedApp()
    main_window.show()
    sys.exit(app.exec_())