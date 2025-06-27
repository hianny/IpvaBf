from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.ui import Select
import ObterDadosLicenciamentoDB
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from escreveLog import escreveLog
import os
import ResultadoEmail
from time import sleep
from ObterResultadoFinalDB import RetornoVeiculosSucesso, RetornoVeiculosErro,RetornoVeiculosSemDebito
import base64
from datetime import datetime
import sys
#OQUE AINDA FALTA
#
#FAZER TRIGGER PARA FAZER DE TODAS AS PLACAS
#COMO FAZER A TRIGGER?
#CRIAR CSV QUE ARMAZENA AS INFORMACOES DO VEICULO
#DPS DO TERMINO DE CADA PLACA ENVIAR UM NOTIFICACAO DE TERMINO 
#MANDAR UM EMAIL COM O RESULTADO DO PROCESSO COM OS ERROS E SUCESSOS
#


def main(final_placa):
    try:
        print(final_placa)
        if final_placa == 'erro':  
             resultadoVeiculos = ObterDadosLicenciamentoDB.RetornoVeiculosErro()   
        else:
            resultadoVeiculos = ObterDadosLicenciamentoDB.RetornoVeiculosLicenciamento(final_placa)
        #print(resultadoVeiculos)
        #PLACA,RENAVAM,CHASSIS,NUM_DOCUMENTO = ObterDadosLicenciamentoDB.RetornoVeiculosLicenciamento()
        escreveLog("---------Iniciando Sequencia de notas Sefaz---------")
        print("---------Iniciando Sequencia de notas Sefaz---------")

        chrome_options = uc.ChromeOptions()
        prefs = {
            "download.default_directory": fr"C:\BOT\LICENCIAMENTO",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        #chrome_options.add_argument('--user-data-dir=/path/to/your/chrome/profile')  # Caminho do perfil
        chrome_options.add_argument('--profile-directory=Profile 1')  # Nome do perfil específico
        chrome_options.add_argument('--start-maximized')
        #chrome_options.add_argument('--headless')
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        driver = uc.Chrome(options=chrome_options, version_main=137)
        driver.set_window_size(1200, 700)
        url = "https://www.detran.mt.gov.br/"
        driver.implicitly_wait(2)
        driver.get(url)
        escreveLog('Abrindo o navegador')

        idVeiculo = veiculos[0]
        placaVeiculo = veiculos[1]
        renavamVeiculo = veiculos[2]
        num_documentoVeiculo = veiculos[4]

        realizandoLicenciamento(driver,placaVeiculo,renavamVeiculo,num_documentoVeiculo,idVeiculo)
        escreveLog("Finalizando as consultas do veiculo com a placa: ",placaVeiculo)
        escreveLog("fechando navegador definitivamente")
        print("fechando navegador definitivamente")
        


        escreveLog("---------Finalizando Sequencia de notas Sefaz---------")    
        print("---------Finalizando Sequencia de notas Sefaz---------")
        arquivoCsvSucesso , numeroCsvSucesso = RetornoVeiculosSucesso() 
        arquivoCsvErro, numeroCsErro = RetornoVeiculosErro()
        arquivoCsvSemDebito, numeroCsvDebito = RetornoVeiculosSemDebito()
        print('Enviando email de finalizacao')
        escreveLog('Enviando email de finalizacao')
        ResultadoEmail.ResultadoFinalEmail('0', len(resultadoVeiculos),numeroCsErro,numeroCsvSucesso,numeroCsvDebito,arquivoCsvSucesso,arquivoCsvErro,arquivoCsvSemDebito)

        #criar funcao de banco com3  selects criando em csv para cada status
        #Colocar um email de notificacao de finalizacao do processo com numero de veiculos com falha, sucesso e sem debito
        #no email colocar o csv com cada status
        #
    except Exception as e :
        escreveLog('Ocorreu um erro no FOR principal: ',e)
        print('Ocorreu um Erro no FOR principal: ',e)
        escreveLog("---------Finalizando Sequencia de notas Sefaz---------")    
        print("---------Finalizando Sequencia de notas Sefaz---------")
        arquivoCsvSucesso , numeroCsvSucesso = RetornoVeiculosSucesso() 
        arquivoCsvErro, numeroCsErro = RetornoVeiculosErro()
        arquivoCsvSemDebito, numeroCsvDebito = RetornoVeiculosSemDebito()
        print('Enviando email de finalizacao')
        escreveLog('Enviando email de finalizacao')
        ResultadoEmail.ResultadoErro('0', len(resultadoVeiculos),numeroCsErro,numeroCsvSucesso,numeroCsvDebito,arquivoCsvSucesso,arquivoCsvErro,arquivoCsvSemDebito)
        pass

def realizandoLicenciamento(driver,placaVeiculo,renavamVeiculo,num_documentoVeiculo,idVeiculo):
    def emitirLicenciamento():
        escreveLog(f'Emitindo licenciamento')
        emitir = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.ID, "spanDAR_LicenciamentoExercicio"))
                )
        emitir.click()

        sleep(2)

        driver.execute_script("window.focus();")
        #print("mudando a pagina")
        driver.switch_to.window(driver.window_handles[2])

        #---------------------
        # Nova aba
        #------------------------trocando para nova aba do navegador----------------------------------
        #print("Título da nova aba:", driver.title)

        try:
            ErroSiteIndiposnivel = driver.find_elements(By.XPATH, "/html/body/center/font")
            if ErroSiteIndiposnivel:
                print("O site NAO esta disponivel")
                ObterDadosLicenciamentoDB.updateErroLic(idVeiculo)
        except:
            print("O site esta disponivel")
            

        state = driver.execute_script('return document.readyState')
        total_height = driver.execute_script("return document.body.scrollHeight")
        sleep(10)
        pdf = driver.execute_cdp_cmd("Page.printToPDF", {
            "printBackground": True
        })
        #------------------------------------
        # salvando pagina para pdf
        #------------------------------------
        anoAtual = datetime.now().year
        caminhoLicenciamento = fr"C:\BOT\LICENCIAMENTO\TESTE Lic Licenciamento {anoAtual} - RENAVAM {renavamVeiculo}.pdf"

        with open(caminhoLicenciamento, "wb") as f:
            f.write(base64.b64decode(pdf['data']))

        if os.path.exists(caminhoLicenciamento):
            print("PDF salvo com sucesso!")
            print("valor que esta no licenciamento: ",valorliceinciamento)
            ObterDadosLicenciamentoDB.updateValor(valorLicenciamento,caminhoLicenciamento,idVeiculo)
            driver.close()
            driver.switch_to.window(driver.window_handles[1])
            #ObterDadosLicenciamentoDB.updateValorMultas(valorLicenciamento,caminhoLicenciamento,idVeiculo)
            #updatebanco 
        else:
            print("Erro ao salvar o PDF.")
            driver.close()
            driver.switch_to.window(driver.window_handles[1])
