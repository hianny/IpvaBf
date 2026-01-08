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

def RetornoVeiculosIpva():
    cursor.execute(fr"""
        SELECT
            RENAVAM,
            NUM_DOCUMENTO,
            CHASSI,
            ID
        FROM
            {tabela_ipva_lic}
        WHERE
            STATUS_IPVA IS NULL
	    --AND (GRUPO NOT IN (406, 309, 306)--
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

    return Veiculos

def updateErro(mensagemErro,idVeiculoAtual):
    cursor.execute(fr"""
        UPDATE {tabela_ipva_lic} SET  STATUS_IPVA = '{mensagemErro}',
            DT_ULT_CONSULTA_DETRAN = sysdate WHERE  ID = '{idVeiculoAtual}'
            """)
    connectionBd.commit()
    print(cursor.rowcount)

def update(mensagem,idVeiculoAtual):
    cursor.execute(fr"""
        UPDATE {tabela_ipva_lic} SET STATUS_LICENCIAMENTO = '{mensagem}',
            DT_ULT_CONSULTA_DETRAN = sysdate WHERE  ID = '{idVeiculoAtual}'
            """)
    connectionBd.commit()
    print(cursor.rowcount)    

def updateValor(valorLicenciamento,arquivoLicenciamento,idVeiculoAtual):
    sql = (fr"""
        UPDATE {tabela_ipva_lic} 
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
    updateErro('','')
    update('','')
    updateValor('','','')

