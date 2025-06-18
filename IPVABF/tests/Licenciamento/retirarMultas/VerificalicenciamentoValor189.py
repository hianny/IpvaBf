import os
import re
import pytesseract
from PIL import Image
from PyPDF2 import PdfReader
import pdf2image
import io

# Configuração importante para caminhos no Windows
def safe_path(path):
    return os.path.normpath(path)

def extract_text_from_pdf(pdf_path):
    """
    Extrai texto de um PDF, usando OCR se necessário
    """
    try:
        # Primeiro tenta extrair texto diretamente
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
        
        # Se o texto extraído for muito pequeno, tenta OCR
        if len(text.strip()) < 100:  # Limite arbitrário para considerar que precisa de OCR
            try:
                images = pdf2image.convert_from_path(pdf_path)
                ocr_text = ""
                for image in images:
                    ocr_text += pytesseract.image_to_string(image) + "\n"
                if len(ocr_text) > len(text):
                    text = ocr_text
            except Exception as ocr_error:
                print(f"Erro no OCR para {pdf_path}: {str(ocr_error)}")
        
        return text
    except Exception as e:
        print(f"Erro ao processar {pdf_path}: {str(e)}")
        return ""

def find_licensing_value(text, target_value):
    """
    Busca o valor de licenciamento no texto extraído
    """
    # Padrões para encontrar valores monetários
    patterns = [
        r"Licenciamento\s*Anual.*?R\$\s*([\d.,]+)",  # Padrão específico para licenciamento
        r"R\$\s*([\d.,]+).*?Licenciamento",  # Inverso
        r"Valor.*?R\$\s*([\d.,]+)",  # Padrão genérico para valores
        r"R\$\s*([\d.,]+)"  # Qualquer valor monetário
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            # Normaliza o valor encontrado
            cleaned_value = match.replace(".", "").replace(",", ".")
            try:
                numeric_value = float(cleaned_value)
                # Verifica se o valor está dentro de uma pequena margem do alvo
                if abs(numeric_value - target_value) < 0.01:  # Margem de 1 centavo
                    return True
            except ValueError:
                continue
    
    return False

def check_pdfs_in_folder(folder_path, target_value):
    """
    Verifica todos os PDFs em uma pasta
    """
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    missing_value_files = []
    
    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_path = os.path.join(folder_path, pdf_file)
        print(f"Processando {i}/{len(pdf_files)}: {pdf_file}...", end=" ")
        
        text = extract_text_from_pdf(pdf_path)
        if not find_licensing_value(text, target_value):
            missing_value_files.append(pdf_file)
            print("VALOR NÃO ENCONTRADO")
        else:
            print("valor encontrado")
    
    return missing_value_files

if __name__ == "__main__":
    # Configurações - USAR raw string ou barras normais
    pdf_folder = r"C:\BOT\LICENCIAMENTO"  # Raw string para evitar problemas com \
    # ou alternativamente:
    # pdf_folder = "C:/BOT/LICENCIAMENTO/ALTERADOS"  # Funciona no Windows também
    
    target_value = 189.34
    
    # Configuração do Tesseract (se necessário)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    # Configuração do poppler (necessário para pdf2image)
    # Baixe em: https://github.com/oschwartz10612/poppler-windows/releases/
    # E extraia em uma pasta como C:\poppler-xx\bin
    poppler_path = fr"C:\poppler-24.08.0\Library\bin"  # Ajuste para seu caminho
    os.environ["PATH"] += os.pathsep + poppler_path
    
    print(f"Verificando arquivos PDF em {pdf_folder} pelo valor R${target_value:.2f}...")
    
    # Executa a verificação
    files_without_value = check_pdfs_in_folder(pdf_folder, target_value)
    
    # Salva os resultados
    with open("resultados_finais.txt", "w", encoding="utf-8") as f:
        f.write(f"Arquivos que NÃO contêm o valor R${target_value:.2f}:\n")
        f.write("\n".join(files_without_value))
    
    print("\nRelatório completo salvo em 'resultados_finais.txt'")
    print(f"Total de arquivos sem o valor: {len(files_without_value)}")