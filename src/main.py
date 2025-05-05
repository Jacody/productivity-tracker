import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Importiere die drei Programme
from tracker import MainApp  # Gesichtserkennung (Produktivitäts-Tracker)
from todo_manager_calendar import TodoAppWithCalendar  # Erweiterter To-Do-Manager mit Google Calendar
# Importiere die integrierte Visualisierung aus csv_reader
from csv_reader import CsvVisualizerCombined  # Integrierte CSV-Visualisierung

# Wrappen der MainApp als QWidget für Integration
class ProductivityTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.main_app = MainApp()  # Produktivitäts-Tracker GUI
        self.layout.addWidget(self.main_app)
        self.setLayout(self.layout)

# Haupt-App mit vertikalem Layout für alle drei Programme
class CombinedApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Productivity-Tracker")
        self.setGeometry(100, 100, 1100, 700)  # Etwas höher und breiter für mehr Platz

        # Zentrales Widget mit vertikalem Layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Oberen Teil (ursprüngliches horizontales Split-Layout) erstellen
        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.addWidget(ProductivityTracker())  # Produktivitäts-Tracker
        
        # Erweiterte Todo-App mit Google Calendar-Integration erstellen
        todo_app = TodoAppWithCalendar()
        
        # Splitter-Verhältnis einstellen (50/50)
        top_splitter.addWidget(todo_app)
        top_splitter.setSizes([500, 500])
        
        # Trennlinie zwischen oberem und unterem Bereich
        separator = QLabel()
        separator.setStyleSheet("background-color: #cccccc; min-height: 2px; max-height: 2px;")
        
        # Integrierte CSV-Visualisierung im unteren Bereich hinzufügen
        csv_widget = CsvVisualizerCombined()
        
        # Elemente zum Layout hinzufügen
        main_layout.addWidget(top_splitter, 2)  # 2 = doppelte Gewichtung für den oberen Teil
        main_layout.addWidget(separator)
        main_layout.addWidget(csv_widget, 3)   # 3 = dreifache Gewichtung für die Visualisierungen
        
        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = CombinedApp()
    main_window.show()
    sys.exit(app.exec_())