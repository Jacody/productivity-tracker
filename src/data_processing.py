# File 2: data_processing.py
# Contains all CSV reading and data processing logic

import csv
from datetime import datetime
from tabulate import tabulate
from data_models import Config, TodoManager
import os
import json

class DataProcessor:
    """Class for all data processing functions"""
    
    @staticmethod
    def format_seconds(seconds):
        """Konvertiert Sekunden in ein lesbareres Format (Stunden und Minuten)"""
        hours = seconds / 3600
        return f"{int(hours)}h {int((hours % 1) * 60)}m"
    
    @staticmethod
    def read_csv(file_path):
        """Reads a CSV file and returns the data as a list of dictionaries."""
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = [row for row in reader]
            
            # Remove all rows at the beginning that are not 1,1,1
            while data and (int(data[0]["Mode"]) != 1 or int(data[0]["Status"]) != 1 or int(data[0]["Work"]) != 1):
                data.pop(0)
            
            # Add last row for live timer
            current_time = datetime.now().strftime("%H:%M:%S")
            new_row = {"Mode": "0", "Status": "0", "Work": "0", "Time": current_time }
            data.append(new_row)
            
            # Add extra columns if not present in CSV
            for row in data:
                row["Start"] = row["Time"] if int(row["Mode"]) == 1 and int(row["Status"]) == 1 and int(row["Work"]) == 1 else "False"
            
            # Assign "Stop" time from the next row
            for i in range(len(data) - 1):
                if data[i]["Start"] != "False":
                    data[i]["Stop"] = data[i + 1]["Time"]
            
            # Calculate "Actual Time"
            for row in data:
                try:
                    if row["Start"] != "False":
                        start_time = datetime.strptime(row["Start"], "%H:%M:%S")
                        stop_time = datetime.strptime(row["Stop"], "%H:%M:%S")
                        actual_time = (stop_time - start_time).total_seconds()
                        row["Actual Time"] = int(actual_time)
                    else:
                        row["Actual Time"] = 0
                except Exception:
                    row["Actual Time"] = 0
            return data
        
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    @staticmethod
    def print_csv_nicely(data, file_path):
        """Prints the CSV data in a formatted table."""
        if not data:
            print(f"No data found for {file_path}")
            return
        
        headers = list(data[0].keys())  # Extract column names
        rows = [list(row.values()) for row in data]  # Extract row values
        
        print(f"Data from {file_path}:")
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        print("\n" + "=" * 50 + "\n")  # Separator for better readability
    
    @staticmethod
    def sum_actual_times(data_dict):
        """
        Original function (renamed for backward compatibility)
        Sums up all actual times for each data element and converts to an array of hours.
        """
        return DataProcessor.sum_actual_times_original(data_dict)
    
    @staticmethod
    def sum_actual_times_original(data_dict):
        """
        Original function for backward compatibility with fixed handling of missing days
        Sums up all actual times for each data element and converts to an array of hours.
        Ensures all 7 days of the week are represented with 0.0 for missing days.
        """
        # Initialize array with zeros for all 7 days (Monday to Sunday)
        total_actual_times = [0.0] * 7
        
        # Fill in actual data where available
        for index in sorted(data_dict.keys()):  # Sort keys to maintain order
            if index <= 7:  # Ensure we only process days 1-7 (Monday-Sunday)
                total_time = sum(int(row["Actual Time"]) for row in data_dict[index] if str(row["Actual Time"]).isdigit())
                total_actual_times[index-1] = round(total_time / 3600, 2)  # Convert seconds to hours
        
        return total_actual_times

    # Similarly, update the sum_actual_times_extended method

    @staticmethod
    def sum_actual_times_extended(data_dict):
        """
        Extended function for calculating task times with fixed handling of missing days
        Sums up all actual times for each data element and calculates task and subtask totals.
        Ensures all 7 days of the week are represented with 0.0 for missing days.
        
        Returns:
        - total_actual_times: List of total hours per day (7 elements for Mon-Sun)
        - task_totals: Dictionary with total seconds per task
        - subtask_totals: Dictionary with total seconds per subtask combination
        """
        # Initialize array with zeros for all 7 days (Monday to Sunday)
        total_actual_times = [0.0] * 7
        task_totals = {}
        subtask_totals = {}
        
        for index in sorted(data_dict.keys()):  # Sort keys to maintain order
            if index <= 7:  # Ensure we only process days 1-7 (Monday-Sunday)
                # Calculate sum of times for the day
                total_time = sum(int(row["Actual Time"]) for row in data_dict[index] if str(row["Actual Time"]).isdigit())
                total_actual_times[index-1] = round(total_time / 3600, 2)  # Convert seconds to hours
                
                # Analyze tasks and subtasks in this dataset
                for row in data_dict[index]:
                    if (str(row["Actual Time"]).isdigit() and 
                        "Task" in row and "Subtask" in row and 
                        row["Start"] != "False"):
                        
                        actual_time = int(row["Actual Time"])
                        task = row.get("Task", "").strip()
                        subtask = row.get("Subtask", "").strip()
                        
                        # Create subtask key (Task + Subtask combination)
                        task_subtask_key = f"{task}:{subtask}" if task and subtask else task or "(No Task)"
                        
                        # Update task counter
                        if task:
                            task_totals[task] = task_totals.get(task, 0) + actual_time
                        
                        # Count Task + Subtask combination
                        subtask_totals[task_subtask_key] = subtask_totals.get(task_subtask_key, 0) + actual_time
        
        return total_actual_times, task_totals, subtask_totals

    # Finally, add a helper function to print the day-by-day breakdown in DataManager
        
    @staticmethod 
    def sum_hacken_hustle_times(task_totals, todo_manager):
        """
        Calculate sum of times for Hacken and Hustle
        
        Returns:
        - hacken_time: Total time in seconds for 'Hacken' categories
        - hustle_time: Total time in seconds for 'Hustle' categories
        - uncategorized_time: Total time in seconds for uncategorized tasks
        """
        hacken_time = 0
        hustle_time = 0
        uncategorized_time = 0
        
        # Task lists for detailed output
        hacken_tasks = {}
        hustle_tasks = {}
        uncategorized_tasks = {}
        
        # Iterate through all tasks and sum by category
        for task_name, seconds in task_totals.items():
            task_info = todo_manager.task_info.get(task_name, {})
            category = task_info.get("category", "").lower()  # Category in lowercase for comparison
            
            if "hacken" in category:
                hacken_time += seconds
                hacken_tasks[task_name] = seconds
            elif "hustle" in category:
                hustle_time += seconds
                hustle_tasks[task_name] = seconds
            else:
                uncategorized_time += seconds
                uncategorized_tasks[task_name] = seconds
        
        return {
            "hacken": {"total": hacken_time, "tasks": hacken_tasks},
            "hustle": {"total": hustle_time, "tasks": hustle_tasks},
            "uncategorized": {"total": uncategorized_time, "tasks": uncategorized_tasks}
        }
    
    @staticmethod
    def print_hacken_hustle_summary(hacken_hustle_data):
        """Prints a summary of Hacken vs. Hustle time distribution"""
        
        # Calculate totals
        hacken_time = hacken_hustle_data["hacken"]["total"]
        hustle_time = hacken_hustle_data["hustle"]["total"]
        uncategorized_time = hacken_hustle_data["uncategorized"]["total"]
        total_time = hacken_time + hustle_time + uncategorized_time
        
        # Create a table for Hacken vs. Hustle comparison
        table_data = []
        
        # Format time for each category
        hacken_formatted = DataProcessor.format_seconds(hacken_time)
        hustle_formatted = DataProcessor.format_seconds(hustle_time)
        uncategorized_formatted = DataProcessor.format_seconds(uncategorized_time)
        total_formatted = DataProcessor.format_seconds(total_time)
        
        # Calculate percentages
        hacken_percent = (hacken_time / total_time * 100) if total_time > 0 else 0
        hustle_percent = (hustle_time / total_time * 100) if total_time > 0 else 0
        uncategorized_percent = (uncategorized_time / total_time * 100) if total_time > 0 else 0
        
        # Add rows
        table_data.append(["Hacken", hacken_formatted, f"{hacken_percent:.1f}%"])
        table_data.append(["Hustle", hustle_formatted, f"{hustle_percent:.1f}%"])
        table_data.append(["Uncategorized", uncategorized_formatted, f"{uncategorized_percent:.1f}%"])
        table_data.append(["Total", total_formatted, "100.0%"])
        
        # Print the table
        print("\n==== Hacken vs. Hustle Summary ====\n")
        print(tabulate(table_data, headers=["Category", "Time", "Percentage"], tablefmt="grid"))
        
        # Print tables for each category's tasks
        print("\nHacken Tasks:")
        print("-" * 40)
        if hacken_hustle_data["hacken"]["tasks"]:
            hacken_tasks = []
            for task, seconds in hacken_hustle_data["hacken"]["tasks"].items():
                percentage = (seconds / hacken_time * 100) if hacken_time > 0 else 0
                hacken_tasks.append([task, DataProcessor.format_seconds(seconds), f"{percentage:.1f}%"])
            print(tabulate(hacken_tasks, headers=["Task", "Time", "% of Category"], tablefmt="grid"))
        else:
            print("No Hacken tasks recorded.")
        
        if hustle_time > 0:
            print("\nHustle Tasks:")
            print("-" * 40)
            if hacken_hustle_data["hustle"]["tasks"]:
                hustle_tasks = []
                for task, seconds in hacken_hustle_data["hustle"]["tasks"].items():
                    percentage = (seconds / hustle_time * 100) if hustle_time > 0 else 0
                    hustle_tasks.append([task, DataProcessor.format_seconds(seconds), f"{percentage:.1f}%"])
                print(tabulate(hustle_tasks, headers=["Task", "Time", "% of Category"], tablefmt="grid"))
            else:
                print("No Hustle tasks recorded.")
        
        print("\n" + "=" * 50)

    @staticmethod
    def print_subtasks_by_category(subtask_totals, todo_manager):
        """Prints detailed subtasks grouped by category (Hacken/Hustle)"""
        
        # Debug-Ausgabe zur Fehleranalyse
        print("\nAlle Subtasks:")
        for key, value in subtask_totals.items():
            print(f"Key: '{key}', Value: {value}")
        
        # Erstelle Dictionaries für jede Kategorie
        hacken_subtasks = {}
        hustle_subtasks = {}
        uncategorized_subtasks = {}
        
        # Iteriere durch alle Subtasks und sortiere sie nach Kategorie
        for task_subtask, seconds in subtask_totals.items():
            parts = task_subtask.split(':')
            if len(parts) == 2:
                task = parts[0].strip()
                subtask = parts[1].strip()
                
                # Hole Aufgabeninformationen aus dem Todo-Manager
                task_info = todo_manager.task_info.get(task, {})
                category = task_info.get("category", "uncategorized").lower()
                
                # Füge zur entsprechenden Kategorie hinzu
                if category == "hacken":
                    hacken_subtasks[task_subtask] = seconds
                elif category == "hustle":
                    hustle_subtasks[task_subtask] = seconds
                else:
                    uncategorized_subtasks[task_subtask] = seconds
        
        # Berechne Gesamtzeiten
        hacken_total = sum(hacken_subtasks.values())
        hustle_total = sum(hustle_subtasks.values())
        uncategorized_total = sum(uncategorized_subtasks.values())
        
        # Erstelle und drucke Tabelle für Hacken Subtasks
        print("\n==== Detaillierte Subtasks nach Kategorie ====\n")
        
        if hacken_subtasks:
            print("Hacken Subtasks:")
            print("-" * 60)
            
            # Sortiere Subtasks nach Zeit (absteigend)
            sorted_hacken = sorted(hacken_subtasks.items(), key=lambda x: x[1], reverse=True)
            
            # Erstelle Tabellendaten
            hacken_table = []
            for task_subtask, seconds in sorted_hacken:
                task, subtask = task_subtask.split(':')
                percentage = (seconds / hacken_total * 100) if hacken_total > 0 else 0
                formatted_time = DataProcessor.format_seconds(seconds)
                hacken_table.append([task.strip(), subtask.strip(), formatted_time, f"{percentage:.1f}%"])
            
            # Drucke Tabelle
            print(tabulate(hacken_table, headers=["Task", "Subtask", "Time", "% of Category"], tablefmt="grid"))
        else:
            print("Keine Hacken Subtasks aufgezeichnet.")
        
        # Tabelle für Hustle Subtasks
        if hustle_subtasks:
            print("\nHustle Subtasks:")
            print("-" * 60)
            
            # Sortiere Subtasks nach Zeit (absteigend)
            sorted_hustle = sorted(hustle_subtasks.items(), key=lambda x: x[1], reverse=True)
            
            # Erstelle Tabellendaten
            hustle_table = []
            for task_subtask, seconds in sorted_hustle:
                task, subtask = task_subtask.split(':')
                percentage = (seconds / hustle_total * 100) if hustle_total > 0 else 0
                formatted_time = DataProcessor.format_seconds(seconds)
                hustle_table.append([task.strip(), subtask.strip(), formatted_time, f"{percentage:.1f}%"])
            
            # Drucke Tabelle
            print(tabulate(hustle_table, headers=["Task", "Subtask", "Time", "% of Category"], tablefmt="grid"))
        else:
            print("Keine Hustle Subtasks aufgezeichnet.")
        
        # Tabelle für nicht kategorisierte Subtasks
        if uncategorized_subtasks:
            print("\nUncategorized Subtasks:")
            print("-" * 60)
            
            # Sortiere Subtasks nach Zeit (absteigend)
            sorted_uncategorized = sorted(uncategorized_subtasks.items(), key=lambda x: x[1], reverse=True)
            
            # Erstelle Tabellendaten
            uncategorized_table = []
            for task_subtask, seconds in sorted_uncategorized:
                task, subtask = task_subtask.split(':')
                percentage = (seconds / uncategorized_total * 100) if uncategorized_total > 0 else 0
                formatted_time = DataProcessor.format_seconds(seconds)
                uncategorized_table.append([task.strip(), subtask.strip(), formatted_time, f"{percentage:.1f}%"])
            
            # Drucke Tabelle
            print(tabulate(uncategorized_table, headers=["Task", "Subtask", "Time", "% of Category"], tablefmt="grid"))
        
        print("\n" + "=" * 50)

    @staticmethod
    def print_task_statistics(task_totals, subtask_totals):
        """Prints a formatted overview of task and subtask times"""
        print("\n==== Task Statistics ====\n")
        
        # Sort by time spent (descending)
        sorted_tasks = sorted(task_totals.items(), key=lambda x: x[1], reverse=True)
        
        print("Total time per task:")
        print("======================")
        task_rows = []
        for task, seconds in sorted_tasks:
            hours = seconds / 3600
            minutes = (seconds % 3600) / 60
            task_rows.append([task, f"{int(hours)}h {int(minutes)}m", seconds])
        
        print(tabulate(task_rows, headers=["Task", "Time", "Seconds"], tablefmt="grid"))
        
        # Sort by time spent (descending)
        sorted_subtasks = sorted(subtask_totals.items(), key=lambda x: x[1], reverse=True)
        
        print("\nTotal time per task + subtask:")
        print("====================================")
        subtask_rows = []
        for task_subtask, seconds in sorted_subtasks:
            hours = seconds / 3600
            minutes = (seconds % 3600) / 60
            task, *subtask_parts = task_subtask.split(":", 1)
            subtask = subtask_parts[0] if subtask_parts else "-"
            subtask_rows.append([task, subtask, f"{int(hours)}h {int(minutes)}m", seconds])
        
        print(tabulate(subtask_rows, headers=["Task", "Subtask", "Time", "Seconds"], tablefmt="grid"))
        print("\n" + "=" * 50 + "\n")
    
    @staticmethod
    def print_enhanced_task_statistics(task_totals, subtask_totals, todo_manager):
        """Prints an enhanced formatted overview of task and subtask times with Todo information"""
        print("\n==== Enhanced Task Statistics ====\n")
        
        # Sort by time spent (descending)
        sorted_tasks = sorted(task_totals.items(), key=lambda x: x[1], reverse=True)
        
        print("Total time per task with Todo data:")
        print("====================================")
        task_rows = []
        for task, seconds in sorted_tasks:
            # Format time
            hours = seconds / 3600
            minutes = (seconds % 3600) / 60
            time_str = f"{int(hours)}h {int(minutes)}m"
            
            # Retrieve Todo information
            task_info = todo_manager.task_info.get(task, {})
            task_type = task_info.get("type", "N/A")
            category = task_info.get("category", "N/A")
            estimated_time = task_info.get("estimated_time", "N/A")
            color = task_info.get("color", "#cccccc")
            
            # Convert estimated time to hours:minutes, if possible
            est_time_display = "N/A"
            if estimated_time != "N/A":
                try:
                    est_hours = float(estimated_time)
                    est_hours_int = int(est_hours)
                    est_minutes = int((est_hours - est_hours_int) * 60)
                    est_time_display = f"{est_hours_int}h {est_minutes}m"
                except ValueError:
                    est_time_display = estimated_time
            
            # Calculate progress (actual/estimated in %)
            progress = "N/A"
            if estimated_time != "N/A" and estimated_time != "0":
                try:
                    est_hours = float(estimated_time)
                    act_hours = hours
                    if est_hours > 0:
                        progress = f"{(act_hours / est_hours) * 100:.1f}%"
                except ValueError:
                    progress = "N/A"
            
            # Add row to array
            task_rows.append([
                task, 
                time_str, 
                est_time_display, 
                progress,
                task_type, 
                category,
                color,  # Color added
                seconds
            ])
        
        # Print table
        print(tabulate(
            task_rows, 
            headers=["Task", "Actual Time", "Estimated Time", "Progress", "Type", "Category", "Color", "Seconds"], 
            tablefmt="grid"
        ))
        
        # Sort by time spent (descending)
        sorted_subtasks = sorted(subtask_totals.items(), key=lambda x: x[1], reverse=True)
        
        print("\nTotal time per task + subtask with Todo data:")
        print("==================================================")
        subtask_rows = []
        for task_subtask, seconds in sorted_subtasks:
            # Format time
            hours = seconds / 3600
            minutes = (seconds % 3600) / 60
            time_str = f"{int(hours)}h {int(minutes)}m"
            
            # Separate task and subtask
            task, *subtask_parts = task_subtask.split(":", 1)
            subtask = subtask_parts[0] if subtask_parts else "-"
            
            # Retrieve Todo information
            task_info = todo_manager.task_info.get(task, {})
            subtask_info = task_info.get("subtasks", {}).get(subtask, {})
            
            task_type = task_info.get("type", "N/A")
            category = task_info.get("category", "N/A")
            subtask_status = subtask_info.get("status", "N/A")
            estimated_time = subtask_info.get("estimated_time", "N/A")
            color = task_info.get("color", "#cccccc")
            
            # Convert estimated time to hours:minutes, if possible
            est_time_display = "N/A"
            if estimated_time != "N/A":
                try:
                    est_hours = float(estimated_time)
                    est_hours_int = int(est_hours)
                    est_minutes = int((est_hours - est_hours_int) * 60)
                    est_time_display = f"{est_hours_int}h {est_minutes}m"
                except ValueError:
                    est_time_display = estimated_time
            
            # Calculate progress (actual/estimated in %)
            progress = "N/A"
            if estimated_time != "N/A" and estimated_time != "0":
                try:
                    est_hours = float(estimated_time)
                    act_hours = hours
                    if est_hours > 0:
                        progress = f"{(act_hours / est_hours) * 100:.1f}%"
                except ValueError:
                    progress = "N/A"
            
            # Add row to array
            subtask_rows.append([
                task, 
                subtask, 
                time_str, 
                est_time_display,
                progress,
                subtask_status,
                task_type, 
                category,
                color,  # Color added
                seconds
            ])
        
        # Print table
        print(tabulate(
            subtask_rows, 
            headers=[
                "Task", "Subtask", "Actual Time", "Estimated Time", 
                "Progress", "Status", "Type", "Category", "Color", "Seconds"
            ], 
            tablefmt="grid"
        ))
        print("\n" + "=" * 50 + "\n")
    
    
    @staticmethod
    def extract_start_times(data_dict):
        """Extracts the first start time from each dataset."""
        start_times = [' ', ' ', ' ', ' ', ' ', ' ', ' ']  # Now 7 elements for Mon-Sun
        
        # Iterate through all loaded CSV data
        for index, data in data_dict.items():
            if data:  # Ensure the file contains data
                for row in data:
                    if row["Start"] != "False":
                        # Save time without seconds (HH:MM)
                        start_time = datetime.strptime(row["Start"], "%H:%M:%S").strftime("%H:%M")
                        start_times[index - 1] = start_time  # Save the time at the correct position
                        break  # Exit loop for this file once a start time is found
        
        return start_times
    
    @staticmethod
    def update_todo_with_actual_times(subtask_totals, todo_manager):
        """Aktualisiert die tatsächlichen Zeiten der Subtasks in der todo.json Datei"""
        # Lade die aktuelle todo.json Datei
        todo_data = todo_manager.todo_data
        modified = False
        
        # Durchlaufe alle Tasks und Subtasks
        for task in todo_data.get("tasks", []):
            task_name = task.get("task", "")
            
            for subtask in task.get("subtasks", []):
                subtask_name = subtask.get("subtask", "")
                
                # Suche nach den tatsächlichen Zeiten in den subtask_totals
                key = f"{task_name}:{subtask_name}"
                if key in subtask_totals:
                    # Konvertiere Sekunden in Stunden
                    hours = subtask_totals[key] / 3600
                    # Runde auf 2 Dezimalstellen
                    formatted_time = round(hours, 2)
                    
                    # Aktualisiere die tatsächliche Zeit, wenn sie sich unterscheidet
                    if subtask.get("actual_time") != str(formatted_time):
                        subtask["actual_time"] = str(formatted_time)
                        modified = True
        
        # Speichere die aktualisierte todo.json Datei, falls Änderungen vorgenommen wurden
        if modified:
            try:
                with open(todo_manager.todo_path, "w", encoding="utf-8") as file:
                    json.dump(todo_data, file, indent=4)
                print(f"Todo-Datei mit tatsächlichen Zeiten aktualisiert: {todo_manager.todo_path}")
                return True
            except Exception as e:
                print(f"Fehler beim Speichern der Todo-Datei: {e}")
                return False
        
        return False

