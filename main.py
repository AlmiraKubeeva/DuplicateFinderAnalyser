import sys
from PyQt6.QtWidgets import QApplication

from src.frontend.MainWindow import MainWindow

def main():
    # создаем приложение
    app = QApplication(sys.argv)
    # создаем окно
    w=MainWindow()
    # показываем окно
    w.show()
    sys.exit(app.exec())

if (__name__ == "__main__"):
    main()