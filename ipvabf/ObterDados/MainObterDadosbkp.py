import ipvabf.ObterDados.ObterDadosDBbkp as ObterDadosDBbkp
import sys

finalPlaca = str(sys.argv[1:][0])

try:

    veiculosbens = ObterDadosDBbkp.RetornoVeiculosBen(finalPlaca)

    if veiculosbens.empty:
        print("Nao foi encontrado veiculos no banco")
    else:
        for _, row in veiculosbens.iterrows():
            try:
                #print(row)
                ObterDadosDBbkp.veiculoIndividual(row['PLACA'], row['RENAVAM'], row['CHASSIS'], row['GRUPO'])
                ObterDadosDBbkp.InserirDadosTabela(row['PLACA'], row['RENAVAM'], row['CHASSIS'], row['GRUPO'])
            except Exception as e:
                print(f"O VEICULO COM A PLACA {row['PLACA']} DEU ERRO: {e}")

except Exception as e:
    print(fr'ocorreu um erro {e}')
    pass