import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                             QApplication, QFrame, QHBoxLayout)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush
from data_processing import DataProcessor, DataManager
from data_models import TodoManager, Config
from circular_progress import CircularProgressWidget

class WeeklyCircularProgress(CircularProgressWidget):
    """
    Modified circular progress widget for weekly hour tracking.
    Shows progress toward weekly goals instead of time tracking.
    """
    
    def __init__(self, title="Progress", color=QColor(74, 134, 232), parent=None):
        super().__init__(parent)
        
        self.title = title
        self.work_color = color  # Override the default color
        self.break_color = color  # Use same color for entire circle
        
        # Set size - made smaller
        self.setMinimumSize(150, 150)  # Smaller than before
        
        # Override values for progress tracking
        self.total_time_max = 100  # Use percentage (0-100)
        self.work_time_ratio = 1.0  # Use entire circle for progress
        self.work_time_max = self.total_time_max  # 100%
        self.break_time_max = 0  # No break segment
        
        # Override time text with progress percentage
        self.time_text = "0%"
        
        # Add hours text
        self.hours_text = "0 / 0"
    
    def set_progress(self, current, maximum):
        """Set progress as current/maximum values"""
        # Calculate percentage
        percentage = min(int((current / maximum) * 100), 100) if maximum > 0 else 0
        
        # Set time to represent percentage (0-100)
        super().set_current_time(percentage)
        
        # Override time text to show percentage
        self.time_text = f"{percentage}%"
        
        # We'll no longer use the built-in hours text
        # Instead we'll use external labels in the main UI
        self.hours_text = ""
        
        self.update()
    
    def paintEvent(self, event):
        """Override the paintEvent to customize appearance and hide the ARBEIT/PAUSE text"""
        # Don't call super().paintEvent() directly to avoid drawing the ARBEIT/PAUSE text
        # Instead, we'll replicate the parent's paintEvent but skip the status text
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get dimensions
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        diameter = min(width, height) - 40
        radius = diameter / 2
        
        # Draw background circle
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.bg_color)
        painter.drawEllipse(QRectF(center_x - radius, center_y - radius, diameter, diameter))
        
        # Determine if we're in break time
        is_break_time = self.current_time > self.work_time_max
        
        if self.current_time > 0:
            # Draw work time slice
            work_time_to_draw = min(self.current_time, self.work_time_max)
            if work_time_to_draw > 0:
                angle = work_time_to_draw / self.total_time_max * 360
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(self.work_color))
                self.drawPieSlice(painter, center_x, center_y, radius, 90, -angle)
            
            # Draw break time slice
            if is_break_time:
                break_time = self.current_time - self.work_time_max
                break_angle = break_time / self.total_time_max * 360
                work_angle = self.work_time_max / self.total_time_max * 360
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(self.break_color))
                self.drawPieSlice(painter, center_x, center_y, radius, 90 - work_angle, -break_angle)
        
        # Draw inner white circle (donut appearance)
        inner_radius = radius * 0.7
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.white))
        painter.drawEllipse(QRectF(center_x - inner_radius, center_y - inner_radius, inner_radius * 2, inner_radius * 2))
        
        # Draw time text (percentage)
        painter.setPen(Qt.black)
        font = QFont("Arial", 24, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(0, 0, width, height), Qt.AlignCenter, self.time_text)
        
        # Draw our custom elements
        
        # Title not displayed as requested
        
        # No longer drawing hours text here - will use standalone labels instead


class WeeklyVisualizationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Weekly goals
        self.hacken_goal_hours = 20  # 20 hours weekly goal
        self.hustle_goal_hours = 10  # 10 hours weekly goal
        
        # Load the actual data from CSV files
        self.load_data()
        
        # Setup UI
        self.init_ui()
        
    def load_data(self):
        """Load real data from CSV files"""
        # Create data manager to load all CSV data
        self.data_manager = DataManager()
        self.data_manager.load_all_data(verbose=False)
        
        # The hacken_hustle_data is already calculated in DataManager
        self.hacken_hustle_data = self.data_manager.hacken_hustle_data
    
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Add title
        title_label = QLabel("Weekly Goals")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(15)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Calculate hours
        hacken_hours = self.hacken_hustle_data["hacken"]["total"] / 3600
        hustle_hours = self.hacken_hustle_data["hustle"]["total"] / 3600
        
        # Create vertical layout for circular progress widgets (changed from horizontal to vertical)
        circular_layout = QVBoxLayout()
        circular_layout.setSpacing(30)  # Add spacing between widgets
        
        # Create a container widget for Hacken progress and its label
        hacken_container = QWidget()
        hacken_layout = QVBoxLayout(hacken_container)
        hacken_layout.setSpacing(5)  # Reduced spacing inside container
        hacken_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        # Hacken progress widget first
        self.hacken_progress = WeeklyCircularProgress(
            title="Hacken", 
            color=QColor(74, 134, 232)  # Blue
        )
        self.hacken_progress.set_progress(hacken_hours, self.hacken_goal_hours)
        hacken_layout.addWidget(self.hacken_progress, 0, Qt.AlignCenter)
        
        # Add label for Hacken hours text below the progress widget
        hacken_label = QLabel(f"Hacken: {hacken_hours:.1f}h / {self.hacken_goal_hours:.0f}h")
        hacken_label.setAlignment(Qt.AlignCenter)
        hacken_label.setFont(QFont("Arial", 15))
        hacken_layout.addWidget(hacken_label, 0, Qt.AlignCenter)
        
        # Add the container to the main layout
        circular_layout.addWidget(hacken_container, 0, Qt.AlignCenter)
        
        # Add spacing between the two widgets
        circular_layout.addSpacing(20)  # Additional spacing
        
        # Create a container widget for Hustle progress and its label
        hustle_container = QWidget()
        hustle_layout = QVBoxLayout(hustle_container)
        hustle_layout.setSpacing(5)  # Reduced spacing inside container
        hustle_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        # Hustle progress widget first
        self.hustle_progress = WeeklyCircularProgress(
            title="Hustle", 
            color=QColor(230, 124, 115)  # Red
        )
        self.hustle_progress.set_progress(hustle_hours, self.hustle_goal_hours)
        hustle_layout.addWidget(self.hustle_progress, 0, Qt.AlignCenter)
        
        # Add label for Hustle hours text below the progress widget
        hustle_label = QLabel(f"Hustle: {hustle_hours:.1f}h / {self.hustle_goal_hours:.0f}h")
        hustle_label.setAlignment(Qt.AlignCenter)
        hustle_label.setFont(QFont("Arial", 15))
        hustle_layout.addWidget(hustle_label, 0, Qt.AlignCenter)
        
        # Add the container to the main layout
        circular_layout.addWidget(hustle_container, 0, Qt.AlignCenter)
        
        # Add circular progress widgets to main layout
        main_layout.addLayout(circular_layout)
        
        # Add spacer to push info labels lower
        main_layout.addSpacing(20)
        
        # Add remaining/excess info labels
        #self.add_info_section(main_layout, "Hacken", hacken_hours, self.hacken_goal_hours)
        #self.add_info_section(main_layout, "Hustle", hustle_hours, self.hustle_goal_hours)
        
        # Add spacer at the bottom
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    '''
    def add_info_section(self, layout, category, actual_hours, goal_hours):
        """Add remaining/excess info section"""
        if actual_hours > goal_hours:
            excess = actual_hours - goal_hours
            info_text = f"{category}: Exceeded goal by +{int(excess)}h {int((excess % 1) * 60)}m"
            color = "green"
        else:
            remaining = goal_hours - actual_hours
            info_text = f"{category}: {int(remaining)}h {int((remaining % 1) * 60)}m remaining to goal"
            color = "black"
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet(f"color: {color};")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setFont(QFont("Arial", 15))
        layout.addWidget(info_label)'''


if __name__ == "__main__":
    # Stand-alone execution for testing
    app = QApplication(sys.argv)
    
    # Create widget (no need to pass data, it loads automatically)
    widget = WeeklyVisualizationWidget()
    widget.setWindowTitle("Weekly Goals")
    widget.resize(500, 400)
    widget.show()
    
    sys.exit(app.exec_())