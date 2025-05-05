# File: csv_reader.py
# Application entry point for reading CSV files and visualizing data
# Integrated version with both daily and weekly visualizations

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QSplitter
from PyQt5.QtCore import Qt

from data_processing import DataManager
from visualization import BarChartApp
from visualization_weekly import WeeklyVisualizationWidget

class IntegratedVisualizationApp(QWidget):
    """
    Main application window that integrates both the bar chart visualization
    and the weekly progress visualization side by side.
    """
    def __init__(self):
        super().__init__()
        
        # Initialize DataManager and load data
        self.data_manager = DataManager()
        self.data_dict, self.total_actual_times, self.start_times = self.data_manager.load_all_data()
        
        # Output enhanced statistics with Todo data
        self.data_manager.print_enhanced_statistics()
        
        # Setup UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI with a splitter for the two visualizations"""
        # Set window properties
        self.setWindowTitle("Time Tracking Visualization")
        self.resize(1200, 600)  # Wider window to accommodate both visualizations
        
        # Create main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Create and add the bar chart visualization (left side)
        self.bar_chart = BarChartApp(self.data_dict, self.total_actual_times, self.start_times)
        splitter.addWidget(self.bar_chart)
        
        # Create and add the weekly visualization (right side)
        self.weekly_viz = WeeklyVisualizationWidget()
        splitter.addWidget(self.weekly_viz)
        
        # Set initial sizes (60% for bar chart, 40% for weekly visualization)
        splitter.setSizes([600, 400])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Set the layout
        self.setLayout(main_layout)
        
    def closeEvent(self, event):
        """Wird aufgerufen, wenn das Fenster geschlossen wird"""
        # Achten Sie darauf, dass alle untergeordneten Widgets abgemeldet werden,
        # wenn sie sich bei Config.registered_widgets registriert haben
        # Hinweis: Die einzelnen Widgets sollten sich selbst abmelden
        super().closeEvent(event)

# For use in main.py - create a class that can be imported directly
class CsvVisualizerCombined(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for resizable panels
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Initialize DataManager and load data
        data_manager = DataManager()
        data_dict, total_actual_times, start_times = data_manager.load_all_data(verbose=False)
        
        # Create and add the bar chart visualization (left side)
        self.bar_chart = BarChartApp(data_dict, total_actual_times, start_times)
        self.splitter.addWidget(self.bar_chart)
        
        # Create and add the weekly visualization (right side)
        self.weekly_viz = WeeklyVisualizationWidget()
        self.splitter.addWidget(self.weekly_viz)
        
        # Set initial sizes (60% for bar chart, 40% for weekly visualization)
        self.splitter.setSizes([700, 300])
        
        # Add splitter to main layout
        self.layout.addWidget(self.splitter)
        
        # Set the layout
        self.setLayout(self.layout)
    
    def closeEvent(self, event):
        """Wird aufgerufen, wenn das Fenster geschlossen wird"""
        # Achten Sie darauf, dass alle untergeordneten Widgets abgemeldet werden,
        # wenn sie sich bei Config.registered_widgets registriert haben
        # Hinweis: Die einzelnen Widgets sollten sich selbst abmelden
        super().closeEvent(event)

# Main entry point when run directly
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create and show the integrated application
    window = IntegratedVisualizationApp()
    window.show()
    
    sys.exit(app.exec_())