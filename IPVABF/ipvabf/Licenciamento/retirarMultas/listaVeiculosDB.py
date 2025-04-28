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
        WHERE NUM_DOCUMENTO is not null 
        AND STATUS_LICENCIAMENTO = 'A PAGAR'
        AND SUBSTR(PLACA, LENGTH(PLACA),1) IN ('9','8','0')
        AND DT_ULT_CONSULTA_DETRAN > TO_TIMESTAMP('2025-04-23 9:00:00', 'YYYY-MM-DD HH24:MI:SS')
        ORDER BY RENAVAM DESC

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
        WHERE NUM_DOCUMENTO is not null 
        AND STATUS_LICENCIAMENTO = 'A PAGAR'
        AND SUBSTR(PLACA, LENGTH(PLACA),1) IN ('9','8','0')
        AND DT_ULT_CONSULTA_DETRAN > TO_TIMESTAMP('2025-04-23 9:00:00', 'YYYY-MM-DD HH24:MI:SS')
        ORDER BY RENAVAM DESC

            """)
    # Usar fetchall() para pegar todas as linhas
    lista_tuplas = cursor.fetchall()
    lista_pdfs = [linha[0] for linha in lista_tuplas]
    for vei in lista_pdfs:
        
        print(vei)
    return lista_pdfs

if __name__ == "__main__":
    RetornoVeiculosBen()

