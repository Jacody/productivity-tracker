# Google Calendar Integration für den Todo-Manager

Diese Integration ermöglicht es, Termine aus Google Calendar in den Todo-Manager zu importieren. Termine werden als Tasks mit Subtasks dargestellt, wobei Details wie Ort, Beschreibung und Zeitpunkt als Subtasks angezeigt werden.

## Voraussetzungen

Um die Google Calendar Integration nutzen zu können, benötigen Sie:

1. Python 3.6 oder höher
2. Die folgenden Python-Pakete:
   - `google-auth-oauthlib`
   - `google-auth`
   - `google-api-python-client`

Diese können Sie mit folgendem Befehl installieren:

```bash
pip install google-auth-oauthlib google-auth google-api-python-client
```

## Einrichtung der Google Cloud API

Bevor Sie die Integration nutzen können, müssen Sie ein Google Cloud Projekt erstellen und die Google Calendar API aktivieren:

1. Gehen Sie zur [Google Cloud Console](https://console.cloud.google.com/).
2. Erstellen Sie ein neues Projekt.
3. Aktivieren Sie die Google Calendar API:
   - Gehen Sie zu "APIs & Dienste" > "Bibliothek"
   - Suchen Sie nach "Google Calendar API" und aktivieren Sie sie
4. Erstellen Sie OAuth 2.0-Anmeldedaten:
   - Gehen Sie zu "APIs & Dienste" > "Anmeldedaten"
   - Klicken Sie auf "Anmeldedaten erstellen" > "OAuth-Client-ID"
   - Wählen Sie als Anwendungstyp "Desktop-Anwendung"
   - Geben Sie einen Namen für die Anmeldedaten ein
5. Laden Sie die JSON-Datei mit den Anmeldedaten herunter.
6. Speichern Sie die heruntergeladene JSON-Datei als `credentials.json` im selben Verzeichnis wie die Skript-Dateien.

## Verwendung

### Eigenständige Nutzung

Sie können die Google Calendar Integration direkt über die Kommandozeile nutzen:

```bash
python calendar_todo_integration.py
```

Das Skript führt Sie durch den Prozess:
1. Sie können einen Kalender aus Ihren verfügbaren Google Kalendern auswählen.
2. Sie können den Zeitraum angeben, für den Termine importiert werden sollen.
3. Die Termine werden als Tasks in die Todo-Liste importiert.

### Integration in den Todo-Manager

Sie können die Calendar-Integration auch in den Todo-Manager integrieren:

1. Fügen Sie einen Button zum Importieren von Kalenderterminen hinzu:
   - Öffnen Sie `todo_manager.py`
   - Fügen Sie einen Button im Button-Layout hinzu:
   ```python
   # Button zum Importieren von Kalenderterminen
   self.import_calendar_button = QPushButton("Kalender importieren")
   self.import_calendar_button.setFixedSize(150, 40)
   self.import_calendar_button.clicked.connect(self.import_calendar)
   self.import_calendar_button.setStyleSheet(self.button_style)
   button_layout.addWidget(self.import_calendar_button)
   ```

2. Fügen Sie die Import-Funktion hinzu:
   ```python
   def import_calendar(self):
       """Importiert Kalendertermine in die Todo-Liste"""
       from calendar_todo_integration import import_calendar_events_to_todo
       
       # Standard-Kalender importieren (7 Tage)
       num_imported = import_calendar_events_to_todo()
       
       if num_imported > 0:
           QMessageBox.information(self, "Kalender importiert", 
                                    f"{num_imported} Termine wurden erfolgreich importiert.")
           # Daten neu laden
           self.load_data()
       else:
           QMessageBox.information(self, "Kalender importiert",
                                    "Keine Termine zum Importieren gefunden.")
   ```

## Funktionen und Anpassungen

### Anpassung der Darstellung

Sie können die Darstellung der importierten Termine anpassen, indem Sie die Funktion `create_task_from_calendar_event` in `calendar_todo_integration.py` bearbeiten. Hier können Sie beispielsweise:

- Die Farbgebung der Termine ändern
- Die Struktur der Subtasks anpassen
- Zusätzliche Informationen hinzufügen

### Einstellung der Zeiträume

Standardmäßig werden Termine für die nächsten 7 Tage importiert. Sie können dies ändern, indem Sie den Parameter `days_ahead` in der Funktion `import_calendar_events_to_todo` anpassen.

### Regelmäßiger Import

Sie können einen regelmäßigen Import einrichten, indem Sie einen Cron-Job oder Task-Scheduler verwenden, der das Skript `calendar_todo_integration.py` in regelmäßigen Abständen ausführt.

## Fehlerbehebung

1. **Authentifizierungsfehler**: Stellen Sie sicher, dass die Datei `credentials.json` korrekt im Verzeichnis platziert ist und die richtigen Berechtigungen enthält.

2. **Token-Probleme**: Wenn Probleme mit dem gespeicherten Token auftreten, löschen Sie die Datei `token.pickle` und führen Sie die Authentifizierung erneut durch.

3. **API-Limits**: Die Google Calendar API hat Nutzungslimits. Bei Problemen prüfen Sie die [Google Cloud Console](https://console.cloud.google.com/) auf mögliche Ratenbegrenzungen.

4. **Darstellungsprobleme**: Bei Problemen mit der Darstellung der importierten Termine passen Sie die Konvertierungsfunktionen in `calendar_todo_integration.py` an. 