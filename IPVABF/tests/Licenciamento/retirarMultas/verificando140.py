import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

# Defina o caminho do tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_page(page):
    """
    Função para extrair texto de uma página do PDF.
    Se o texto não for encontrado, tenta usar OCR para extrair o texto da imagem.
    """
    text = page.get_text("text").strip()
    if not text:
        # Se não encontrar texto, tenta usar OCR
        img = page.get_pixmap()
        img_bytes = img.tobytes("png")
        img_pil = Image.open(io.BytesIO(img_bytes))
        text = pytesseract.image_to_string(img_pil)
    return text

def check_word_in_pdf(pdf_path, word, debug=False):
    """
    Função para verificar se uma palavra está presente no texto de um PDF.
    """
    try:
        doc = fitz.open(pdf_path)
        word_clean = word.strip().lower()  # Convertendo a palavra para minúscula para comparação insensível ao caso

        full_text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            page_text = extract_text_from_page(page)
            full_text += page_text + "\n"
        
        # Exibindo o texto completo extraído, para depuração
        if debug:
            #print(full_text)
            pass
        # Convertendo o texto extraído para minúscula para comparação insensível ao caso
        full_text_clean = full_text.lower()

        if word_clean in full_text_clean:
            return False  # Palavra encontrada
        else:
            return True  # Palavra não encontrada
    except Exception as e:
        print(f"[ERRO] Não foi possível processar o arquivo {pdf_path}: {e}")
        return False

def find_pdfs_in_directory(directory, word, debug=False):
    """
    Função para procurar arquivos PDF em um diretório e verificar se a palavra NÃO está presente neles.
    """
    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith(".pdf")]
    results = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(directory, pdf_file)
        if check_word_in_pdf(pdf_path, word, debug):
            print(f"[RESULTADO] O arquivo '{pdf_file}' NÃO contém a palavra '{word}'.")
            results.append(pdf_file)
        else:
            print(f"[RESULTADO] O arquivo '{pdf_file}' contém a palavra '{word}'.")
            
    
    return results

# Defina o diretório onde seus PDFs estão armazenados
directory = "C:\\BOT\\LICENCIAMENTO"  # Substitua com o caminho correto

# Defina a palavra que você está procurando
word = "OITENTA "  # Substitua com a palavra desejada

# Encontre os PDFs que NÃO contêm a palavra
pdfs_not_found = find_pdfs_in_directory(directory, word, debug=True)

# Exiba os resultados finais
if pdfs_not_found:
    print("Arquivos encontrados que NÃO contêm a palavra:", pdfs_not_found)
else:
    print("Todos os arquivos contêm a palavra.")
