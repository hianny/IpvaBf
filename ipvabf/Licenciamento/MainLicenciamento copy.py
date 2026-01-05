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
import os
import rapidfuzz
import pandas as pd
from time import sleep
import pytesseract
from PrettyColorPrinter import add_printer
import numpy as np
import pyautogui
import time
import captchaLic
from datetime import datetime

#imagemSucesso = pyautogui.locateOnScreen(fr"\tipvabfLicenciamento\img\simboloSucesso.png")

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
            driver = uc.Chrome(options=chrome_options, version_main=135)
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
            driver.close()

    except Exception as e :
        print(e)
        pass

def realizandoLicenciamento(driver,placaVeiculo,renavamVeiculo,num_documentoVeiculo,idVeiculo):
    #tentativa = 0
    while True:
        sleep(3)
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

        #windows = driver.window_handles
        driver.execute_script("window.focus();")
        print("mudando a pagina")
        driver.switch_to.window(driver.window_handles[1])

        # Troca pra nova aba
#------------------------trocando para nova aba do navegador----------------------------------

        print("Título da nova aba:", driver.title)
        # Checa se a página terminou de carregar
        state = driver.execute_script('return document.readyState')
        print("Estado da página:", state)

        cpfCnpj = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'DocumentoProprietarioValidacao'))
        )
        cpfCnpj.send_keys(num_documentoVeiculo) 
        sleep(5)

        token = captchaLic.capsolver()  # Chama a função para resolver o captcha

        driver.execute_script(f'''
        document.querySelector('input[name="cf-turnstile-response"]').value = "{token}";
        document.querySelector('input[name="g-recaptcha-response"]').value = "{token}";
        ''')

        #comecando a etapa de resolver o captcha
        print("comecando a resolver a captcha")

        '''max_tentativas = 5
        tentativa = 0

        while tentativa < max_tentativas:
            print(f"Tentativa {tentativa + 1}")
            tentativa += 1

            # Tenta clicar no CAPTCHA
            clicarCaptcha()
            time.sleep(2)

            # Verifica se o símbolo de sucesso aparece por até 20 segundos
            location = None
            end_time = time.time() + 20
            countTimer = 0
            sleepTime = 0.5
            image_sucesso = fr'.\tipvabfLicenciamento\img\simboloSucesso.png'
            
            print('Entrando no while para verificar símbolo de sucesso')
            while time.time() < end_time:
                try:
                    location = pyautogui.locateOnScreen(image_sucesso)
                except:
                    location = None
                if location:
                    print("Símbolo de sucesso encontrado.")
                    break
                time.sleep(sleepTime)
                countTimer += sleepTime

            # Se encontrou o símbolo de sucesso, finaliza
            if location:
                print("Captcha resolvido com sucesso. Saindo do loop.")
                break
            else:
                print("Símbolo de sucesso não encontrado. Verificando se ainda está esperando confirmação...")

                # Verifica se a imagem do captcha ainda está visível (confirmar.png)
                try:
                    esperando_confirmacao = pyautogui.locateOnScreen(fr'.\tipvabfLicenciamento\img\confirmar.png')
                except:
                    esperando_confirmacao = None

                if esperando_confirmacao:
                    print("Captcha ainda visível. Tentando novamente após 5 segundos...")
                    time.sleep(5)
                else:
                    print("Captcha não está mais visível. Interrompendo tentativas.")
                    break

        print("Captcha finalizado")

        #confirmando '''
        btConsultar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'btOk'))
        )
        btConsultar.click()
        print("clicando no botao consultar")
        sleep(2)


        try:
            textoErro = ''                         #/html/body/center/div/table/tbody/tr/td/text()[2]
            erro =  driver.find_element(By.XPATH, "/html/body/center/div/table/tbody/tr/td")
            textoErro = erro.text
            print(textoErro)

        except:
            pass
        print("verificando erro")
        #verificando informacoes no documento
        #caso nao tenha debito o
        if textoErro:
            if textoErro[23:] == "Documento Proprietario informado não confere com o proprietario do veiculo.":
                ObterDadosLicenciamentoDB.updateErro('ERRO - Documento N/ Confere',idVeiculo)

            elif textoErro[23:] == "Documento do Proprietario invalido.":
                print(type(idVeiculo))
                #Idatual = f"{int(idVeiculo):,}".replace(",", ".")
                #print(Idatual)
                ObterDadosLicenciamentoDB.updateErro('ERRO - Documento Invalido',idVeiculo)

            elif textoErro[23:] == "Confirme Nao sou Robo":
                ObterDadosLicenciamentoDB.updateErro('ERRO - Captcha',idVeiculo)

            elif textoErro[23:] == "Favor acessar o formulário para nova consulta":
                ObterDadosLicenciamentoDB.updateErro('ERRO - Formulario',idVeiculo)

            elif textoErro[23:] == "Renavam informado não confere com a Placa.":
                ObterDadosLicenciamentoDB.updateErro('ERRO - Renavam Invalido',idVeiculo)

            elif textoErro[23:] == "Operação cancelada. Veículo não emplacado na base local ou não possui infrações na base local":
                ObterDadosLicenciamentoDB.updateErro('ERRO - N/ emplacado base local',idVeiculo)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            break

