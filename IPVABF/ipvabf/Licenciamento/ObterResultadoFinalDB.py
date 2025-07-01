import oracledb
import pandas as pd
from datetime import datetime

usernameBd = 'rpa' 
passwordBd= 'Rpa!2023'
dsn = 'oracledbdev.bomfuturo.local:1521/homollnx'
#dsn = 'oracle.bomfuturo.local:1521/protheus'
connectionBd = oracledb.connect(user=usernameBd, password=passwordBd, dsn=dsn)
cursor = connectionBd.cursor()

def RetornoVeiculosSucesso(finalPlaca):
    cursor.execute(
        fr'''SELECT 
                PLACA
                ,RENAVAM
                ,CHASSI
                ,NUM_DOCUMENTO
                ,DT_ULT_CONSULTA_DETRAN        
                ,sTATUS_LICENCIAMENTO
                ,VALOR_LICENCIAMENTO
                ,ARQUIVO_LICENCIAMENTO
                ,DT_ULT_CONSULTA_MULTAS
                ,STATUS_MULTAS
                ,MULTAS
                ,PRECO_MULTAS
                ,ARQUIVO_MULTAS
            FROM IPVA_LICENCIAMENTO
            WHERE NUM_DOCUMENTO IS NOT NULL
            --AND VALOR_LICENCIAMENTO = '140' 
            AND  substr(placa,7,1) IN ('{finalPlaca}') 
            AND (STATUS_MULTAS ='A PAGAR' OR STATUS_LICENCIAMENTO  ='A PAGAR' )
            '''
        )    
    # Usar fetchall() para pegar todas as linhas
    VeiculosTotal = cursor.fetchall()
    veiculosporPlacas = pd.DataFrame(VeiculosTotal, columns=['PLACA','RENAVAM','CHASSIS','NUM_DOCUMENTO',
        'DT_ULT_CONSULTA_DETRAN','STATUS_LICENCIAMENTO','VALOR_LICENCIAMENTO','ARQUIVO_LICENCIAMENTO',
        'DT_ULT_CONSULTA_MULTAS','STATUS_MULTAS','MULTAS','PRECO_MULTAS','ARQUIVO_MULTAS'])
    arquivo_csv = fr'ipvabf\Licenciamento\ResultadoCsv\Veiculos_A_PAGAR_{datetime.now().strftime("%d_%m_%Y")}.csv'
    veiculosporPlacas.to_csv(arquivo_csv, index=False, header=True, sep=";")
    print('concluido csv de veiculos a pagar')
    #print(type(veiculosporPlacas))
    numeroVeiculos = len(veiculosporPlacas)
    return arquivo_csv ,numeroVeiculos

def RetornoVeiculosErro(finalPlaca):
    cursor.execute(
        fr'''SELECT 
                PLACA
                ,RENAVAM
                ,CHASSI
                ,NUM_DOCUMENTO
                ,DT_ULT_CONSULTA_DETRAN        
                ,sTATUS_LICENCIAMENTO
                ,DT_ULT_CONSULTA_MULTAS
                ,STATUS_MULTAS
            FROM IPVA_LICENCIAMENTO
            WHERE NUM_DOCUMENTO IS NOT NULL
            --AND VALOR_LICENCIAMENTO = '140' 
            AND  substr(placa,7,1) IN ('{finalPlaca}') 
            AND (STATUS_MULTAS != 'SEM DEBITOS' AND multas = 0 )  
            '''
        )    
    # Usar fetchall() para pegar todas as linhas
    VeiculosTotal = cursor.fetchall()
    veiculosporPlacas = pd.DataFrame(VeiculosTotal, columns=['PLACA','RENAVAM','CHASSIS','NUM_DOCUMENTO',
        'DT_ULT_CONSULTA_DETRAN','STATUS_LICENCIAMENTO','DT_ULT_CONSULTA_MULTAS','STATUS_MULTAS'])
    arquivo_csv = fr'ipvabf\Licenciamento\ResultadoCsv\Veiculos_ERRO_{datetime.now().strftime("%d_%m_%Y")}.csv'
    veiculosporPlacas.to_csv(arquivo_csv, index=False, header=True, sep=";")
    print('concluido csv de veiculos com erro')
    #print(type(veiculosporPlacas))
    numeroVeiculos = len(veiculosporPlacas)
    return arquivo_csv, numeroVeiculos

def RetornoVeiculosSemDebito(finalPlaca):
    cursor.execute(
        fr'''SELECT 
               PLACA
                ,RENAVAM
                ,CHASSI
                ,NUM_DOCUMENTO
                ,DT_ULT_CONSULTA_DETRAN        
                ,sTATUS_LICENCIAMENTO
                ,DT_ULT_CONSULTA_MULTAS
                ,STATUS_MULTAS
            FROM IPVA_LICENCIAMENTO
            WHERE NUM_DOCUMENTO IS NOT NULL
            --AND VALOR_LICENCIAMENTO = '140' 
            AND  substr(placa,7,1) IN ('{finalPlaca}') 
            AND (STATUS_MULTAS ='SEM DEBITOS' AND STATUS_LICENCIAMENTO  !='A PAGAR' )
            '''
        )
    # Usar fetchall() para pegar todas as linhas
    VeiculosTotal = cursor.fetchall()
    veiculosporPlacas = pd.DataFrame(VeiculosTotal, columns=['PLACA','RENAVAM','CHASSIS','NUM_DOCUMENTO',
        'DT_ULT_CONSULTA_DETRAN','STATUS_LICENCIAMENTO','DT_ULT_CONSULTA_MULTAS','STATUS_MULTAS'])
    arquivo_csv = fr'ipvabf\Licenciamento\ResultadoCsv\Veiculos_SEM_DEBITO_{datetime.now().strftime("%d_%m_%Y")}.csv'
    veiculosporPlacas.to_csv(arquivo_csv, index=False, header=True, sep=";")
    print('concluido csv de veiculos sem debito')
    numeroVeiculos = len(veiculosporPlacas)
    return arquivo_csv, numeroVeiculos

if __name__ == "__main__":
    RetornoVeiculosSucesso('')
    RetornoVeiculosErro('')
    RetornoVeiculosSemDebito('')
