import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

# Caminho do Tesseract
pytesseract.pytesseract.tesseract_cmd = fr'C:\Program Files\Tesseract-OCR\tesseract.exe'

def pdf_to_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")
        
        # Se não tiver texto extraído, tenta OCR
        if not text.strip():
            img = page.get_pixmap()
            img_bytes = img.tobytes("png")
            img_pil = Image.open(io.BytesIO(img_bytes))
            ocr_text = pytesseract.image_to_string(img_pil)
            text += ocr_text

    return text

def check_number_in_pdf(pdf_path, number):
    text = pdf_to_text(pdf_path)
    return str(number) in text

def main():
    directory = fr'C:\BOT\LICENCIAMENTO\ALTERADO'
    number_to_search = "140"
    
    for filename in os.listdir(directory):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(directory, filename)
            if not check_number_in_pdf(pdf_path, number_to_search):
                print(f'O número {number_to_search} NÃO foi encontrado no arquivo: {filename}')

if __name__ == "__main__":
    main()
