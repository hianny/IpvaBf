import oracledb

usernameBd = 'rpa' 
passwordBd= 'Rpa!2023'
dsn = 'oracle.bomfuturo.local:1521/protheus'
connectionBd = oracledb.connect(user=usernameBd, password=passwordBd, dsn=dsn)
cursor = connectionBd.cursor()

def RetornoVeiculosBen():
    cursor.execute("""
        SELECT arquivo_licenciamento
        FROM rpa.IPVA_LICENCIAMENTO a
        where renavam  in ( '1302349586')
            """)
    # Usar fetchall() para pegar todas as linhas
    lista_tuplas = cursor.fetchall()
    lista_pdfs = [linha[0] for linha in lista_tuplas]
    for vei in lista_pdfs:
        
        print(vei)
    return lista_pdfs

def Retornolicenciamento():
    cursor.execute("""
        SELECT arquivo_licenciamento
        FROM rpa.IPVA_LICENCIAMENTO a
        where renavam  in  ('1280572296')
            """)
    # Usar fetchall() para pegar todas as linhas
    lista_tuplas = cursor.fetchall()
    lista_pdfs = [linha[0] for linha in lista_tuplas]
    for vei in lista_pdfs:
        
        print(vei)
    return lista_pdfs

if __name__ == "__main__":
    RetornoVeiculosBen()

