import sys
import todo_manager
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer
from face_detection import FaceDetectorApp
from csv_logger import CSVLogger  # Importiere den Logger
from circular_progress import CircularProgressWidget  # Importiere den kreisförmigen Fortschrittsbalken


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Detection Launcher")
        self.setGeometry(200, 200, 500, 600)  # Etwas größer für die kreisförmigen Widgets

        # Layout erstellen
        layout = QVBoxLayout
        
        self.blocktime = timedelta(seconds=45*60)  # 45 Minuten Arbeitszeit pro Block
        self.breaktime = timedelta(seconds=15*60)   # 15 Minuten Pausenzeit
        self.block = 1                          # Aktueller Blockzähler
        self.work = 1                           # Pausenstatus
        
        # Kreisförmiger Fortschrittsbalken für Arbeitszeit hinzufügen
        self.progress_circle = CircularProgressWidget(self)
        self.progress_circle.set_max_times(
            total_max=int(self.blocktime.total_seconds() + self.breaktime.total_seconds()),
            work_ratio=self.blocktime.total_seconds() / (self.blocktime.total_seconds() + self.breaktime.total_seconds())
        )
        self.progress_circle.set_current_time(0)  # Anfangswert
        
        # "Start"-Button
        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_face_detection)

        # "Hold"-Button
        self.hold_button = QPushButton("Pause", self)
        self.hold_button.setStyleSheet("background-color: none;")
        self.hold_button.clicked.connect(self.toggle_hold_mode)

        # "End"-Button
        self.end_button = QPushButton("End", self)
        self.end_button.setStyleSheet("background-color: none;")  
        self.end_button.clicked.connect(self.close_application)
        
        # Hole die aktuelle Task-Informationen
        latest_task = todo_manager.get_latest_in_progress()
        
        layout = QVBoxLayout()

        # Label für Status-Anzeige
        self.status_label = QLabel("Status: Not started yet", self)
        
        # Die Zeit-Labels werden nicht mehr benötigt, da sie im CircularProgressWidget angezeigt werden
        
        # Breaktimer Settings
        self.break_timer = QTimer(self)
        self.break_timer.timeout.connect(self.update_break_timer)
        self.break_seconds_elapsed = 0

        # Kreisförmigen Fortschrittsbalken dem Layout hinzufügen
        layout.addWidget(self.progress_circle)
        
        # Horizontal Layout für die Buttons
        button_layout = QHBoxLayout()
        
        # macOS-Stil für Buttons
        button_style = """
            QPushButton {
                background-color: #f2f2f2;
                border: 1px solid #d1d1d1;
                border-radius: 5px;
                color: #333333;
                padding: 5px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #d9d9d9;
            }
        """
        
        # Feste Button-Größe definieren
        button_size = (120, 30)
        
        self.start_button.setFixedSize(*button_size)
        self.start_button.setStyleSheet(button_style)
        
        self.hold_button.setFixedSize(*button_size)
        self.hold_button.setStyleSheet(button_style)
        
        self.end_button.setFixedSize(*button_size)
        self.end_button.setStyleSheet(button_style)
        
        # Button Layout mit Abständen wie im macOS-Stil
        button_layout.addStretch(1)  # Platz links hinzufügen
        button_layout.addWidget(self.start_button)
        button_layout.addSpacing(10)  # Abstand zwischen Buttons
        button_layout.addWidget(self.hold_button)
        button_layout.addSpacing(10)  # Abstand zwischen Buttons
        button_layout.addWidget(self.end_button)
        button_layout.addStretch(1)  # Platz rechts hinzufügen
        
        layout.addLayout(button_layout)
        
        # Status-Information (zentriert)
        status_layout = QHBoxLayout()
        status_layout.addStretch(1)  # Fügt Abstand ein, um Status-Label zu zentrieren
        status_layout.addWidget(self.status_label)
        status_layout.addStretch(1)  # Fügt Abstand ein, um Status-Label zu zentrieren
        layout.addLayout(status_layout)

        self.setLayout(layout)

        self.face_detector_window = None
        self.start_time = None
        self.mode = 1  
        self.status = 0  

        # Timer zur Aktualisierung der GUI-Zeit
        self.active_time = timedelta(seconds=0)
        self.last_timer_start = None
        self.gui_timer = QTimer()
        self.gui_timer.timeout.connect(self.update_timer_label)
        self.gui_timer.start(1000)
        # Beim ersten Start kein Sound abspielen, da noch keine Arbeit begonnen hat

        # Timer zur Aktualisierung der Pausenzeit (Break Timer)
        self.break_timer = QTimer(self)
        self.break_timer.timeout.connect(self.update_break_timer)

        # CSV-Logger initialisieren
        self.logger = CSVLogger()

    def close_application(self):
        """Beendet die Anwendung komplett."""
        print("❌ Anwendung wird geschlossen...")
        
        # Hole die aktuelle Task-Informationen für den Log
        latest_task = todo_manager.get_latest_in_progress()
        
        self.logger.log(0, 0, 0, self.block, latest_task[0], latest_task[1], self.get_total_time_str())  # Letzter Log-Eintrag
        QApplication.quit()  # Beendet das PyQt5-Fenster
        sys.exit()  # Beendet das ganze Programm

    def start_face_detection(self):
        """Startet die Gesichtserkennung und speichert die Startzeit."""
        if not self.face_detector_window:
            self.start_time = datetime.now()
            
            # Start-Sound abspielen, wenn die Gesichtserkennung (und damit die Arbeit) beginnt
            # HINWEIS: Der Startsound wird hier beim Start der Gesichtserkennung abgespielt
            self.progress_circle.explicit_start()
            
            # Hole die aktuelle Task-Informationen für den Log
            latest_task = todo_manager.get_latest_in_progress()
            
            log_message = self.get_log_message()
            print(log_message)
            self.logger.log(self.mode, self.status, self.work, self.block, latest_task[0], latest_task[1], self.get_total_time_str())

            self.face_detector_window = FaceDetectorApp()
            self.face_detector_window.status_changed.connect(self.update_status)
            self.face_detector_window.show()
            self.update_labels()

    def toggle_hold_mode(self):
        """Schaltet den Hold-Modus an/aus"""
        self.mode = 0 if self.mode == 1 else 1
        
        # macOS-Stil für Buttons
        button_style = """
            QPushButton {
                background-color: #f2f2f2;
                border: 1px solid #d1d1d1;
                border-radius: 5px;
                color: #333333;
                padding: 5px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #d9d9d9;
            }
        """
        
        hold_button_style_active = """
            QPushButton {
                background-color: #e03131;
                border: 1px solid #c92a2a;
                border-radius: 5px;
                color: white;
                padding: 5px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #c92a2a;
            }
            QPushButton:pressed {
                background-color: #b42525;
            }
        """
        
        self.hold_button.setStyleSheet(hold_button_style_active if self.mode == 0 else button_style)

        # Hole die aktuelle Task-Informationen für den Log
        latest_task = todo_manager.get_latest_in_progress()
        
        log_message = self.get_log_message()
        print(log_message)
        self.logger.log(self.mode, self.status, self.work, self.block, latest_task[0], latest_task[1], self.get_total_time_str())
        self.update_timer_label()

    def update_timer_label(self):
        """Aktualisiert die Timer-Anzeige und den Fortschrittsbalken in der GUI."""
        # Statische Variable, um zu verfolgen, ob wir uns im Arbeitsmodus befinden
        if not hasattr(self, '_was_in_work_mode'):
            self._was_in_work_mode = False
            self._program_just_started = True  # Flag für ersten Programmstart
        
        # Erkennen, ob wir gerade in den Arbeitsmodus gewechselt haben
        current_in_work_mode = (self.status == 1 and self.mode == 1 and self.work == 1)
        
        # Sound nur abspielen, wenn es nicht der erste Programmstart ist
        if current_in_work_mode and not self._was_in_work_mode and not self._program_just_started:
            # Wir sind gerade in den Arbeitsmodus gewechselt - Sound abspielen
            self.progress_circle.explicit_start()
        
        # Das Flag nach der ersten Ausführung zurücksetzen
        self._program_just_started = False
        self._was_in_work_mode = current_in_work_mode
        
        time_str = self.get_total_time_str()
        if len(time_str.split(':')) == 3:
            time_str = ':'.join(time_str.split(':')[1:])  # Entfernt die Stunden
        # Kein Timer-Label mehr zu aktualisieren, da es im CircularProgressWidget angezeigt wird

        # Berechne den Fortschritt als Verhältnis
        total_seconds = self.get_total_time().total_seconds()
        max_seconds = self.blocktime.total_seconds()

        # Aktualisiere den kreisförmigen Fortschrittsbalken
        if self.work == 1:  # Arbeitszeit
            self.progress_circle.set_current_time(int(total_seconds))
        
        # Prüfe, ob die Arbeitszeit vorbei ist
        if total_seconds >= max_seconds:
            self.block += 1  # Block hochzählen
            self.active_time = timedelta(seconds=0)  # Total Time zurücksetzen
            self.last_timer_start = None
            self.work = 0  # Wechsel zu Pause
            self.break_seconds_elapsed = 0  # Break-Timer zurücksetzen
            self.gui_timer.stop()  # Arbeits-Timer stoppen
            self.break_timer.start(1000)  # Break-Timer starten!
            self.update_labels()  # Aktualisiert die Labels
            # Timer-Anzeige wird jetzt im CircularProgressWidget angezeigt
            
            # Hole die aktuelle Task-Informationen für den Log
            latest_task = todo_manager.get_latest_in_progress()
            
            log_message = self.get_log_message()
            print(log_message)
            self.logger.log(self.mode, self.status, self.work, self.block, latest_task[0], latest_task[1], self.get_total_time_str())

    def update_break_timer(self):
        """Break-Timer zählt hoch, wenn work = 0, und aktualisiert den kreisförmigen Fortschrittsbalken."""
        if self.work == 0:
            self.break_seconds_elapsed += 1  # Sekunde hinzufügen
            minutes = self.break_seconds_elapsed // 60
            seconds = self.break_seconds_elapsed % 60
            # Pausenzeit wird jetzt im CircularProgressWidget angezeigt

            # Kreisförmigen Fortschrittsbalken für Pause aktualisieren
            work_seconds = self.blocktime.total_seconds()
            self.progress_circle.set_current_time(int(work_seconds + self.break_seconds_elapsed))

            # Prüfen, ob die Pause vorbei ist
            if self.break_seconds_elapsed >= self.breaktime.total_seconds():
                self.work = 1  # Wechsel zurück zu Work
                self.break_timer.stop()  # Break-Timer stoppen
                self.break_seconds_elapsed = 0  # Break-Timer zurücksetzen
                # Pausenzeit wird jetzt im CircularProgressWidget angezeigt
                self.progress_circle.set_current_time(0)  # Fortschrittsbalken zurücksetzen
                # HINWEIS: Der Startsound wird hier nach Ende einer Pause abgespielt
                self.progress_circle.explicit_start()  # Start-Sound abspielen
                self.gui_timer.start(1000)  # Arbeitszeit-Timer erneut starten!
                self.update_labels()  # Labels aktualisieren
                
                # Hole die aktuelle Task-Informationen für den Log
                latest_task = todo_manager.get_latest_in_progress()
                
                log_message = self.get_log_message()
                print(log_message)
                self.logger.log(self.mode, self.status, self.work, self.block, latest_task[0], latest_task[1], self.get_total_time_str())

    def update_status(self, status):
        """Aktualisiert den Status"""
        previous_status = self.status
        self.status = status
        status_text = "✅ Working" if status == 1 else "❌ Not Working"
        self.status_label.setText(f"Status: {status_text}")
        
        # Zeitberechnung
        if status == 1 and self.mode == 1 and self.work == 1:
            # Beginn einer aktiven Periode
            self.last_timer_start = datetime.now()
        
        # Hole die aktuelle Task-Informationen für den Log
        latest_task = todo_manager.get_latest_in_progress()
        
        log_message = self.get_log_message()
        print(log_message)
        self.logger.log(self.mode, self.status, self.work, self.block, latest_task[0], latest_task[1], self.get_total_time_str())
        self.update_timer_label()
        
    def update_labels(self):
        """Aktualisiert die Labels"""
        # Block-Anzeige wurde entfernt, hier ist nichts mehr zu aktualisieren
        pass

    def get_total_time(self):
        """Berechnet die gesamte vergangene Zeit (total_time)"""
        if self.status == 1 and self.mode == 1 and self.work == 1:  
            if self.last_timer_start is None:
                self.last_timer_start = datetime.now()
            elapsed_time = datetime.now() - self.last_timer_start
            return self.active_time + elapsed_time
        else:
            if self.last_timer_start is not None:
                self.active_time += datetime.now() - self.last_timer_start
                self.last_timer_start = None
            return self.active_time  

    def get_total_time_str(self):
        """Gibt die aktuelle Gesamtzeit als String HH:MM:SS zurück"""
        return str(self.get_total_time()).split('.')[0]

    def get_log_message(self):
        """Erzeugt die Log-Nachricht für print und CSV"""
        # Hole die aktuelle Task-Informationen
        latest_task = todo_manager.get_latest_in_progress()
        
        return f"Mode= {self.mode} Status= {self.status} Work= {self.work} Block = {self.block} Task = {latest_task[0]} Subtask = {latest_task[1]} Timer= {self.get_total_time_str()} Est.Time= {latest_task[2]} Act.Time= {latest_task[3]} Time= {datetime.now().strftime('%H:%M:%S')}"