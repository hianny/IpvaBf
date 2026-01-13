import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import undetected_chromedriver as uc
import ObterDadosIpvaDB
import os
import requests
import captchaIPVA
import json
import re
from decimal import Decimal

# Configuração do logging
def configurar_logging():
    # Criar diretório de logs se não existir
    log_dir = 'C:\\IpvaBf\\logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar formato do log
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    log_filename = os.path.join(log_dir, f'ipva_processo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Também exibe no console
        ]
    )
    
    return logging.getLogger(__name__)

# Inicializar logger
logger = configurar_logging()

def main():
    """Função principal que inicia o processo de consulta IPVA"""
    try:
        logger.info("=" * 60)
        logger.info("INICIANDO PROCESSO DE CONSULTA IPVA - SEFAZ/MT")
        logger.info("=" * 60)
        logger.info("Versão do script: 2.0")
        logger.info(f"Data/hora de início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        # ---------------------------
        # Busca veículos no banco
        # ---------------------------
        logger.info("Etapa 1: Buscando veículos no banco de dados...")
        resultadoIpva = ObterDadosIpvaDB.RetornoVeiculosIpva()
        logger.info(f"Total de veículos encontrados: {len(resultadoIpva)}")
        
        if not resultadoIpva:
            logger.warning("Nenhum veículo encontrado no banco. Encerrando processo.")
            return

        logger.info(f"Configuração: Nova sessão do Chrome será criada para cada veículo")
        
        # ---------------------------
        # Loop principal - UMA NOVA SESSÃO POR VEÍCULO
        # ---------------------------
        veiculos_processados = 0
        veiculos_com_erro = 0
        
        for index, veiculo in enumerate(resultadoIpva, start=1):
            renavam, num_documento, chassi, idVeiculo = veiculo
            
            logger.info("-" * 50)
            logger.info(f"PROCESSANDO VEÍCULO {index}/{len(resultadoIpva)}")
            logger.info(f"ID Veículo: {idVeiculo}")
            logger.info(f"RENAVAM: {renavam}")
            logger.info(f"CPF/CNPJ: {num_documento}")
            logger.info(f"Chassi: {chassi}")
            logger.info("-" * 50)
            
            try:
                # ---------------------------
                # Configurações do Chrome - PARA CADA VEÍCULO
                # ---------------------------
                logger.debug("Configurando opções do Chrome...")
                caminho_download = 'C:\\IpvaBf\\IPVABF'
                
                # Verificar se diretório de download existe
                if not os.path.exists(caminho_download):
                    logger.info(f"Criando diretório de download: {caminho_download}")
                    os.makedirs(caminho_download)
                
                chrome_options = webdriver.ChromeOptions()
                settings = {
                    "recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}],
                    "selectedDestinationId": "Save as PDF",
                    "version": 2
                }

                prefs = {
                    'printing.print_preview_sticky_settings.app_state': json.dumps(settings),
                    'savefile.default_directory': caminho_download,
                    'download.prompt_for_download': False,
                    'download.directory_upgrade': True,
                    'plugins.always_open_pdf_externally': True
                }

                chrome_options.add_experimental_option('prefs', prefs)
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--mute-audio')
                chrome_options.add_argument('--kiosk-printing')
                chrome_options.add_argument('--disable-session-crashed-bubble')
                chrome_options.add_argument('--window-size=1200,700')
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_experimental_option("prefs", prefs)

                # ---------------------------
                # Inicializa o Driver - NOVA SESSÃO PARA CADA VEÍCULO
                # ---------------------------
                logger.info("Inicializando nova sessão do Chrome...")
                try:
                    driver = uc.Chrome(options=chrome_options, version_main=142)
                    logger.info("Sessão do Chrome inicializada com sucesso")
                except Exception as e_driver:
                    logger.error(f"Erro ao inicializar Chrome: {e_driver}")
                    veiculos_com_erro += 1
                    continue
                
                try:
                    # Processamento do veículo
                    resultado = processar_veiculo(driver, renavam, num_documento, chassi, idVeiculo)
                    
                    if resultado:
                        veiculos_processados += 1
                        logger.info(f"Veículo {renavam} processado com sucesso")
                    else:
                        veiculos_com_erro += 1
                        logger.warning(f"Veículo {renavam} não processado completamente")
                        
                except Exception as e_veiculo:
                    logger.error(f"Erro durante processamento do veículo {renavam}: {e_veiculo}", exc_info=True)
                    veiculos_com_erro += 1
                    
                finally:
                    # ---------------------------
                    # FECHA A SESSÃO APÓS CADA VEÍCULO
                    # ---------------------------
                    logger.info("Finalizando sessão do Chrome...")
                    try:
                        driver.quit()
                        logger.debug("Sessão do Chrome finalizada")
                    except Exception as e_quit:
                        logger.warning(f"Erro ao finalizar sessão: {e_quit}")
                    
                    # Pequena pausa entre sessões
                    if index < len(resultadoIpva):
                        logger.debug("Aguardando 3 segundos antes do próximo veículo...")
                        sleep(3)
                        
            except Exception as e_sessao:
                logger.error(f"Erro na criação da sessão para veículo {renavam}: {e_sessao}", exc_info=True)
                veiculos_com_erro += 1
                continue

        # Resumo final
        logger.info("=" * 60)
        logger.info("RESUMO DO PROCESSAMENTO")
        logger.info("=" * 60)
        logger.info(f"Total de veículos: {len(resultadoIpva)}")
        logger.info(f"Veículos processados com sucesso: {veiculos_processados}")
        logger.info(f"Veículos com erro: {veiculos_com_erro}")
        logger.info(f"Data/hora de término: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        logger.info("PROCESSO FINALIZADO")

    except Exception as e:
        logger.critical(f"Erro crítico na execução principal: {e}", exc_info=True)
        raise

def processar_veiculo(driver, renavam, num_documento, chassi, idVeiculo):
    """Processa um único veículo em uma sessão específica"""
    
    try:
        logger.info("Iniciando processamento do veículo...")
        
        # ---------------------------
        # Acessar página inicial
        # ---------------------------
        url_inicial = "https://www.sefaz.mt.gov.br/ipva/emissaoguia/emitir"
        logger.info(f"Acessando página: {url_inicial}")
        driver.get(url_inicial)
        
        # Aguardar carregamento da página
        logger.debug("Aguardando carregamento da página...")
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        logger.info("Página carregada com sucesso")
        
        # ---------------------------
        # Preenchimento do formulário
        # ---------------------------
        logger.info("Preenchendo formulário de consulta...")
        
        # CPF/CNPJ
        logger.debug("Preenchendo CPF/CNPJ...")
        cpf_cnpj = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="numrDoc"]'))
        )
        cpf_cnpj.clear()
        cpf_cnpj.send_keys(str(num_documento))
        logger.info(f"CPF/CNPJ preenchido: {num_documento}")

        # RENAVAM
        if renavam:
            logger.debug("Preenchendo RENAVAM...")
            campo_renavam = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/center/form/table[2]/tbody/tr[4]/td[2]/input'))
            )
            campo_renavam.clear()
            campo_renavam.send_keys(str(renavam))
            logger.info(f"RENAVAM preenchido: {renavam}")

        # CHASSI
        if chassi:
            logger.debug("Preenchendo CHASSI...")
            campo_chassi = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/center/form/table[2]/tbody/tr[2]/td[2]/input'))
            )
            campo_chassi.clear()
            campo_chassi.send_keys(str(chassi))
            logger.info(f"CHASSI preenchido: {chassi}")

        # ---------------------------
        # CAPTCHA
        # ---------------------------
        logger.info("Processando CAPTCHA...")
        try:
            logger.debug("Solicitando solução do CAPTCHA...")
            token = captchaIPVA.anticaptcha()
            logger.info("CAPTCHA resolvido com sucesso")
            
            # Aplicar token do CAPTCHA
            driver.execute_script(f'''
                let input = document.getElementsByName("cf-turnstile-response")[0];
                if (input) {{
                    input.value = "{token}";
                }}

                if (typeof habilitarBotao === "function") {{
                    habilitarBotao("{token}");
                }}
            ''')
            
            # Clicar no botão de consulta
            logger.debug("Clicando no botão de consulta...")
            boton_consultar = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, 'botaoSubmit'))
            )
            boton_consultar.click()
            logger.info("Consulta solicitada")

        except Exception as e_captcha:
            logger.warning(f"Erro no processamento do CAPTCHA: {e_captcha}")
            try:
                logger.info("Tentando clique forçado via JavaScript...")
                driver.execute_script("document.getElementById('botaoSubmit').click();")
            except:
                logger.error("Falha ao contornar CAPTCHA")
                ObterDadosIpvaDB.updateErro("Erro no CAPTCHA", idVeiculo)
                return False

        # ---------------------------
        # Verifica mensagem de Erro
        # ---------------------------
        logger.info("Verificando mensagens de erro...")
        try:
            erro = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/center/form/table/tbody/tr[2]/td/font'))
            )
            mensagem_erro = erro.text.strip()
            logger.warning(f"Mensagem de erro encontrada: {mensagem_erro}")

            if mensagem_erro == "O CPF/CNPJ informado é inválido para este veiculo.":
                logger.error(f"CPF/CNPJ {num_documento} inválido para o veículo {renavam}")
                ObterDadosIpvaDB.updateErro("ERRO - CPF/CNPJ invalido", idVeiculo)
                return False
            
            elif mensagem_erro == "Dados inválidos, , preencha corretamente.":
                logger.error("Dados inválidos fornecidos")
                ObterDadosIpvaDB.updateErro('ERRO - Dados inválidos', idVeiculo)
                return False
            
            elif mensagem_erro == "java.lang.Exception: Validação do CAPTCHA falhou.":
                logger.error("Validação do CAPTCHA falhou")
                ObterDadosIpvaDB.updateErro("ERRO -  Validação do CAPTCHA", idVeiculo)
                return False
                
            elif mensagem_erro == 'For input string: "None"':
                logger.error('For input string: "None"')
                ObterDadosIpvaDB.updateErro('ERRO - Documento vazio', idVeiculo)
                return False
            
            elif mensagem_erro == 'Veículo informado nao foi encontrado.':
                logger.error('Veículo informado nao foi encontrado.')
                ObterDadosIpvaDB.updateErro('ERRO - Veículo nao encontrado', idVeiculo)
                return False
            
        except TimeoutException:
            logger.debug("Nenhuma mensagem de erro encontrada")
        except Exception as e_erro:
            logger.warning(f"Erro ao verificar mensagens de erro: {e_erro}")

        # ---------------------------
        # Verifica mensagem de Débito
        # ---------------------------
        logger.info("Verificando existência de débitos...")
        try:
            debito = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/center/form/div/p'))
            )
            mensagem_debito = debito.text
            
            if "Nenhum débito foi localizado" in mensagem_debito:
                logger.info(f"Veículo {renavam} não possui débitos (IPVA quitado)")
                ObterDadosIpvaDB.updateErro("QUITADO", idVeiculo)
                return True
                
        except TimeoutException:
            logger.info("Débitos encontrados, prosseguindo com emissão da guia...")
        except Exception as e_debito:
            logger.warning(f"Erro ao verificar débitos: {e_debito}")
            
        # ---------------------------
        # Emissão da Guia
        # ---------------------------
        logger.info("Iniciando processo de emissão da guia...")
        return emissaoGuia(driver, renavam, chassi, idVeiculo)

    except TimeoutException as e_timeout:
        logger.error(f"Timeout durante processamento do veículo {renavam}: {e_timeout}")
        ObterDadosIpvaDB.updateErro(f"Timeout: {str(e_timeout)[:100]}", idVeiculo)
        return False
    except Exception as e:
        logger.error(f"Erro no processamento do veículo {renavam}: {e}", exc_info=True)
        ObterDadosIpvaDB.updateErro(f"Erro processamento: {str(e)[:100]}", idVeiculo)
        return False

