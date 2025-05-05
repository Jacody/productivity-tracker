#!/usr/bin/env python3
"""
Dieses Modul integriert Google Kalender-Termine in die Todo-Liste.
"""

import os
import datetime
import json
from google_calendar_integration import GoogleCalendarAPI, create_csv_for_event

# Basisverzeichnis bestimmen (geht eine Ebene nach oben)
base_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
todo_path = os.path.join(base_dir, "data", "todo.json")

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

def create_task_from_calendar_event(event, task_color="#3498db"):
    """
    Erstellt ein Task-Objekt aus einem Google Calendar-Event.
    
    Args:
        event: Google Calendar-Event als Dictionary
        task_color: Farbe für den Task
    
    Returns:
        dict: Task-Dictionary, kompatibel mit dem Todo Manager
    """
    # Termin-Titel als Task-Name verwenden
    task_name = event['summary']
    
    # Beschreibung und Ort als Subtasks verwenden
    subtasks = []
    
    # Termin-Zeit als ersten Subtask hinzufügen
    time_str = format_event_time_for_subtask(event)
    subtasks.append({
        "subtask": f"Termin: {time_str}",
        "status": "Pending",
        "estimated_time": "1.0h",  # Standardwert
        "actual_time": "0.0"
    })
    
    # Ort als Subtask hinzufügen, falls vorhanden
    if event['location']:
        subtasks.append({
            "subtask": f"Ort: {event['location']}",
            "status": "Pending",
            "estimated_time": "0.0h",
            "actual_time": "0.0"
        })
    
    # Beschreibung als Subtask hinzufügen, falls vorhanden
    if event['description']:
        subtasks.append({
            "subtask": f"Details: {event['description'][:100]}",  # Auf 100 Zeichen begrenzen
            "status": "Pending",
            "estimated_time": "0.0h",
            "actual_time": "0.0"
        })
    
    # Für die geschätzte Gesamtzeit berechnen wir die Termindauer in Stunden
    duration_hours = calculate_event_duration(event)
    
    return {
        "task": task_name,
        "type": "Termin",
        "category": "Kalender",
        "estimated_time": str(duration_hours),
        "actual_time": "0.0",
        "color": task_color,
        "subtasks": subtasks
    }

def format_event_time_for_subtask(event):
    """
    Formatiert die Zeit eines Events für die Anzeige als Subtask.
    
    Args:
        event: Event-Dictionary
    
    Returns:
        str: Formatierte Zeit-Zeichenkette
    """
    if event['is_all_day']:
        start_date = event['start_time']
        return f"Ganztägig am {start_date}"
    else:
        start = datetime.datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
        end = datetime.datetime.fromisoformat(event['end_time'].replace('Z', '+00:00'))
        
        start_local = start.astimezone()
        end_local = end.astimezone()
        
        if start_local.date() == end_local.date():
            return f"{start_local.strftime('%d.%m.%Y %H:%M')} - {end_local.strftime('%H:%M')}"
        else:
            return f"{start_local.strftime('%d.%m.%Y %H:%M')} - {end_local.strftime('%d.%m.%Y %H:%M')}"

def calculate_event_duration(event):
    """
    Berechnet die Dauer eines Termins in Stunden.
    
    Args:
        event: Event-Dictionary
    
    Returns:
        float: Dauer in Stunden
    """
    if event['is_all_day']:
        return 8.0  # Standardwert für Ganztagestermine: 8 Stunden
    
    start = datetime.datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
    end = datetime.datetime.fromisoformat(event['end_time'].replace('Z', '+00:00'))
    
    duration = end - start
    hours = duration.total_seconds() / 3600
    
    return round(hours, 1)  # Auf eine Dezimalstelle runden

def import_calendar_events_to_todo(calendar_id='primary', days_ahead=7):
    """
    Importiert Google Calendar-Termine als Tasks in die Todo-Anwendung.
    
    Args:
        calendar_id: ID des zu importierenden Kalenders
        days_ahead: Anzahl der Tage in die Zukunft, für die Termine importiert werden
        
    Returns:
        int: Anzahl der importierten Termine
    """
    # Google Calendar API initialisieren
    api = GoogleCalendarAPI()
    
    if not api.authenticate():
        print("Fehler bei der Authentifizierung mit Google Calendar.")
        return 0
    
    # Zeitraum festlegen: von heute bis X Tage in die Zukunft
    today = datetime.date.today()
    end_date = today + datetime.timedelta(days=days_ahead)
    
    # Termine abrufen - hier setzen wir create_csv auf True, um CSV-Dateien zu erzeugen
    events = api.get_events_by_date_range(today, end_date, calendar_id, create_csv=True)
    
    # Aktuelle Todo-Daten laden
    todo_data = load_todo()
    
    # Kalender-Task-Gruppe erstellen oder finden
    calendar_task_name = f"Kalendertermine ({today.strftime('%d.%m')} - {end_date.strftime('%d.%m')})"
    
    # Prüfen, ob eine ähnliche Kalender-Task-Gruppe bereits existiert und diese entfernen
    todo_data["tasks"] = [task for task in todo_data["tasks"] 
                         if not task["task"].startswith("Kalendertermine")]
    
    # Neue Kalender-Task-Gruppe erstellen
    calendar_tasks = []
    
    # Konvertiere alle Events zu Tasks
    for event in events:
        task = create_task_from_calendar_event(event)
        calendar_tasks.append(task)
        
        # Zusätzlich die CSV-Datei für diesen Termin erstellen
        create_csv_for_event(event)
    
    # Füge alle Kalender-Tasks zur Todo-Liste hinzu
    todo_data["tasks"].extend(calendar_tasks)
    
    # Aktualisierte Daten speichern
    save_todo(todo_data)
    
    return len(calendar_tasks)

def main():
    """
    Hauptfunktion zur Demonstration der Kalender-Todo-Integration
    """
    print("Google Kalender-Integration für den Todo-Manager")
    print("=" * 50)
    
    # Google Calendar API initialisieren
    api = GoogleCalendarAPI()
    
    if not api.authenticate():
        print("Fehler bei der Authentifizierung mit Google Calendar.")
        return
    
    # Verfügbare Kalender anzeigen
    print("\nVerfügbare Kalender:")
    calendars = api.get_calendars()
    
    for i, calendar in enumerate(calendars, 1):
        print(f"{i}. {calendar['summary']} (ID: {calendar['id']})")
    
    # Benutzer nach dem zu importierenden Kalender fragen
    calendar_id = 'primary'  # Standardwert
    
    if len(calendars) > 1:
        try:
            choice = int(input("\nWählen Sie einen Kalender (1-{}): ".format(len(calendars))))
            if 1 <= choice <= len(calendars):
                calendar_id = calendars[choice-1]['id']
        except (ValueError, IndexError):
            print("Ungültige Auswahl. Der Hauptkalender wird verwendet.")
    
    # Benutzer nach dem Zeitraum fragen
    days_ahead = 7  # Standardwert
    
    try:
        days_input = input("\nWie viele Tage in die Zukunft importieren? [7]: ")
        if days_input.strip():
            days_ahead = int(days_input)
    except ValueError:
        print("Ungültige Eingabe. Standardwert (7 Tage) wird verwendet.")
    
    # Termine importieren
    num_imported = import_calendar_events_to_todo(calendar_id, days_ahead)
    
    if num_imported > 0:
        print(f"\nErfolgreich {num_imported} Termine in die Todo-Liste importiert!")
        print("Starten Sie den Todo-Manager neu, um die importierten Termine zu sehen.")
    else:
        print("\nKeine Termine zum Importieren gefunden.")

if __name__ == "__main__":
    main() 