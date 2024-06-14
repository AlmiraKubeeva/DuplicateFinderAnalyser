import os 
import docx2txt
import PyPDF2
from PIL import Image
from src.backend.OCR import tesseractOCR, easyOCR
import fitz  # PyMuPDF
from PIL import Image
import io

# статический класс
class FileUtils():
    # поиск файлов в директории
    def deepSearchDir(path: str) -> list:
        # возвращает список путей до файлов
            files_list = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    files_list.append( os.path.join(root, file).replace("\\","/"))
            return files_list

    def deleteFile(path: str) -> None:
        os.remove(path)

    def readTxt(path):
        with open(path,"r",encoding = 'utf-8') as f:
            return f.read()
        
    def convertDocToTxt(docFilePath):
        text = docx2txt.process(docFilePath)
        return text

    def convertPDFToTxt(pdfFilePath):
        
        with open(pdfFilePath, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            # Чтение содержимого каждой страницы PDF и объединение в одну строку
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        return text
    def convertPic2txt(img_path):
        img = Image.open(img_path)
        ocr=tesseractOCR()
        text =ocr.readText(img_path)
        return text
    
    def convertPDF2Txt(pdfFilePath):
        doc = fitz.open(pdfFilePath)
        content = []
        ocr=easyOCR()
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_content = []

            # Извлечение текста
            text_blocks = page.get_text("dict")["blocks"]
            for block in text_blocks:
                if block["type"] == 0:  # block of text
                    text = ""
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text += span["text"] + " "
                    page_content.append({
                        "type": "text",
                        "content": text.strip(),
                        "position": block["bbox"]
                    })

            # Извлечение изображений
            image_blocks = page.get_images(full=True)
            for img_index, img in enumerate(image_blocks):
                xref = img[0]
                base_image = doc.extract_image(xref)
                pos=page.get_image_rects(img[0])
                
                if base_image:  # Убедимся, что изображение было извлечено
                    image_bytes = base_image["image"]
                    image_stream = io.BytesIO(image_bytes)
                    pillow_image = Image.open(image_stream)
                    page_content.append({
                        "type": "image",
                        "content": ocr.readText(pillow_image),
                        "position": pos[0]  # img[1] содержит положение изображения на странице
                    })

            # Сортировка содержимого страницы по вертикальной позиции на странице
            page_content.sort(key=lambda item: (item["position"][1]))
            content.extend(page_content)
        res = ""
        for block in content:
            res = res + block['content'] + ' '
        return res
        

        