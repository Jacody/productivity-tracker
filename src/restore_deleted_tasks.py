#!/usr/bin/env python3
import json
import os
import csv
from decimal import Decimal

# Basisverzeichnis bestimmen
base_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
todo_path = os.path.join(base_dir, "data", "todo.json")
task_storage_path = os.path.join(base_dir, "data", "Task_storage_tracker - Tabellenblatt1.csv")

def load_todo():
    """Lädt die aktuelle Todo-JSON-Datei"""
    if os.path.exists(todo_path):
        with open(todo_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return {"tasks": []}

def save_todo(data):
    """Speichert die aktualisierte Todo-JSON-Datei"""
    os.makedirs(os.path.dirname(todo_path), exist_ok=True)
    with open(todo_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def task_exists(todo_data, task_name):
    """Überprüft, ob ein Task bereits in der JSON-Datei existiert"""
    for task in todo_data["tasks"]:
        if task["task"] == task_name:
            return True
    return False

def subtask_exists(todo_data, task_name, subtask_name):
    """Überprüft, ob ein Subtask in einem bestimmten Task bereits existiert"""
    for task in todo_data["tasks"]:
        if task["task"] == task_name:
            for subtask in task["subtasks"]:
                if subtask["subtask"] == subtask_name:
                    return True
    return False

def restore_tasks_from_csv():
    """Stellt gelöschte Tasks aus CSV-Dateien wieder her"""
    todo_data = load_todo()
    
    # Füge den "To-Do Tracker" Task hinzu, falls er nicht bereits existiert
    if not task_exists(todo_data, "To-Do Tracker"):
        todo_data["tasks"].append({
            "task": "To-Do Tracker",
            "type": "Digital",
            "category": "Hacken",
            "estimated_time": "2.0",
            "actual_time": "1.8",
            "color": "#3498db",
            "subtasks": []
        })
    
    # Lese die CSV-Datei mit den Task-Storage-Informationen
    try:
        with open(task_storage_path, "r", encoding="utf-8") as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)  # Überspringen der Header-Zeile
            
            # Verarbeite jede Zeile der CSV-Datei
            for row in csv_reader:
                if len(row) >= 6:  # Stellen Sie sicher, dass die Zeile genügend Spalten hat
                    task_name = row[0]
                    subtask_name = row[2]
                    
                    # Konvertiere die geschätzte Zeit von Sekunden in Stunden
                    try:
                        estimated_time_sec = int(row[4])
                        estimated_time = str(round(estimated_time_sec / 3600, 2))
                    except (ValueError, IndexError):
                        estimated_time = "0.0"
                    
                    # Bestimme den Status
                    try:
                        status_code = int(row[5])
                        if status_code == 0:
                            status = "Pending"
                        elif status_code == 1:
                            status = "In Progress"
                        elif status_code == 2:
                            status = "Completed"
                        else:
                            status = "Pending"
                    except (ValueError, IndexError):
                        status = "Pending"
                    
                    # Bestimme die tatsächliche Zeit (falls vorhanden)
                    try:
                        if len(row) >= 7 and row[6] and row[6] != "":
                            actual_time_sec = int(row[6])
                            actual_time = str(round(actual_time_sec / 3600, 2))
                        else:
                            actual_time = "0.0"
                    except (ValueError, IndexError):
                        actual_time = "0.0"
                    
                    # Füge den Task hinzu, wenn er noch nicht existiert
                    if not task_exists(todo_data, task_name):
                        todo_data["tasks"].append({
                            "task": task_name,
                            "type": "Digital",
                            "category": "Hacken",
                            "estimated_time": "0.0",
                            "actual_time": "0.0",
                            "color": "#3498db",  # Standard-Farbe
                            "subtasks": []
                        })
                    
                    # Füge den Subtask hinzu, wenn er noch nicht existiert
                    if not subtask_exists(todo_data, task_name, subtask_name):
                        for task in todo_data["tasks"]:
                            if task["task"] == task_name:
                                task["subtasks"].append({
                                    "subtask": subtask_name,
                                    "status": status,
                                    "estimated_time": estimated_time + "h",
                                    "actual_time": actual_time
                                })
                                
                                # Aktualisiere die Gesamtzeiten des Tasks
                                task_estimated = Decimal(task["estimated_time"] or "0")
                                task_actual = Decimal(task["actual_time"] or "0")
                                
                                task_estimated += Decimal(estimated_time)
                                task_actual += Decimal(actual_time)
                                
                                task["estimated_time"] = str(task_estimated)
                                task["actual_time"] = str(task_actual)
    
    except FileNotFoundError:
        print(f"CSV-Datei {task_storage_path} nicht gefunden.")
    except Exception as e:
        print(f"Fehler beim Lesen der CSV-Datei: {e}")
    
    # Füge auch den 'Relax' Task hinzu, falls er nicht existiert
    if not task_exists(todo_data, "Relax"):
        todo_data["tasks"].append({
            "task": "Relax",
            "type": "Other",
            "category": "Persönlich",
            "estimated_time": "0.0",
            "actual_time": "0.0",
            "color": "#2ecc71",  # Eine entspannte grüne Farbe
            "subtasks": [
                {
                    "subtask": "Slay",
                    "status": "Pending",
                    "estimated_time": "0.0h",
                    "actual_time": "0.0"
                }
            ]
        })
    
    # Speichere die aktualisierte JSON-Datei
    save_todo(todo_data)
    print("Gelöschte Tasks wurden erfolgreich wiederhergestellt!")

if __name__ == "__main__":
    restore_tasks_from_csv() 