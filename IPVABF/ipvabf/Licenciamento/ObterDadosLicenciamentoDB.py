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
        '''SELECT 
                ID
                ,PLACA
                ,RENAVAM
                ,CHASSI
                ,NUM_DOCUMENTO 
            FROM IPVA_LICENCIAMENTO_MULTAS 
            WHERE NUM_DOCUMENTO IS NOT NULL
            --AND PLACA = 'QCZ0J70' 
            AND  substr(placa,7,1) IN ('0') 
            AND STATUS_MULTAS IS NOT null  
            '''
        ) 
    # Usar fetchall() para pegar todas as linhas
    VeiculosTotal = cursor.fetchall()
    veiculosporPlacas = pandas.DataFrame(VeiculosTotal,columns=['ID','PLACA','RENAVAM','CHASSIS','NUM_DOCUMENTO'])
    #VEICULOSPLACA = df.columns['PLACA','RENAVAM','CHASSIS']
    #df.to_csv(fr'sequencianotas\cnpjFiliais\resultado.csv', index=False, header=False)
    print(type(veiculosporPlacas))
    return VeiculosTotal

def updateErro(mensagemErro,erroPmulta,idVeiculoAtual):
    cursor.execute(fr"""
        UPDATE IPVA_LICENCIAMENTO_MULTAS
            SET  STATUS_LICENCIAMENTO = '{mensagemErro}',
            STATUS_MULTAS = '{erroPmulta}',
            MULTAS = '0',
            DT_ULT_CONSULTA_DETRAN = sysdate,
            DT_ULT_CONSULTA_MULTAS = sysdate 
            WHERE  ID = '{idVeiculoAtual}'
            """)
    connectionBd.commit()
    print('Mudanca no banco: ',cursor.rowcount)


def updateErroLic(idVeiculoAtual):
    cursor.execute(fr"""
        UPDATE IPVA_LICENCIAMENTO_MULTAS
            SET  STATUS_LICENCIAMENTO = 'ERRO - Servico indisponivel',
            DT_ULT_CONSULTA_DETRAN = sysdate,
            DT_ULT_CONSULTA_MULTAS = sysdate 
            WHERE  ID = '{idVeiculoAtual}'
            """)
    connectionBd.commit()
    print('Mudanca no banco: ',cursor.rowcount)

def updateErroMulta(idVeiculoAtual):
    cursor.execute(fr"""
        UPDATE IPVA_LICENCIAMENTO_MULTAS
            SET STATUS_MULTAS = 'ERRO-Site',
            MULTAS = '0',
            DT_ULT_CONSULTA_MULTAS = sysdate 
            WHERE  ID = '{idVeiculoAtual}'
            """)
    connectionBd.commit()
    print('Mudanca no banco: ',cursor.rowcount)


def update(mensagem,idVeiculoAtual):
    cursor.execute(fr"""
        UPDATE IPVA_LICENCIAMENTO_MULTAS
            SET  STATUS_LICENCIAMENTO = '{mensagem}',
            STATUS_MULTAS = 'SEM DEBITOS',
            MULTAS = '0',
            DT_ULT_CONSULTA_DETRAN = sysdate,
            DT_ULT_CONSULTA_MULTAS = sysdate 
              WHERE  ID = '{idVeiculoAtual}'
            """)
    connectionBd.commit()
    print('Mudanca no banco: ',cursor.rowcount) 

def updateValor(valorLicenciamento,arquivoLicenciamento,idVeiculoAtual):
    sql = (fr"""
        UPDATE IPVA_LICENCIAMENTO_MULTAS 
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
    print('Mudanca no banco: ',cursor.rowcount)

def updateValorMultas(valorDebitos,arquivoDebitos,caminhoMultas,idDebitos):
    arquivoDebitos = arquivoDebitos.replace(',', '.')
    cursor.execute(fr"""
        UPDATE IPVA_LICENCIAMENTO_MULTAS
        SET STATUS_MULTAS = 'A PAGAR',
            MULTAS = '{valorDebitos}',
            DT_ULT_CONSULTA_MULTAS = SYSDATE,
            PRECO_MULTAS = '{arquivoDebitos}',
            ARQUIVO_MULTAS = '{caminhoMultas}'
        WHERE ID = '{idDebitos}'
            """)
    connectionBd.commit()
    print('Mudanca no banco: ',cursor.rowcount)
  

def updateValorSDebitos(idDebitos):
    cursor.execute(fr"""
        UPDATE IPVA_LICENCIAMENTO_MULTAS 
            SET DT_ULT_CONSULTA_MULTAS = SYSDATE,
            MULTAS = '0',
            STATUS_MULTAS = 'SEM DEBITOS'
        WHERE ID = '{idDebitos}'
            """)
    connectionBd.commit()
    print('Mudanca no banco: ',cursor.rowcount)    

def updateValorSDebitosLic(idDebitos):
    cursor.execute(fr"""
        UPDATE IPVA_LICENCIAMENTO_MULTAS 
            SET DT_ULT_CONSULTA_DETRAN = SYSDATE,
            STATUS_LICENCIAMENTO = 'QUITADO'
        WHERE ID = '{idDebitos}'
            """)
    connectionBd.commit()
    print('Mudanca no banco: ',cursor.rowcount)        

if __name__ == "__main__":
    RetornoVeiculosLicenciamento()
    updateErro('','')
    updateErroLic('')
    updateValorSDebitosLic('')
    updateValorSDebitos('')
    updateErroMulta('')
    update('','')
    updateValor('','','')
    updateValorMultas('','','')

