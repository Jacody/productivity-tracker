import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

# Importiere die beiden Programme
from tracker import MainApp  # Gesichtserkennung (Produktivitäts-Tracker)
from todo_manager import TodoApp  # To-Do-Manager

# Wrappen der MainApp als QWidget für Integration
class ProductivityTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.main_app = MainApp()  # Produktivitäts-Tracker GUI
        self.layout.addWidget(self.main_app)
        self.setLayout(self.layout)

# Haupt-App mit Splitter für beide Programme
class CombinedApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Produktivitäts-Tracker & To-Do-Manager")
        self.setGeometry(100, 100, 1000, 400)

        # Splitter für geteilte Ansicht
        splitter = QSplitter(Qt.Horizontal)  # Nebeneinander (Qt.Vertical für übereinander)
        splitter.addWidget(ProductivityTracker())  # Produktivitäts-Tracker-Widget
        splitter.addWidget(TodoApp())  # To-Do-Manager-Widget

        self.setCentralWidget(splitter)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = CombinedApp()
    main_window.show()
    sys.exit(app.exec_())

