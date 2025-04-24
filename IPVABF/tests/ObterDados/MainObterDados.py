import ObterDadosDB
import sys

finalPlaca = str(sys.argv[1:][0])

try:

    veiculosbens = ObterDadosDB.RetornoVeiculosBen(finalPlaca)

    if veiculosbens.empty:
        print("Nao foi encontrado veiculos no banco")
    else:
        for _, row in veiculosbens.iterrows():
            try:
                #print(row)
                ObterDadosDB.veiculoIndividual(row['PLACA'], row['RENAVAM'], row['CHASSIS'], row['GRUPO'])
                ObterDadosDB.InserirDadosTabela(row['PLACA'], row['RENAVAM'], row['CHASSIS'], row['GRUPO'])
            except Exception as e:
                print(f"O VEICULO COM A PLACA {row['PLACA']} DEU ERRO: {e}")

except Exception as e:
    print(fr'ocorreu um erro {e}')
    pass