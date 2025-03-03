# File 2: data_processing.py
# Contains all CSV reading and data processing logic

import csv
from datetime import datetime
from tabulate import tabulate
from data_models import Config, TodoManager
import os

class DataProcessor:
    """Class for all data processing functions"""
    
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
        """Prints a summary of Hacken/Hustle times"""
        print("\n==== Hacken vs. Hustle Summary ====\n")
        
        # Format total times
        hacken_hours = hacken_hustle_data["hacken"]["total"] / 3600
        hustle_hours = hacken_hustle_data["hustle"]["total"] / 3600
        uncategorized_hours = hacken_hustle_data["uncategorized"]["total"] / 3600
        total_hours = hacken_hours + hustle_hours + uncategorized_hours
        
        # Calculate percentages (if total time > 0)
        hacken_percentage = (hacken_hours / total_hours * 100) if total_hours > 0 else 0
        hustle_percentage = (hustle_hours / total_hours * 100) if total_hours > 0 else 0
        uncategorized_percentage = (uncategorized_hours / total_hours * 100) if total_hours > 0 else 0
        
        # Table for the summary
        summary_table = [
            ["Hacken", f"{int(hacken_hours)}h {int((hacken_hours % 1) * 60)}m", f"{hacken_percentage:.1f}%"],
            ["Hustle", f"{int(hustle_hours)}h {int((hustle_hours % 1) * 60)}m", f"{hustle_percentage:.1f}%"],
            ["Uncategorized", f"{int(uncategorized_hours)}h {int((uncategorized_hours % 1) * 60)}m", f"{uncategorized_percentage:.1f}%"],
            ["Total", f"{int(total_hours)}h {int((total_hours % 1) * 60)}m", "100.0%"]
        ]
        
        print(tabulate(summary_table, headers=["Category", "Time", "Percentage"], tablefmt="grid"))
        
        # Details on individual categories
        for category, data in [
            ("Hacken Tasks", hacken_hustle_data["hacken"]["tasks"]), 
            ("Hustle Tasks", hacken_hustle_data["hustle"]["tasks"]), 
            ("Uncategorized Tasks", hacken_hustle_data["uncategorized"]["tasks"])
        ]:
            if data:  # Only display if data is available
                print(f"\n{category}:")
                print("-" * 40)
                
                # Sort tasks by time (descending)
                sorted_tasks = sorted(data.items(), key=lambda x: x[1], reverse=True)
                
                tasks_table = []
                for task, seconds in sorted_tasks:
                    hours = seconds / 3600
                    tasks_table.append([
                        task, 
                        f"{int(hours)}h {int((hours % 1) * 60)}m",
                        f"{(seconds / hacken_hustle_data[category.split(' ')[0].lower()]['total'] * 100):.1f}%" if hacken_hustle_data[category.split(' ')[0].lower()]['total'] > 0 else "0.0%"
                    ])
                
                print(tabulate(tasks_table, headers=["Task", "Time", "% of Category"], tablefmt="grid"))
        
        print("\n" + "=" * 50 + "\n")
    
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
        """Loads all CSV files for the current week"""
        self.data_dict = {}  # Reset data dictionary for refresh
        
        for index, (day, date) in enumerate(self.week_dates.items(), start=1):
            file_path = os.path.join(self.base_dir, "data", f"{date}.csv")
            if os.path.exists(file_path):
                if verbose:
                    print(f"Loading CSV file for {day}: {file_path}")
                self.data_dict[index] = DataProcessor.read_csv(file_path)
                if verbose:
                    DataProcessor.print_csv_nicely(self.data_dict[index], file_path)
            else:
                if verbose:
                    print(f"File does not exist: {file_path}")
        
        # Original calculation for backward compatibility
        self.total_actual_times = DataProcessor.sum_actual_times_original(self.data_dict)
        self.start_times = DataProcessor.extract_start_times(self.data_dict)
        
        # New calculation for task statistics
        _, self.task_totals, self.subtask_totals = DataProcessor.sum_actual_times_extended(self.data_dict)
        
        # Initialize Todo-Manager for categories
        todo_manager = TodoManager(self.base_dir)
        
        # Calculate Hacken vs. Hustle data
        self.hacken_hustle_data = DataProcessor.sum_hacken_hustle_times(self.task_totals, todo_manager)
        
        if verbose:
            print("Total actual times per dataset:", self.total_actual_times)
            # Output task statistics
            DataProcessor.print_task_statistics(self.task_totals, self.subtask_totals)
            # Output Hacken/Hustle statistics
            DataProcessor.print_hacken_hustle_summary(self.hacken_hustle_data)
        
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