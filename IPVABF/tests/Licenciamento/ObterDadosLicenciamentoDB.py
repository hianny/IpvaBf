import oracledb
import pandas

usernameBd = 'rpa' 
passwordBd= 'Rpa!2023'
dsn = 'oracledbdev.bomfuturo.local:1521/homollnx'
connectionBd = oracledb.connect(user=usernameBd, password=passwordBd, dsn=dsn)
cursor = connectionBd.cursor()

def RetornoVeiculosLicenciamento():
    cursor.execute("""
        SELECT 
            ID
            ,PLACA
            ,RENAVAM
            ,CHASSI
            ,NUM_DOCUMENTO 
        FROM IPVA_LICENCIAMENTO 
        WHERE NUM_DOCUMENTO is not null 
        --AND STATUS_LICENCIAMENTO IS NULL 
        AND RENAVAM <>'0'
        --AND SUBSTR(PLACA, LENGTH(PLACA),1) IN ('7','6','5')
        --	AND (STATUS_LICENCIAMENTO IS NULL 
        --	OR  STATUS_LICENCIAMENTO = 'ERRO - Captcha' 
        --	OR  STATUS_LICENCIAMENTO = 'ERRO - Documento Invalido')
        ORDER BY STATUS_LICENCIAMENTO DESC,  RENAVAM ASC
            """)
    # Usar fetchall() para pegar todas as linhas
    VeiculosTotal = cursor.fetchall()
    #print(type(VeiculosTotal))
    #for veiculo in VeiculosTotal:
        #print(veiculo[0])
    
    veiculosporPlacas = pandas.DataFrame(VeiculosTotal,columns=['ID','PLACA','RENAVAM','CHASSIS','NUM_DOCUMENTO'])
    #VEICULOSPLACA = df.columns['PLACA','RENAVAM','CHASSIS']
    #df.to_csv(fr'sequencianotas\cnpjFiliais\resultado.csv', index=False, header=False)
    print(type(veiculosporPlacas))
    return VeiculosTotal


if __name__ == "__main__":
    RetornoVeiculosLicenciamento()

