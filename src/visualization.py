# File 3: visualization.py
# Contains all visualization and GUI components

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
from data_models import Config, TodoManager
from datetime import datetime


class BarChartApp(QWidget):
    def __init__(self, data_dict, total_actual_times, start_times):
        super().__init__()
        self.data_dict = data_dict
        self.start_times = start_times
        self.total_actual_times = total_actual_times
        
        # Initialize Todo-Manager for color assignment
        self.base_dir = Config.get_base_dir()
        self.todo_manager = TodoManager(self.base_dir)
        
        # Registriere bei Config für Datumsaktualisierungen
        Config.register_widget(self)
        
        self.setup_ui()
        self.setup_timer()
        self.draw_chart()

    def setup_ui(self):
        """Initializes the UI components"""
        layout = QVBoxLayout(self)
        self.setWindowTitle("Working Time Visualization")

        # Prepare Matplotlib Canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        
        # Show only the chart, no info panels
        layout.addWidget(self.canvas)

    def setup_timer(self):
        """Sets up the timer for automatic updates"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(Config.REFRESH_INTERVAL)  # Update every 36 seconds
        print(f"Auto-refresh activated: Every {Config.REFRESH_INTERVAL/1000} seconds")

    def refresh_data(self):
        """Updates the data and display"""
        print("Updating data...")
        
        # Reload data (without detailed output)
        from data_processing import DataManager
        data_manager = DataManager()
        self.data_dict, self.total_actual_times, self.start_times = data_manager.load_all_data(verbose=False)
        
        # Update Todo-Manager
        self.todo_manager = TodoManager(self.base_dir)
        
        # Redraw chart
        self.draw_chart()
        
        print("Update completed.")

    def draw_chart(self):
        """Draws a modern, more appealing bar chart with task-specific colors"""
        self.ax.clear()
        categories = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        x_pos = np.arange(len(categories))
        bar_width = 0.6  # Wider bars for a more modern look
        
        # Colors for a modern color scheme
        default_color = '#3498db'  # Standard blue for tasks without color
        highlight_color = '#2ecc71'  # Green for achieved hour goals
        background_color = '#ececec'  # Changed to requested background color
        grid_color = '#A0A0A0'  # Light gray grid lines
        text_color = '#2c3e50'  # Dark blue/gray for text
        
        # Set background
        self.figure.patch.set_facecolor(background_color)
        self.ax.set_facecolor(background_color)
        
        # Target work hours (e.g. 8 hours per day for weekdays, 0 for weekends)
        target_hours = [8.0, 8.0, 8.0, 8.0, 8.0, 0.0, 0.0]  # Mon-Fri: 8h, Sat-Sun: 0h
        
        # Draw bars for each day
        for day_idx in range(1, 8):  # Index 1-7 for Monday-Sunday
            if day_idx in self.data_dict:
                day_data = self.data_dict[day_idx]
                last_valid_bar = None
                daily_total = 0.0 if day_idx-1 >= len(self.total_actual_times) else self.total_actual_times[day_idx-1]
                
                # Process all work intervals of the day
                for i, row in enumerate(day_data[:-1]):  # Ignore last row
                    if row["Start"] != "False" and row["Actual Time"] > 0:
                        start = Config.time_to_decimal(row["Start"])
                        duration = row["Actual Time"] / 3600
                        
                        # Determine color from todo.json, if task is defined
                        task_color = default_color
                        
                        # Check if task information is present in the row
                        if "Task" in row and row["Task"].strip():
                            task_name = row["Task"].strip()
                            # Retrieve color from the Todo-Manager
                            task_info = self.todo_manager.task_info.get(task_name, {})
                            if "color" in task_info:
                                task_color = task_info["color"]
                        
                        # Draw bar with task-specific color
                        bar = self.ax.bar(
                            x_pos[day_idx-1], 
                            duration,
                            bottom=start,
                            width=bar_width,
                            color=task_color,
                            alpha=0.85,
                            edgecolor='none',
                            zorder=3
                        )
                        
                        last_valid_bar = bar
                
                # Display total time above last bar with a more modern style
                if last_valid_bar and day_idx-1 < len(self.total_actual_times):
                    total_time = self.total_actual_times[day_idx-1]
                    bar_top = last_valid_bar[0].get_height() + last_valid_bar[0].get_y()
                    
                    # Hour count as simple black number
                    self.ax.text(
                        x_pos[day_idx-1], 
                        bar_top + 0.8, 
                        f"{total_time:.2f}h",
                        ha='center', 
                        va='center',
                        fontsize=10,
                        fontweight='normal',
                        color='black',  # Black number
                        zorder=4
                    )

        # Highlight horizontal lines for work hours (9-17)
        self.ax.axhspan(9, 17, color='#ececec', alpha=0.5, zorder=1)  # Changed to match background
        
        # Chart formatting
        self.ax.set_ylim(7, 20)
        self.ax.set_yticks(np.arange(8, 21, 1))
        self.ax.set_yticklabels([f"{h}:00" for h in range(8, 21)], fontsize=9, color=text_color)
        self.ax.set_xticks(x_pos)
        
        # Formatted X-axis labels with weekday and start time
        formatted_labels = []
        for day, time in zip(categories, self.start_times):
            # Hole das aktuelle Wochendatum aus Config
            week_dates = Config.get_current_week_dates()
            date_str_raw = week_dates.get(day, "")
            
            # Konvertiere das Datum von "DD-MM-YY" zu "DD.MM."
            if date_str_raw:
                try:
                    day_month = date_str_raw.split('-')[:2]  # Nur Tag und Monat nehmen
                    date_str = f"{day_month[0]}.{day_month[1]}."
                except:
                    date_str = date_str_raw
            else:
                date_str = ""
            
            if time.strip() not in ['', ' ']:
                formatted_labels.append(f"{day}\n{date_str}\n{time}")
            else:
                formatted_labels.append(f"{day}\n{date_str}")
        
        # Anpassen der Schriftart entsprechend dem Haupt-Stylesheet
        self.ax.set_xticklabels(formatted_labels, fontsize=9, color=text_color, fontfamily='sans-serif')
        
        # Darker grid lines
        self.ax.grid(True, axis='y', linestyle='-', alpha=0.4, color=grid_color, zorder=0)
        
        # Display week total
        week_total = sum(self.total_actual_times)
        week_goal = sum(target_hours)  # Sum of daily goals
        percentage = (week_total / week_goal) * 100 if week_goal > 0 else 0
        
        # Remove axis lines for a cleaner look
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color(grid_color)
        self.ax.spines['bottom'].set_color(grid_color)
        
        # Highlight today
        today = datetime.today().weekday()  # 0 = Monday, 6 = Sunday
        if 0 <= today <= 6:
            self.ax.get_xticklabels()[today].set_color(highlight_color)
            self.ax.get_xticklabels()[today].set_fontweight('extra bold')
        
        # Optimize layout
        self.figure.tight_layout(pad=2.0)
        self.canvas.draw()

    def closeEvent(self, event):
        """Wird aufgerufen, wenn das Fenster geschlossen wird"""
        # Bei Schließen abmelden, um Speicherlecks zu vermeiden
        Config.unregister_widget(self)
        super().closeEvent(event)