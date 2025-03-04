import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, 
    QHeaderView, QDialog, QLineEdit, QComboBox, QLabel, QFormLayout, QDialogButtonBox, 
    QDoubleSpinBox, QAbstractItemView
)
from PyQt5.QtGui import QColor, QDrag, QCursor
from PyQt5.QtCore import Qt, QMimeData, QByteArray, QPoint

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
        
        # Add color dropdown instead of text input
        self.color_dropdown = QComboBox()
        # Add a selection of colors in similar tone
        self.colors = [
            {"name": "Blue", "hex": "#3498db"},
            {"name": "Purple", "hex": "#9b59b6"},
            {"name": "Pink", "hex": "#e91e63"},
            {"name": "Red", "hex": "#e74c3c"},
            {"name": "Orange", "hex": "#e67e22"},
            {"name": "Yellow", "hex": "#f1c40f"},
            {"name": "Green", "hex": "#2ecc71"},
            {"name": "Teal", "hex": "#1abc9c"},
            {"name": "Dark Blue", "hex": "#2c3e50"},
            {"name": "Dark Purple", "hex": "#3f1c4f"},
            {"name": "Light Pink", "hex": "#ff6b81"}
        ]
        
        # Add colors to dropdown
        for color in self.colors:
            self.color_dropdown.addItem(color["name"])

        layout.addRow(QLabel("Task Name:"), self.task_input)
        layout.addRow(QLabel("Type:"), self.type_dropdown)
        layout.addRow(QLabel("Category:"), self.category_dropdown)
        layout.addRow(QLabel("Estimated Time (in hours):"), self.estimated_time_input)
        layout.addRow(QLabel("Color:"), self.color_dropdown)

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
        layout.addRow(QLabel("Estimated Time (in hours):"), self.estimated_time_input)
        
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

# Benutzerdefinierter TableWidgetItem mit Task und Subtask Informationen
class TaskSubtaskItem(QTableWidgetItem):
    def __init__(self, text, task, subtask):
        super().__init__(text)
        self.task = task
        self.subtask = subtask

