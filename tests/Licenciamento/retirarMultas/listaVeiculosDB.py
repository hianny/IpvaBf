import oracledb

usernameBd = 'rpa' 
passwordBd= 'Rpa!2023'
dsn = 'oracle.bomfuturo.local:1521/protheus'
connectionBd = oracledb.connect(user=usernameBd, password=passwordBd, dsn=dsn)
cursor = connectionBd.cursor()

def RetornoVeiculosBen():
    cursor.execute("""
        SELECT 
            ARQUIVO_LICENCIAMENTO
        FROM IPVA_LICENCIAMENTO 
        WHERE NUM_DOCUMENTO IS NOT NULL
        AND VALOR_LICENCIAMENTO = '140' 
        AND  substr(placa,7,1) IN ('5','6','7') 
        AND IPVA_LICENCIAMENTO.STATUS_LICENCIAMENTO ='A PAGAR'

            """)
    # Usar fetchall() para pegar todas as linhas
    lista_tuplas = cursor.fetchall()
    lista_pdfs = [linha[0] for linha in lista_tuplas]
    for vei in lista_pdfs:
        
        print(vei)
    return lista_pdfs

def Retornolicenciamento():
    cursor.execute("""
        SELECT 
            ARQUIVO_LICENCIAMENTO
        FROM IPVA_LICENCIAMENTO 
        WHERE NUM_DOCUMENTO IS NOT NULL
        AND VALOR_LICENCIAMENTO = '140' 
        AND  substr(placa,7,1) IN ('5','6','7') 
        AND IPVA_LICENCIAMENTO.STATUS_LICENCIAMENTO ='A PAGAR'

            """)
    # Usar fetchall() para pegar todas as linhas
    lista_tuplas = cursor.fetchall()
    lista_pdfs = [linha[0] for linha in lista_tuplas]
    for vei in lista_pdfs:
        
        print(vei)
    return lista_pdfs

if __name__ == "__main__":
    RetornoVeiculosBen()