#            driver.close()
#            driver.switch_to.window(driver.window_handles[0])
#            driver.close()
            print("fechando navegador do emitir licenciamento")

    def emitirMultas(quantidade_checkboxes):
        escreveLog(f'Emitindo multa')

        select.select_by_value("Multa")
        
        for i in range(1, quantidade_checkboxes + 1):
            checkbox_id = f"DebitoMulta{i}"

            try:
                checkbox = driver.find_element(By.ID, checkbox_id)
                
                # Verifica se já está selecionado
                if not checkbox.is_selected():
                    checkbox.click()
            except Exception as e:
                print(f"Não foi possível encontrar ou clicar em {checkbox_id}: {e}")

        emitir = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "spanDAR_Multa"))
        )
        emitir.click()

        sleep(2)

        driver.execute_script("window.focus();")
        #print("mudando a pagina")
        driver.switch_to.window(driver.window_handles[2])

        #---------------------
        # Nova aba
        #------------------------trocando para nova aba do navegador----------------------------------
        #print("Título da nova aba:", driver.title)

        try:
            ErroSiteIndiposnivel = driver.find_elements(By.XPATH, "/html/body/center/font")
            if ErroSiteIndiposnivel:
                print("O site NAO esta disponivel")
                ObterDadosLicenciamentoDB.updateErroMulta(idVeiculo)
        except:
            print("O site esta disponivel")

        state = driver.execute_script('return document.readyState')
        total_height = driver.execute_script("return document.body.scrollHeight")

        sleep(15)
        pdf = driver.execute_cdp_cmd("Page.printToPDF", {
            "printBackground": True
        })

        #------------------------------------
        # salvando pagina para pdf
        #------------------------------------
        anoAtual = datetime.now().year
        caminhoMultas = fr"C:\BOT\MULTAS\MULTAS - {anoAtual} - RENAVAM {renavamVeiculo}.pdf"

        with open(caminhoMultas, "wb") as f:
            f.write(base64.b64decode(pdf['data']))

        if os.path.exists(caminhoMultas):
            print("PDF salvo com sucesso!")
            print("valor que esta no licenciamento: ",valorliceinciamento)
            #print(valorliceinciamento)
            #ObterDadosLicenciamentoDB.updateValor(valorLicenciamento,caminhoLicenciamento,idVeiculo)
            #ObterDadosLicenciamentoDB.updateValorMultas(valorLicenciamento,caminhoMultas,idVeiculo)
            ObterDadosLicenciamentoDB.updateValorMultas(numeroDebitos,valorDebitos,caminhoMultas,idVeiculo)
            #updatebanco 
            driver.close()
            driver.switch_to.window(driver.window_handles[1])
            
        else:
            print("Erro ao salvar o PDF.")
            driver.close()
            driver.switch_to.window(driver.window_handles[1])
