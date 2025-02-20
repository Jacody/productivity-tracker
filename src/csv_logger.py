import csv
import os
from datetime import datetime

class CSVLogger:
    """Kümmert sich um das Speichern der Logs in einer CSV-Datei mit aktuellem Datum als Namen."""
    
    def __init__(self, folder_path=None):
        """Initialisiert den Logger und erstellt die Datei falls nötig."""
        # Standard-Ordner setzen, falls nicht übergeben
        self.folder_path = folder_path or "/Users/Coby/Desktop/GitHub/productivity-tracker/data"
        os.makedirs(self.folder_path, exist_ok=True)  # Ordner erstellen, falls nicht existiert

        # Dateiname nach aktuellem Datum setzen
        self.file_path = os.path.join(self.folder_path, datetime.now().strftime("%d-%m-%y") + ".csv")
        self.init_csv()

    def init_csv(self):
        """Erstellt die CSV-Datei mit Header, falls sie nicht existiert."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Mode", "Status", "Work", "Block", "Task", "Subtask", "Timer", "Time" ])  # Kopfzeile schreiben

    def log(self, mode, status, work, block, task, subtask, timer):
        """Speichert einen Eintrag in die CSV-Datei."""
        current_time = datetime.now().strftime("%H:%M:%S")
        data = [mode, status, work, block, task, subtask, timer, current_time]
        
        with open(self.file_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(data)

        #print(f"✅ Log gespeichert: {self.file_path}")
