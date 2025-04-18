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
import captchaLicenciamento
import random
import rapidfuzz
import pandas as pd
from time import sleep
import pytesseract
from PrettyColorPrinter import add_printer
import numpy as np
import pyautogui

#imagemSucesso = pyautogui.locateOnScreen(fr"\tests\Licenciamento\img\simboloSucesso.png")

add_printer(1)
import mousekey

mkey = mousekey.MouseKey()
mkey.enable_failsafekill("ctrl+e")

pytesseract.pytesseract.tesseract_cmd = fr'C:\Program Files\Tesseract-OCR\tesseract.exe'
from fast_ctypes_screenshots import (
    ScreenshotOfOneMonitor,
)


def get_screenshot_tesser(minlen=2):
    with ScreenshotOfOneMonitor(
        monitor=0, ascontiguousarray=True
    ) as screenshots_monitor:
        img5 = screenshots_monitor.screenshot_one_monitor()
    df = pytesseract.image_to_data(img5, output_type="data.frame")
    df = df.dropna(subset="text")
    df = df.loc[df.text.str.len() > minlen].reset_index(drop=True)
    return df

def move_mouse(
    x,
    y,
    variationx=(-5, 5),
    variationy=(-5, 5),
    up_down=(0.2, 0.3),
    min_variation=-10,
    max_variation=10,
    use_every=4,
    sleeptime=(0.009, 0.019),
    linear=90,
):
    mkey.left_click_xy_natural(
        int(x) - random.randint(*variationx),
        int(y) - random.randint(*variationy),
        delay=random.uniform(*up_down),
        min_variation=min_variation,
        max_variation=max_variation,
        use_every=use_every,
        sleeptime=sleeptime,
        print_coords=True,
        percent=linear,
    )

def clicarCaptcha():
    #comacando o resolve captcha do pyajudeme
    df = get_screenshot_tesser(minlen=2)
    #print(dfdf = get_screenshot_tesser(minlen=2)
    df = pd.concat(
        [
            df,
            pd.DataFrame(
                rapidfuzz.process_cpp.cdist(["Confirme", "que"], df.text.to_list())
            ).T.rename(columns={0: "Confirme", 1: "que"}),
        ],
        axis=1,
    )

    try:
        vamosclicar = (
            np.diff(
                df.loc[
                    ((df.Confirme == df.Confirme.max()) & (df.Confirme > 90))
                    | ((df.que == df.que.max()) & (df.que > 90))
                ][:2].index
            )[0]
            == 1
        )
    except Exception:
        vamosclicar = False

    if vamosclicar:
        x, y = df.loc[df.Confirme == df.Confirme.max()][["left", "top"]].__array__()[0]
        move_mouse(
            x,
            y,
            variationx=(-10, 10),
            variationy=(-10, 10),
            up_down=(0.2, 0.3),
            min_variation=-10,
            max_variation=10,
            use_every=4,
            sleeptime=(0.009, 0.019),
            linear=90,
        )
    #final resolve captcha do pyajudeme

def main():
    try:
        resultadoVeiculos = ObterDadosLicenciamentoDB.RetornoVeiculosLicenciamento()
        #PLACA,RENAVAM,CHASSIS,NUM_DOCUMENTO = ObterDadosLicenciamentoDB.RetornoVeiculosLicenciamento()
        escreveLog("---------Iniciando Sequencia de notas Sefaz---------")
        #options = webdriver.ChromeOptions()
        #options.add_argument('--headless')
        #options.add_argument('--no-sandbox')
        #options.add_argument('--mute-audio')
        chrome_options = Options()
        chrome_options.add_argument('--user-data-dir=/path/to/your/chrome/profile')  # Caminho do perfil
        chrome_options.add_argument('--profile-directory=Profile 1')  # Nome do perfil específico
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        driver = uc.Chrome(options=chrome_options)
        url = "https://www.detran.mt.gov.br/"
        driver.implicitly_wait(2)
        driver.get(url)
        escreveLog('Abrindo o navegador')

        for veiculos in resultadoVeiculos:
            placa = veiculos[1]
            renavam = veiculos[2]
            num_documento = veiculos[4]
            realizandoLicenciamento(driver)
            driver.close()

    except Exception as e :
        print(e)
        pass

