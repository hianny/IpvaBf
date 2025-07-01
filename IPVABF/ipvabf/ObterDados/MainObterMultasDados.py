import ObterDadosMultasDB 
import sys

tabela_ipva='ipva_licenciamento'
#finalPlaca = str(sys.argv[1:][0])
#finalPlaca = '0'
def mainObterDados(finalPlaca):
    try:

        veiculosbens = ObterDadosMultasDB.RetornoVeiculosBen(finalPlaca)
        #print(veiculosbens)

        if veiculosbens.empty:
            print("Nao foi encontrado veiculos no banco")
        else:
            for _, row in veiculosbens.iterrows():
                try:
                    print(row)
                    ObterDadosMultasDB.veiculoIndividual(row['PLACA'], row['RENAVAM'], row['CHASSIS'], row['GRUPO'])
                    ObterDadosMultasDB.InserirDadosTabela(row['PLACA'], row['RENAVAM'], row['CHASSIS'], row['GRUPO'])
                    ObterDadosMultasDB.RetornoVeiculosIpva(row['PLACA'],row['CHASSIS'],tabela_ipva) #peha o num documento da utima tabela de ipva e lic
                except Exception as e:
                    print(f"O VEICULO COM A PLACA {row['PLACA']} DEU ERRO: {e}")

    except Exception as e:
        print(fr'ocorreu um erro {e}')
        pass
        
if __name__ == "__main__":
    if len(sys.argv) > 1:
        final_placa = sys.argv[1]
        mainObterDados(final_placa)