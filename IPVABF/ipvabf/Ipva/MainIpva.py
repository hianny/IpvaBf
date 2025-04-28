from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from escreveLog import escreveLog
import ObterDadosIpvaDB
import random
import os
import pandas as pd
from time import sleep
import pytesseract
import numpy as np
import pyautogui
import time
from datetime import datetime

def main():
    try:
        resultadoIpva= ObterDadosIpvaDB.RetornoVeiculosIpva()
        #PLACA,RENAVAM,CHASSIS,NUM_DOCUMENTO = ObterDadosLicenciamentoDB.RetornoVeiculosLicenciamento()
        escreveLog("---------Iniciando Sequencia de notas Sefaz---------")
        print("---------Iniciando Sequencia de notas Sefaz---------")
        #options = webdriver.ChromeOptions()
        #options.add_argument('--headless')
        #options.add_argument('--no-sandbox')
        #options.add_argument('--mute-audio')
        
        for veiculos in resultadoIpva:
            #print(resultadoIpva)
            chrome_options = Options()
            chrome_options.add_argument('--user-data-dir=/path/to/your/chrome/profile')  # Caminho do perfil
            chrome_options.add_argument('--profile-directory=Profile 1')  # Nome do perfil específico
            chrome_options.add_argument('--disable-session-crashed-bubble')
            chrome_options.add_argument('--window-size=600,500')
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument('--incognito')
            driver = uc.Chrome(options=chrome_options)
            driver.set_window_size(1200, 700)
            url = "https://www.sefaz.mt.gov.br/ipva/emissaoguia/emitir"
            driver.implicitly_wait(2)
            driver.get(url)
            escreveLog('Abrindo o navegador na sefaz')
            
            renavam = veiculos[0]
            print("renavam: ", renavam)
            idVeiculo = veiculos[1]
            emissaoGuia(driver,renavam,idVeiculo)
            driver.quit()
    except Exception as e :
        print(e)
        pass

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