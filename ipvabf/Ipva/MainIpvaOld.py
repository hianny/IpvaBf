from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from escreveLog import escreveLog
import  ObterDadosIpvaDB
import os
import pandas as pd
import requests
from time import sleep
import numpy as np
import pyautogui
import time
from datetime import datetime
import  captchaIPVA 
import base64
import json
from escreveLog import escreveLog

def main():
    try:
        escreveLog("Iniciando execução do processo SEFAZ-IPVA")
        print("Iniciando execução do processo SEFAZ-IPVA")

        # ---------------------------
        # Busca veículos no banco
        # ---------------------------
        resultadoIpva = ObterDadosIpvaDB.RetornoVeiculosIpva()
        escreveLog(f"Total de veículos encontrados: {len(resultadoIpva)}")
        print(f"Total de veículos encontrados: {len(resultadoIpva)}")

        if not resultadoIpva:
            escreveLog("Nenhum veículo encontrado no banco. Encerrando.")
            print("Nenhum veículo encontrado no banco. Encerrando.")
            return

        # ---------------------------
        # Configurações do Chrome
        # ---------------------------
        caminho_download = 'C:\\IpvaBf\\IPVABF'
        escreveLog("Configurando Chrome...")
        chrome_options = webdriver.ChromeOptions()
        settings = {
            "recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}],
            "selectedDestinationId": "Save as PDF",
            "version": 2
        }

        prefs = {
            'printing.print_preview_sticky_settings.app_state': json.dumps(settings),
            'savefile.default_directory': caminho_download,
            # ESTA LINHA É A CHAVE: impede a janela de "Salvar Como" do sistema
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'plugins.always_open_pdf_externally': True
        }

        chrome_options.add_experimental_option('prefs', prefs)
        
        chrome_options.add_argument('--no-sandbox')
        #chrome_options.add_argument('--headless') 
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--kiosk-printing')
        chrome_options.add_argument('--disable-session-crashed-bubble')
        chrome_options.add_argument('--window-size=1200,700')
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-component-update")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_experimental_option("prefs", prefs)

        # ---------------------------
        # Inicializa o Driver
        # ---------------------------
        escreveLog("Iniciando ChromeDriver com undetected_chromedriver...")
        driver = uc.Chrome(options=chrome_options,version_main=142)
        driver.set_window_size(1200, 700)

        url_inicial = "https://www.sefaz.mt.gov.br/ipva/emissaoguia/emitir"
        escreveLog(f"Acessando página inicial: {url_inicial}")
        driver.get(url_inicial)
        driver.implicitly_wait(2)

        try:
            for index, veiculo in enumerate(resultadoIpva, start=1):
                renavam, num_documento, chassi, idVeiculo = veiculo

                escreveLog(f"[{index}/{len(resultadoIpva)}] Processando veículo: RENAVAM={renavam}, CPF/CNPJ={num_documento}, CHASSI={chassi}")
                print(f"[{index}/{len(resultadoIpva)}] Processando veículo: RENAVAM={renavam}, CPF/CNPJ={num_documento}, CHASSI={chassi}")

                try:
                    driver.get(url_inicial)
                    driver.implicitly_wait(2)
                    # ---------------------------
                    # Preenchimento do formulário
                    # ---------------------------
                    cpf_cnpj = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="numrDoc"]'))
                    )
                    cpf_cnpj.clear()
                    cpf_cnpj.send_keys(str(num_documento))
                    escreveLog(f"CPF/CNPJ preenchido: {num_documento}")

                    if renavam:
                        campo_renavam = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '/html/body/center/form/table[2]/tbody/tr[4]/td[2]/input'))
                        )
                        campo_renavam.clear()
                        campo_renavam.send_keys(str(renavam))
                        escreveLog(f"RENAVAM preenchido: {renavam}")

                    if chassi:
                        campo_chassi = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '/html/body/center/form/table[2]/tbody/tr[2]/td[2]/input'))
                        )
                        campo_chassi.clear()
                        campo_chassi.send_keys(str(chassi))
                        escreveLog(f"CHASSI preenchido: {chassi}")

                    # ---------------------------
                    # CAPTCHA
                    # ---------------------------
                    try:
                        token = captchaIPVA.anticaptcha()  # Chama a função para resolver o captcha
                        
                        # Injeta o token e executa o callback que o site espera para ativar o botão
                        driver.execute_script(f'''
                            // 1. Tenta encontrar o campo de resposta (pode ser hidden input ou textarea)
                            let input = document.getElementsByName("cf-turnstile-response")[0];
                            if (input) {{
                                input.value = "{token}";
                            }}

                            // 2. Chama a função de callback do próprio site para habilitar o botão Consultar
                            if (typeof habilitarBotao === "function") {{
                                habilitarBotao("{token}");
                            }}
                        ''')
                        
                        escreveLog("O captcha foi resolvido e o callback disparado")
                        print("Captcha finalizado")

                        # Aguarda o botão ficar clicável (o callback deve remover o 'disabled')
                        boton_consultar = WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable((By.ID, 'botaoSubmit'))
                        )
                        boton_consultar.click()

                    except Exception as e_captcha:
                        # Se o clique normal falhar, tentamos um clique via JavaScript como último recurso
                        try:
                            print("Tentando clique forçado via JS...")
                            driver.execute_script("document.getElementById('botaoSubmit').click();")
                        except:
                            escreveLog(f"Erro ao resolver CAPTCHA: {e_captcha}")
                            print(f"Erro ao resolver CAPTCHA: {e_captcha}")

                    # ---------------------------
                    # Verifica mensagem de Erro
                    # ---------------------------
                    try:
                        erro = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '/html/body/center/form/table/tbody/tr[2]/td/font'))
                        )
                        mensagem_erro = erro.text.strip()

                        if mensagem_erro == "O CPF/CNPJ informado é inválido para este veiculo.":
                            escreveLog(f"Erro: CPF/CNPJ {num_documento} inválido para o veículo {renavam}.")
                            print(f"Erro: CPF/CNPJ {num_documento} inválido para o veículo {renavam}.")

                            # Atualiza status no banco
                            
                            escreveLog(f"Erro atualizado no banco para ID {idVeiculo}.")

                            # Clica no botão voltar
                            voltar = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, '/html/body/center/form/table/tbody/tr[4]/td/input[1]'))
                            )
                            voltar.click()
                            escreveLog("Cliquei no botão Voltar após erro de CPF/CNPJ inválido.")
                            print("Cliquei no botão Voltar após erro de CPF/CNPJ inválido.")
                            continue

                        elif mensagem_erro == "Veículo informado nao foi encontrado.":
                            escreveLog(f"Erro: Veículo com RENAVAM {renavam} ou Chassi {chassi} não encontrado.")
                            print(f"Erro: Veículo com RENAVAM {renavam} ou Chassi {chassi} não encontrado.")


                            # Clica no botão voltar
                            voltar = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, '/html/body/center/form/table/tbody/tr[4]/td/input[1]'))
                            )
                            voltar.click()
                            escreveLog("Cliquei no botão Voltar após erro de veículo não encontrado.")
                            print("Cliquei no botão Voltar após erro de veículo não encontrado.")
                            continue
                    except:
                        pass

                    # ---------------------------
                    # Verifica mensagem de Débito
                    # ---------------------------
                    try:
                        debito = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '/html/body/center/form/div/p'))
                        )
                        mensagem_debito = debito.text
                        if "Nenhum débito foi localizado" in mensagem_debito:
                            escreveLog(f"Nenhum débito para o veículo {renavam}. Retornando à tela inicial.")
                            print(f"Nenhum débito para o veículo {renavam}. Retornando à tela inicial.")
                            voltar_btn = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, '/html/body/center/form/input[7]'))
                            )
                            voltar_btn.click()
                            continue
                    except:
                        escreveLog("Nenhuma mensagem de débito encontrada. Continuando processamento...")
                        print("Nenhuma mensagem de débito encontrada. Continuando processamento...")
                        emissaoGuia(driver,renavam,idVeiculo)

                    # ---------------------------
                    # Finaliza processamento do veículo
                    # ---------------------------
                    escreveLog(f"Veículo {renavam} processado com sucesso.")

                except Exception as e_veiculo:
                    escreveLog(f"Erro ao processar veículo {renavam}: {e_veiculo}")
                    print(f"Erro ao processar veículo {renavam}: {e_veiculo} ")
                    continue

        finally:
            driver.quit()
            escreveLog("Driver encerrado após processamento de todos os veículos.")

    except Exception as e:
        escreveLog(f"Erro crítico na execução principal: {e}")
        print(f"Erro crítico na execução principal: {e}")



