import oracledb
import pandas
import os

usernameBd = 'rpa' 
passwordBd= 'Rpa!2023'
#dsn = 'oracledbdev.bomfuturo.local:1521/homollnx'
dsn = 'oracle.bomfuturo.local:1521/protheus'
connectionBd = oracledb.connect(user=usernameBd, password=passwordBd, dsn=dsn)
cursor = connectionBd.cursor()


cursor.execute("""
    SELECT 
        ARQUIVO_LICENCIAMENTO
    FROM IPVA_LICENCIAMENTO 
    WHERE NUM_DOCUMENTO is not null 
    --AND STATUS_LICENCIAMENTO IS NULL
    AND STATUS_LICENCIAMENTO = 'A PAGAR'
    AND SUBSTR(PLACA, LENGTH(PLACA),1) IN ('9','8','0')
    AND DT_ULT_CONSULTA_DETRAN > TO_TIMESTAMP('2025-04-23 9:00:00', 'YYYY-MM-DD HH24:MI:SS') 
    --	AND (STATUS_LICENCIAMENTO IS NULL 
    --	OR  STATUS_LICENCIAMENTO = 'ERRO - Captcha' 
    --	OR  STATUS_LICENCIAMENTO = 'ERRO - Documento Invalido')
    ORDER BY RENAVAM DESC
        """)

arquivos_faltando = []
arquivos_ok = []

# Usar fetchall() para pegar todas as linhas
VeiculosTotal = cursor.fetchall()

for id_licenca, caminho in VeiculosTotal:
    if caminho and os.path.exists(caminho):
        arquivos_ok.append((id_licenca, caminho))
    else:
        arquivos_faltando.append((id_licenca, caminho))

# Exibe o que foi encontrado
print("Arquivos OK:")
for item in arquivos_ok:
    print(f"ID {item[0]} - {item[1]}")

print("\nArquivos com problema:")
for item in arquivos_faltando:
    print(f"ID {item[0]} - {item[1]} (não encontrado)")

# Fecha a conexão com o banco
connectionBd.close()