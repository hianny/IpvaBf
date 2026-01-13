import oracledb
import pandas
import dotenv
import os
from decimal import Decimal

dotenv.load_dotenv()

usernameBd = os.getenv('usernameBd')
passwordBd= os.getenv('passwordBd')
dsn = os.getenv('dsn')
connectionBd = oracledb.connect(user=usernameBd, password=passwordBd, dsn=dsn)
cursor = connectionBd.cursor()

tabela_ipva_lic = 'ipva_licenciamento'

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
            NUM_DOCUMENTO IS NOT NULL
            AND length(renavam) > 1
            AND (
                (STATUS_IPVA IS NULL AND GRUPO NOT IN ('0306','0309','0406'))
                OR
                (STATUS_IPVA NOT IN ('QUITADO', 'A PAGAR', 'ERRO - Erro ao buscar dados')
                AND GRUPO NOT IN ('0306','0309','0406'))
            )
        ORDER BY STATUS_IPVA desc, RENAVAM ASC
            """)
    # Usar fetchall() para pegar todas as linhas
    Veiculos = cursor.fetchall()

    return Veiculos

def updateErro(mensagemErro,idVeiculoAtual):
    cursor.execute(fr"""
        UPDATE {tabela_ipva_lic} SET  STATUS_IPVA = '{mensagemErro}',
            DT_ULT_CONSULTA_SEFAZ = sysdate WHERE  ID = '{idVeiculoAtual}'
            """)
    connectionBd.commit()
    print(cursor.rowcount)

def update(mensagem,idVeiculoAtual):
    cursor.execute(fr"""
        UPDATE {tabela_ipva_lic} SET STATUS_IPVA = '{mensagem}',
            DT_ULT_CONSULTA_SEFAZ = sysdate WHERE  ID = '{idVeiculoAtual}'
            """)
    connectionBd.commit()
    print(cursor.rowcount)    

from decimal import Decimal

def updateValor(valorLicenciamento, arquivoLicenciamento, idVeiculoAtual):
    try:
        # 1️⃣ Verificar escala da coluna
        cursor.execute(f"""
            SELECT data_scale
            FROM user_tab_columns
            WHERE table_name = UPPER(:1)
              AND column_name = 'VALOR_IPVA'
        """, (tabela_ipva_lic,))
        
        row = cursor.fetchone()

        if row is None:
            raise Exception("Coluna VALOR_IPVA não encontrada")

        data_scale = row[0]

        # 2️⃣ Alterar coluna se escala for menor que 5
        if data_scale is None or data_scale < 5:
            print("Alterando escala da coluna VALOR_IPVA para 5 casas decimais...")
            cursor.execute(f"""
                ALTER TABLE {tabela_ipva_lic}
                MODIFY VALOR_IPVA NUMBER(10,5)
            """)
            connectionBd.commit()
            print("Coluna VALOR_IPVA alterada com sucesso.")

        # 3️⃣ Update do valor
        sql_update = f"""
            UPDATE {tabela_ipva_lic} 
            SET DT_ULT_CONSULTA_SEFAZ = SYSDATE,
                STATUS_IPVA = 'A PAGAR',
                VALOR_IPVA = :1,
                ARQUIVO_IPVA = :2
            WHERE ID = :3
        """

        cursor.execute(sql_update, (
            Decimal(valorLicenciamento),
            arquivoLicenciamento,
            idVeiculoAtual
        ))

        connectionBd.commit()
        print(f"Sucesso! Linhas atualizadas: {cursor.rowcount}")

    except Exception as e:
        connectionBd.rollback()
        print(f"Erro ao atualizar banco de dados: {e}")


if __name__ == "__main__":
    RetornoVeiculosIpva()
    updateErro('','')
    update('','')
    updateValor('','','')