def realizandoLicenciamento(driver):
    sleep(3)
    propagranda = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="mtSitesPopup"]/div/div/div[1]/button'))
    )
    propagranda.click() 
    sleep(3)
    placa = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'Placa'))
    )
    placa.send_keys('NJM7C99') 
    sleep(3)

    renavam = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'Renavam'))
    )
    renavam.send_keys('984909834') 
    sleep(3)

    consultar = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="formVeiculo"]/div[4]/input[2]'))
    )
    consultar.click() 
    #windows = driver.window_handles
    driver.execute_script("window.focus();")
    driver.switch_to.window(driver.window_handles[1])

    # Troca pra nova aba
    
    print("Título da nova aba:", driver.title)
    # Checa se a página terminou de carregar
    state = driver.execute_script('return document.readyState')
    print("Estado da página:", state)

    cpfCnpj = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'DocumentoProprietarioValidacao'))
    )
    cpfCnpj.send_keys('10425282004705') 
    sleep(5)


    clicarCaptcha()  


    '''token = captchaLicenciamento.captchaChato()

    try:
        # Tenta localizar o elemento usando XPath
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='cf-turnstile-response']"))
        )
        print("Elemento encontrado!")
    except:
        print("Elemento não encontrado!")
    # Define o valor via JavaScript
    driver.execute_script("arguments[0].value = arguments[1];", element, token)

    # Envia o formulário (se necessário)
    try:
        checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//label[@class='cb-lb']/input[@type='checkbox']"))
        )

        # Clica no checkbox
        checkbox.click()
    except:
        print("Botão não encontrado!")'''

    sleep  (2)

    location = None
    imageFile = fr'.\tests\Licenciamento\img\simboloSucesso.png'

    while (location == None):
        try:
            location = pyautogui.locateOnScreen(imageFile)
        except Exception as e:
            pass
            #print(e)

    print(location)
    '''while imagemSucesso ==None:
        imagemSucesso = pyautogui.locateOnScreen(fr"\tests\Licenciamento\img\simboloSucesso.png")
        print("still haven't found the image")'''

    btOK = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'btOk'))
    )
    btOK.click()
    debito = None
    '''try:
        debito = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="div_servicos_Debitos"]/table/tbody/tr/td'))
        )
    except:
        pass'''
    select_element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "cmbTipoDebito"))
        )
    #select_element = driver.find_element(By.ID, "cmbTipoDebito")
    # Cria um objeto Select
    select = Select(select_element)

    # Verifica se a opção "Licenciamento 2025" está presente
    opcoes = [option.text.strip() for option in select.options]
    if "Licenciamento 2025" in opcoes:
        print("Opção encontrada. Pode continuar.")
    else:
        print("Opção NÃO encontrada. Interrompendo.")  
    emitir = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "spanDAR_LicenciamentoExercicio"))
            )
    emitir.click()

    driver.switch_to.window(driver.window_handles[2])
    WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "form1"))
            )
    while True:

        pyautogui.click()
        pyautogui.keyDown('ctrl')
        pyautogui.keyDown('p')
        pyautogui.keyUp('ctrl')
        print("crtl feito")
        sleep(5)
        print("procurando botao de salvar")
        
        try:
            sleep(1)
            location = None
            imageFile = fr'.\tests\Licenciamento\img\salvarBorda.png'

            while (location == None):
                try:
                    location = pyautogui.locateOnScreen(imageFile)
                except Exception as e:
                    pass

            if location != None:

                x,y = pyautogui.locateCenterOnScreen(fr".\tests\Licenciamento\img\salvarBorda.png")
                print("localizado")
                
            
            pyautogui.click(x, y)
        except Exception as e:
            print(f"Erro capturado: {e}")
            continue

        sleep(5)
        #print("localizado")
        '''if x:
            pyautogui.click(x, y)
        else:
            break'''
        sleep(5)
        pyautogui.write(fr'C:\Users\hianny.urt\Documents\BOT\teste.pdf', interval=0.25)
        pyautogui.press('enter')
        print("salvo")
        break


    if debito:
        driver.close()

if __name__ == "__main__":
    main()