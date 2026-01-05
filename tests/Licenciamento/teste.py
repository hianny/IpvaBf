from selenium import webdriver
from selenium.webdriver.common.by import By

# Iniciar o navegador
driver = webdriver.Chrome()

# Acessar a página com o formulário
driver.get('https://internet.detrannet.mt.gov.br/ConsultaVeiculo.asp')

# Preencher campos ocultos via JavaScript
driver.execute_script("document.getElementById('Placa').value = 'NUC7534';")
driver.execute_script("document.getElementById('Renavam').value = '1144979622';")
driver.execute_script("document.getElementById('ValidarProprietario').value = '1';")

# Preencher o campo de CPF/CNPJ
driver.find_element(By.NAME, 'DocumentoProprietarioValidacao').send_keys('12345678900')  # Preenche o campo visível de CPF/CNPJ

# Enviar o formulário
driver.find_element(By.NAME, 'btOk').click()

# Opcionalmente, aguarde até a resposta ou verifique se a ação foi bem-sucedida
driver.implicitly_wait(5)  # Aguardar até 5 segundos para que a página carregue

# Fechar o navegador
driver.quit()
