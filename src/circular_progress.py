from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush
from PyQt5.QtCore import Qt, QRectF, QTimer, QPointF
import pygame
import os

class CircularProgressWidget(QWidget):
    """
    Ein benutzerdefiniertes Widget, das einen kreisförmigen Fortschrittsbalken darstellt.
    Der Balken füllt sich wie ein Tortendiagramm, beginnend bei 12 Uhr und läuft im Uhrzeigersinn.
    Nach 3/4 des Kreises wechselt die Farbe von Blau zu Rot, um die Pausenzeit zu signalisieren.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Dimensionen festlegen
        self.setMinimumSize(300, 300)
        
        # Standardwerte
        self.total_time_max = 60 * 60  # 60 Minuten in Sekunden
        self.work_time_ratio = 0.75     # 3/4 der Gesamtzeit ist Arbeitszeit
        self.work_time_max = int(self.total_time_max * self.work_time_ratio)  # 45 Minuten
        self.break_time_max = self.total_time_max - self.work_time_max       # 15 Minuten
        self.current_time = 0           # Aktuelle Zeit in Sekunden
        
        # Farben
        self.work_color = QColor(74, 134, 232)    # Blau (#4A86E8)
        self.break_color = QColor(230, 124, 115)  # Rot (#E67C73)
        self.bg_color = QColor(240, 240, 240)     # Hellgrau
        
        # Aktuelle Zeit als Text
        self.time_text = "00:00"
        
        # Timer für Test-Animation
        self._test_timer = None
        
        # Sound-Initialisierung
        pygame.mixer.init()
        
        # Pfade zu den Sound-Dateien
        self.sound_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sounds')
        self.start_sound_path = os.path.join(self.sound_dir, 'start.wav')
        self.end_sound_path = os.path.join(self.sound_dir, 'end.wav')
        
        # Flag für den ersten Programmstart
        self._first_time_set = True
        
        # Flag, ob Sounds abgespielt werden sollen
        self.play_sounds = True
    
    def set_max_times(self, total_max, work_ratio=0.75):
        """Setzt die maximale Gesamtzeit und das Verhältnis für Arbeitszeit."""
        self.total_time_max = total_max
        self.work_time_ratio = work_ratio
        self.work_time_max = int(self.total_time_max * self.work_time_ratio)
        self.break_time_max = self.total_time_max - self.work_time_max
        self.update()
    
    def explicit_start(self):
        """Wird aufgerufen, wenn der Timer explizit gestartet wird, und spielt den Start-Sound ab."""
        # Start-Sound abgespielt beim Statuswechsel zu "Working" deaktiviert
        # Kommentar: Start-Sound-Wiedergabe wurde hier deaktiviert, da sie beim Statuswechsel zu "Working" nicht erwünscht ist
        pass
    
    def set_current_time(self, seconds):
        """Setzt die aktuelle Zeit in Sekunden."""
        previous_time = self.current_time
        self.current_time = min(seconds, self.total_time_max)
        
        # Spiele End-Sound, wenn Arbeitszeit gerade erreicht wurde, aber nicht beim ersten Programmstart
        if previous_time < self.work_time_max and self.current_time >= self.work_time_max and not self._first_time_set and self.play_sounds:
            self.play_end_sound()
        
        # Flag nach dem ersten Aufruf zurücksetzen
        if self._first_time_set:
            self._first_time_set = False
        
        self.update_display()
    
    def play_start_sound(self):
        """Spielt den Start-Sound ab."""
        try:
            # Sound-Objekt jedes Mal neu erstellen, um Probleme mit der Wiederverwendung zu vermeiden
            sound = pygame.mixer.Sound(self.start_sound_path)
            sound.play()
        except Exception as e:
            print(f"Fehler beim Abspielen des Start-Sounds: {e}")
    
    def play_end_sound(self):
        """Spielt den End-Sound ab."""
        try:
            # Sound-Objekt jedes Mal neu erstellen, um Probleme mit der Wiederverwendung zu vermeiden
            sound = pygame.mixer.Sound(self.end_sound_path)
            sound.play()
        except Exception as e:
            print(f"Fehler beim Abspielen des End-Sounds: {e}")
    
    def update_display(self):
        """Aktualisiert die Anzeige basierend auf der aktuellen Zeit."""
        # Bestimme, ob wir in der Arbeits- oder Pausenzeit sind
        is_break_time = self.current_time > self.work_time_max
        
        # Setze den Zeittext
        if is_break_time:
            # Zeige verbleibende Pausenzeit an
            pause_seconds = self.current_time - self.work_time_max
            minutes = pause_seconds // 60
            seconds = pause_seconds % 60
        else:
            # Zeige aktuelle Arbeitszeit an
            minutes = self.current_time // 60
            seconds = self.current_time % 60
        
        self.time_text = f"{minutes:02}:{seconds:02}"
        self.update()
    
    def paintEvent(self, event):
        """Malt das Widget mit dem kreisförmigen Fortschrittsbalken als Tortendiagramm."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Zentrum und Radius bestimmen
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        diameter = min(width, height) - 40  # Margin
        radius = diameter / 2
        
        # Hintergrundkreis zeichnen
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.bg_color)
        painter.drawEllipse(QRectF(center_x - radius, center_y - radius, diameter, diameter))
        
        # Bestimme, ob wir in der Arbeits- oder Pausenzeit sind
        is_break_time = self.current_time > self.work_time_max
        
        if self.current_time > 0:
            # Kreisausschnitt für die Arbeitszeit zeichnen
            work_time_to_draw = min(self.current_time, self.work_time_max)
            if work_time_to_draw > 0:
                # Winkel berechnen (in Grad)
                angle = work_time_to_draw / self.total_time_max * 360
                
                # Zeichnen des Kreisausschnitts
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(self.work_color))
                self.drawPieSlice(painter, center_x, center_y, radius, 90, -angle)
            
            # Kreisausschnitt für die Pausenzeit zeichnen
            if is_break_time:
                break_time = self.current_time - self.work_time_max
                break_angle = break_time / self.total_time_max * 360
                work_angle = self.work_time_max / self.total_time_max * 360
                
                # Zeichnen des Pausenzeit-Kreisausschnitts
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(self.break_color))
                self.drawPieSlice(painter, center_x, center_y, radius, 90 - work_angle, -break_angle)
        
        # Inneren weißen Kreis zeichnen (für ein "Donut"-Erscheinungsbild)
        inner_radius = radius * 0.7  # 70% des äußeren Radius
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.white))
        painter.drawEllipse(QRectF(center_x - inner_radius, center_y - inner_radius, inner_radius * 2, inner_radius * 2))
        
        # Zeittext zeichnen
        painter.setPen(Qt.black)
        font = QFont("Arial", 24, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(0, 0, width, height), Qt.AlignCenter, self.time_text)
        
        # Status-Text zeichnen (Arbeit oder Pause)
        status_text = "PAUSE" if is_break_time else "ARBEIT"
        status_color = self.break_color if is_break_time else self.work_color
        painter.setPen(status_color)
        font = QFont("Arial", 14, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(0, height/2 + 30, width, 30), Qt.AlignCenter, status_text)
    
    def drawPieSlice(self, painter, center_x, center_y, radius, start_angle, span_angle):
        """
        Zeichnet einen Kreisausschnitt (Pie Slice) mit dem angegebenen Mittelpunkt,
        Radius, Startwinkel und Spanwinkel.
        
        :param painter: QPainter-Objekt
        :param center_x: x-Koordinate des Mittelpunkts
        :param center_y: y-Koordinate des Mittelpunkts
        :param radius: Radius des Kreises
        :param start_angle: Startwinkel in Grad (0 = rechts, 90 = oben)
        :param span_angle: Spanwinkel in Grad (positiv = gegen den Uhrzeigersinn)
        """
        # Den Tortenausschnitt direkt mit drawPie zeichnen
        rect = QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)
        painter.drawPie(rect, int(start_angle * 16), int(span_angle * 16))
    
    def start_test_animation(self):
        """Startet eine Test-Animation (nur für Demonstrationszwecke)."""
        if self._test_timer is None:
            self._test_seconds = 0
            self._test_timer = QTimer(self)
            self._test_timer.timeout.connect(self._update_test_animation)
            self._test_timer.start(50)  # 50ms für schnellere Animation
    
    def stop_test_animation(self):
        """Stoppt die Test-Animation."""
        if self._test_timer is not None:
            self._test_timer.stop()
            self._test_timer = None
    
    def _update_test_animation(self):
        """Aktualisiert die Test-Animation."""
        previous_seconds = self._test_seconds
        self._test_seconds += 5  # 5 Sekunden pro Tick für eine schnellere Animation
        
        # Animation für die gesamte Zeit (Arbeits- und Pausenzeit)
        self.set_current_time(self._test_seconds)
        
        # Animation nach einem kompletten Zyklus neustarten
        if self._test_seconds >= self.total_time_max:
            self._test_seconds = 0
            # Start-Sound beim Neustart der Animation abspielen
            if self.play_sounds:
                self.play_start_sound()