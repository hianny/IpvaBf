from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import captchaMultas
import base64
from datetime import datetime
import os 


print("---------Iniciando Sequencia de notas Sefaz---------")
chrome_options = uc.ChromeOptions()
prefs = {
    "download.default_directory": fr"C:\PythonIPVA\IPVABF\ipvabf\Multas",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)


chrome_options.add_argument('--user-data-dir=/path/to/your/chrome/profile')  # substitua pelo caminho real
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument('--profile-directory=Profile 1')
chrome_options.add_argument("--window-size=1920,1080")
#chrome_options.add_argument('--headless')
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-extensions")

# Inicia o driver
driver = uc.Chrome(options=chrome_options)
driver.set_window_size(1200, 700)
url = "https://www.detran.mt.gov.br/"
driver.implicitly_wait(2)
driver.get(url)
#------------------------------------
#Inicio do processo de consulta de multas
#------------------------------------
sleep(5)
propagranda = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[4]/section/div/div/div/div/div[12]/section/div/div[2]/div/div/div/div/div/div/div/div[1]/button'))
)
propagranda.click() 

sleep(3)
placa = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, 'Placa'))
)
placa.send_keys('OAT6C07') 
sleep(3)

renavam = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, 'Renavam'))
)
renavam.send_keys('404909930') 
sleep(3)

consultar = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="formVeiculo"]/div[4]/input[2]'))
)
consultar.click() 
#------------------------------------
# Login feito com sucesso
#------------------------------------
# Trocando de aba
#-------------------------------------

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
'''if textoErro:
    if textoErro[23:] == "Documento Proprietario informado não confere com o proprietario do veiculo.":
        #ObterDadosLicenciamentoDB.updateErro('ERRO - Documento N/ Confere',idVeiculo)

    elif textoErro[23:] == "Documento do Proprietario invalido.":
        #print(type(idVeiculo))
        #Idatual = f"{int(idVeiculo):,}".replace(",", ".")
        #print(Idatual)
        #ObterDadosLicenciamentoDB.updateErro('ERRO - Documento Invalido',idVeiculo)

    elif textoErro[23:] == "Confirme Nao sou Robo":
        #ObterDadosLicenciamentoDB.updateErro('ERRO - Captcha',idVeiculo)

    elif textoErro[23:] == "Favor acessar o formulário para nova consulta":
        #ObterDadosLicenciamentoDB.updateErro('ERRO - Formulario',idVeiculo)

    elif textoErro[23:] == "Renavam informado não confere com a Placa.":
        #ObterDadosLicenciamentoDB.updateErro('ERRO - Renavam Invalido',idVeiculo)

    elif textoErro[23:] == "Operação cancelada. Veículo não emplacado na base local ou não possui infrações na base local":
        #ObterDadosLicenciamentoDB.updateErro('ERRO - N/ emplacado base local',idVeiculo)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    break'''


#if error:
#   Documento do Proprietario invalido.
#   Documento Proprietario informado não confere com o proprietario do veiculo.
#   ERRO - Documento Invalido
#   Operação cancelada. Veículo não emplacado na base local ou não possui infrações na base local
#   Confirme Nao sou Robo
#   Renavam informado não confere com a Placa

#windows = driver.window_handles
driver.execute_script("window.focus();")
print("mudando a pagina")
driver.switch_to.window(driver.window_handles[1])

#---------------------
# Nova aba
#------------------------trocando para nova aba do navegador----------------------------------

print("Título da nova aba:", driver.title)

state = driver.execute_script('return document.readyState')
print("Estado da página:", state)
cpfCnpj = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, 'DocumentoProprietarioValidacao'))
)
cpfCnpj.send_keys('10425282000122')  
sleep(5)

#------------------------------------
# Resolvendo captcha 
#------------------------------------
token = captchaMultas.capsolver()  # Chama a função para resolver o captcha

driver.execute_script(f'''
document.querySelector('input[name="cf-turnstile-response"]').value = "{token}";
document.querySelector('input[name="g-recaptcha-response"]').value = "{token}";
''')

#------------------------------------
# captcha resolvido com sucesso
#------------------------------------

# Agora você pode submeter o formulário
driver.find_element(By.NAME, "btOk").click()
sleep(5)
cabecalhopdf = WebDriverWait(driver, 50).until(
    EC.element_to_be_clickable((By.ID, 'exibir_cabecalho')))

sleep(1)

#------------------------------------
# Selecionar multas do veiculo
#------------------------------------

debito = driver.find_element(By.XPATH, '//*[@id="div_servicos_Debitos"]//td').text
print("Débito encontrado:", debito)
if debito == "Nenhum débito em aberto cadastrado para este veículo.":
    print("Nenhum débito encontrado para o veículo.")
    #updatebanco esse veiculo nao a nenhum debito
    #break  Se não houver débito, você pode sair ou continuar com outra lógica

else:    
    select_element = driver.find_element(By.ID, 'cmbTipoDebito')
    select = Select(select_element)

    for option in select.options:
        if option.get_attribute("value") == 'LicenciamentoExercicio':
            print('o veiculo ainda possui pendencia de licenciamento')

        print(f'opção de debito: {option.text}, Valor: {option.get_attribute("value")}')
    select.select_by_value("multas")
    
    sleep(1)

emitir = WebDriverWait(driver, 50).until(
    EC.element_to_be_clickable((By.ID, 'spanDAR_LicenciamentoExercicio')))
emitir.click()

driver.execute_script("window.focus();")
print("mudando a pagina")
driver.switch_to.window(driver.window_handles[2])

#---------------------
# Nova aba
#------------------------trocando para nova aba do navegador----------------------------------

print("Título da nova aba:", driver.title)

state = driver.execute_script('return document.readyState')

total_height = driver.execute_script("return document.body.scrollHeight")
 
sleep(15)

pdf = driver.execute_cdp_cmd("Page.printToPDF", {
    "printBackground": True
})

#------------------------------------
# salvando pagina para pdf
#------------------------------------
dataatual = datetime.now().strftime("%d-%m-%Y")
with open(fr"ipvabf/Multas/pdf/Lic Licenciamento {dataatual} - RENAVAM.pdf", "wb") as f:
    f.write(base64.b64decode(pdf['data']))

if os.path.exists(fr"ipvabf/Multas/pdf/Lic Licenciamento {dataatual} - RENAVAM.pdf"):
    print("PDF salvo com sucesso!")
    #updatebanco 
else:
    print("Erro ao salvar o PDF.")
    #updatebanco status erro salvar pdf