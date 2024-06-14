from PyQt6.QtWidgets import QDialog,QApplication
from PyQt6  import uic

class ErrorWindow(QDialog):
    def __init__(self,text):
        # функция принимает текст ошибки и вызывает окно ошибки
        super().__init__()
        self.uic=uic.loadUi('ui/ErrorWindow.ui', self)
        self.confirmButton.clicked.connect(self.suicide)
        self.errorText.setText(text)
    def suicide(self):
        self.reject()
def makeError(text):
    error = ErrorWindow(text)
    error.exec()
    

    