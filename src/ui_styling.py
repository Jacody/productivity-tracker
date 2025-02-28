"""
UI-Styling für die Produktivitäts-Suite
Diese Datei enthält Stylesheets und UI-Komponenten für das Styling der Anwendung.
"""

# Stylesheet-Definitionen

# Basis-Stylesheet für die gesamte Anwendung
MAIN_STYLESHEET = """
QWidget {
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 10pt;
    color: #333333;
}

QMainWindow {
    background-color: #f5f5f5;
}

QLabel {
    padding: 2px;
}

QPushButton {
    background-color: #4a86e8;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #3a76d8;
}

QPushButton:pressed {
    background-color: #2a66c8;
}

QPushButton:disabled {
    background-color: #cccccc;
    color: #888888;
}

QProgressBar {
    border: 1px solid #cccccc;
    border-radius: 4px;
    text-align: center;
    background-color: #f0f0f0;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #4a86e8;
    border-radius: 3px;
}

QTableWidget {
    border: 1px solid #dddddd;
    gridline-color: #eeeeee;
    background-color: white;
    selection-background-color: #e0e8f5;
    selection-color: #333333;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget QHeaderView::section {
    background-color: #f0f0f0;
    padding: 6px;
    font-weight: bold;
    border: 1px solid #dddddd;
    border-left: none;
    border-top: none;
}

QSplitter::handle {
    background-color: #dddddd;
    height: 2px;
    width: 2px;
}

QSplitter::handle:horizontal {
    width: 4px;
}

QSplitter::handle:vertical {
    height: 4px;
}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 6px;
    background-color: white;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #4a86e8;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 15px;
    border-left-width: 1px;
    border-left-color: #cccccc;
    border-left-style: solid;
}
"""

# Spezifisches Stylesheet für den Tracker
TRACKER_STYLESHEET = """
/* Tracker-Komponente */
#trackerWidget {
    background-color: white;
    border: 1px solid #dddddd;
    border-radius: 6px;
    padding: 10px;
}

#blockLabel {
    font-size: 16pt;
    font-weight: bold;
    color: #4a86e8;
}

#timerLabel {
    font-size: 24pt;
    font-weight: bold;
    color: #333333;
}

#breakTimerLabel {
    font-size: 14pt;
    color: #e67c73;
}

#statusLabel {
    font-weight: bold;
}

/* Spezielle Styles für Fortschrittsbalken */
#workProgressBar::chunk {
    background-color: #4a86e8;
}

#breakProgressBar::chunk {
    background-color: #e67c73;
}
"""

# Spezifisches Stylesheet für den Todo-Manager
TODO_STYLESHEET = """
/* Todo-Manager-Komponente */
#todoWidget {
    background-color: white;
    border: 1px solid #dddddd;
    border-radius: 6px;
    padding: 10px;
}

#currentTaskDisplay {
    font-size: 12pt;
    padding: 8px;
    background-color: #f8f9fa;
    border-radius: 4px;
    border-left: 4px solid #4a86e8;
}

/* Unterschiedliche Farben für Status */
.status-pending {
    background-color: #f5f5f5;
}

.status-in-progress {
    background-color: #fff7d1;
}

.status-completed {
    background-color: #d9ead3;
}

/* Spezielle Buttons */
#addTaskButton {
    background-color: #4a86e8;
}

#addSubtaskButton {
    background-color: #7baaf7;
}

#deleteButton {
    background-color: #e67c73;
}

#changeStatusButton {
    background-color: #f6b26b;
    color: #333333;
}

#updateTimeButton {
    background-color: #93c47d;
}
"""

# Spezifisches Stylesheet für die CSV-Visualisierung
CSV_STYLESHEET = """
/* CSV-Visualisierungs-Komponente */
#csvWidget {
    background-color: white;
    border: 1px solid #dddddd;
    border-radius: 6px;
    padding: 10px;
}

#chartTitle {
    font-size: 14pt;
    font-weight: bold;
    color: #4a86e8;
}

#infoLabel {
    font-weight: bold;
    color: #333333;
}

#lastUpdateLabel {
    font-style: italic;
    color: #777777;
}
"""


# Hilfsfunktionen für einheitliche UI-Komponenten

def create_title_label(text):
    """Erstellt ein einheitlich gestyltes Titel-Label"""
    from PyQt5.QtWidgets import QLabel
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    
    label = QLabel(text)
    label.setAlignment(Qt.AlignCenter)
    font = QFont("Segoe UI", 14)
    font.setBold(True)
    label.setFont(font)
    label.setStyleSheet("color: #4a86e8; margin: 5px 0;")
    return label

def create_section_title(text):
    """Erstellt ein einheitlich gestyltes Abschnitt-Label"""
    from PyQt5.QtWidgets import QLabel
    from PyQt5.QtGui import QFont
    
    label = QLabel(text)
    font = QFont("Segoe UI", 12)
    font.setBold(True)
    label.setFont(font)
    label.setStyleSheet("color: #333333; margin-top: 10px; margin-bottom: 5px;")
    return label

def create_info_box(title, content):
    """Erstellt ein Box-Widget mit Titel und Inhalt"""
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    
    box = QWidget()
    box.setStyleSheet("""
        background-color: #f8f9fa;
        border: 1px solid #dddddd;
        border-radius: 4px;
        padding: 8px;
    """)
    
    layout = QVBoxLayout(box)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(4)
    
    title_label = QLabel(title)
    title_font = QFont("Segoe UI", 10)
    title_font.setBold(True)
    title_label.setFont(title_font)
    title_label.setStyleSheet("color: #4a86e8;")
    
    content_label = QLabel(content)
    content_label.setStyleSheet("color: #333333;")
    content_label.setWordWrap(True)
    
    layout.addWidget(title_label)
    layout.addWidget(content_label)
    
    return box