# GUI-Klasse mit QTableWidget
class TodoApp(QWidget):
    def __init__(self):
        super().__init__()

        self.hide_completed = False

        self.setWindowTitle("Todo Manager")
        self.setGeometry(100, 100, 850, 450)  # Breitere Tabelle für neue Spalten

        # Hauptlayout als vertikales Layout definieren
        self.layout = QVBoxLayout()

        # Tabelle erstellen
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # Added one column for the color dot
        self.table.setHorizontalHeaderLabels(["", "Task", "Subtask", "Status"])
        self.table.verticalHeader().setVisible(False)
        
        # Make the color dot column narrow
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 20)
        
        # Drag & Drop Einstellungen
        self.table.setDragEnabled(True)
        self.table.setAcceptDrops(True)
        self.table.viewport().setAcceptDrops(True)
        self.table.setDragDropOverwriteMode(False)
        self.table.setDropIndicatorShown(True)
        
        # Wir verwenden eigenes Drag & Drop statt QAbstractItemView.InternalMove
        self.table.setDragDropMode(QAbstractItemView.DragDrop)
        
        # Für eine saubere Anzeige setzen wir den Selektionsmodus
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Spaltenbreiten
        self.table.setColumnWidth(0, 20)   # Color dot
        self.table.setColumnWidth(1, 200)  # Task
        self.table.setColumnWidth(2, 300)  # Subtask
        self.table.setColumnWidth(3, 100)  # Status
        
        # Verbinde Drag & Drop-Ereignisse
        self.table.startDrag = self.startDrag
        self.table.dropEvent = self.handleDropEvent
        self.table.dragEnterEvent = self.handleDragEnterEvent
        self.table.dragMoveEvent = self.handleDragMoveEvent
        
        self.layout.addWidget(self.table)
        
        # Horizontales Layout für Buttons
        button_layout = QHBoxLayout()
        
        # Button zum Hinzufügen eines Tasks
        self.add_task_button = QPushButton("Add Task")
        self.add_task_button.setFixedSize(150, 40)
        self.add_task_button.clicked.connect(self.add_task)
        button_layout.addWidget(self.add_task_button)
        
        # Button zum Hinzufügen von Subtasks
        self.add_button = QPushButton("Add Subtask")
        self.add_button.setFixedSize(150, 40)
        self.add_button.clicked.connect(self.add_subtask)
        button_layout.addWidget(self.add_button)
        
        # Button zum Löschen von Subtasks
        self.delete_button = QPushButton("Delete Subtask")
        self.delete_button.setFixedSize(150, 40)
        self.delete_button.clicked.connect(self.delete_subtask)
        button_layout.addWidget(self.delete_button)
        
        # Button zum Ändern des Status von Subtasks
        self.change_status_button = QPushButton("Change Status")  
        self.change_status_button.setFixedSize(150, 40)
        self.change_status_button.clicked.connect(self.change_status)  
        button_layout.addWidget(self.change_status_button)

        # Button zum Ein-/Ausblenden erledigter Aufgaben
        self.hide_completed_button = QPushButton("Hide Completed")
        self.hide_completed_button.setFixedSize(150, 40)
        self.hide_completed_button.setCheckable(True)  # Make it toggleable
        self.hide_completed_button.clicked.connect(self.toggle_completed_tasks)
        button_layout.addWidget(self.hide_completed_button)  
        
        # Button-Layout dem Hauptlayout hinzufügen
        self.layout.addLayout(button_layout)

        #Feld für die Anzeige des aktuellen Tasks
        self.current_task_display = QLabel("")  # Startet leer
        self.current_task_display.setStyleSheet("font-size: 14px; font-weight: normal; padding: 0px; border: 0px solid gray;")
        self.layout.addWidget(self.current_task_display)
                
        self.setLayout(self.layout) 
        self.load_data()

    def toggle_completed_tasks(self):
        """Toggle visibility of completed tasks and update the display"""
        self.hide_completed = self.hide_completed_button.isChecked()
        
        # Update button text based on state
        if self.hide_completed:
            self.hide_completed_button.setText("Show Completed")
        else:
            self.hide_completed_button.setText("Hide Completed")
        
        # Reload the data with the new visibility setting
        self.load_data()
        
    def startDrag(self, actions):
        indexes = self.table.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            row = index.row()
            column = index.column()
            
            # Task ermitteln
            task_name = None
            for r in range(row, -1, -1):
                item = self.table.item(r, 0)
                if item:
                    task_name = item.text()
                    break
            
            if task_name:
                # Prüfen ob Task oder Subtask gezogen wird
                if column == 0 and self.table.item(row, 0) and self.table.item(row, 0).text() == task_name:
                    # Es wird ein Task gezogen (erste Zeile eines Tasks)
                    
                    # Alle Subtasks des Tasks finden
                    task_data = None
                    todo_data = load_todo()
                    for task in todo_data["tasks"]:
                        if task["task"] == task_name:
                            task_data = task
                            break
                    
                    if task_data:
                        # Drag-Daten für Task erstellen
                        data = {
                            "type": "task",
                            "task": task_name,
                            "row": row,
                            "task_data": task_data
                        }
                        
                        # MIME-Daten für Drag erstellen
                        mime_data = QMimeData()
                        mime_data.setData("application/x-todo-task", QByteArray(json.dumps(data).encode()))
                        
                        # Drag starten
                        drag = QDrag(self.table)
                        drag.setMimeData(mime_data)
                        drag.setHotSpot(QPoint(10, 10))
                        
                        # Drag ausführen
                        result = drag.exec_(Qt.MoveAction)
                
                # Subtask ziehen
                else:
                    # Subtask-Infos
                    subtask_item = self.table.item(row, 1)
                    if subtask_item:
                        subtask_name = subtask_item.text()
                        
                        # Drag-Daten erstellen
                        data = {
                            "type": "subtask",
                            "task": task_name,
                            "subtask": subtask_name,
                            "row": row
                        }
                        
                        # MIME-Daten für Drag erstellen
                        mime_data = QMimeData()
                        mime_data.setData("application/x-todo-subtask", QByteArray(json.dumps(data).encode()))
                        
                        # Drag starten
                        drag = QDrag(self.table)
                        drag.setMimeData(mime_data)
                        drag.setHotSpot(QPoint(10, 10))
                        
                        # Drag ausführen
                        result = drag.exec_(Qt.MoveAction)
    
    def handleDragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-todo-subtask") or event.mimeData().hasFormat("application/x-todo-task"):
            event.accept()
        else:
            event.ignore()
    
    def handleDragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-todo-subtask") or event.mimeData().hasFormat("application/x-todo-task"):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()
    
    def handleDropEvent(self, event):
        pos = event.pos()
        drop_index = self.table.indexAt(pos)
        drop_row = drop_index.row()
        
        # Nur fortfahren, wenn eine gültige Zielzeile ausgewählt wurde
        if drop_row >= 0:
            # Behandlung von Subtask-Drag & Drop
            if event.mimeData().hasFormat("application/x-todo-subtask"):
                # Daten aus MIME-Daten extrahieren
                mime_data = event.mimeData().data("application/x-todo-subtask")
                drag_data = json.loads(bytes(mime_data).decode())
                
                source_task = drag_data["task"]
                source_subtask = drag_data["subtask"]
                source_row = drag_data["row"]
                
                # Task für die Zielzeile bestimmen
                target_task = None
                for r in range(drop_row, -1, -1):
                    item = self.table.item(r, 0)
                    if item:
                        target_task = item.text()
                        break
                
                # Nur wenn Quelle und Ziel im gleichen Task sind
                if source_task == target_task:
                    # JSON-Daten laden
                    todo_data = load_todo()
                    
                    # Subtask finden und verschieben
                    for task in todo_data["tasks"]:
                        if task["task"] == source_task:
                            # Subtask finden und aus der Liste entfernen
                            subtask_to_move = None
                            subtask_index = None
                            for i, subtask in enumerate(task["subtasks"]):
                                if subtask["subtask"] == source_subtask:
                                    subtask_to_move = subtask
                                    subtask_index = i
                                    break
                            
                            if subtask_to_move and subtask_index is not None:
                                # Subtask aus der Liste entfernen
                                task["subtasks"].pop(subtask_index)
                                
                                # Zielposition bestimmen
                                target_subtask_name = None
                                if self.table.item(drop_row, 1):
                                    target_subtask_name = self.table.item(drop_row, 1).text()
                                
                                # Zielposition im task["subtasks"] Array finden
                                target_index = 0
                                for i, subtask in enumerate(task["subtasks"]):
                                    if subtask["subtask"] == target_subtask_name:
                                        target_index = i
                                        # Wenn wir nach unten ziehen, erhöhen wir den Index
                                        if source_row < drop_row:
                                            target_index += 1
                                        break
                                
                                # Füge an der Zielposition ein
                                task["subtasks"].insert(target_index, subtask_to_move)
                                
                                # Daten speichern
                                save_todo(todo_data)
                                
                                # GUI aktualisieren
                                self.load_data()
                            
                            break
                
                event.accept()
            
            # Behandlung von Task-Drag & Drop
            elif event.mimeData().hasFormat("application/x-todo-task"):
                # Daten aus MIME-Daten extrahieren
                mime_data = event.mimeData().data("application/x-todo-task")
                drag_data = json.loads(bytes(mime_data).decode())
                
                source_task = drag_data["task"]
                source_row = drag_data["row"]
                task_data = drag_data["task_data"]
                
                # Task für die Zielzeile bestimmen
                target_task = None
                for r in range(drop_row, -1, -1):
                    item = self.table.item(r, 0)
                    if item:
                        target_task = item.text()
                        break
                
                if target_task and target_task != source_task:  # Nur wenn auf einen anderen Task gezogen
                    # JSON-Daten laden
                    todo_data = load_todo()
                    
                    # Task finden und aus der Liste entfernen
                    task_index = None
                    for i, task in enumerate(todo_data["tasks"]):
                        if task["task"] == source_task:
                            task_index = i
                            break
                    
                    if task_index is not None:
                        # Task aus der Liste entfernen
                        todo_data["tasks"].pop(task_index)
                        
                        # Zielposition bestimmen
                        target_task_index = None
                        for i, task in enumerate(todo_data["tasks"]):
                            if task["task"] == target_task:
                                target_task_index = i
                                # Wenn wir nach unten ziehen, erhöhen wir den Index
                                if source_row < drop_row:
                                    target_task_index += 1
                                break
                        
                        if target_task_index is not None:
                            # Füge an der Zielposition ein
                            todo_data["tasks"].insert(target_task_index, task_data)
                            
                            # Daten speichern
                            save_todo(todo_data)
                            
                            # GUI aktualisieren
                            self.load_data()
                
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def load_data(self):
        global latest_in_progress  # Zugriff auf die globale Variable
        data = load_todo()
        tasks = data.get("tasks", [])
    
        # Tabelle leeren
        self.table.setRowCount(0)
        
        # Filter subtasks based on the hide_completed setting
        filtered_tasks = []
        for task in tasks:
            task_name = task["task"]
            # Filter subtasks if hide_completed is True
            if self.hide_completed:
                filtered_subtasks = [subtask for subtask in task["subtasks"] 
                                    if subtask["status"] != "Completed"]
            else:
                filtered_subtasks = task["subtasks"]
            
            # Only include tasks that have visible subtasks
            if filtered_subtasks:
                # Create a copy of the task with filtered subtasks
                filtered_task = task.copy()
                filtered_task["subtasks"] = filtered_subtasks
                filtered_tasks.append(filtered_task)
    
        # Count total rows needed
        row_count = sum(len(task["subtasks"]) for task in filtered_tasks)
        self.table.setRowCount(row_count)
    
        row = 0
        for task in filtered_tasks:
            task_name = task["task"]
            subtasks = task["subtasks"]
            task_span = len(subtasks)
            
            # Get the task color (default to light blue if not set)
            task_color = task.get("color", "#3498db")
    
            for i, subtask in enumerate(subtasks):
                if i == 0:
                    # Statt des einfachen QTableWidgetItem verwenden wir ein Label für den farbigen Punkt
                    # Das gibt uns mehr Kontrolle über die Positionierung
                    color_dot_widget = QWidget()
                    color_dot_layout = QVBoxLayout(color_dot_widget)
                    color_dot_layout.setContentsMargins(0, 5, 0, 0)  # Oberer Rand für bessere Ausrichtung
                    color_dot_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
                    
                    # Label für den farbigen Punkt
                    dot_label = QLabel("●")
                    dot_label.setStyleSheet(f"color: {task_color}; font-size: 16px;")
                    
                    color_dot_layout.addWidget(dot_label)
                    self.table.setCellWidget(row, 0, color_dot_widget)
                    
                    # Create the task item with normal text in the second column
                    task_item = QTableWidgetItem(task_name)
                    task_item.setTextAlignment(Qt.AlignTop)
                    self.table.setItem(row, 1, task_item)
                    
                    # Already added above
                    if task_span > 1:
                        # Span both the color dot and task columns
                        self.table.setSpan(row, 0, task_span, 1)
                        self.table.setSpan(row, 1, task_span, 1)
    
                # Subtask Name mit zusätzlichen Informationen
                subtask_item = TaskSubtaskItem(subtask["subtask"], task_name, subtask["subtask"])
                self.table.setItem(row, 2, subtask_item)
                
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
                
                self.table.setItem(row, 3, status_item)
                
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
            color_name = dialog.color_dropdown.currentText()
            # Get the hex code for the selected color
            color = next((c["hex"] for c in dialog.colors if c["name"] == color_name), "#3498db")
    
            if task_name:
                data = load_todo()
                data["tasks"].append({
                    "task": task_name,
                    "type": task_type,
                    "category": category,
                    "estimated_time": estimated_time or "N/A",
                    "actual_time": "0",
                    "color": color,  # Add color to new tasks
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
                            "actual_time": "0"
                        })
                        break
                
                save_todo(data)
                self.load_data()

    def delete_subtask(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            return  # Keine Zeile ausgewählt, also nichts zu löschen
        
        # Subtask-Name abrufen
        subtask_item = self.table.item(selected_row, 2)  # Changed column index
        if not subtask_item:
            return  # Falls kein Subtask vorhanden ist
        
        subtask_name = subtask_item.text()
    
        # Task-Name suchen 
        task_name = None
        for row in range(selected_row, -1, -1):  # Gehe rückwärts durch die Zeilen
            item = self.table.item(row, 1)  # Changed column index
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
    
        subtask_item = self.table.item(selected_row, 2)  # Changed column index
        if not subtask_item:
            return  # Falls kein Subtask vorhanden ist
    
        subtask_name = subtask_item.text()
    
        # Task-Name ermitteln
        task_name = None
        for row in range(selected_row, -1, -1):  # Rückwärts durch Zeilen gehen
            item = self.table.item(row, 1)  # Changed column index
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

# Anwendung starten
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TodoApp()
    window.show()
    sys.exit(app.exec_())