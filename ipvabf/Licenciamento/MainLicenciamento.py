from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.ui import Select
from database import ObterDadosLicenciamentoDB
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.edge.options import Options
import undetected_chromedriver as uc
from escreveLog import escreveLog
from selenium.webdriver.edge.service import Service
import os
from selenium_stealth import stealth 
import platform
import ipvabf.Licenciamento.email.ResultadoEmail as ResultadoEmail
from time import sleep
from database.ObterResultadoFinalDB import RetornoVeiculosSucesso, RetornoVeiculosErro,RetornoVeiculosSemDebito
import base64
from datetime import datetime
import traceback
from captcha import captchaLicenciamento
import sys
#OQUE AINDA FALTA
#
#FAZER TRIGGER PARA FAZER DE TODAS AS PLACAS
#COMO FAZER A TRIGGER?
#

def main(final_placa):
    try:
        print(final_placa)
        if final_placa == 'erro':  
            resultadoVeiculos = ObterDadosLicenciamentoDB.RetornoVeiculosErro()   
        else:
            resultadoVeiculos = ObterDadosLicenciamentoDB.RetornoVeiculosLicenciamento(final_placa)
            print(resultadoVeiculos)
        escreveLog("---------Iniciando Sequencia de notas Sefaz---------")
        print("---------Iniciando Sequencia de notas Sefaz---------")

        for veiculos in resultadoVeiculos:
            driver = None  # Inicializa a variável driver
            try:
                # Configuração do Chrome
                #edge_options = Options()
                chrome_options = uc.ChromeOptions()
                prefs = {
                    "download.default_directory": r"S:\\Automacao\\bot\\VEICULOS\\LICENCIAMENTO",
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True
                }
                #edge_options.binary_location = "C:\\edgedriver_arm64\\msedgedriver.exe"
                chrome_options.add_experimental_option("prefs", prefs)

                #edge_options.add_argument('--profile-directory=Profile 1')  # Pode não funcionar no Edge
                chrome_options.add_argument('--start-maximized')
                chrome_options.add_argument("--headless=new") 
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')

                # Inicia o Edge com as opções definidas
                try:
                    driver = uc.Chrome(options=chrome_options, version_main=142)
                except:
                    driver = uc.Chrome(options=chrome_options, version_main=140)
                #driver = webdriver.Edge(options=edge_options, service=Service("C:\\edgedriver\\msedgedriver.exe"))
                driver.set_window_size(1200, 700)
                
                stealth(driver,
                    languages=["pt-BR", "pt"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                    )

                # Seu código continua aqui
                driver.set_window_size(1200, 700)
                url = "https://www.detran.mt.gov.br/consulte-seu-veiculo"
                driver.implicitly_wait(2)
                driver.get(url) 

                idVeiculo = veiculos[0]
                placaVeiculo = veiculos[1]
                print(placaVeiculo)
                renavamVeiculo = veiculos[2]
                num_documentoVeiculo = veiculos[4]

                realizandoLicenciamento(driver, placaVeiculo, renavamVeiculo, num_documentoVeiculo, idVeiculo)
                escreveLog(f"Finalizando as consultas do veiculo com a placa: {placaVeiculo}")

            except Exception as e:
                print(e)
                escreveLog(f'Ocorreu um erro ao processar o veiculo {placaVeiculo}: {e}')
                print(f'Ocorreu um erro ao processar o veiculo {placaVeiculo}: {e}')
                traceback.print_exc()
                
            finally:
                if driver is not None:
                    try:
                        # Tenta fechar abas se o driver ainda estiver ativo
                        try:
                            handles = driver.window_handles
                            for handle in handles:
                                try:
                                    driver.switch_to.window(handle)
                                    driver.close()
                                except Exception:
                                    pass  # Ignora erro ao tentar fechar janela específica
                        except Exception as e:
                            escreveLog(f'Não foi possível acessar as janelas do navegador: {e}')
                        
                        # Encerra o driver propriamente
                        driver.quit()

                    except Exception as e:
                        escreveLog(f'Erro ao fechar o navegador: {e}')


        # Restante do seu código...
        escreveLog("---------Finalizando Sequencia de notas Sefaz---------")    
        print("---------Finalizando Sequencia de notas Sefaz---------")
        
        arquivoCsvSucesso, numeroCsvSucesso = RetornoVeiculosSucesso(final_placa) 
        arquivoCsvErro, numeroCsErro = RetornoVeiculosErro(final_placa)
        arquivoCsvSemDebito, numeroCsvDebito = RetornoVeiculosSemDebito(final_placa)
        print('Enviando email de finalizacao')
        escreveLog('Enviando email de finalizacao')
        ResultadoEmail.ResultadoFinalEmail(final_placa, len(resultadoVeiculos),numeroCsErro,numeroCsvSucesso,numeroCsvDebito,arquivoCsvSucesso,arquivoCsvErro,arquivoCsvSemDebito)

    except Exception as e:
        escreveLog(f'Ocorreu um erro no FOR principal: {e}')
        print('Ocorreu um Erro no FOR principal: ', e)
        escreveLog("---------Finalizando Sequencia de notas Sefaz---------")    
        print("---------Finalizando Sequencia de notas Sefaz---------")
        arquivoCsvSucesso, numeroCsvSucesso = RetornoVeiculosSucesso(final_placa) 
        arquivoCsvErro, numeroCsErro = RetornoVeiculosErro(final_placa)
        arquivoCsvSemDebito, numeroCsvDebito = RetornoVeiculosSemDebito(final_placa)
        print('Enviando email de finalizacao')
        escreveLog('Enviando email de finalizacao')
        ResultadoEmail.ResultadoErro(e, final_placa, len(resultadoVeiculos),numeroCsErro,numeroCsvSucesso,numeroCsvDebito,arquivoCsvSucesso,arquivoCsvErro,arquivoCsvSemDebito)

def realizandoLicenciamento(driver,placaVeiculo,renavamVeiculo,num_documentoVeiculo,idVeiculo):
    #-----------------------------------
    #Funcao para baixar o lincenciamento
    #------------------------------------
    
    def emitirLicenciamento():
        print('O veiculo tem licenciamento Pendente')
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
        print('Salvando o Licenciamento')
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
        caminhoLicenciamento = fr"S:\Automacao\bot\VEICULOS\LICENCIAMENTO\Lic Licenciamento {anoAtual} - RENAVAM {renavamVeiculo}.pdf"

        with open(caminhoLicenciamento, "wb") as f:
            f.write(base64.b64decode(pdf['data']))

        if os.path.exists(caminhoLicenciamento):
            print("PDF salvo com sucesso!")
            print("valor que esta no licenciamento: ",valorLicenciamento)
            ObterDadosLicenciamentoDB.updateValor(valorLicenciamento,caminhoLicenciamento,idVeiculo)
            print('')
            driver.close()
            driver.switch_to.window(driver.window_handles[1])
            #ObterDadosLicenciamentoDB.updateValorMultas(numeroDebitos,caminhoLicenciamento,valorLicenciamento,idVeiculo)
            #updatebanco 
        else:
            print("Erro ao salvar o PDF.")
            driver.close()
            driver.switch_to.window(driver.window_handles[1])
            print("fechando navegador do emitir licenciamento")
 
    #-----------------------------------
    #Funcao para baixar as multas
    #------------------------------------
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
        caminhoMultas = fr"S:\Automacao\bot\MULTAS\MULTAS - {anoAtual} - RENAVAM {renavamVeiculo}.pdf"

        with open(caminhoMultas, "wb") as f:
            f.write(base64.b64decode(pdf['data']))

        if os.path.exists(caminhoMultas):
            print("PDF salvo com sucesso!")
            try:
                print("valor que esta no licenciamento: ",valorliceinciamento)
            except:
                pass
            print(valorliceinciamento)
            #ObterDadosLicenciamentoDB.updateValor(valorLicenciamento,caminhoLicenciamento,idVeiculo)
            ObterDadosLicenciamentoDB.updateValorMultas(quantidade_checkboxes,valorLicenciamento,caminhoMultas,idVeiculo)
            #updatebanco 
            driver.close()
            driver.switch_to.window(driver.window_handles[1])
            
        else:
            print("Erro ao salvar o PDF.")
            driver.close()
            driver.switch_to.window(driver.window_handles[1])
            print("fechando navegador do emitir multas")
    
    
    #Inicio do codigo
    #Faz o login no detran
    while True:
        sleep(3)
        escreveLog('Iniciando o site do Detran')
        print('iniciando login no site do Detran')
        sleep(6)
        try:
            propagranda = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mtSitesPopup"]/div/div/div[1]/button'))
            )
            propagranda.click()
        except:
            pass
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
        print('iniciando pagina de captcha e numero de documento')
        cpfCnpj = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'DocumentoProprietarioValidacao'))
        )
        cpfCnpj.send_keys(num_documentoVeiculo) 
        sleep(5)

        
        token = captchaLicenciamento.anticaptcha()  # Chama a função para resolver o captcha

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
                
            elif textoErro[23:] == 'DetranNet. Erro: ["invalid-input-response"]':
                ObterDadosLicenciamentoDB.updateErro('ERRO - invalid-input-response','ERRO-captcha',idVeiculo)
                escreveLog(f'ERRO - invalid-input-response {placaVeiculo}')
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            driver.quit()
            break

#------------------------trocando para nova aba do navegador----------------------------------
        debito = driver.find_element(By.XPATH, '//*[@id="div_servicos_Debitos"]/table/tbody/tr/td')
        debitos = debito.text
        escreveLog(fr'Nao ouve erro')

        if debitos:
            escreveLog(fr'Verificando se existe debito para o veiculo')
            
            if debitos == "Nenhum débito em aberto cadastrado para este veículo.":
                                                                     #-------------------------------------
                ObterDadosLicenciamentoDB.update('QUITADO',idVeiculo)  #ADICIONAR COLUNA DE STATUS MULTAS
                print(fr"o veiculo da placa {placaVeiculo} nao tem nenhum debito")
                escreveLog(fr"o veiculo da placa {placaVeiculo} nao tem nenhum debito")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                driver.quit()
                
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
        existeLic = False
        for option in select.options:
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
            driver.quit()
            print("fechando navegador depois de concluir multas")
            break
                      

if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        final_placa = sys.argv[1]
        main(final_placa)
        
    
   #main('1')
    