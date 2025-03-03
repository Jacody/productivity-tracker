
# File 4: csv_reader.py
# Application entry point for reading CSV files and visualizing data

import sys
from PyQt5.QtWidgets import QApplication

from data_processing import DataManager
from visualization import BarChartApp

# Main entry point - compatible with existing structure
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Initialize DataManager
    data_manager = DataManager()
    
    # Load data
    data_dict, total_actual_times, start_times = data_manager.load_all_data()
    
    # Output enhanced statistics with Todo data
    data_manager.print_enhanced_statistics()
    
    # Start GUI
    window = BarChartApp(data_dict, total_actual_times, start_times)
    window.show()
    sys.exit(app.exec_())