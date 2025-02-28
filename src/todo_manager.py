import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, 
    QHeaderView, QDialog, QLineEdit, QComboBox, QLabel, QFormLayout, QDialogButtonBox, 
    QDoubleSpinBox
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

latest_in_progress = ('Relax', 'Slay', '0', '0')  # (Task, Subtask, Estimated Time, Actual Time)

def get_latest_in_progress():
    """Getter für die globale Variable"""
    return latest_in_progress

# Basisverzeichnis bestimmen (geht eine Ebene nach oben)
base_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
todo_path = os.path.join(base_dir, "data", "todo.json")

# Datei einlesen
def load_todo():
    if os.path.exists(todo_path):
        with open(todo_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return {"tasks": []}  # Falls keine Datei existiert, leere Struktur zurückgeben

# Datei speichern
def save_todo(data):
    os.makedirs(os.path.dirname(todo_path), exist_ok=True)
    with open(todo_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
        
# Dialog für neuen Task
class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Neuen Task hinzufügen")
        layout = QFormLayout()
        
        self.task_input = QLineEdit()
        self.type_dropdown = QComboBox()
        self.type_dropdown.addItems(["Digital", "Analog"])
        self.category_dropdown = QComboBox()
        self.category_dropdown.addItems(["Hacken", "Hustle", "Health", "Hobby"])
        self.estimated_time_input = QLineEdit()

        layout.addRow(QLabel("Task Name:"), self.task_input)
        layout.addRow(QLabel("Type:"), self.type_dropdown)
        layout.addRow(QLabel("Category:"), self.category_dropdown)
        layout.addRow(QLabel("Estimated Time (in hours):"), self.estimated_time_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

# Dialog für neuen Subtask
class AddSubtaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Subtask hinzufügen")
        layout = QFormLayout()
        
        self.task_dropdown = QComboBox()
        self.populate_tasks()
        self.subtask_input = QLineEdit()
        self.status_dropdown = QComboBox()
        self.status_dropdown.addItems(["Pending", "In Progress", "Completed"])
        self.estimated_time_input = QLineEdit()
        
        layout.addRow(QLabel("Task:"), self.task_dropdown)
        layout.addRow(QLabel("Subtask:"), self.subtask_input)
        layout.addRow(QLabel("Status:"), self.status_dropdown)
        layout.addRow(QLabel("Estimated Time (in minutes):"), self.estimated_time_input)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
        self.setLayout(layout)
    
    def populate_tasks(self):
        data = load_todo()
        self.task_dropdown.clear()
        tasks = [task["task"] for task in data.get("tasks", [])]
        self.task_dropdown.addItems(tasks)

# Dialog zum Aktualisieren der tatsächlichen Zeit
class UpdateActualTimeDialog(QDialog):
    def __init__(self, task_name, subtask_name, current_time, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tatsächliche Zeit aktualisieren")
        self.setMinimumWidth(300)
        layout = QFormLayout()
        
        self.task_label = QLabel(task_name)
        self.subtask_label = QLabel(subtask_name)
        
        # Spinner für die tatsächliche Zeit mit Dezimalstellen
        self.actual_time_input = QDoubleSpinBox()
        self.actual_time_input.setRange(0, 1000)  # 0 bis 1000 Stunden
        self.actual_time_input.setDecimals(2)     # Zwei Dezimalstellen
        self.actual_time_input.setSingleStep(0.25)  # 15-Minuten-Schritte (0.25 Stunden)
        
        # Aktuellen Wert einstellen
        try:
            self.actual_time_input.setValue(float(current_time))
        except (ValueError, TypeError):
            self.actual_time_input.setValue(0.0)
        
        layout.addRow(QLabel("Task:"), self.task_label)
        layout.addRow(QLabel("Subtask:"), self.subtask_label)
        layout.addRow(QLabel("Tatsächliche Zeit (Stunden):"), self.actual_time_input)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
        self.setLayout(layout)
    
    def get_actual_time(self):
        """Gibt die eingegebene tatsächliche Zeit zurück"""
        return str(self.actual_time_input.value())

# GUI-Klasse mit QTableWidget
class TodoApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Todo Manager")
        self.setGeometry(100, 100, 850, 450)  # Breitere Tabelle für neue Spalten

        # Hauptlayout als vertikales Layout definieren
        self.layout = QVBoxLayout()

        # Tabelle erstellen
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # 5 Spalten: Task, Subtask, Status, Est. Time, Actual Time
        self.table.setHorizontalHeaderLabels(["Task", "Subtask", "Status", "Est. Time", "Actual Time"])
        self.table.verticalHeader().setVisible(False)
        
        # Spaltenbreiten
        self.table.setColumnWidth(0, 200)  # Task
        self.table.setColumnWidth(1, 200)  # Subtask
        self.table.setColumnWidth(2, 100)  # Status
        self.table.setColumnWidth(3, 100)  # Est. Time
        self.table.setColumnWidth(4, 100)  # Actual Time
        
        self.layout.addWidget(self.table)
        
        # Feld für die Anzeige des aktuellen Tasks
        self.current_task_display = QLabel("")  # Startet leer
        self.current_task_display.setStyleSheet("font-size: 14px; font-weight: normal; padding: 0px; border: 0px solid gray;")
        self.layout.addWidget(self.current_task_display)
                
        # Horizontales Layout für Buttons
        button_layout = QHBoxLayout()
        
        # Button zum Ändern des Status von Subtasks
        self.change_status_button = QPushButton("Change Status")  
        self.change_status_button.setFixedSize(150, 40)
        self.change_status_button.clicked.connect(self.change_status)  
        button_layout.addWidget(self.change_status_button)  

        # Button zum Hinzufügen von Subtasks
        self.add_button = QPushButton("Subtask hinzufügen")
        self.add_button.setFixedSize(150, 40)
        self.add_button.clicked.connect(self.add_subtask)
        button_layout.addWidget(self.add_button)
        
        # Button zum Löschen von Subtasks
        self.delete_button = QPushButton("Subtask löschen")
        self.delete_button.setFixedSize(150, 40)
        self.delete_button.clicked.connect(self.delete_subtask)
        button_layout.addWidget(self.delete_button)
        
        # Button zum Hinzufügen eines Tasks
        self.add_task_button = QPushButton("Task hinzufügen")
        self.add_task_button.setFixedSize(150, 40)
        self.add_task_button.clicked.connect(self.add_task)
        button_layout.addWidget(self.add_task_button)
        
        # Neuer Button zum Aktualisieren der tatsächlichen Zeit
        self.update_time_button = QPushButton("Zeiten aktualisieren")
        self.update_time_button.setFixedSize(150, 40)
        self.update_time_button.clicked.connect(self.update_actual_time)
        button_layout.addWidget(self.update_time_button)

        # Button-Layout dem Hauptlayout hinzufügen
        self.layout.addLayout(button_layout)

        self.setLayout(self.layout) 
        self.load_data()

    def load_data(self):
        global latest_in_progress  # Zugriff auf die globale Variable
        data = load_todo()
        tasks = data.get("tasks", [])
    
        # Tabelle leeren
        self.table.setRowCount(0)
    
        row_count = sum(len(task["subtasks"]) for task in tasks)
        self.table.setRowCount(row_count)
    
        row = 0
        for task in tasks:
            task_name = task["task"]
            subtasks = task["subtasks"]
            task_span = len(subtasks)
    
            for i, subtask in enumerate(subtasks):
                if i == 0:
                    self.table.setItem(row, 0, QTableWidgetItem(task_name))
                    self.table.item(row, 0).setTextAlignment(Qt.AlignTop)
                    if task_span > 1:
                        self.table.setSpan(row, 0, task_span, 1)
    
                # Subtask Name
                self.table.setItem(row, 1, QTableWidgetItem(subtask["subtask"]))
                
                # Status
                status_item = QTableWidgetItem(subtask["status"])
                status_item.setTextAlignment(Qt.AlignCenter)
                
                if subtask["status"] == "Completed":
                    status_item.setBackground(QColor(144, 238, 144))  # Grün für erledigt
                elif subtask["status"] == "In Progress":
                    status_item.setBackground(QColor(255, 255, 102))  # Gelb für in Arbeit
                    # Erweiterte Informationen für in_progress
                    est_time = subtask.get("estimated_time", "0")
                    act_time = subtask.get("actual_time", "0")
                    latest_in_progress = (task_name, subtask["subtask"], est_time, act_time)
                
                self.table.setItem(row, 2, status_item)
                
                # Geschätzte Zeit
                est_time_item = QTableWidgetItem(subtask.get("estimated_time", "N/A"))
                est_time_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 3, est_time_item)
                
                # Tatsächliche Zeit
                act_time_item = QTableWidgetItem(subtask.get("actual_time", "0"))
                act_time_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 4, act_time_item)
                
                row += 1
    
        # Zeige Informationen zum aktuellen "In Progress"-Task
        if latest_in_progress:
            # Format: Task, Subtask, Est. Time, Actual Time
            task, subtask, est_time, act_time = latest_in_progress
            self.current_task_display.setText(
                f"<b>Current Task:</b> {task} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
                f"<b>Subtask:</b> {subtask} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
                f"<b>Est. Time:</b> {est_time} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
                f"<b>Actual Time:</b> {act_time}"
            )
        else:
            self.current_task_display.setText("Kein aktueller Task in Bearbeitung.")

    def add_task(self):
        dialog = AddTaskDialog(self)
        if dialog.exec_():
            task_name = dialog.task_input.text().strip()
            task_type = dialog.type_dropdown.currentText()
            category = dialog.category_dropdown.currentText()
            estimated_time = dialog.estimated_time_input.text().strip()
    
            if task_name:
                data = load_todo()
                data["tasks"].append({
                    "task": task_name,
                    "type": task_type,
                    "category": category,
                    "estimated_time": estimated_time or "N/A",
                    "actual_time": "0",  # Neues Feld
                    "subtasks": []
                })
                
                save_todo(data)
                self.load_data()

    def add_subtask(self):
        dialog = AddSubtaskDialog(self)
        if dialog.exec_():
            task_name = dialog.task_dropdown.currentText().strip()
            subtask_name = dialog.subtask_input.text().strip()
            status = dialog.status_dropdown.currentText()
            estimated_time = dialog.estimated_time_input.text().strip()

            if task_name and subtask_name:
                data = load_todo()
                for task in data["tasks"]:
                    if task["task"] == task_name:
                        task["subtasks"].append({
                            "subtask": subtask_name, 
                            "status": status, 
                            "estimated_time": estimated_time or "N/A",
                            "actual_time": "0"  # Neues Feld
                        })
                        break
                
                save_todo(data)
                self.load_data()

    def delete_subtask(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            return  # Keine Zeile ausgewählt, also nichts zu löschen
        
        # Subtask-Name abrufen
        subtask_item = self.table.item(selected_row, 1)
        if not subtask_item:
            return  # Falls kein Subtask vorhanden ist
        
        subtask_name = subtask_item.text()
    
        # Task-Name suchen 
        task_name = None
        for row in range(selected_row, -1, -1):  # Gehe rückwärts durch die Zeilen
            item = self.table.item(row, 0)
            if item:
                task_name = item.text()
                break
    
        if not task_name:
            return  # Kein gültiger Task gefunden
        
        # JSON-Daten laden
        data = load_todo()
        
        # Subtask aus der richtigen Task entfernen
        for task in data["tasks"]:
            if task["task"] == task_name:
                # Subtask entfernen
                task["subtasks"] = [s for s in task["subtasks"] if s["subtask"] != subtask_name]
                
                # Falls keine Subtasks mehr übrig sind, kann man optional die ganze Task entfernen
                if not task["subtasks"]:
                    data["tasks"].remove(task)
                
                break  # Task gefunden, keine weitere Iteration nötig
    
        # Aktualisierte Daten speichern und GUI neu laden
        save_todo(data)
        self.load_data()
        
    # Methode zum Ändern des Status
    def change_status(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            return  # Keine Zeile ausgewählt
    
        subtask_item = self.table.item(selected_row, 1)
        if not subtask_item:
            return  # Falls kein Subtask vorhanden ist
    
        subtask_name = subtask_item.text()
    
        # Task-Name ermitteln
        task_name = None
        for row in range(selected_row, -1, -1):  # Rückwärts durch Zeilen gehen
            item = self.table.item(row, 0)
            if item:
                task_name = item.text()
                break
    
        if not task_name:
            return  # Kein gültiger Task gefunden
    
        # Lade JSON-Daten
        data = load_todo()
    
        # Status-Logik definieren
        STATUS_CYCLE = ["Pending", "In Progress", "Completed"]
        for task in data["tasks"]:
            if task["task"] == task_name:
                for subtask in task["subtasks"]:
                    if subtask["subtask"] == subtask_name:
                        current_status = subtask["status"]
                        next_status = STATUS_CYCLE[(STATUS_CYCLE.index(current_status) + 1) % len(STATUS_CYCLE)]
                        subtask["status"] = next_status
                        break
    
        # Speichern und GUI aktualisieren
        save_todo(data)
        self.load_data()
    
    # Neue Methode zum Aktualisieren der tatsächlichen Zeit
    def update_actual_time(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            return  # Keine Zeile ausgewählt
        
        # Subtask-Infos abrufen
        subtask_item = self.table.item(selected_row, 1)
        actual_time_item = self.table.item(selected_row, 4)
        
        if not subtask_item:
            return  # Kein Subtask vorhanden
        
        subtask_name = subtask_item.text()
        current_time = actual_time_item.text() if actual_time_item else "0"
        
        # Task-Name ermitteln
        task_name = None
        for row in range(selected_row, -1, -1):
            item = self.table.item(row, 0)
            if item:
                task_name = item.text()
                break
        
        if not task_name:
            return  # Kein Task gefunden
        
        # Dialog zum Aktualisieren der Zeit anzeigen
        dialog = UpdateActualTimeDialog(task_name, subtask_name, current_time, self)
        if dialog.exec_():
            new_time = dialog.get_actual_time()
            
            # Daten aktualisieren
            data = load_todo()
            for task in data["tasks"]:
                if task["task"] == task_name:
                    for subtask in task["subtasks"]:
                        if subtask["subtask"] == subtask_name:
                            subtask["actual_time"] = new_time
                            break
            
            save_todo(data)
            self.load_data()

# Anwendung starten
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TodoApp()
    window.show()
    sys.exit(app.exec_())