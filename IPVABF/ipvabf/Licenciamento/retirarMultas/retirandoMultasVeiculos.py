import os
import shutil
from PyPDF2 import PdfReader, PdfWriter
import listaVeiculosDB

def processar_pdfs(pagina):
    lista_pdfs = listaVeiculosDB.RetornoVeiculosBen() 
    pasta_backup = fr'C:\BOT\LICENCIAMENTO\ALTERADOS'
    os.makedirs(pasta_backup, exist_ok=True)

    for caminho_pdf in lista_pdfs:
        if not caminho_pdf.lower().endswith('.pdf'):
            print(f"Ignorado (não é PDF): {caminho_pdf}")
            continue

        if not os.path.exists(caminho_pdf):
            print(f"Arquivo não encontrado: {caminho_pdf}")
            continue

        try:
            nome_arquivo = os.path.basename(caminho_pdf)
            caminho_backup = os.path.join(pasta_backup, nome_arquivo)

            reader = PdfReader(caminho_pdf)
            writer = PdfWriter()

            if len(reader.pages) > pagina:  # Verifica se a página existe
                writer.add_page(reader.pages[pagina])  # Adiciona a página especificada

                with open(caminho_backup, 'wb') as saida_pdf:
                    writer.write(saida_pdf)

                print(f"✔ {nome_arquivo} processado! Modificado salvo em '{caminho_backup}'")
            else:
                print(f"⚠ {nome_arquivo} não possui a página {pagina}!")

        except Exception as e:
            print(f"❌ Erro ao processar {caminho_pdf}: {e}")

if __name__ == "__main__":
    # Especifique qual página você quer extrair (0 para primeira página, 1 para segunda, etc.)
    processar_pdfs(0)  # Aqui deve ser um número inteiro