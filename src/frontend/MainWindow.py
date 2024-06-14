# импорт библиотек
from PyQt6  import uic
from PyQt6.QtWidgets import QMainWindow,QFileDialog,QAbstractItemView,QTableWidget, QDialog
from PyQt6.QtGui import QIcon, QStandardItem 
from src.backend.FileUtils import FileUtils
from src.backend.DataBase import DB
from src.backend.SemanticAnalysis import SemanticAnalysis
from src.frontend.ErrorWindow import makeError
from src.frontend.Semantic import SemanticWindow
from src.frontend.SelectionAnalysis import SelectionAnalysis
from src.frontend.ProgressBarWindow import ProgressBarWindow, startProgressBarWindow
from PyQt6.QtGui import QStandardItemModel, QStandardItem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # загрузка интерфейса
        self.uic=uic.loadUi('ui/MainWindow.ui', self)
        # установка названия окна
        self.setWindowTitle("DuplicateFinder") 
        # установка иконки
        self.setWindowIcon(QIcon('ui/icon.png'))
        # запрет изменения строки ввода
        self.currentPath.setReadOnly(True)
        # установка фиксированной ширины и высоты окна
        self.setFixedSize(800,600)
        # инициализация базы данных
        self.db = None
        self.path = None
        # состояние окна
        self.state = "ReadyRead"
        # задаем кнопкам их функции, которые написаны ниже
        self.openDirectoryButton.clicked.connect(self.browseDir)
        self.deleteFilesButton.clicked.connect(self.removeFile)
        self.deleteDuplicatesButton.clicked.connect(self.removeAllCopy)
        self.duplicateShowButton.clicked.connect(self.showDuplicate)
        self.DuplicatehideButton.clicked.connect(self.hideDuplicate)
        self.semanticCompareButton.clicked.connect(self.semanticAnalyse)
        
    
    def changeState(self,action):
        """Инициализируем состояния и производим переходы между ними
        
        Переходы между следующими состояниями:
        ReadyRead - готов открыть папку
        OpenFolder - открыта папка
        ShowDuplicates - показывает дубликаты
        
        Действия:
        EmptyRead - прочли пустую папку
        ReadDir - прочли папку
        ShowCurrDuplicates - показывает дубликаты текущего выбранного файла
        BackOpenFolder - вернулись в состояние OpenFolder
        
        :param action: действие, которое меняет состояние окна
        """
        states = {
            ("ReadyRead","EmptyRead"):"ReadyRead",
            ("ReadyRead","ReadDir"):"OpenFolder",
            ("OpenFolder",'ReadDir') : "OpenFolder",
            ("OpenFolder",'EmptyRead') : "ReadyRead",
            ("OpenFolder","ShowCurrDuplicates"): "ShowDuplicates"     ,
            ("ShowDuplicates","BackOpenFolder") : "OpenFolder",
            ("ShowDuplicates",'ReadDir'):"OpenFolder",
                    }
        # меняем состояния на основе хэшмапы states
        self.state =  states[(self.state,action)]

        
        
        
        
    def browseDir(self):
        # возвращает существующий путь до папки
        folder_path = QFileDialog.getExistingDirectory(self, 'Выберите папку')
        # меняем текст в строке ввода на путь к папке
        self.currentPath.setText(folder_path)
        # сохраняем путь к папке в классе
        self.path = folder_path
        # читаем папку
        self.fullUpdate()
            
    def fullUpdate(self):
        """
        Функция читает папку,обновляет таблицу и меняет состояние окна
        """
        self.db=DB(FileUtils.deepSearchDir(self.path))
        # если база данных не пустая
        if(len(self.db) != 0 ):
            # считаем мд5-хэш для каждого документа
            self.db.calculateMD5Hash()
            # выводим таблицу
            self.viewTable(self.db)
            # меняем состояние окна с ReadyRead на OpenFolder
            self.changeState("ReadDir")
        else:
            # меняем состояние окна с ReadyRead на EmptyRead
            self.changeState("EmptyRead")
            self.viewTable(self.db)
    
        
    def viewTable(self,db):
        # запускаем функцию для отображения всех файлов
        # создаем модель таблицы
        model = QStandardItemModel()
        # создаем заголовки столбцов таблицы
        model.setHorizontalHeaderItem(0, QStandardItem("path"))
        model.setHorizontalHeaderItem(1, QStandardItem("type"))
        model.setHorizontalHeaderItem(2,  QStandardItem("uuid"))
        model.setHorizontalHeaderItem(3,  QStandardItem("md5_hash"))
        # заполняем таблицу данными
        for key, values in enumerate(db):
            # заполняем каждую строчку данными
            for i, (name,value) in enumerate(values.__dict__.items()):
                # заполняем столбец строки данными
                item = QStandardItem(str(value))
                # добавляем данные в ячейку по key-столбцу и i-строке
                model.setItem(key, i, item)
        # устанавливаем модель в таблицу
        self.tableView.setModel(model)
        # запрет на изменение таблицы
        self.tableView.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tableView.setSortingEnabled(False)
        # устанавливаем ширину столбцов
        total_width =self.tableView.viewport().size().width()
        column_widths = [0.5, 0.1, 0.1,0.3]  # Примерное процентное соотношение для каждого столбца
        for i, width_ratio in enumerate(column_widths):
            self.tableView.setColumnWidth(i, int(total_width * width_ratio))
        
    def removeFile(self):
        # если папка не открыта
        if(self.state == "ReadyRead"):
            makeError("Сначала откройте папку")
            return 0
        # чтобы узнать какой выбран файл
        select = self.selectChoice()
        if(select is not None):
            # удаляем выбранный файл и его из таблицы
            self.db.removeByIndex(select)
            # обновляем таблицу
            self.viewTable(self.db)
        else:
            # выводим окно с ошибкой
            makeError("файл не выбран")
        
    def selectChoice(self):
        # функция, которая определяет, какой файл выбран
        # узнает, сколько строк в таблице
        row_count = self.tableView.model().rowCount()
        # определяем выделенную ячейку
        selection_model = self.tableView.selectionModel()
        # определяем, с какой строкой пересекается выделенная ячейка
        select = None
        for row in range(row_count):
            if(selection_model.rowIntersectsSelection(row)):
                select = row
        # возвращаем номер строки, с которой пересекается ячейка
        return select
    
    def removeAllCopy(self):
        # если папка не открыта
        if(self.state == "ReadyRead"):
            makeError("Сначала откройте папку")
            return 0 
        # определяем выделенную строчку
        select=self.selectChoice()
        # если строчка найдена
        if(select is not None):
            # удаляем все файлы, у которых одинаковый хэш, кроме выделенного
            self.db.removeCurrCopyMD5(select)
            # обновляем таблицу
            self.viewTable(self.db)
        else:
            makeError("файл не выбран")
    
    def showDuplicate(self):
        # если папка не открыта
        if(self.state == "ReadyRead"):
            makeError("Сначала откройте папку")
            return 0 
        # если дубликаты уже просматриваются
        if(self.state == "ShowDuplicates"):
            makeError("Дубликаты уже просматриваются")
            return 0
        # находим пересечение ячейки и строки
        select = self.selectChoice()
        # и если мы нашли это пересечение
        if(select is not None):
            # просматриваем мд5-хэш выделенного файла
            md5_curr=self.db[select].md5
            # меняем состояние
            self.changeState("ShowCurrDuplicates")
            # создаем новое множество дубликатов
            listDuplicates = [obj for obj in self.db if obj.md5 == md5_curr]
            # показываем дубликаты
            self.viewTable(listDuplicates)
        else:
            makeError("файл не выбран")
    def hideDuplicate(self):
        # если папка не открыта
        if(self.state == "ReadyRead"):
            makeError("Сначала откройте папку")
            return 0 
        # если дубликаты не просматриваются
        if(self.state == "OpenFolder"):
            makeError("Сначала покажите дубликаты")
            return 0 
        # меняем состояние
        self.changeState("BackOpenFolder")
        # показываем новую таблицу
        self.viewTable(self.db)
        
    def semanticAnalyse(self):
        # если папка не открыта
        if(self.state == "ReadyRead"):
            makeError("Сначала откройте папку")
            return 0 
        # определяем выделенную строчку
        select=self.selectChoice()
        if(select is not None):
            # создает окно выбора метода обработки текста, возвращает строку
            method=self.analyse_method_choice()
            # создает экзепляр класса семантического анализа
            semantic_analysis=SemanticAnalysis(self.db,select,method)
            startProgressBarWindow(semantic_analysis.observer)
            ratings_mass=semantic_analysis.res
            sw=SemanticWindow(ratings_mass)
            sw.exec()
            self.fullUpdate()
        else:
            makeError("Файл не выбран")
    def analyse_method_choice(self):
        dialog = SelectionAnalysis(self)
        dialog.exec()
        return dialog.selected_parameter()
        
        
    

        
        