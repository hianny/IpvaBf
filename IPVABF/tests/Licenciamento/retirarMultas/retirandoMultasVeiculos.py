import os
import shutil
from PyPDF2 import PdfReader, PdfWriter
import listaVeiculosDB

def processar_pdfs(x):
    lista_pdfs = listaVeiculosDB.RetornoVeiculosBen() 
    pasta_backup = fr'C:\BOT\LICENCIAMENTO\ALTERADO'
    os.makedirs(pasta_backup, exist_ok=True)

    for caminho_pdf in lista_pdfs:
        if not caminho_pdf.lower().endswith('.pdf'):
            print(f"Ignorado (não é PDF): {caminho_pdf}")
            continue

        if not os.path.exists(caminho_pdf):
            print(f"Arquivo não encontrado: {caminho_pdf}")
            continue

        try:
            # Extrai informações do caminho
            #pasta_origem = os.path.dirname(caminho_pdf)
            nome_arquivo = os.path.basename(caminho_pdf)
            caminho_backup = os.path.join(pasta_backup, nome_arquivo)

            # Lê o PDF original
            reader = PdfReader(caminho_pdf)
            writer = PdfWriter()

            if len(reader.pages) > 0:
                writer.add_page(reader.pages[{x}])  # Adiciona só a primeira página

                # Salva o PDF modificado (com a primeira página) na pasta de backup
                with open(caminho_backup, 'wb') as saida_pdf:
                    writer.write(saida_pdf)

                # Faz o backup (move o arquivo original para o backup)
                print(f"✔ {nome_arquivo} processado! Modificado salvo em '{caminho_backup}'")

            else:
                print(f"⚠ {nome_arquivo} não possui páginas!")

        except Exception as e:
            print(f"❌ Erro ao processar {caminho_pdf}: {e}")

if __name__ == "__main__":
    processar_pdfs('')