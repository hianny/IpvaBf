import oracledb
import pandas

usernameBd = 'rpa' 
passwordBd= 'Rpa!2023'
dsn = 'oracledbdev.bomfuturo.local:1521/homollnx'
connectionBd = oracledb.connect(user=usernameBd, password=passwordBd, dsn=dsn)
cursor = connectionBd.cursor()

def RetornoVeiculosBen(finalPlaca):
    cursor.execute("""
        SELECT N1_PLACA, N1_RENAVAN, N1_CHASSIS
        FROM PROTHEUS11.AV_BENSMTI BENS
        WHERE SUBSTR(N1_PLACA, LENGTH(N1_PLACA)) = '{finalPlaca}'
        AND NOT EXISTS (
            SELECT 1
            FROM RPA.IPVA_LICENCIAMENTO LC
            WHERE BENS.N1_PLACA = LC.PLACA
                 AND BENS.N1_CHASSIS = LC.CHASSI
                 AND BENS.N1_RENAVAN = TO_NUMBER(LC.RENAVAM))
            """)
    # Usar fetchall() para pegar todas as linhas
    veiculos = cursor.fetchall()
    print(type(veiculos))
    for veiculo in veiculos:
        print(veiculo[0])
    
    veiculosporPlacas = pandas.DataFrame(veiculos,columns=['PLACA','RENAVAM','CHASSIS'])
    #VEICULOSPLACA = df.columns['PLACA','RENAVAM','CHASSIS']
   # df.to_csv(fr'sequencianotas\cnpjFiliais\resultado.csv', index=False, header=False)
    print(veiculosporPlacas)
    return veiculosporPlacas

def veiculoIndividual(placa,renavam,chassi):
    cursor.execute(fr"""
            SELECT ID FROM IPVA_LICENCIAMENTO 
            WHERE PLACA = '{placa}' 
            AND RENAVAM = '{renavam}' 
            and CHASSI = '{chassi}'
            """)
    # Usar fetchall() para pegar todas as linhas
    idVeiculo = cursor.fetchall()

    return idVeiculo

def InserirDadosTabela(placa,renavam,chassi):
    cursor.execute(fr"""
            INSERT INTO IPVA_LICENCIAMENTO (PLACA, RENAVAM, CHASSI) 
            VALUES ('{placa}', '{renavam}', '{chassi}')

            """)
    # Usar fetchall() para pegar todas as linhas
    #idVeiculo = cursor.fetchall()

    return #idVeiculo

if __name__ == "__main__":
    RetornoVeiculosBen('')
    veiculoIndividual('','','')
    InserirDadosTabela('','','')