#            driver.close()
#            driver.switch_to.window(driver.window_handles[0])
#            driver.close()
            print("fechando navegador do emitir multas")
    
    while True:
        sleep(3)
        escreveLog('Iniciando o site do Detran')
        print('iniciando login no site do Detran')
        propagranda = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mtSitesPopup"]/div/div/div[1]/button'))
        )
        propagranda.click() 
        sleep(3)
        placa = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'Placa'))
        )
        placa.send_keys(placaVeiculo) 
        sleep(3)

        renavam = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'Renavam'))
        )
        renavam.send_keys(renavamVeiculo) 
        sleep(3)

        consultar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="formVeiculo"]/div[4]/input[2]'))
        )
        consultar.click() 
        print('login realizado')
        escreveLog('login realizado')
        #windows = driver.window_handles
        driver.execute_script("window.focus();")
        #print("mudando a pagina")
        driver.switch_to.window(driver.window_handles[1])

        # Troca pra nova aba
#------------------------trocando para nova aba do navegador----------------------------------

        #print("Título da nova aba:", driver.title)
        # Checa se a página terminou de carregar
        state = driver.execute_script('return document.readyState')
        print("Estado da página:", state)
        print('inicinando pagina de captcha e numero de documento')
        cpfCnpj = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'DocumentoProprietarioValidacao'))
        )
        cpfCnpj.send_keys(num_documentoVeiculo) 
        sleep(5)


        import captchaLic
        token = captchaLic.capsolver()  # Chama a função para resolver o captcha

        driver.execute_script(f'''
        document.querySelector('input[name="cf-turnstile-response"]').value = "{token}";
        document.querySelector('input[name="g-recaptcha-response"]').value = "{token}";
        ''')
        #comecando a etapa de resolver o captcha
        escreveLog("O captcha foi resolvido")
        print("Captcha finalizado")

        #confirmando '''
        btConsultar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'btOk'))
        )
        btConsultar.click()
        print("clicando no botao consultar")
        escreveLog("Consultando o veiculo")
        sleep(2)
        try:
            textoErro = ''                         #/html/body/center/div/table/tbody/tr/td/text()[2]
            erro =  driver.find_element(By.XPATH, "/html/body/center/div/table/tbody/tr/td")
            textoErro = erro.text
            print(textoErro)
        except:
            pass
        print("Verificando se houve erro na consulta do veiculo")
        escreveLog("Verificando se houve erro na consulta do veiculo")
        #verificando informacoes no documento
        #caso nao tenha debito o
        #-------------------------------------
        #ACRESCENTAR O MULTAS NESSA PARTE DO BANCO 
        if textoErro:
            if textoErro[23:] == "Documento Proprietario informado não confere com o proprietario do veiculo.":
                ObterDadosLicenciamentoDB.updateErro('ERRO - Documento N/ Confere','ERRO-Doc',idVeiculo)
                escreveLog(f'Erro - Documento N/ Confere para o veiculo {placaVeiculo}')
            elif textoErro[23:] == "Documento do Proprietario invalido.":
                print(type(idVeiculo))
                #Idatual = f"{int(idVeiculo):,}".replace(",", ".")
                #print(Idatual)
                ObterDadosLicenciamentoDB.updateErro('ERRO - Documento Invalido','ERRO-Doc',idVeiculo)
                escreveLog(f'Erro - Documento Invalido para o veiculo {placaVeiculo}')

            elif textoErro[23:] == "Confirme Nao sou Robo":
                ObterDadosLicenciamentoDB.updateErro('ERRO - Captcha','ERRO-Captcha',idVeiculo)
                escreveLog(f'Erro - Captcha para o veiculo {placaVeiculo}')

            elif textoErro[23:] == "Favor acessar o formulário para nova consulta":
                ObterDadosLicenciamentoDB.updateErro('ERRO - Formulario','ERRO-Form',idVeiculo)
                escreveLog(f'Erro - Acessar o formulário para nova consulta {placaVeiculo}')

            elif textoErro[23:] == "Renavam informado não confere com a Placa.":
                ObterDadosLicenciamentoDB.updateErro('ERRO - Renavam Invalido','ERRO-Renavam',idVeiculo)
                escreveLog(f'Erro - Renavam Invalido para o veiculo {placaVeiculo}')

            elif textoErro[23:] == "Operação cancelada. Veículo não emplacado na base local ou não possui infrações na base local":
                ObterDadosLicenciamentoDB.updateErro('ERRO - N/ emplacado base local','ERRO-baseLoc',idVeiculo)
                escreveLog(f'Erro - N/ emplacado na base local para o veiculo {placaVeiculo}')
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            driver.close()
            break