def emissaoGuia(driver,renavamveiculo,idVeiculo):
        tabela=''
        try:   
            tabela = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/center/form/table[2]/tbody/tr[1]/td'))
            )
        except: 
            pass
        
        if tabela is not None:
        
            elemento = driver.find_element(By.XPATH, "//tbody[@id='cota1']//tr[td[2][contains(text(), '5%')]]/td[1]/input")
            elemento.click()
            
            try:
                email = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, 'email'))
                )
                telefone = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, 'celular'))
                )
                email.send_keys('hianny.urt@bomfuturo.com.br')
                
                telefone.send_keys('65998178793')
            except Exception as e:
                print(f"Nao precisa preencher email/telefone")    
            sleep(3)
            
            botao_gerar = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='Gerar Guia - pdf']"))
            )
            botao_gerar.click()
            
            #salvarGuia(driver)
            janela_original = driver.current_window_handle
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
            
            # 4. Loop para encontrar o ID da nova janela
            for handle in driver.window_handles:
                if handle != janela_original:
                    # 5. Troca o foco para a nova aba
                    driver.switch_to.window(handle)
                    break

                # Agora você está na nova aba!
            driver.switch_to.window(handle)

            # 1. Pegue a URL do PDF que está na barra de endereços da nova aba
            sleep(5)
            driver.execute_script('window.print();')
            sleep(2)
            pyautogui.write(fr"S:\Automacao\bot\VEICULOS\IPVA_2026\IPVA {anoAtual} - RENAVAM {renavamveiculo}.pdf", interval=0.5)
            pyautogui.press('enter')
            
            try:
                print("URL da aba atual:", driver.current_url)
                def imprimir_aba_atual(driver, nome_arquivo="saida.pdf"):
                    # Parâmetros que forçam a renderização total
                    print_options = {
                        'landscape': False,
                        'displayHeaderFooter': False,
                        'printBackground': True,
                        'preferCSSPageSize': True,
                        'generateTaggedPDF': True,
                        'generateDocumentOutline': True
                    }
                    
                    try:
                        # O comando 'Page.printToPDF' não depende de seletores HTML/Shadow DOM
                        # Ele "fotografa" o que o navegador está renderizando na aba
                        result = driver.execute_cdp_cmd("Page.printToPDF", print_options)
                        
                        with open(nome_arquivo, "wb") as f:
                            f.write(base64.b64decode(result['data']))
                        print(f"PDF gerado com sucesso: {nome_arquivo}")
                    except Exception as e:
                        print(f"Erro ao imprimir: {e}")
                                
            except Exception as e:
                driver.close()
                driver.switch_to.window(janela_original)
                print(f"Erro ao gerar PDF: {e}")
                driver.close()
                return
            
            
            anoAtual = datetime.now().year
            sleep(3)
            caminhoIpva = fr"S:\Automacao\bot\VEICULOS\IPVA_2026\IPVA {anoAtual} - RENAVAM {renavamveiculo}.pdf"

            pyautogui.write(caminhoIpva, interval=0.1)
            pyautogui.press('enter')

            salvarcomo = fr'.\ipvabf\Ipva\img\salvarComo.png'
            simSalvar = fr'.\ipvabf\Ipva\img\Sim.png'
            
            print('Verificando se o arquivo ja existe')
            locationSalvarComo = None
            try:
                locationSalvarComo = pyautogui.locateOnScreen(salvarcomo)
            except:
                pass

            if locationSalvarComo is not None:
                x, y = pyautogui.locateCenterOnScreen(simSalvar)
                print("o arquivo ja existe, substituindo")
                pyautogui.click(x, y)

            print('Entrando no while para se o arquivo foi salvo')
            while not os.path.exists(caminhoIpva):
                sleep(1)
            print("verificando se o arquivo foi salvo ")
            sleep(5)
            if os.path.exists(caminhoIpva):
                print(fr"o arquivo {caminhoIpva} foi salvo")
                #print(valorliceinciamento)
                #ObterDadosLicenciamentoDB.updateValor(valorLicenciamento,caminhoLicenciamento,idVeiculo)
            else:
                print("o arquivo nao foi salvo")
                pass
            print(fr"finalizando veiculo atual - renavam {renavamveiculo}")
            
def salvarGuia(driver):
    imagemsalvar = fr'.\ipvabf\Ipva\img\salvarAnonimo.png'
    location = None
    end_time = time.time() + 20
    countTimer = 0
    sleepTime = 0.5
    
    print('procurando o salvar...')
    while time.time() < end_time:
        try:
            location = pyautogui.locateOnScreen(imagemsalvar)
        except:
            location = None
        if location:
            print("Salvar encontrado")
            x, y = pyautogui.locateCenterOnScreen(imagemsalvar)
            print("clicando em salvar")
            pyautogui.click(x, y)
            break
        time.sleep(sleepTime)
        countTimer += sleepTime

if __name__ == "__main__":
    main()