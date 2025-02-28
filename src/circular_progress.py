from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QRectF, QTimer

class CircularProgressWidget(QWidget):
    """
    Ein benutzerdefiniertes Widget, das einen kreisförmigen Fortschrittsbalken darstellt.
    Der Balken füllt sich wie ein Uhrzeiger, beginnend bei 12 Uhr und läuft im Uhrzeigersinn.
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
    
    def set_max_times(self, total_max, work_ratio=0.75):
        """Setzt die maximale Gesamtzeit und das Verhältnis für Arbeitszeit."""
        self.total_time_max = total_max
        self.work_time_ratio = work_ratio
        self.work_time_max = int(self.total_time_max * self.work_time_ratio)
        self.break_time_max = self.total_time_max - self.work_time_max
        self.update()
    
    def set_current_time(self, seconds):
        """Setzt die aktuelle Zeit in Sekunden."""
        self.current_time = min(seconds, self.total_time_max)
        self.update_display()
    
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
        """Malt das Widget mit dem kreisförmigen Fortschrittsbalken."""
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
        
        # Fortschrittskreis zeichnen
        pen_width = 25  # Dicke des Kreisbogens
        
        # Bestimme, ob wir in der Arbeits- oder Pausenzeit sind
        is_break_time = self.current_time > self.work_time_max
        
        # Arbeitszeit zeichnen (bis zu 3/4 des Kreises)
        if self.current_time > 0:
            # Zuerst die Arbeitszeit zeichnen (blau)
            work_time_to_draw = min(self.current_time, self.work_time_max)
            if work_time_to_draw > 0:
                painter.setPen(QPen(self.work_color, pen_width, Qt.SolidLine, Qt.RoundCap))
                # Startwinkel: 90 Grad (oben), nach rechts drehend (im Uhrzeigersinn)
                start_angle = 90 * 16
                # Spanwinkel: Wie viel vom Kreis abgedeckt wird (im Uhrzeigersinn, negativ)
                span_angle = -(work_time_to_draw / self.total_time_max * 360 * 16)
                
                rect = QRectF(center_x - radius + pen_width/2, center_y - radius + pen_width/2, 
                            diameter - pen_width, diameter - pen_width)
                painter.drawArc(rect, start_angle, span_angle)
            
            # Dann die Pausenzeit zeichnen (rot), wenn wir bereits in der Pausenzeit sind
            if is_break_time:
                painter.setPen(QPen(self.break_color, pen_width, Qt.SolidLine, Qt.RoundCap))
                # Startwinkel: 90 - (3/4 * 360) = -180 Grad (bei 9 Uhr Position)
                start_angle = int(90 - (self.work_time_ratio * 360)) * 16
                # Spanwinkel für die Pausenzeit
                break_time = self.current_time - self.work_time_max
                span_angle = -(break_time / self.total_time_max * 360 * 16)
                
                rect = QRectF(center_x - radius + pen_width/2, center_y - radius + pen_width/2, 
                            diameter - pen_width, diameter - pen_width)
                painter.drawArc(rect, start_angle, span_angle)
        
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
        self._test_seconds += 5  # 5 Sekunden pro Tick für eine schnellere Animation
        
        # Animation für die gesamte Zeit (Arbeits- und Pausenzeit)
        self.set_current_time(self._test_seconds)
        
        # Animation nach einem kompletten Zyklus neustarten
        if self._test_seconds >= self.total_time_max:
            self._test_seconds = 0