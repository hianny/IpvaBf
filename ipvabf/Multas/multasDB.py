import oracledb
import pandas

usernameBd = 'rpa' 
passwordBd= 'Rpa!2023'
#dsn = 'oracledbdev.bomfuturo.local:1521/homollnx'
dsn = 'oracle.bomfuturo.local:1521/protheus'
connectionBd = oracledb.connect(user=usernameBd, password=passwordBd, dsn=dsn)
cursor = connectionBd.cursor()

def RetornoVeiculosLicenciamento():
    cursor.execute("""
        SELECT PLACA, RENAVAM, CHASSI, NUM_DOCUMENTO 
        FROM rpa.ipva_licenciamento ipva
        WHERE SUBSTR(PLACA, LENGTH(PLACA)) = '0'
        AND NOT EXISTS (
            SELECT 1
            FROM RPA.MULTAS_LICENCIAMENTO_BETA MULTAS
            WHERE ipva.PLACA = MULTAS.PLACA_VEICULO
                 AND ipva.CHASSI = MULTAS.CHASSI_VEICULO
                 AND ipva.RENAVAM = TO_NUMBER(MULTAS.RENAVAM_VEICULO)
                 AND ipva.NUM_DOCUMENTO = MULTAS.NUM_DOCUMENTO_VEICULO
                 )
            """)
    # Usar fetchall() para pegar todas as linhas
    VeiculosTotal = cursor.fetchall()
    #print(type(VeiculosTotal))
    #for veiculo in VeiculosTotal:
        #print(veiculo[0])

    '''        --AND STATUS_LICENCIAMENTO IS NULL
        AND STATUS_LICENCIAMENTO = 'A PAGAR'
        AND SUBSTR(PLACA, LENGTH(PLACA),1) IN ('7')
        AND DT_ULT_CONSULTA_DETRAN < TO_TIMESTAMP('2025-04-23 9:00:00', 'YYYY-MM-DD HH24:MI:SS')
        --	AND (STATUS_LICENCIAMENTO IS NULL 
        --	OR  STATUS_LICENCIAMENTO = 'ERRO - Captcha' 
        --	OR  STATUS_LICENCIAMENTO = 'ERRO - Documento Invalido')
        ORDER BY RENAVAM DESC'''
    
    veiculosporPlacas = pandas.DataFrame(VeiculosTotal,columns=['ID','PLACA','RENAVAM','CHASSIS','NUM_DOCUMENTO'])
    #VEICULOSPLACA = df.columns['PLACA','RENAVAM','CHASSIS']
    #df.to_csv(fr'sequencianotas\cnpjFiliais\resultado.csv', index=False, header=False)
    print(type(veiculosporPlacas))
    return VeiculosTotal

def updateErro(mensagemErro,idVeiculoAtual):
    cursor.execute(fr"""
        UPDATE IPVA_LICENCIAMENTO SET  STATUS_LICENCIAMENTO = '{mensagemErro}',
            DT_ULT_CONSULTA_DETRAN = sysdate WHERE  ID = '{idVeiculoAtual}'
            """)
    connectionBd.commit()
    print(cursor.rowcount)

def update(mensagem,idVeiculoAtual):
    cursor.execute(fr"""
        UPDATE IPVA_LICENCIAMENTO SET  STATUS_LICENCIAMENTO = '{mensagem}',
            DT_ULT_CONSULTA_DETRAN = sysdate WHERE  ID = '{idVeiculoAtual}'
            """)
    connectionBd.commit()
    print(cursor.rowcount)    

def updateValor(valorLicenciamento,arquivoLicenciamento,idVeiculoAtual):
    sql = (fr"""
        UPDATE IPVA_LICENCIAMENTO 
        SET DT_ULT_CONSULTA_DETRAN = SYSDATE,
            STATUS_LICENCIAMENTO = 'A PAGAR',
            VALOR_LICENCIAMENTO = :valorLicenciamento,
            ARQUIVO_LICENCIAMENTO = :arquivoLicenciamento
        WHERE ID = :idVeiculo
            """)
    cursor.execute(sql, {
        "valorLicenciamento": valorLicenciamento,
        "arquivoLicenciamento": arquivoLicenciamento,
        "idVeiculo": idVeiculoAtual
    })

    connectionBd.commit()
    print(cursor.rowcount)     

if __name__ == "__main__":
    RetornoVeiculosLicenciamento()
    updateErro('','')
    update('','')
    updateValor('','','')

