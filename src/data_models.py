# File 1: data_models.py
# Contains basic data structures and configuration

import os
from datetime import datetime, timedelta

class Config:
    """Class for all configuration settings and general helper functions"""
    
    # Update interval in milliseconds (36 seconds)
    REFRESH_INTERVAL = 36000
    
    # Statische Variable für benutzerdefiniertes Datum
    custom_date = None
    
    # Liste der registrierten Widgets, die benachrichtigt werden sollen
    registered_widgets = []
    
    @staticmethod
    def register_widget(widget):
        """Registriert ein Widget, das benachrichtigt werden soll, wenn sich das Datum ändert"""
        if widget not in Config.registered_widgets:
            Config.registered_widgets.append(widget)
    
    @staticmethod
    def unregister_widget(widget):
        """Entfernt ein Widget aus der Liste der zu benachrichtigenden Widgets"""
        if widget in Config.registered_widgets:
            Config.registered_widgets.remove(widget)
    
    @staticmethod
    def notify_widgets():
        """Benachrichtigt alle registrierten Widgets, dass sich das Datum geändert hat"""
        for widget in Config.registered_widgets:
            if hasattr(widget, 'refresh_data'):
                widget.refresh_data()
    
    @staticmethod
    def set_custom_date(date):
        """Setzt ein benutzerdefiniertes Datum für die Wochenanzeige und benachrichtigt alle registrierten Widgets"""
        Config.custom_date = date
        Config.notify_widgets()
    
    @staticmethod
    def get_current_week_dates():
        """Calculates dates for the current week (Monday to Sunday)"""
        # Get today's date (or set manually for testing)
        today = datetime.today()
        
        # Benutze benutzerdefiniertes Datum falls vorhanden
        if Config.custom_date:
            today = Config.custom_date
        
        # Get current ISO calendar week
        year, week, weekday = today.isocalendar()
        
        # Calculate Monday of the current week
        monday = today - timedelta(days=weekday - 1)
        
        # Generate dates for Monday to Sunday in "DD-MM-YY" format
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        week_dates = {day: (monday + timedelta(days=i)).strftime("%d-%m-%y") for i, day in enumerate(days)}
        
        return week_dates
    

    @staticmethod
    def get_base_dir():
        """Finds the base directory of the application"""
        # Zunächst den Pfad zum aktuellen Skript bestimmen
        current_file_path = os.path.abspath(__file__)
        # Der src-Ordner ist der übergeordnete Ordner dieses Skripts
        src_dir = os.path.dirname(current_file_path)
        # Das Basisverzeichnis ist der übergeordnete Ordner des src-Ordners
        base_dir = os.path.dirname(src_dir)
        print("Base Directory:", base_dir)
        return base_dir
    
    @staticmethod
    def time_to_decimal(time_str):
        """Helper function to convert time strings to decimal hours"""
        try:
            if time_str.strip() in ['', 'False']:
                return 0.0
            parts = list(map(int, time_str.split(':')))
            return parts[0] + parts[1]/60 + (parts[2] if len(parts)>2 else 0)/3600
        except:
            return 0.0

class TodoManager:
    """Class for managing Todo data"""
    
    def __init__(self, base_dir):
        import json
        
        self.base_dir = base_dir
        self.todo_path = os.path.join(base_dir, "data", "todo.json")
        self.todo_data = self.load_todo()
        self.task_info = self.prepare_task_info()
    
    def load_todo(self):
        """Loads the Todo file"""
        import json
        
        if os.path.exists(self.todo_path):
            print(f"Loading Todo file: {self.todo_path}")
            try:
                with open(self.todo_path, "r", encoding="utf-8") as file:
                    return json.load(file)
            except Exception as e:
                print(f"Error loading todo file: {e}")
                return {"tasks": []}
        else:
            print(f"Todo file not found: {self.todo_path}")
            return {"tasks": []}  # Return empty structure if no file exists
    
    def prepare_task_info(self):
        """Prepares a dictionary with task information for quick access"""
        task_info = {}
        for task in self.todo_data.get("tasks", []):
            task_name = task.get("task", "")
            if task_name:
                task_info[task_name] = {
                    "type": task.get("type", "N/A"),
                    "category": task.get("category", "N/A"),
                    "estimated_time": task.get("estimated_time", "N/A"),
                    "color": task.get("color", "#cccccc"),  # Default color if none specified
                    "subtasks": {}
                }
                
                # Prepare subtask information
                for subtask in task.get("subtasks", []):
                    subtask_name = subtask.get("subtask", "")
                    if subtask_name:
                        task_info[task_name]["subtasks"][subtask_name] = {
                            "status": subtask.get("status", "N/A"),
                            "estimated_time": subtask.get("estimated_time", "N/A")
                        }
        
        return task_info