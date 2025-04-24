import oracledb
import pandas

usernameBd = 'rpa' 
passwordBd= 'Rpa!2023'
dsn = 'oracledbdev.bomfuturo.local:1521/homollnx'
connectionBd = oracledb.connect(user=usernameBd, password=passwordBd, dsn=dsn)
cursor = connectionBd.cursor()

def RetornoVeiculosIpva():
    cursor.execute("""
        SELECT
            RENAVAM,
            ID
        FROM
            IPVA_LICENCIAMENTO
        WHERE
            STATUS_IPVA IS NULL
        AND GRUPO NOT IN (0406, 0309, 0306)
        AND length(renavam)>1
            OR (
                STATUS_IPVA <> 'QUITADO'
                AND STATUS_IPVA <> 'A PAGAR'
                AND STATUS_IPVA <> 'ERRO - Erro ao buscar dados'
                AND length(renavam)>1
            )
        ORDER BY STATUS_IPVA desc, RENAVAM ASC
            """)
    # Usar fetchall() para pegar todas as linhas
    Veiculos = cursor.fetchall()
    print(Veiculos)
    return Veiculos

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
    RetornoVeiculosIpva()
    #updateErro('','')
    #update('','')
    #updateValor('','','')