#------------------------trocando para nova aba do navegador----------------------------------
        debito = driver.find_element(By.XPATH, '//*[@id="div_servicos_Debitos"]/table/tbody/tr/td')
        debitos = debito.text

        if debitos:
            if debitos == "Nenhum débito em aberto cadastrado para este veículo.":
                                                                     #-------------------------------------
                ObterDadosLicenciamentoDB.update('QUITADO',idVeiculo)  #ADICIONAR COLUNA DE STATUS MULTAS
                print(fr"o veiculo da placa {placaVeiculo} nao tem nenhum debito")
                escreveLog(fr"o veiculo da placa {placaVeiculo} nao tem nenhum debito")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                driver.close()
                
                break
        else:
            pass

        #print("verificando a data do licenciamento")
        select_element = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "cmbTipoDebito"))
            )
        #select_element = driver.find_element(By.ID, "cmbTipoDebito")
        # Cria um objeto Select
        select = Select(select_element)

        existeMulta = False
        temIntegral = False

        for option in select.options:
            existeLic = False
            value = option.get_attribute("value")
            text = option.text.strip()

            if value == 'LicenciamentoExercicio':
                existeLic = True
                select.select_by_value("LicenciamentoExercicio")
                ObterDadosLicenciamentoDB.update('A PAGAR', idVeiculo)
                print(fr'O veículo da placa {placaVeiculo} ainda possui pendência de licenciamento')
                escreveLog(fr'O veículo da placa {placaVeiculo} ainda possui pendência de licenciamento')
                valorliceinciamento = driver.find_element(By.ID, 'spanDAR_LicenciamentoExercicio')
                valorLicenciamento = valorliceinciamento.text
                valorLicenciamento = valorLicenciamento[35:-4]
                print('O valor do licenciamento ficou: ',valorLicenciamento)
                emitirLicenciamento()

            elif text == 'Multas':
                existeMulta = True

            elif text == 'Todos os débitos':
                temIntegral = True
        if existeLic == False:
            ObterDadosLicenciamentoDB.updateValorSDebitosLic(idVeiculo)  
        if temIntegral:

            try:
                select.select_by_value("Multa")
            except:
                pass
            select.select_by_value("Integral")
            tbody = driver.find_element(By.XPATH, '//*[@id="Integral"]/table/tbody')
            trs = tbody.find_elements(By.TAG_NAME, 'tr')

            if existeMulta and len(trs) > 2:
                print(fr"O veículo da placa {placaVeiculo} possui multas pendentes")
                escreveLog(fr"O veículo da placa {placaVeiculo} possui multas pendentes")
                numeroDebitos = len(trs) - 2  # Subtrai 2: cabeçalho e valor total
                print('NÚMERO DE DÉBITOS DO VEÍCULO:', numeroDebitos)
                valorDebito= driver.find_element(By.ID, 'spanDAR_Integral')
                valorDebitoSemEdicao = valorDebito.text
                valorDebitos = valorDebitoSemEdicao[20:-1]
                if not numeroDebitos:
                    numeroDebitos = 0
                #print('numeros DE DÉBITOS:', numeroDebitos)    
                print('VALOR DEBITO:',valorDebitos)
                #print('ID VEICULO:',idVeiculo)
                emitirMultas(numeroDebitos)

            else:
                print(fr'O veículo da placa {placaVeiculo} NAO possui multas pendentes')
                escreveLog(fr'O veículo da placa {placaVeiculo} NAO possui multas pendentes')
                ObterDadosLicenciamentoDB.updateValorSDebitos(idVeiculo)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            driver.close()
            print("fechando navegador definitivamente")
            break
                      
#---------------------------------------------------------------------
#FAZER FUNCAO APRA MULTAS E UIMA SO PARA PEGAR O VALOR TOTAL DE DEBITOS 

    
if __name__ == "__main__":
#    if len(sys.argv) > 1:
#        final_placa = sys.argv[1]
#        main(final_placa)
        
    main('9')