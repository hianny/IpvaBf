from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from escreveLog import escreveLog
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
        #resultadoVeiculos = ObterDadosLicenciamentoDB.RetornoVeiculosLicenciamento()
        #PLACA,RENAVAM,CHASSIS,NUM_DOCUMENTO = ObterDadosLicenciamentoDB.RetornoVeiculosLicenciamento()
        escreveLog("---------Iniciando Sequencia de notas Sefaz---------")
        print("---------Iniciando Sequencia de notas Sefaz---------")
        #options = webdriver.ChromeOptions()
        #options.add_argument('--headless')
        #options.add_argument('--no-sandbox')
        #options.add_argument('--mute-audio')
        
        for veiculos in resultadoVeiculos:
            chrome_options = Options()
            chrome_options.add_argument('--user-data-dir=/path/to/your/chrome/profile')  # Caminho do perfil
            chrome_options.add_argument('--profile-directory=Profile 1')  # Nome do perfil específico
            #chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--window-size=600,500')
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-extensions")
            driver = uc.Chrome(options=chrome_options)
            driver.set_window_size(1200, 700)
            url = "https://www.sefaz.mt.gov.br/ipva/emissaoguia/emitir"
            driver.implicitly_wait(2)
            driver.get(url)
            escreveLog('Abrindo o navegador na sefaz')

    except Exception as e :
        print(e)
        pass