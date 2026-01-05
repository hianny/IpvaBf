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
from time import sleep
import pytesseract
import numpy as np
import pyautogui
import time
from datetime import datetime
from  captchaIPVA import anticaptcha
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
        escreveLog("Configurando Chrome...")
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        #chrome_options.add_argument('--headless') 
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--disable-session-crashed-bubble')
        chrome_options.add_argument('--window-size=1200,700')
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-component-update")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-background-networking")

        # ---------------------------
        # Inicializa o Driver
        # ---------------------------
        escreveLog("Iniciando ChromeDriver com undetected_chromedriver...")
        driver = uc.Chrome(options=chrome_options, version_main=139)
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
                        turnstile_input = WebDriverWait(driver, 10).until(
                        lambda d: d.find_element(By.NAME, "cf-turnstile-response") 
                                if len(d.find_element(By.NAME, "cf-turnstile-response").get_attribute("value")) > 10 
                                else False
                        )
                        escreveLog("CAPTCHA já resolvido automaticamente pelo site.")
                        print("CAPTCHA já resolvido automaticamente pelo site.")
                    except TimeoutException:
                        escreveLog("CAPTCHA não resolvido. Gerando token...")
                        print("CAPTCHA não resolvido. Gerando token...")
                        token = anticaptcha()
                        driver.execute_script(f'''
                        const host = document.querySelector('div.cf-turnstile');
                        const input = host.querySelector('input[name="cf-turnstile-response"]');
                        input.value = "{token}";

                        // 2️⃣ Disparar eventos para garantir que o frontend registre a mudança
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('blur'));

                        // 3️⃣ Chamar função callback se existir
                        if (typeof window.habilitarBotao === "function") {{
                            window.habilitarBotao("{token}");
                        }}
                        ''')

                        # 4️⃣ Confirmar se o token foi injetado
                        valor = driver.execute_script('return document.querySelector("input[name=\'cf-turnstile-response\']").value;')
                        escreveLog(f"Token CAPTCHA injetado: {valor[:30]}...")
                        print(f"Token CAPTCHA injetado: {valor[:30]}...")

                        # Verificar se houve erro no servidor
                        erroCaptcha = driver.execute_script("return document.body.innerText.includes('captcha')")
                        if erroCaptcha:
                            escreveLog("Servidor rejeitou o token CAPTCHA.")
                            print("Servidor rejeitou o token CAPTCHA.")
                        else:
                            escreveLog("CAPTCHA aceito pelo servidor.")
                            print("CAPTCHA aceito pelo servidor.")

                    # ---------------------------
                    # Consulta
                    # ---------------------------
                    boton_consultar = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.NAME, 'botaoSubmit'))
                    )
                    boton_consultar.click()
                    escreveLog("Botão Consultar clicado.")
                    print("Botão Consultar clicado.")

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

                    # ---------------------------
                    # Finaliza processamento do veículo
                    # ---------------------------
                    escreveLog(f"Veículo {renavam} processado com sucesso.")

                except Exception as e_veiculo:
                    escreveLog(f"Erro ao processar veículo {renavam}: {e_veiculo}")
                    continue

        finally:
            driver.quit()
            escreveLog("Driver encerrado após processamento de todos os veículos.")

    except Exception as e:
        escreveLog(f"Erro crítico na execução principal: {e}")
        print(f"Erro crítico na execução principal: {e}")



def emissaoGuia(driver,renavamveiculo,idVeiculo):
    while True:
        mensagemErro = None 
        tabela = None 
        print(renavamveiculo)
        print(idVeiculo)

        renavam = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, 'vclRen'))
            )
        renavam.send_keys(renavamveiculo)   
        sleep(5)
        consultar = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, 'botaoSubmit'))
            )
        consultar.click()  
        
        try:
            mensagemErro = driver.find_element(By.XPATH, '/html/body/center/form/table/tbody/tr[2]/td/font')   
            
        except:
            pass
        
        if mensagemErro is not None:
            mensagemdeErro = mensagemErro.text 
            if mensagemdeErro == "Erro ao buscar os dados do veículo":
                print('erro ao buscar dados do veiculo')
                break
                
        tabela
        try:   
            tabela = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/center/form/table[2]/tbody/tr[1]/td'))
            )
        except: 
            pass
        
        if tabela is not None:

            
            desconto = driver.find_element(By.XPATH, "/html/body/center/form/div/div/div[3]/label/span[1]")
            
            textoDesconto = desconto.text

            if "5%" in textoDesconto:
                print(fr"Contém 5% de desconto")
            
                debitoVeiculo = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, 'tipoGuia.2025.2'))
                )
                debitoVeiculo.click()

                gerarGuias = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, 'btnOK'))
                )
                gerarGuias.click()
                sleep(3)
                salvarGuia(driver)

                anoAtual = datetime.now().year
                sleep(3)
                caminhoIpva = fr"C:\BOT\IPVA\IPVA {anoAtual} - RENAVAM {renavamveiculo}.pdf"

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
                break



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