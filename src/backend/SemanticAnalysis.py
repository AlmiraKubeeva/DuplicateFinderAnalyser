import re 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.backend.FileUtils import FileUtils
from src.backend.BertAnalyse import BertAnalyse
from PyQt6.QtCore import Qt, pyqtSignal,QObject
import weakref

class SemanticAnalysiObserver(QObject):
    """ класс для реализации паттерна обсервер
    имеет внутри себя 2 флага, которые может читать окно
    прогресс бара 
    """
    progress_updated = pyqtSignal(int,str) 
    finished = pyqtSignal() 
    def __init__(self,semantic_analysis=None):
        super().__init__()
        # слабая ссылка на класс семантического анализа
        self.semantic_analysis = weakref.ref(semantic_analysis)
    def run(self):
        """
        Вызывает run у семантического анализа
        """
        if(self.semantic_analysis() is not None):
            self.semantic_analysis().run()
        self.finished.emit()
        
        
        
    
class SemanticAnalysis():
    def __init__(self,db,curr,method):
        """
        Класс семантического анализа
        :param db: база данных
        :param curr: текущий файл, выбранный мышкой
        :param method: метод анализа
        """
        # создаем объект для общения с прогресс баром
        self.observer = SemanticAnalysiObserver(self)
        self.res=[]
        self.db = db
        self.curr = curr
        self.method = method
        self.support_type = {
            "txt" : FileUtils.readTxt, 
            "docx" : FileUtils.convertDocToTxt, 
            "doc" : FileUtils.convertDocToTxt, 
            "pdf" : FileUtils.convertPDF2Txt,
            "jpg" : FileUtils.convertPic2txt,
            "png" : FileUtils.convertPic2txt,
        }
        self.methods ={
            "Tf-idf" : self.compare_texts_tfidf,
            "Bert" : self.compare_texts_bert
        }
        
    def clear_text(self,text):
        # меняем один символ на другой
        text= text.replace('ё','е')
        regular=[r'\<[^>]*\>',r"[\n\r]",r"&\w{4};",'[^a-zA-Zа-яА-Я ]',r'\s.\s',r'\s..\s']
        for i in regular:
            text = re.sub(i,' ',text)
        return text.lower()
    def compare_texts_tfidf(self,text1, text2):
        # Создаем объект TfidfVectorizer
        tfidf_vectorizer = TfidfVectorizer()
        # очищаем тексты
        text1 = self.clear_text(text1)
        text2 = self.clear_text(text2)
        # Собираем корпус текстов
        corpus = [text1, text2]
        
        # проверяем что векторизатор не выдал ошибку(выдает когда символы пустые)
        try:
            # Преобразуем тексты в TF-IDF вектора
            tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
            # Считаем косинусное сходство между TF-IDF векторами
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        except Exception as e:
            return 0

        return similarity[0][0]
    def compare_texts_bert(self,text1, text2):
        bert = BertAnalyse()
        # очищаем тексты
        text1 = self.clear_text(text1)
        text2 = self.clear_text(text2)
        return bert.compare_text(text1, text2)
        
    def run(self): 
        # проверяем, файлы типа txt или нет
        res = []
        # если нет, то мы идем по всем остальным файлам и говорим что не поддерживается сравнение
        if(self.db[self.curr].type not in self.support_type.keys()):
            for i, doc in enumerate(self.db):
                if(i != self.curr):
                    rating = "not_support"
                    res.append((doc.filepath,rating))
            self.observer.progress_updated.emit(100, " ")
            self.res = res
            return res
        # проверяем что выбранный файл читается, если нет, то рейтинг будет 0
        try: 
            curr_text = self.support_type[self.db[self.curr].type](self.db[self.curr].filepath)
        except Exception as e:
            rating = 0
            for i, doc in enumerate(self.db):
                if(i != self.curr):
                    res.append((doc.filepath,rating))
            self.observer.progress_updated.emit(100, " ")
            self.res = res
            return res
        # после этого мы идем по всем файлам, которые support, и считаем одинаковые слова
        # если файл прочитался корректно
        
        # считаем длину базы данных
        total_files = len(self.db)
        # выбираем метод для анализа
        method=self.methods[self.method]
        for i, doc in enumerate(self.db):
            # считаем прогресс
            progress_percent = int((i + 1) / total_files * 100)
            # проверяем что это не выбранный файл
            if(i != self.curr):      
                # проверяем что он поддерживатся
                if(doc.type in self.support_type.keys()):
                    # проверяем что он корректно читается
                    try:
                        # считаем рейтинг
                        file_text = self.support_type[doc.type](doc.filepath)
                        rating = str(round(method(curr_text, file_text), 5))
                    except Exception as e:
                        print(e)
                        rating = 'incorrect_reading'
                else:
                    rating = 'not_support'
                res.append((doc.filepath,rating))
                #обновляем переменную прогресса, для прогресс бара
                self.observer.progress_updated.emit(progress_percent, doc.basename)
        # сохраняем результат        
        self.res = res
        return res
    



        
            
            
            
