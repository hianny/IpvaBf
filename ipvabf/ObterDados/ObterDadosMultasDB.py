import oracledb
import pandas

usernameBd = 'rpa' 
passwordBd= 'Rpa!2023'
#dsn = 'oracledbdev.bomfuturo.local:1521/homollnx'
dsn = 'oracle.bomfuturo.local:1521/protheus'
connectionBd = oracledb.connect(user=usernameBd, password=passwordBd, dsn=dsn)
cursor = connectionBd.cursor()

def RetornoVeiculosBen(finalPlaca):
    cursor.execute(fr"""
        SELECT N1_PLACA, N1_RENAVAN, N1_CHASSIS, N1_GRUPO
        FROM PROTHEUS11.AV_BENSMTI BENS 
        WHERE SUBSTR(N1_PLACA, LENGTH(N1_PLACA)) = '{finalPlaca}'
        AND NOT EXISTS (
            SELECT 1
            FROM RPA.IPVA_LICENCIAMENTO LC
            WHERE BENS.N1_PLACA = LC.PLACA
                 AND BENS.N1_CHASSIS = LC.CHASSI
                 AND BENS.N1_RENAVAN = TO_NUMBER(LC.RENAVAM)
            )
            """)
    # Usar fetchall() para pegar todas as linhas
    veiculos = cursor.fetchall()
    #print(type(veiculos))
    #for veiculo in veiculos:
    #    print(veiculo[0])
    
    veiculosporPlacas = pandas.DataFrame(veiculos,columns=['PLACA','RENAVAM','CHASSIS','GRUPO'])
    #VEICULOSPLACA = df.columns['PLACA','RENAVAM','CHASSIS']
   # df.to_csv(fr'sequencianotas\cnpjFiliais\resultado.csv', index=False, header=False)
    print(veiculosporPlacas)
    return veiculosporPlacas

def RetornoVeiculosIpva(PLACA, CHASSI,tabela_ipva):
    cursor.execute(fr"""
        SELECT num_documento
        FROM rpa.{tabela_ipva}
        WHERE placa = :placa
        AND chassi = :chassi
    """, {
        "placa": PLACA,
        "chassi": CHASSI
    })
    
    veiculos = cursor.fetchall()
    num_doc_veiculos = pandas.DataFrame(veiculos, columns=['NUM_DOCUMENTO'])

    for _, row in num_doc_veiculos.iterrows():
        cursor.execute("""
            UPDATE rpa.IPVA_LICENCIAMENTO
            SET NUM_DOCUMENTO = :num_doc
            WHERE PLACA = :placa AND CHASSI = :chassi
        """, {
            "num_doc": row["NUM_DOCUMENTO"],
            "placa": PLACA,
            "chassi": CHASSI
        })
        connectionBd.commit()


    return num_doc_veiculos

def veiculoIndividual(placa,renavam,chassi,grupo):
    cursor.execute(fr"""
            SELECT ID FROM IPVA_LICENCIAMENTO
            WHERE PLACA = '{placa}' 
            AND RENAVAM = '{renavam}' 
            AND CHASSI = '{chassi}'
            AND GRUPO = '{grupo}'
            """)
    # Usar fetchall() para pegar todas as linhas
    idVeiculo = cursor.fetchall()


    return idVeiculo

def InserirDadosTabela(placa,renavam,chassi,grupo):
    cursor.execute(fr"""
            INSERT INTO IPVA_LICENCIAMENTO (PLACA, RENAVAM, CHASSI, GRUPO) 
            VALUES ('{placa}', '{renavam}', '{chassi}',{grupo})
            """)
    # Usar fetchall() para pegar todas as linhas
    #idVeiculo = cursor.fetchall()
    #print(f'Veiculo {idVeiculo} inserido com sucesso!')
    connectionBd.commit()
    return #idVeiculo

def InserirNumDoc(placa,chassi,numDoc):
    cursor.execute(fr"""
            INSERT INTO IPVA_LICENCIAMENTO (NUM_DOCUMENTO) 
            VALUES ('{numDoc}') WHERE PLACA = '{placa}' AND CHASSI = '{chassi}'
            """)
    # Usar fetchall() para pegar todas as linhas
    #idVeiculo = cursor.fetchall()
    connectionBd.commit()
    return #idVeiculo

if __name__ == "__main__":
    RetornoVeiculosBen('')
    RetornoVeiculosIpva('','','')
    veiculoIndividual('','','','')
    InserirDadosTabela('','','')
    InserirNumDoc('','','')