class DataManager:
    """Class for collecting and managing all data"""
    
    def __init__(self):
        self.week_dates = Config.get_current_week_dates()
        self.base_dir = Config.get_base_dir()
        self.data_dict = {}
        self.task_totals = {}
        self.subtask_totals = {}
        self.hacken_hustle_data = {}
        
    def load_all_data(self, verbose=True):
        """Loads and processes all data from CSV files"""
        
        base_dir = Config.get_base_dir()
        
        # Create a TodoManager to handle todo.json operations
        todo_manager = TodoManager(base_dir)
        
        # Week dates for file naming
        week_dates = Config.get_current_week_dates()
        
        # Load data for each day of the week
        self.data_dict = {}
        for i, (day, date_str) in enumerate(week_dates.items(), 1):
            csv_path = os.path.join(base_dir, "data", f"{date_str}.csv")
            
            if os.path.exists(csv_path):
                if verbose:
                    print(f"Loading CSV file for {day}: {csv_path}")
                csv_data = DataProcessor.read_csv(csv_path)
                if verbose:
                    DataProcessor.print_csv_nicely(csv_data, csv_path)
                self.data_dict[i] = csv_data
            else:
                if verbose:
                    print(f"File does not exist: {csv_path}")
                self.data_dict[i] = []
            
        if verbose:
            print(f"Loading Todo file: {os.path.join(base_dir, 'data', 'todo.json')}")
            
        # Calculate actual time spent for each dataset
        self.total_actual_times = DataProcessor.sum_actual_times(self.data_dict)
        if verbose:
            print(f"Total actual times per dataset: {self.total_actual_times}")
            
        # Extract start times from data
        self.start_times = DataProcessor.extract_start_times(self.data_dict)
        
        # Calculate total time per task and subtask
        self.total_actual_times, self.task_totals, self.subtask_totals = DataProcessor.sum_actual_times_extended(self.data_dict)
        
        # Calculate Hacken vs. Hustle statistics
        self.hacken_hustle_data = DataProcessor.sum_hacken_hustle_times(
            self.task_totals, 
            todo_manager
        )
        
        # Aktualisiere Todo-Daten mit den tatsächlichen Zeiten der Subtasks
        DataProcessor.update_todo_with_actual_times(self.subtask_totals, todo_manager)
        
        # Output Hacken/Hustle statistics
        DataProcessor.print_hacken_hustle_summary(self.hacken_hustle_data)
        
        # Output detaillierte Subtasks nach Kategorie
        DataProcessor.print_subtasks_by_category(self.subtask_totals, todo_manager)
        
        # Return original return values for backward compatibility
        return self.data_dict, self.total_actual_times, self.start_times
    
    def print_enhanced_statistics(self):
        """Prints enhanced statistics with Todo data"""
        # Initialize Todo-Manager
        todo_manager = TodoManager(self.base_dir)
        
        # Output enhanced statistics
        DataProcessor.print_enhanced_task_statistics(
            self.task_totals, 
            self.subtask_totals, 
            todo_manager
        )
        
        # Output Hacken/Hustle statistics
        DataProcessor.print_hacken_hustle_summary(self.hacken_hustle_data)

# Hauptausführungsblock, wird nur ausgeführt, wenn die Datei direkt gestartet wird
if __name__ == "__main__":
    print("Starte Datenverarbeitung...")
    data_manager = DataManager()
    data_manager.load_all_data(verbose=True)
    data_manager.print_enhanced_statistics()
    print("Datenverarbeitung abgeschlossen.")