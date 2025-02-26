import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, 
    QHeaderView, QDialog, QLineEdit, QComboBox, QLabel, QFormLayout, QDialogButtonBox
)

from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

latest_in_progress = ('Relax', 'Slay')

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
        self.estimated_time_input = QLineEdit()  # Neues Eingabefeld für geschätzte Zeit
        
        layout.addRow(QLabel("Task:"), self.task_dropdown)
        layout.addRow(QLabel("Subtask:"), self.subtask_input)
        layout.addRow(QLabel("Status:"), self.status_dropdown)
        layout.addRow(QLabel("Estimated Time (in minutes):"), self.estimated_time_input)  # Neues Feld
        
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
# GUI-Klasse mit QTableWidget
class TodoApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Todo Manager")
        self.setGeometry(100, 100, 650, 450)

        #layout = QVBoxLayout()
        # Hauptlayout als vertikales Layout definieren
        self.layout = QVBoxLayout()

        # Tabelle erstellen
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Task", "Subtask", "Status"])
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(2, 150)
        self.layout.addWidget(self.table)
        # Label für "Current Task"
        #self.current_task_label = QLabel("Current Task:")
        #self.layout.addWidget(self.current_task_label)
        
        # Feld für die Anzeige des aktuellen Tasks
        self.current_task_display = QLabel("")  # Startet leer
        self.current_task_display.setStyleSheet("font-size: 14px; font-weight: normal; padding: 0px; border: 0px solid gray;")
        self.layout.addWidget(self.current_task_display)
                
        # Horizontales Layout für Buttons
        button_layout = QHBoxLayout()
        
        # Zeile 126: Button zum Ändern des Status von Subtasks
        self.change_status_button = QPushButton("Change Status")  
        self.change_status_button.setFixedSize(150, 40)  # Breite: 150px, Höhe: 40px

        self.change_status_button.clicked.connect(self.change_status)  
        button_layout.addWidget(self.change_status_button)  

        # Button zum Hinzufügen von Subtasks
        self.add_button = QPushButton("Subtask hinzufügen")
        self.add_button.setFixedSize(150, 40) # Breite: 180px, Höhe: 50px
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

        # Button-Layout dem Hauptlayout hinzufügen
        self.layout.addLayout(button_layout)  # Fügt die Buttons in einer Zeile hinzu

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
                    if task_span > 1:  # Verhindert die Fehlermeldung
                        self.table.setSpan(row, 0, task_span, 1)

    
                self.table.setItem(row, 1, QTableWidgetItem(subtask["subtask"]))
                status_item = QTableWidgetItem(subtask["status"])
                status_item.setTextAlignment(Qt.AlignCenter)
    
                if subtask["status"] == "Completed":
                    status_item.setBackground(QColor(144, 238, 144))  # Grün für erledigt
                elif subtask["status"] == "In Progress":
                    status_item.setBackground(QColor(255, 255, 102))  # Gelb für in Arbeit
                    latest_in_progress = (task_name, subtask["subtask"])  # Speichern
                    
    
                self.table.setItem(row, 2, status_item)
                row += 1
    
        # Zeige nur den aktuellsten "In Progress"-Task
        if latest_in_progress:
            self.current_task_display.setText(f"<b>Current Task:</b>  {latest_in_progress[0]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  <b>Subtask:</b> {latest_in_progress[1]}")
        else:
            self.current_task_display.setText("Kein aktueller Task in Bearbeitung.")
        #print(f"Ende von load data:{latest_in_progress}")


    def add_task(self):
        print(f"add task triggert:{latest_in_progress}")
        print(f"getter methode:{get_latest_in_progress()}")
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
                    "subtasks": []
                })
                
                save_todo(data)
                self.load_data()

    def add_subtask(self):  # Korrekte Einrückung!
        dialog = AddSubtaskDialog(self)
        if dialog.exec_():
            task_name = dialog.task_dropdown.currentText().strip()
            subtask_name = dialog.subtask_input.text().strip()
            status = dialog.status_dropdown.currentText()
            estimated_time = dialog.estimated_time_input.text().strip()  # Neue Zeile für geschätzte Zeit

            if task_name and subtask_name:
                data = load_todo()
                for task in data["tasks"]:
                    if task["task"] == task_name:
                        task["subtasks"].append({
                            "subtask": subtask_name, 
                            "status": status, 
                            "estimated_time": estimated_time or "N/A"  # Falls leer, setze "N/A"
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
    
        # Task-Name suchen (möglicherweise durch setSpan() nicht direkt abrufbar)
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
        
     #Methode zum Ändern des Status
    def change_status(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            return  # Zeile 275: Keine Zeile ausgewählt
    
        subtask_item = self.table.item(selected_row, 1)
        if not subtask_item:
            return  # Zeile 279: Falls kein Subtask vorhanden ist
    
        subtask_name = subtask_item.text()
    
        # Zeile 283: Task-Name ermitteln
        task_name = None
        for row in range(selected_row, -1, -1):  # Rückwärts durch Zeilen gehen
            item = self.table.item(row, 0)
            if item:
                task_name = item.text()
                break
    
        if not task_name:
            return  # Zeile 290: Kein gültiger Task gefunden
    
        # Zeile 293: Lade JSON-Daten
        data = load_todo()
    
        # Zeile 296: Status-Logik definieren
        STATUS_CYCLE = ["Pending", "In Progress", "Completed"]
        for task in data["tasks"]:
            if task["task"] == task_name:
                for subtask in task["subtasks"]:
                    if subtask["subtask"] == subtask_name:
                        current_status = subtask["status"]
                        next_status = STATUS_CYCLE[(STATUS_CYCLE.index(current_status) + 1) % len(STATUS_CYCLE)]
                        subtask["status"] = next_status
                        break  # Zeile 304: Status aktualisiert, weitere Suche abbrechen
    
        # Zeile 307: Speichern und GUI aktualisieren
        save_todo(data)
        self.load_data()



# Anwendung starten
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TodoApp()
    window.show()
    #sys.exit(app.exec_())
    app.exec_()

