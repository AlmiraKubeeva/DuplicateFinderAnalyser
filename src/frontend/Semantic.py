import os

from PyQt6.QtWidgets import QDialog,QApplication
from PyQt6  import uic
from PyQt6.QtWidgets import QMainWindow,QFileDialog,QAbstractItemView,QTableWidget
from PyQt6.QtGui import QIcon, QStandardItem,QDoubleValidator
from src.backend.FileUtils import FileUtils
from src.backend.DataBase import DB
from src.frontend.ErrorWindow import makeError
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QLocale



class SemanticWindow(QDialog):
    def __init__(self,db):
        super().__init__()
        # загрузка интерфейса
        self.uic=uic.loadUi('ui/semantic.ui', self)
        self.setWindowTitle("Семантический анализ")
        # задаем самоуничтожение окна на кнопку
        self.confirmButton.clicked.connect(self.suicide)
        self.viewTable(db)
        # стави ограничение на ввод threshold
        validator = QDoubleValidator(0.0, 1.0, 4)
        self.thresh_line.setValidator(validator)
        # назначаем на кнопку удаление по трешхолду
        self.delete_button.clicked.connect(self.delete)
        self.db = db
        
        
    def suicide(self):
        self.reject()
    def viewTable(self,db):
        model = QStandardItemModel()
        model.setHorizontalHeaderItem(0, QStandardItem("path"))
        model.setHorizontalHeaderItem(1, QStandardItem("rating"))
        
        for key, values in enumerate(db):
            for i, value in enumerate(values):
                item = QStandardItem(str(value))
                model.setItem(key, i, item)

        self.tableView.setModel(model)
        self.tableView.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        total_width =self.tableView.viewport().size().width()
        column_widths = [0.8, 0.2]  # Примерное процентное соотношение для каждого столбца
        for i, width_ratio in enumerate(column_widths):
            self.tableView.setColumnWidth(i, int(total_width * width_ratio))
    def delete(self):
        # удаляем по трешхолду 
        thresh = self.thresh_line.text()
        # меняем запятую на точку
        thresh = thresh.replace(",",".")
        # если неккоректно задан трешхолд ставим его значительно больше 1
        try:
            thresh = float(thresh)
        except ValueError as e:
            makeError("Некорректное значение порога")
            thresh = 2.0
        # удаляем все документы с рейтингом выше трешхолда
        # при этом, если рейтинг это строка с ошибкой, то пропускаем
        for doc in self.db:
            try:
                if float(doc[1]) > thresh:
                    os.remove(doc[0])
            except ValueError as e:
                continue
        self.suicide()
    
