#!/usr/bin/env python3
"""
Erweiterte Todo-Manager-Klasse mit Google Calendar Integration.
Dieses Skript erweitert die TodoApp-Klasse aus todo_manager.py
um Google Calendar-Funktionalitäten.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QPushButton, QHBoxLayout, QDialog, QVBoxLayout, QFormLayout, QLabel, QComboBox, QLineEdit, QDialogButtonBox
from PyQt5.QtCore import Qt
from todo_manager import TodoApp, load_todo, save_todo

# Ergänzungen für die Google Calendar-Integration
from google_calendar_integration import GoogleCalendarAPI
from calendar_todo_integration import import_calendar_events_to_todo

class CalendarImportDialog(QDialog):
    """Dialog zur Auswahl von Kalender und Zeitraum für den Import."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kalender importieren")
        self.setMinimumWidth(400)
        
        # Google Calendar API initialisieren
        self.api = GoogleCalendarAPI()
        self.calendars = []
        
        # Button-Stil vom Hauptfenster übernehmen, falls verfügbar
        button_style = ""
        if parent and hasattr(parent, 'button_style'):
            button_style = parent.button_style
        
        layout = QVBoxLayout()
        
        # Status-Label für Authentifizierung
        self.status_label = QLabel("Verbinde mit Google Calendar...")
        layout.addWidget(self.status_label)
        
        # Formular für Kalender- und Zeitraumauswahl
        form_layout = QFormLayout()
        
        # Kalenderauswahl
        self.calendar_dropdown = QComboBox()
        form_layout.addRow(QLabel("Kalender:"), self.calendar_dropdown)
        
        # Zeitraumauswahl
        self.days_input = QLineEdit("7")  # Standardwert: 7 Tage
        form_layout.addRow(QLabel("Tage in die Zukunft:"), self.days_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        if button_style:
            self.buttons.setStyleSheet(button_style)
            
        layout.addWidget(self.buttons)
        
        self.setLayout(layout)
        
        # Verbinde mit Google Calendar und lade verfügbare Kalender
        self.load_calendars()
    
    def load_calendars(self):
        """Lädt verfügbare Kalender von Google Calendar."""
        # Versuche, mit Google zu authentifizieren
        if not self.api.authenticate():
            self.status_label.setText("Fehler bei der Authentifizierung mit Google Calendar.")
            self.status_label.setStyleSheet("color: red;")
            return
        
        # Kalender laden
        self.calendars = self.api.get_calendars()
        
        if not self.calendars:
            self.status_label.setText("Keine Kalender gefunden.")
            self.status_label.setStyleSheet("color: red;")
            return
        
        # Kalender zum Dropdown hinzufügen
        self.calendar_dropdown.clear()
        for calendar in self.calendars:
            self.calendar_dropdown.addItem(calendar['summary'], calendar['id'])
        
        self.status_label.setText("Erfolgreich mit Google Calendar verbunden.")
        self.status_label.setStyleSheet("color: green;")
    
    def get_selected_calendar_id(self):
        """Gibt die ID des ausgewählten Kalenders zurück."""
        current_index = self.calendar_dropdown.currentIndex()
        if current_index >= 0 and current_index < len(self.calendars):
            return self.calendars[current_index]['id']
        return 'primary'  # Standardwert
    
    def get_days_ahead(self):
        """Gibt die Anzahl der Tage in die Zukunft zurück."""
        try:
            return int(self.days_input.text())
        except ValueError:
            return 7  # Standardwert

class TodoAppWithCalendar(TodoApp):
    """Erweiterte Todo-App mit Google Calendar-Integration."""
    
    def __init__(self):
        super().__init__()
        
        # Button zum Importieren von Kalenderterminen zum Layout hinzufügen
        # Wir suchen das vorhandene HBoxLayout für Buttons
        button_layout = None
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            if isinstance(item, QHBoxLayout):
                button_layout = item
                break
        
        if button_layout:
            # Button zum Importieren von Kalenderterminen
            self.import_calendar_button = QPushButton("Kalender importieren")
            self.import_calendar_button.setFixedSize(150, 40)
            self.import_calendar_button.clicked.connect(self.import_calendar)
            self.import_calendar_button.setStyleSheet(self.button_style)
            button_layout.addWidget(self.import_calendar_button)
        else:
            # Wenn kein passendes Layout gefunden wurde, erstellen wir ein neues
            button_layout = QHBoxLayout()
            
            # Button zum Importieren von Kalenderterminen
            self.import_calendar_button = QPushButton("Kalender importieren")
            self.import_calendar_button.setFixedSize(150, 40)
            self.import_calendar_button.clicked.connect(self.import_calendar)
            self.import_calendar_button.setStyleSheet(self.button_style)
            button_layout.addWidget(self.import_calendar_button)
            
            self.layout.addLayout(button_layout)
    
    def import_calendar(self):
        """Öffnet den Dialog zum Importieren von Kalenderterminen."""
        dialog = CalendarImportDialog(self)
        
        if dialog.exec_():
            calendar_id = dialog.get_selected_calendar_id()
            days_ahead = dialog.get_days_ahead()
            
            # Zeige Warte-Nachricht
            QMessageBox.information(
                self, 
                "Importiere Termine", 
                "Importiere Termine aus Google Calendar.\nDies kann einen Moment dauern."
            )
            
            # Termine importieren
            num_imported = import_calendar_events_to_todo(calendar_id, days_ahead)
            
            if num_imported > 0:
                QMessageBox.information(
                    self, 
                    "Kalender importiert", 
                    f"{num_imported} Termine wurden erfolgreich importiert."
                )
                # Daten neu laden
                self.load_data()
            else:
                QMessageBox.information(
                    self, 
                    "Kalender importiert", 
                    "Keine Termine zum Importieren gefunden."
                )

def main():
    """Hauptfunktion zum Starten der erweiterten Todo-App."""
    app = QApplication(sys.argv)
    window = TodoAppWithCalendar()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 