def emissaoGuia(driver, renavamveiculo, chassi, idVeiculo):
    """Emite a guia para um veículo específico"""
    
    try:
        logger.info("Procurando tabela de débitos...")
        tabela = None
        
        try:   
            tabela = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/center/form/table[2]/tbody/tr[1]/td'))
            )
            logger.info("Tabela de débitos encontrada")
        except TimeoutException: 
            logger.warning("Tabela de débitos não encontrada")
            return False
        
        if tabela:
            # Selecionar a opção com 5% de desconto
            logger.debug("Selecionando opção com 5% de desconto...")
            elemento = driver.find_element(By.XPATH, "//tbody[@id='cota1']//tr[td[2][contains(text(), '5%')]]/td[1]/input")
            elemento.click()
            logger.info("Opção de 5% de desconto selecionada")
            
            # Preencher email e telefone
            logger.debug("Preenchendo email e telefone...")
            try:
                email = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, 'email'))
                )
                telefone = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, 'celular'))
                )
                email.send_keys('hianny.urt@bomfuturo.com.br')
                telefone.send_keys('65998178793')
                logger.info("Email e telefone preenchidos")
            except Exception as e:
                logger.warning(f"Não foi possível preencher email/telefone: {e}")
            
            logger.debug("Aguardando 3 segundos...")
            sleep(3)
            
            # Chama a função de download
            logger.info("Iniciando download da guia...")
            return download_guia(driver, chassi, renavamveiculo, idVeiculo)
            
        return False
            
    except Exception as e:
        logger.error(f"Erro na emissão da guia para {renavamveiculo}: {e}", exc_info=True)
        ObterDadosIpvaDB.updateErro(f"Erro emissão guia: {str(e)[:100]}", idVeiculo)
        return False

