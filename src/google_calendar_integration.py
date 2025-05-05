#!/usr/bin/env python3
import os
import datetime
import pickle
import csv
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Berechtigungen festlegen, die wir von Google benötigen
# Für Nur-Lese-Zugriff auf den Kalender reicht CALENDAR.READONLY
# Wenn Sie später Termine erstellen möchten, benötigen Sie CALENDAR
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Basisverzeichnis bestimmen (geht eine Ebene nach oben)
base_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
data_dir = os.path.join(base_dir, "data")

class GoogleCalendarAPI:
    def __init__(self, token_path='token.pickle', credentials_path='credentials.json'):
        """
        Initialisiert die Verbindung zur Google Calendar API.
        
        Args:
            token_path: Pfad zur Token-Datei (für persistente Anmeldung)
            credentials_path: Pfad zur Credentials-Datei (von Google Console)
        """
        self.token_path = token_path
        self.credentials_path = credentials_path
        self.service = None
        
    def authenticate(self):
        """
        Führt die Authentifizierung mit Google durch und erstellt den API-Service.
        
        Returns:
            bool: True, wenn die Authentifizierung erfolgreich war, sonst False
        """
        creds = None
        
        # Token aus vorherigen Anmeldungen laden, falls vorhanden
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Wenn keine Anmeldedaten vorhanden oder ungültig sind, neu anmelden
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    print(f"FEHLER: Credentials-Datei nicht gefunden: {self.credentials_path}")
                    print("Bitte laden Sie Ihre Credentials-Datei von der Google Cloud Console herunter.")
                    print("1. Gehen Sie zu https://console.cloud.google.com/")
                    print("2. Erstellen Sie ein Projekt und aktivieren Sie die Google Calendar API")
                    print("3. Erstellen Sie OAuth 2.0-Client-IDs unter 'APIs & Dienste > Anmeldedaten'")
                    print("4. Laden Sie die JSON-Datei herunter und speichern Sie sie als 'credentials.json'")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Token für zukünftige Nutzung speichern
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # API-Service erstellen
        self.service = build('calendar', 'v3', credentials=creds)
        return True
    
    def get_calendars(self):
        """
        Holt eine Liste aller Kalender des Benutzers.
        
        Returns:
            list: Liste von Kalender-Dicts mit 'id' und 'summary'
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        calendar_list = self.service.calendarList().list().execute()
        calendars = []
        
        for calendar_entry in calendar_list.get('items', []):
            calendars.append({
                'id': calendar_entry['id'],
                'summary': calendar_entry['summary']
            })
        
        return calendars
    
    def get_events(self, calendar_id='primary', time_min=None, time_max=None, max_results=50, create_csv=True):
        """
        Holt Termine aus einem Kalender innerhalb eines Zeitraums.
        
        Args:
            calendar_id: ID des Kalenders, 'primary' für den Hauptkalender
            time_min: Startzeit für die Terminsuche (datetime, optional)
            time_max: Endzeit für die Terminsuche (datetime, optional)
            max_results: Maximale Anzahl der zurückgegebenen Termine (int)
            create_csv: Ob CSV-Dateien für jeden Termin erstellt werden sollen
            
        Returns:
            list: Liste von Termin-Dicts mit relevanten Informationen
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        # Standardwerte für Zeitbereiche setzen
        if time_min is None:
            time_min = datetime.datetime.utcnow()
        if time_max is None:
            time_max = time_min + datetime.timedelta(days=30)  # 30 Tage ab jetzt
        
        # Zeiten ins ISO-Format umwandeln
        time_min_iso = time_min.isoformat() + 'Z'  # 'Z' zeigt UTC-Zeit an
        time_max_iso = time_max.isoformat() + 'Z'
        
        # Events abrufen
        events_result = self.service.events().list(
            calendarId=calendar_id,
            timeMin=time_min_iso,
            timeMax=time_max_iso,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        # Events verarbeiten
        events = []
        for event in events_result.get('items', []):
            # Start- und Endzeit des Termins abholen
            start_time = event.get('start', {})
            end_time = event.get('end', {})
            
            # Überprüfen, ob es sich um einen Ganztagestermin handelt
            is_all_day = 'date' in start_time and 'date' in end_time
            
            # Formatiertes Event-Objekt erstellen
            event_data = {
                'id': event.get('id', ''),
                'summary': event.get('summary', '(Kein Titel)'),
                'description': event.get('description', ''),
                'location': event.get('location', ''),
                'is_all_day': is_all_day,
                'start_time': start_time.get('dateTime', start_time.get('date', '')),
                'end_time': end_time.get('dateTime', end_time.get('date', '')),
                'creator': event.get('creator', {}).get('email', ''),
                'attendees': [attendee.get('email', '') for attendee in event.get('attendees', [])]
            }
            
            events.append(event_data)
            
            # CSV-Datei für diesen Termin erstellen, falls gewünscht
            if create_csv:
                create_csv_for_event(event_data)
        
        return events
    
    def get_events_by_date_range(self, start_date, end_date, calendar_id='primary', create_csv=True):
        """
        Holt Termine in einem bestimmten Datumsbereich.
        
        Args:
            start_date: Startdatum (datetime.date)
            end_date: Enddatum (datetime.date)
            calendar_id: ID des Kalenders
            create_csv: Ob CSV-Dateien für jeden Termin erstellt werden sollen
        
        Returns:
            list: Liste der Termine im angegebenen Zeitraum
        """
        # Umwandlung von date zu datetime
        start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
        end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
        
        return self.get_events(calendar_id, start_datetime, end_datetime, create_csv=create_csv)
    
    def get_todays_events(self, calendar_id='primary', create_csv=True):
        """
        Holt die Termine des heutigen Tages.
        
        Args:
            calendar_id: ID des Kalenders
            create_csv: Ob CSV-Dateien für jeden Termin erstellt werden sollen
            
        Returns:
            list: Liste der heutigen Termine
        """
        today = datetime.date.today()
        return self.get_events_by_date_range(today, today, calendar_id, create_csv=create_csv)
    
    def get_weeks_events(self, calendar_id='primary', create_csv=True):
        """
        Holt die Termine der aktuellen Woche.
        
        Args:
            calendar_id: ID des Kalenders
            create_csv: Ob CSV-Dateien für jeden Termin erstellt werden sollen
            
        Returns:
            list: Liste der Termine der aktuellen Woche
        """
        today = datetime.date.today()
        start_of_week = today - datetime.timedelta(days=today.weekday())  # Montag
        end_of_week = start_of_week + datetime.timedelta(days=6)  # Sonntag
        
        return self.get_events_by_date_range(start_of_week, end_of_week, calendar_id, create_csv=create_csv)

def create_csv_for_event(event):
    """
    Erstellt oder aktualisiert eine CSV-Datei für einen Termin.
    
    Args:
        event: Event-Dictionary mit Termindaten
    """
    # Verarbeite nur Ereignisse mit einer Start- und Endzeit
    if not event['start_time'] or not event['end_time']:
        return
    
    # Parse Startzeit
    if event['is_all_day']:
        # Bei ganztägigen Terminen setzen wir Standardzeiten
        start_date = datetime.date.fromisoformat(event['start_time'])
        start_datetime = datetime.datetime.combine(start_date, datetime.time(9, 0))  # 09:00 Uhr
        end_datetime = datetime.datetime.combine(start_date, datetime.time(17, 0))  # 17:00 Uhr
    else:
        # Bei zeitgebundenen Terminen verwenden wir die exakten Zeiten
        start_datetime = datetime.datetime.fromisoformat(event['start_time'].replace('Z', '+00:00')).astimezone()
        end_datetime = datetime.datetime.fromisoformat(event['end_time'].replace('Z', '+00:00')).astimezone()
    
    # Formatiere das Datum für den Dateinamen (DD-MM-YY.csv)
    date_for_filename = start_datetime.strftime("%d-%m-%y")
    
    # Sorge dafür, dass das Datenverzeichnis existiert
    os.makedirs(data_dir, exist_ok=True)
    
    # CSV-Dateipfad
    csv_path = os.path.join(data_dir, f"{date_for_filename}.csv")
    
    # Startzeit und Endzeit im Format HH:MM:SS
    start_time_str = start_datetime.strftime("%H:%M:%S")
    end_time_str = end_datetime.strftime("%H:%M:%S")
    
    # Überprüfen, ob die Datei bereits existiert
    file_exists = os.path.exists(csv_path)
    
    # Öffne die CSV-Datei im Append-Modus oder erstelle sie neu
    with open(csv_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # Wenn die Datei neu erstellt wurde, füge den Header hinzu
        if not file_exists:
            csv_writer.writerow(['Mode', 'Status', 'Work', 'Block', 'Task', 'Subtask', 'Timer', 'Time'])
        
        # Füge die Zeilen für den Termin hinzu
        # Startzeile: Termin beginnt
        csv_writer.writerow(['1', '1', '1', '1', event['summary'], '', '00:00:00', start_time_str])
        # Endzeile: Termin endet
        csv_writer.writerow(['0', '0', '0', '0', event['summary'], '', '0:00:00', end_time_str])

def format_event_time(event):
    """
    Formatiert die Zeit eines Events für die Anzeige.
    
    Args:
        event: Event-Dictionary mit start_time und end_time
    
    Returns:
        str: Formatierte Zeitangabe
    """
    is_all_day = event['is_all_day']
    
    if is_all_day:
        # Bei ganztägigen Terminen nur das Datum anzeigen
        start_date = event['start_time']  # Bereits im ISO-Format YYYY-MM-DD
        return f"Ganztägig am {start_date}"
    else:
        # Bei zeitgebundenen Terminen Start- und Endzeit anzeigen
        start = datetime.datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
        end = datetime.datetime.fromisoformat(event['end_time'].replace('Z', '+00:00'))
        
        # Zu lokaler Zeit konvertieren
        start_local = start.astimezone()  # Konvertiert zu lokaler Zeitzone
        end_local = end.astimezone()
        
        # Formatierung: "DD.MM.YYYY HH:MM - HH:MM"
        if start_local.date() == end_local.date():
            # Gleicher Tag
            return f"{start_local.strftime('%d.%m.%Y %H:%M')} - {end_local.strftime('%H:%M')}"
        else:
            # Verschiedene Tage
            return f"{start_local.strftime('%d.%m.%Y %H:%M')} - {end_local.strftime('%d.%m.%Y %H:%M')}"

def print_events(events):
    """
    Gibt eine formatierte Liste von Terminen aus.
    
    Args:
        events: Liste von Event-Dictionaries
    """
    if not events:
        print("Keine Termine gefunden.")
        return
    
    print(f"Gefundene Termine: {len(events)}")
    print("-" * 50)
    
    for i, event in enumerate(events, 1):
        print(f"{i}. {event['summary']}")
        print(f"   Zeit: {format_event_time(event)}")
        
        if event['location']:
            print(f"   Ort: {event['location']}")
        
        if event['description']:
            # Beschreibung auf 50 Zeichen kürzen, wenn sie zu lang ist
            description = event['description']
            if len(description) > 50:
                description = description[:47] + "..."
            print(f"   Beschreibung: {description}")
        
        print("-" * 50)

def main():
    """
    Hauptfunktion zum Testen der Google Calendar API-Integration.
    """
    # Google Calendar API initialisieren
    calendar_api = GoogleCalendarAPI()
    
    # Authentifizieren
    if not calendar_api.authenticate():
        print("Authentifizierung fehlgeschlagen.")
        return
    
    print("Erfolgreich authentifiziert!")
    
    # Alle verfügbaren Kalender anzeigen
    calendars = calendar_api.get_calendars()
    print("\nVerfügbare Kalender:")
    for i, calendar in enumerate(calendars, 1):
        print(f"{i}. {calendar['summary']} (ID: {calendar['id']})")
    
    # Standardmäßig den Hauptkalender verwenden
    calendar_id = 'primary'
    
    # Termine der aktuellen Woche abrufen
    print("\nTermine der aktuellen Woche:")
    events = calendar_api.get_weeks_events(calendar_id)
    print_events(events)
    
    # Termine des heutigen Tages abrufen
    print("\nTermine des heutigen Tages:")
    events = calendar_api.get_todays_events(calendar_id)
    print_events(events)
    
    # Hinweis auf erstellte CSV-Dateien
    print("\nFür alle Termine wurden CSV-Dateien im Format DD-MM-YY.csv erstellt.")
    print(f"Sie finden diese im Verzeichnis: {data_dir}")

if __name__ == "__main__":
    main() 