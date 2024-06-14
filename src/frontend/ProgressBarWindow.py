from PyQt6.QtWidgets import QApplication, QMainWindow, QProgressBar, QVBoxLayout, QWidget, QPushButton,QDialog
from PyQt6.QtCore import Qt, pyqtSignal,QThread
from PyQt6  import uic
import threading
from src.backend.SemanticAnalysis import SemanticAnalysis
class ProgressBarWindow(QDialog):
    def __init__(self,observer):
        super().__init__()

        
        # Загружаем дизайн
        self.uic = uic.loadUi('ui/ProgressAnalyse.ui', self)
        # установка названия окна
        self.setWindowTitle("Семантический анализ")
        
        self.observer = observer

        
        
        self.semantic_analysis_thread = QThread()  # Создаем поток
        # передаем observer в поток обьявленный выше
        self.observer.moveToThread(self.semantic_analysis_thread)
        # говорим какую функцию выполнять, когда поток запустится
        self.semantic_analysis_thread.started.connect(self.observer.run)
        # говорим какую функцию выполнять, когда через обсервер, получим обновления
        self.observer.progress_updated.connect(self.update_progress_bar)
        # говорим какие действия выполнять, когда поток завершится (все 3 строки)
        self.semantic_analysis_thread.finished.connect(self.suicide)
        self.observer.finished.connect(self.semantic_analysis_thread.quit)
        self.semantic_analysis_thread.finished.connect(self.semantic_analysis_thread.deleteLater)
        
        # функция для запуска потока
        self.start_file_processing()
        
    def start_file_processing(self):
        # Запуск процесса анализа файлов в отдельном потоке
        self.semantic_analysis_thread.start()
    def update_progress_bar(self, value, file_name):
        # Обновление текста метки с именем файла
        self.file_label.setText(f"Обрабатываемый файл: {file_name}")
        self.progress_bar.setValue(value)
        
    def suicide(self):
        self.reject()
def startProgressBarWindow(observer):
    # Инициализируем окно и запрещаем идти дальше, пока не закроем его
    progress_bar = ProgressBarWindow(observer)
    progress_bar.exec()