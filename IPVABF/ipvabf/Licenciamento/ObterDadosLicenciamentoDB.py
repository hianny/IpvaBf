import oracledb
import pandas

usernameBd = 'rpa' 
passwordBd= 'Rpa!2023'
#dsn = 'oracledbdev.bomfuturo.local:1521/homollnx'
dsn = 'oracle.bomfuturo.local:1521/protheus'
connectionBd = oracledb.connect(user=usernameBd, password=passwordBd, dsn=dsn)
cursor = connectionBd.cursor()

def RetornoVeiculosLicenciamento(final_placa):
    cursor.execute(
        fr'''SELECT 
                ID
                ,PLACA
                ,RENAVAM
                ,CHASSI
                ,NUM_DOCUMENTO 
            FROM IPVA_LICENCIAMENTO
            WHERE NUM_DOCUMENTO IS NOT NULL
            --AND PLACA in ('OBE3I59')
            AND  substr(placa,7,1) IN ('{final_placa}') 
            --AND STATUS_MULTAS IS null  
            --AND DT_ULT_CONSULTA_MULTAS < TRUNC(SYSDATE, 'MM')
            --OR DT_ULT_CONSULTA_MULTAS IS NULL 
            '''
        ) 
    # Usar fetchall() para pegar todas as linhas
    VeiculosTotal = cursor.fetchall()
    veiculosporPlacas = pandas.DataFrame(VeiculosTotal,columns=['ID','PLACA','RENAVAM','CHASSIS','NUM_DOCUMENTO'])
    #VEICULOSPLACA = df.columns['PLACA','RENAVAM','CHASSIS']
    #df.to_csv(fr'sequencianotas\cnpjFiliais\resultado.csv', index=False, header=False)
    print(type(veiculosporPlacas))
    return VeiculosTotal


def RetornoVeiculosErro():
    cursor.execute(
        fr'''SELECT 
                ID
                ,PLACA
                ,RENAVAM
                ,CHASSI
                ,NUM_DOCUMENTO 
            FROM IPVA_LICENCIAMENTO
            WHERE NUM_DOCUMENTO IS NOT NULL
            AND (STATUS_MULTAS LIKE '%ERRO%'
            OR STATUS_LICENCIAMENTO LIKE '%ERRO%') 
            AND DT_ULT_CONSULTA_MULTAS < TRUNC(SYSDATE, 'MM')
            OR DT_ULT_CONSULTA_MULTAS IS NULL   
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
        UPDATE IPVA_LICENCIAMENTO
            SET  STATUS_LICENCIAMENTO = '{mensagemErro}',
            STATUS_MULTAS = '{erroPmulta}',
            MULTAS = '0',
            DT_ULT_CONSULTA_DETRAN = sysdate,
            DT_ULT_CONSULTA_MULTAS = sysdate 
            WHERE  ID = '{idVeiculoAtual}'
            """)
    connectionBd.commit()
    print('Mudanca no banco com update de erro geral: ',cursor.rowcount)


def updateErroLic(idVeiculoAtual):
    cursor.execute(fr"""
        UPDATE IPVA_LICENCIAMENTO
            SET  STATUS_LICENCIAMENTO = 'ERRO - Servico indisponivel',
            DT_ULT_CONSULTA_DETRAN = sysdate,
            DT_ULT_CONSULTA_MULTAS = sysdate 
            WHERE  ID = '{idVeiculoAtual}'
            """)
    connectionBd.commit()
    print('Mudanca no banco com update de erro no licenciamento: ',cursor.rowcount)

def updateErroMulta(idVeiculoAtual):
    cursor.execute(fr"""
        UPDATE IPVA_LICENCIAMENTO
            SET STATUS_MULTAS = 'ERRO-Site',
            MULTAS = '0',
            DT_ULT_CONSULTA_MULTAS = sysdate 
            WHERE  ID = '{idVeiculoAtual}'
            """)
    connectionBd.commit()
    print('Mudanca no bancocom update de erro nas multas: ',cursor.rowcount)


def update(mensagem,idVeiculoAtual):
    cursor.execute(fr"""
        UPDATE IPVA_LICENCIAMENTO
            SET  STATUS_LICENCIAMENTO = '{mensagem}',
            STATUS_MULTAS = 'SEM DEBITOS',
            MULTAS = '0',
            DT_ULT_CONSULTA_DETRAN = sysdate,
            DT_ULT_CONSULTA_MULTAS = sysdate 
              WHERE  ID = '{idVeiculoAtual}'
            """)
    connectionBd.commit()
    print('Mudanca no banco com update: ',cursor.rowcount) 

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
    print('Mudanca no banco com update de valor no licenciamento: ',cursor.rowcount)

def updateValorMultas(valorDebitos,arquivoDebitos,caminhoMultas,idDebitos):
    arquivoDebitos = arquivoDebitos.replace(',', '.')
    cursor.execute(fr"""
        UPDATE IPVA_LICENCIAMENTO
        SET STATUS_MULTAS = 'A PAGAR',
            MULTAS = '{valorDebitos}',
            DT_ULT_CONSULTA_MULTAS = SYSDATE,
            PRECO_MULTAS = '{arquivoDebitos}',
            ARQUIVO_MULTAS = '{caminhoMultas}'
        WHERE ID = '{idDebitos}'
            """)
    connectionBd.commit()
    print('Mudanca no banco com update de valor nas multas: ',cursor.rowcount)
  

def updateValorSDebitos(idDebitos):
    cursor.execute(fr"""
        UPDATE IPVA_LICENCIAMENTO 
            SET DT_ULT_CONSULTA_MULTAS = SYSDATE,
            MULTAS = '0',
            STATUS_MULTAS = 'SEM DEBITOS'
        WHERE ID = '{idDebitos}'
            """)
    connectionBd.commit()
    print('Mudanca no banco com update de veiculo sem debito nas multas: ',cursor.rowcount)    

def updateValorSDebitosLic(idDebitos):
    cursor.execute(fr"""
        UPDATE IPVA_LICENCIAMENTO
            SET DT_ULT_CONSULTA_DETRAN = SYSDATE,
            STATUS_LICENCIAMENTO = 'QUITADO'
        WHERE ID = '{idDebitos}'
            """)
    connectionBd.commit()
    print('Mudanca no banco com update de veiculo sem debito no licenciamento: ',cursor.rowcount)        

if __name__ == "__main__":
    RetornoVeiculosLicenciamento('')
    RetornoVeiculosErro()
    updateErro('','')
    updateErroLic('')
    updateValorSDebitosLic('')
    updateValorSDebitos('')
    updateErroMulta('')
    update('','')
    updateValor('','','')
    updateValorMultas('','','')