def download_guia(driver, chassi, renavam, idVeiculo):
    """Realiza o download da guia de pagamento"""
    
    try:
        logger.info("Iniciando processo de download do PDF...")
        
        anoAtual = datetime.now().year
        session = requests.Session()
        
        # Copiar cookies do Selenium para a sessão requests
        logger.debug("Copiando cookies da sessão do Chrome...")
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])
        
        # Capturar dados do formulário
        logger.debug("Capturando dados do formulário...")
        url_action = driver.find_element(By.NAME, "formulario").get_attribute("action")
        csrf_token = driver.execute_script('return window["_csrf_"];')
        user_agent = driver.execute_script("return navigator.userAgent;")
        
        # Montar payload
        logger.debug("Montando payload da requisição...")
        payload = {}
        
        # Pegar todos os inputs da página
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for i in inputs:
            name = i.get_attribute("name")
            value = i.get_attribute("value")
            tipo = i.get_attribute("type")

            if not name: 
                continue

            # Mantém valores de campos hidden
            if tipo == "hidden":
                payload[name] = value
            
            # Seleciona a cota específica (Ex: Opção com 5% de desconto que é o value="2")
            if name.startswith("tipoGuia") and tipo == "radio":
                if value == "2": 
                    payload[name] = value
        
        # Pegar VALOR DO IPVA
        logger.debug("Extraindo valor do IPVA...")
        xpath_valor = "//input[@value='2']/ancestor::tr//td[contains(text(), 'R$')]"
        elemento_valor = driver.find_element(By.XPATH, xpath_valor)
        
        # Converter valor para formato numérico
        valor_texto = elemento_valor.text.replace('R$', '').strip()

        # 1. Remove qualquer caractere que não seja número, ponto ou vírgula
        valor_limpo = re.sub(r'[^\d.,]', '', valor_texto)

        # 2. Lógica para identificar o separador decimal real:
        # Se o último sinal for uma vírgula, é padrão BR (1.280,87)
        if valor_limpo.find(',') > valor_limpo.find('.'):
            valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
        # Se o último sinal for um ponto, é padrão US (1,280.87)
        else:
            valor_limpo = valor_limpo.replace(',', '')

        print(f"Valor extraído: {valor_texto}") 
        print(f"Valor limpo para o banco: {valor_limpo}")           # 1280.87

        # 3. Converte para Decimal
        valorIpva = Decimal(valor_limpo)
        
        # Adicionar campos críticos ao payload
        payload["_csrf_"] = csrf_token
        payload["pdf"] = "1"
        payload["pix"] = "1"
        payload["chassi"] = chassi.strip()
        logger.debug(f"Payload montado com {len(payload)} campos")

        # Headers da requisição
        headers = {
            "User-Agent": user_agent,
            "Referer": driver.current_url,
            "Origin": "https://www.sefaz.mt.gov.br",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        }
        
        # Enviar requisição POST
        logger.info("Enviando requisição para geração do PDF...")
        response = session.post(url_action, data=payload, headers=headers, stream=True)
        logger.info(f"Resposta recebida - Status: {response.status_code}")
        
        # Validar e salvar PDF
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            
            if 'application/pdf' in content_type:
                logger.info("PDF válido recebido. Salvando arquivo...")
                
                # Criar diretório se não existir
                output_dir = r"S:\Automacao\bot\VEICULOS\IPVA"
                if not os.path.exists(output_dir):
                    logger.info(f"Criando diretório: {output_dir}")
                    os.makedirs(output_dir)
                
                # Gerar nome do arquivo
                filename = os.path.join(output_dir, f"IPVA {anoAtual} - RENAVAM {renavam}.pdf")
                
                # Salvar PDF
                with open(filename, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                logger.info(f"✅ PDF baixado com sucesso: {filename}")
                logger.info(f"Tamanho do arquivo: {os.path.getsize(filename)} bytes")
                
                # Atualizar banco de dados
                ObterDadosIpvaDB.updateValor(valorIpva, filename, idVeiculo)
                return True
                
            else:
                logger.error(f"❌ Servidor não enviou um PDF. Content-Type: {content_type}")
                
                # Salvar resposta para análise
                erro_file = f"erro_sefaz_{renavam}_{datetime.now().strftime('%H%M%S')}.html"
                with open(erro_file, "w", encoding="utf-8") as f:
                    f.write(response.text)
                logger.info(f"Resposta salva em: {erro_file}")
                
                return False
        else:
            logger.error(f"❌ Erro HTTP na requisição: {response.status_code}")
            logger.error(f"Resposta: {response.text[:500]}...")
            return False
            
    except Exception as e:
        logger.error(f"Erro durante o download da guia para {renavam}: {e}", exc_info=True)
        ObterDadosIpvaDB.updateErro(f"Erro download: {str(e)[:100]}", idVeiculo)
        return False

if __name__ == "__main__":
    main()