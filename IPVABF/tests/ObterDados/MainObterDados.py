import ObterDadosDB
import sys

finalPlaca = str(sys.argv[1:][0])

try:
    veiculosbens = ObterDadosDB.RetornoVeiculosBen(finalPlaca)

    for veiculos in veiculosbens:
        if veiculos:
            try:
                ObterDadosDB.veiculoIndividual(veiculos[0],veiculos[1],veiculos[2])

                ObterDadosDB.InserirDadosTabela(veiculos[0],veiculos[1],veiculos[2])
            except Exception as e:
                print("O VEICULO COM A PLACA "+veiculos[0]+" DEU ERRO")
        else:
            print("nao foi encontrado veiculos no banco ")

except Exception as e:
    print('ocorreu um erro')
    pass