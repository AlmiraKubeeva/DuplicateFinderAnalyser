import pytesseract
import easyocr
import numpy as np
from PIL import Image

class tesseractOCR():
    # быстрее работает, чем easyOCR, но похуже
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = 'Tesseract-OCR/tesseract.exe'

    def readText(self,path):
        return pytesseract.image_to_string(path,lang= 'rus')         

class easyOCR():
    # медленнее работает, чем tesseractOCR, но лучше
    def __init__(self):
       self.reader = easyocr.Reader(['ru'])

    def readText(self,img):
        if type(img) == str:
            img =Image.open(img)
        else:
            img = img
        texts = self.reader.readtext(np.array(img))
                 
        return self.textWithPolygons2text(texts)

    def inters(self,a,b):
        # являются ли 2 прямоугольника частью одной строки
        ma=max(a[0][0][1],b[0][0][1] )
        mi = min(a[0][3][1],b[0][3][1])
        size = a[0][0][1] - a[0][3][1]
        return ((ma-mi)/ size>0.5)
    def  sorting( self,a):
        # сортирует прямоугольники
        res={}
        k=0
        while( a):
            el=a.pop(0)
            mass=[el]
            for i in a:
                if(self.inters(el,i)):
                    mass.append(i)
            mass = sorted(mass,reverse= False,key=lambda b:b[0][0][0])
            res[k]= mass
            a=self.minus(a,mass)
            k=k+1
        return res
    def minus(self,A,B):
        # из массива А удаляет все элементы, которые есть в массиве B
        C=[]
        for i in A:
            if not (i in B):
                C.append(i)
        return C
    def glue(self,result):
        # склеивает сортированные прямоугольники в один текст
        res=""
        for i in result.values():
            for j in i:
                res = res +" "+ j[1]
        return res
    def textWithPolygons2text(self,textWithPolygons):
        # сортирует и склеивает
        return self.glue(self.sorting(textWithPolygons))
    