#------------------------trocando para nova aba do navegador----------------------------------
        debito = driver.find_element(By.XPATH, '//*[@id="div_servicos_Debitos"]/table/tbody/tr/td')
        debitos = debito.text

        if debitos:
            if debitos == "Nenhum débito em aberto cadastrado para este veículo.":
                ObterDadosLicenciamentoDB.update('QUITADO',idVeiculo)
                print("o veiculo nao tem nenhum debito")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                
                break
        else:
            pass

        print("verificando a data do licenciamento")
        select_element = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "cmbTipoDebito"))
            )
        #select_element = driver.find_element(By.ID, "cmbTipoDebito")
        # Cria um objeto Select
        select = Select(select_element)

        # Verifica se a opção "Licenciamento 2025" está presente

        opcoes = [option.text.strip() for option in select.options]

        anoAtual = datetime.now().year
        if fr"Licenciamento {anoAtual}" in opcoes:
            print("Opção encontrada. Pode continuar.")

            valorliceinciamento = driver.find_element(By.ID, 'spanDAR_LicenciamentoExercicio')
            valorLicenciamento = valorliceinciamento.text
            valorLicenciamento = valorLicenciamento[35:-4]
            print(valorLicenciamento)

        else:
            print("Opção NÃO encontrada. Interrompendo.")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            break

        emitir = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.ID, "spanDAR_LicenciamentoExercicio"))
                )
        emitir.click()

        sleep(2)

        driver.switch_to.window(driver.window_handles[2])
        WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.ID, "form1"))
                )
        print("acessando tela de imprimir")
        while True:
            print("clicando no arquivo")
            sleep(4)
            pyautogui.click()
            print("abrindo imprimir")
            pyautogui.keyDown('ctrl')
            pyautogui.keyDown('p')
            pyautogui.keyUp('ctrl')
            print("crtl feito")
            sleep(10)
            print("procurando botao de salvar")
            pyautogui.press('enter')
            
            location = None
            location2 = None
            end_time = time.time() + 20
            countTimer = 0
            sleepTime = 0.5
            imageFile = fr'.\tipvabfLicenciamento\img\salvar.png'
            imageFile2 = fr'.\tipvabfLicenciamento\img\salvarBorda.png'
            
            print('Entrando no while para verificar símbolo de sucesso')
            '''while time.time() < end_time:

                try:
                    location = pyautogui.locateOnScreen(imageFile)
                    #location2 = pyautogui.locateOnScreen(imageFile2)
                except Exception as e:
                    location = None

                try:
                    #location = pyautogui.locateOnScreen(imageFile)
                    location2 = pyautogui.locateOnScreen(imageFile2)
                except Exception as e:
                    location2 = None

                if location is not None or location2 is not None:
                    try:
                        x, y = pyautogui.locateCenterOnScreen(imageFile)
                        print("Localizado salvar, clicando...")
                        pyautogui.click(x, y)
                        break  # Se quiser sair do while após clicar
                    except:
                        print("Imagem 'salvar.png' não encontrada.")

                    try:
                        x, y = pyautogui.locateCenterOnScreen(imageFile2)
                        print("Localizado salvar com borda, clicando...")
                        pyautogui.click(x, y)
                        break  # Se quiser sair do while após clicar
                    except:
                        print("Imagem 'salvarBorda.png' não encontrada.")
                else:
                    time.sleep(sleepTime)
                    countTimer += sleepTime'''

            sleep(10)
            
            caminhoLicenciamento = fr"C:\BOT\LICENCIAMENTO\Lic Licenciamento {anoAtual} - RENAVAM {renavamVeiculo}.pdf"

            pyautogui.write(caminhoLicenciamento, interval=0.2)
            pyautogui.press('enter')
            sleep(5)

            '''salvarcomo = fr'.\ipvabf\Licenciamento\img\salvarComo.png'
            simSalvar = fr'.\tipvabfLicenciamento\img\Sim.png'
            
            print('Verificando se o arquivo ja existe')
            locationSalvarComo = None
            try:
                locationSalvarComo = pyautogui.locateOnScreen(salvarcomo)
            except:
                pass

            if locationSalvarComo is not None:
                x, y = pyautogui.locateCenterOnScreen(simSalvar)
                print("o arquivo ja existe, substituindo")
                pyautogui.click(x, y)'''
            


            print('Entrando no while para verificar símbolo de sucesso')
            while not os.path.exists(caminhoLicenciamento):
                sleep(1)

            print("verificando se o arquivo foi salvo ")
            sleep(3)
            if os.path.exists(caminhoLicenciamento):
                print(fr"o arquivo {caminhoLicenciamento} foi salvo")
                print(valorliceinciamento)
                ObterDadosLicenciamentoDB.updateValor(valorLicenciamento,caminhoLicenciamento,idVeiculo)
            else:
                print("o arquivo nao foi salvo")
                pass

            #print("salvo")
            driver.close()
            driver.switch_to.window(driver.window_handles[1])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            print("fechando navegador")
            break
        break
    

if __name__ == "__main__":
    main()