import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from circular_progress import CircularProgressWidget

class DemoApp(QMainWindow):
    """Eine einfache Demo-Anwendung, um die kreisförmige Fortschrittsanzeige zu testen."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Kreisförmige Fortschrittsanzeige Demo")
        self.setGeometry(100, 100, 400, 500)
        
        # Zentrales Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Kreisförmige Fortschrittsanzeige
        self.progress_widget = CircularProgressWidget()
        layout.addWidget(self.progress_widget)
        
        # Buttons für Demo-Funktionen
        start_demo_button = QPushButton("Animation starten")
        start_demo_button.clicked.connect(self.start_animation)
        
        stop_demo_button = QPushButton("Animation stoppen")
        stop_demo_button.clicked.connect(self.stop_animation)
        
        layout.addWidget(start_demo_button)
        layout.addWidget(stop_demo_button)
    
    def start_animation(self):
        """Startet die Test-Animation."""
        self.progress_widget.start_test_animation()
    
    def stop_animation(self):
        """Stoppt die Test-Animation."""
        self.progress_widget.stop_test_animation()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = DemoApp()
    demo.show()
    sys.exit(app.exec_())