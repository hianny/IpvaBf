import oracledb
import pandas
import dotenv
import os
dotenv.load_dotenv()

usernameBd = os.getenv('usernameBd')
passwordBd= os.getenv('passwordBd')
dsn = os.getenv('dsnhomol')
connectionBd = oracledb.connect(user=usernameBd, password=passwordBd, dsn=dsn)
cursor = connectionBd.cursor()

tabela_ipva_lic = 'ipva2026'

def RetornoVeiculosBen(finalPlaca):
    cursor.execute(fr"""
        SELECT N1_PLACA, N1_RENAVAN, N1_CHASSIS, N1_GRUPO
        FROM PROTHEUS11.AV_BENSMTI BENS 
        WHERE SUBSTR(N1_PLACA, LENGTH(N1_PLACA)) = '{finalPlaca}'
        AND NOT EXISTS (
            SELECT 1
            FROM RPA.{tabela_ipva_lic} LC
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
        cursor.execute(fr"""
            UPDATE rpa.{tabela_ipva_lic}
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
            SELECT ID FROM {tabela_ipva_lic}
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
            INSERT INTO rpa.{tabela_ipva_lic} (PLACA, RENAVAM, CHASSI, GRUPO)
            VALUES (:placa, :renavam, :chassi, :grupo)""", 
            {
                "placa": placa, 
                "renavam": renavam, 
                "chassi": chassi, 
                "grupo": grupo
            })
    # Usar fetchall() para pegar todas as linhas
    #idVeiculo = cursor.fetchall()
    #print(f'Veiculo {idVeiculo} inserido com sucesso!')
    connectionBd.commit()
    return #idVeiculo

def InserirNumDoc(placa,chassi,numDoc):
    cursor.execute(fr"""
            INSERT INTO {tabela_ipva_lic} (NUM_DOCUMENTO) 
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
