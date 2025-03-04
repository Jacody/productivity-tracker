# File 1: data_models.py
# Contains basic data structures and configuration

import os
from datetime import datetime, timedelta

class Config:
    """Class for all configuration settings and general helper functions"""
    
    # Update interval in milliseconds (36 seconds)
    REFRESH_INTERVAL = 36000
    
    @staticmethod
    def get_current_week_dates():
        """Calculates dates for the current week (Monday to Sunday)"""
        # Get today's date (or set manually for testing)
        today = datetime.today()
        
        # Get current ISO calendar week
        year, week, weekday = today.isocalendar()
        
        # Calculate Monday of the current week
        monday = today - timedelta(days=weekday - 1)
        
        '''for testing'''
        #fixed_date = datetime(2025, 2, 28)  # Fixed date (Friday)
        
        # Calculate Monday of the same week
        #monday = fixed_date - timedelta(days=4)
        
        # Generate dates for Monday to Sunday in "DD-MM-YY" format
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        week_dates = {day: (monday + timedelta(days=i)).strftime("%d-%m-%y") for i, day in enumerate(days)}
        
        return week_dates
    

    @staticmethod
    def get_base_dir():
        """Finds the base directory of the application"""
        base_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
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