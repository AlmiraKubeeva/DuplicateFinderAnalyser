from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox, QDialog
from PyQt6 import uic

class SelectionAnalysis(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.methods = ["Bert","Tf-idf"]
        # Загружаем дизайн
        self.uic = uic.loadUi('ui/SelectionAnalysis.ui', self)
        
        # назначаем подтверждение на кнопкку
        self.pushButton.clicked.connect(self.accept)
        
        # Добавляем свои элементы в QComboBox
        self.comboBox.addItems(self.methods)
    
    def selected_parameter(self):
        # возвращает выбранный параметр
        return self.comboBox.currentText()
    def default_method(self):
        # возвращает метод по умолчанию
        return self.methods[1]