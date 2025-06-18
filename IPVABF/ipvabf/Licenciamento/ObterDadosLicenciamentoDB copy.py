import oracledb
import pandas

usernameBd = 'rpa' 
passwordBd= 'Rpa!2023'
dsn = 'oracledbdev.bomfuturo.local:1521/homollnx'
#dsn = 'oracle.bomfuturo.local:1521/protheus'
connectionBd = oracledb.connect(user=usernameBd, password=passwordBd, dsn=dsn)
cursor = connectionBd.cursor()

def RetornoVeiculosLicenciamento():
    cursor.execute(
        ''' SELECT 
                ID
                ,PLACA
                ,RENAVAM
                ,CHASSI
                ,NUM_DOCUMENTO 
            FROM IPVA_LICENCIAMENTO_MULTAS 
            WHERE NUM_DOCUMENTO IS NOT NULL
            --AND VALOR_LICENCIAMENTO = '140' 
            AND  substr(placa,7,1) IN ('0') 
            --AND STATUS_LICENCIAMENTO ='A PAGAR'  
            '''
        )
       
    # Usar fetchall() para pegar todas as linhas
    VeiculosTotal = cursor.fetchall()
    
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

def updateMulta(numDebito,preco,idVeiculoAtual):
    cursor.execute("""
    UPDATE IPVA_LICENCIAMENTO_MULTAS
    SET STATUS_MULTAS = ':1',
        MULTAS = ':2',
        DT_ULT_CONSULTA_DETRAN = SYSDATE,
        PRECO_MULTAS = ':3'
    WHERE ID = ':4'
""", ('A PAGAR', numDebito, preco, idVeiculoAtual))
    
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

def updateValorMultas(valorDebitos,arquivoDebitos,idDebitos):
    sql = (fr"""
        UPDATE IPVA_LICENCIAMENTO 
        SET DT_ULT_CONSULTA_MULTAS = SYSDATE,
            STATUS_MULTAS = 'A PAGAR',
            PRECO_MULTAS = ':valorMultas,'
            ARQUIVO_MULTAS = ':arquivoMultas,'
        WHERE ID = :'idVeiculo'
            """)
    cursor.execute(sql, {
        "valorMultas": valorDebitos,
        "arquivoMultas": arquivoDebitos,
        "idVeiculo": idDebitos
    })

    connectionBd.commit()
    print(cursor.rowcount)  

def updateValorSDebitos(idDebitos):
    sql = (fr"""
        UPDATE IPVA_LICENCIAMENTO 
        SET DT_ULT_CONSULTA_MULTAS = SYSDATE,
            STATUS_MULTAS = 'SEM DEBITOS',
        WHERE ID = ':idVeiculo'
            """)
    cursor.execute(sql, {
        "idVeiculo": idDebitos
    })

    connectionBd.commit()
    print(cursor.rowcount)        

if __name__ == "__main__":
    RetornoVeiculosLicenciamento()
    updateErro('','')
    update('','')
    updateValor('','','')
    updateMulta('','','')

