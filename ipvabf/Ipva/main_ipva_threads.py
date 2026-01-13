from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from escreveLog import escreveLog
import ObterDadosIpvaDB
import os
import pandas as pd
import requests
import re
import numpy as np
import pyautogui
import time
from datetime import datetime
import captchaIPVA 
import base64
import json
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue
import random
from typing import List, Tuple, Optional
import traceback

# Configurações globais
MAX_THREADS = 3  # Número máximo de threads simultâneas
MAX_RETRIES = 2  # Número máximo de tentativas por veículo
REQUEST_TIMEOUT = 30  # Timeout para requisições
DRIVER_TIMEOUT = 60  # Timeout para driver
DOWNLOAD_PATH = 'C:\\IpvaBf\\IPVABF'
SESSION_DELAY = random.uniform(1, 3)  # Delay aleatório entre sessões

# Lock para operações de banco de dados
db_lock = threading.Lock()
log_lock = threading.Lock()

def escreveLog_threadsafe(mensagem: str):
    """Escreve log com thread safety"""
    with log_lock:
        escreveLog(mensagem)
        print(mensagem)

class VeiculoProcessor:
    """Classe para processar veículos individualmente"""
    
    def __init__(self, veiculo_data: Tuple, thread_id: int):
        self.renavam, self.num_documento, self.chassi, self.idVeiculo = veiculo_data
        self.thread_id = thread_id
        self.driver = None
        self.session = None
        
    def create_driver(self) -> Optional[webdriver.Chrome]:
        """Cria uma nova instância do driver com configurações"""
        try:
            escreveLog_threadsafe(f"[Thread-{self.thread_id}] Criando driver para RENAVAM: {self.renavam}")
            
            chrome_options = webdriver.ChromeOptions()
            
            # Configurações para download de PDF
            settings = {
                "recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}],
                "selectedDestinationId": "Save as PDF",
                "version": 2
            }
            
            prefs = {
                'printing.print_preview_sticky_settings.app_state': json.dumps(settings),
                'savefile.default_directory': DOWNLOAD_PATH,
                'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'plugins.always_open_pdf_externally': True,
                'profile.default_content_settings.popups': 0
            }
            
            chrome_options.add_experimental_option('prefs', prefs)
            
            # Opções de performance e stealth
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--mute-audio')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User-Agent aleatório
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
            ]
            chrome_options.add_argument(f'user-agent={random.choice(user_agents)}')
            
            # Configurações adicionais
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-notifications')
            
            # Inicializar driver
            driver = uc.Chrome(
                options=chrome_options,
                version_main=142,
                driver_executable_path=None  # Deixe o undetected_chromedriver gerenciar
            )
            
            # Configurar timeouts
            driver.set_page_load_timeout(DRIVER_TIMEOUT)
            driver.implicitly_wait(10)
            
            # Executar scripts stealth
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
            
        except Exception as e:
            escreveLog_threadsafe(f"[Thread-{self.thread_id}] Erro ao criar driver: {e}")
            return None
    
    def process(self) -> bool:
        """Processa um veículo com retry automático"""
        for attempt in range(MAX_RETRIES + 1):
            try:
                escreveLog_threadsafe(f"[Thread-{self.thread_id}] Tentativa {attempt + 1} para RENAVAM: {self.renavam}")
                
                # Criar novo driver para cada tentativa
                self.driver = self.create_driver()
                if not self.driver:
                    continue
                
                # Processar veículo
                success = self._process_vehicle()
                
                if success:
                    escreveLog_threadsafe(f"[Thread-{self.thread_id}] Sucesso no processamento do RENAVAM: {self.renavam}")
                    return True
                else:
                    escreveLog_threadsafe(f"[Thread-{self.thread_id}] Falha no processamento do RENAVAM: {self.renavam}")
                    
            except Exception as e:
                escreveLog_threadsafe(f"[Thread-{self.thread_id}] Erro na tentativa {attempt + 1}: {e}")
                escreveLog_threadsafe(traceback.format_exc())
                
            finally:
                # Fechar driver sempre
                self._close_driver()
                
                # Delay entre tentativas (exceto na última)
                if attempt < MAX_RETRIES:
                    sleep(random.uniform(2, 5))
        
        # Se chegou aqui, todas as tentativas falharam
        with db_lock:
            ObterDadosIpvaDB.updateErro("Falha após múltiplas tentativas", self.idVeiculo)
        return False
    
    def _process_vehicle(self) -> bool:
        """Lógica principal de processamento do veículo"""
        try:
            # Acessar página inicial
            url_inicial = "https://www.sefaz.mt.gov.br/ipva/emissaoguia/emitir"
            self.driver.get(url_inicial)
            
            # Aguardar carregamento
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="numrDoc"]'))
            )
            
            # Preencher formulário
            self._fill_form()
            
            # Resolver CAPTCHA
            if not self._solve_captcha():
                return False
            
            # Verificar erros
            error_message = self._check_errors()
            if error_message:
                with db_lock:
                    ObterDadosIpvaDB.updateErro(error_message, self.idVeiculo)
                return False
            
            # Verificar débitos
            if self._check_no_debits():
                with db_lock:
                    ObterDadosIpvaDB.updateErro("QUITADO", self.idVeiculo)
                return True
            
            # Emitir guia
            return self._emit_guide()
            
        except TimeoutException:
            escreveLog_threadsafe(f"[Thread-{self.thread_id}] Timeout no processamento do veículo {self.renavam}")
            return False
        except Exception as e:
            escreveLog_threadsafe(f"[Thread-{self.thread_id}] Erro no processamento: {e}")
            return False
    
    def _fill_form(self):
        """Preenche o formulário com dados do veículo"""
        # CPF/CNPJ
        cpf_cnpj = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="numrDoc"]'))
        )
        cpf_cnpj.clear()
        cpf_cnpj.send_keys(str(self.num_documento))
        
        # RENAVAM (se existir)
        if self.renavam:
            campo_renavam = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/center/form/table[2]/tbody/tr[4]/td[2]/input'))
            )
            campo_renavam.clear()
            campo_renavam.send_keys(str(self.renavam))
        
        # CHASSI (se existir)
        if self.chassi:
            campo_chassi = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/center/form/table[2]/tbody/tr[2]/td[2]/input'))
            )
            campo_chassi.clear()
            campo_chassi.send_keys(str(self.chassi))
    
    def _solve_captcha(self) -> bool:
        """Resolve o CAPTCHA com retry"""
        try:
            token = captchaIPVA.anticaptcha()
            
            # Injetar token via JavaScript
            self.driver.execute_script(f'''
                let input = document.getElementsByName("cf-turnstile-response")[0];
                if (input) {{
                    input.value = "{token}";
                }}
                
                if (typeof habilitarBotao === "function") {{
                    habilitarBotao("{token}");
                }}
            ''')
            
            # Clicar no botão de consulta
            boton_consultar = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.ID, 'botaoSubmit'))
            )
            boton_consultar.click()
            
            return True
            
        except Exception as e:
            escreveLog_threadsafe(f"[Thread-{self.thread_id}] Erro no CAPTCHA: {e}")
            
            # Tentar clique forçado
            try:
                self.driver.execute_script("document.getElementById('botaoSubmit').click();")
                return True
            except:
                return False
    
    def _check_errors(self) -> Optional[str]:
        """Verifica mensagens de erro na página"""
        error_xpaths = [
            ('/html/body/center/form/table/tbody/tr[2]/td/font', [
                "O CPF/CNPJ informado é inválido para este veiculo.",
                "Veículo informado nao foi encontrado.",
                "Dados inválidos, , preencha corretamente.",
                "java.lang.Exception: Validação do CAPTCHA falhou."
            ])
        ]
        
        for xpath, messages in error_xpaths:
            try:
                element = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                text = element.text.strip()
                if text in messages:
                    return text
            except:
                continue
        
        return None
    
    def _check_no_debits(self) -> bool:
        """Verifica se não há débitos"""
        try:
            debito = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/center/form/div/p'))
            )
            mensagem_debito = debito.text
            if "Nenhum débito foi localizado" in mensagem_debito:
                return True
        except:
            pass
        return False
    
    def _emit_guide(self) -> bool:
        """Emite a guia de pagamento"""
        try:
            # Encontrar e selecionar cota com 5% de desconto
            tabela = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/center/form/table[2]/tbody/tr[1]/td'))
            )
            
            elemento = self.driver.find_element(
                By.XPATH, 
                "//tbody[@id='cota1']//tr[td[2][contains(text(), '5%')]]/td[1]/input"
            )
            elemento.click()
            
            # Preencher email e telefone (opcional)
            try:
                email = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.ID, 'email'))
                )
                telefone = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.ID, 'celular'))
                )
                email.send_keys('hianny.urt@bomfuturo.com.br')
                telefone.send_keys('65998178793')
            except:
                pass
            
            # Fazer download da guia
            return self._download_guide()
            
        except Exception as e:
            escreveLog_threadsafe(f"[Thread-{self.thread_id}] Erro na emissão da guia: {e}")
            return False
    
    def _download_guide(self) -> bool:
        """Faz download da guia em PDF"""
        try:
            # Configurar sessão para download
            session = requests.Session()
            for cookie in self.driver.get_cookies():
                session.cookies.set(cookie['name'], cookie['value'])
            
            # Obter dados do formulário
            url_action = self.driver.find_element(By.NAME, "formulario").get_attribute("action")
            csrf_token = self.driver.execute_script('return window["_csrf_"];')
            user_agent = self.driver.execute_script("return navigator.userAgent;")
            
            # Montar payload
            payload = {}
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            
            for i in inputs:
                name = i.get_attribute("name")
                value = i.get_attribute("value")
                tipo = i.get_attribute("type")
                
                if not name:
                    continue
                
                if tipo == "hidden":
                    payload[name] = value
                elif name.startswith("tipoGuia") and tipo == "radio" and value == "2":
                    payload[name] = value
            
            # Obter valor do IPVA
            xpath_valor = "//input[@value='2']/ancestor::tr//td[contains(text(), 'R$')]"
            elemento_valor = self.driver.find_element(By.XPATH, xpath_valor)
            valorIpva = elemento_valor.text.replace('R$', '').replace('.', '').replace(',', '.').strip()
            
            # Adicionar campos obrigatórios
            payload["_csrf_"] = csrf_token
            payload["pdf"] = "1"
            payload["pix"] = "1"
            payload["chassi"] = self.chassi.strip() if self.chassi else ""
            
            # Headers
            headers = {
                "User-Agent": user_agent,
                "Referer": self.driver.current_url,
                "Origin": "https://www.sefaz.mt.gov.br",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
            }
            
            # Fazer requisição para download
            response = session.post(
                url_action, 
                data=payload, 
                headers=headers, 
                stream=True,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
                # Criar nome do arquivo
                ano_atual = datetime.now().year
                filename = os.path.join(
                    DOWNLOAD_PATH,
                    f"IPVA {ano_atual} - RENAVAM {self.renavam}.pdf"
                )
                
                # Garantir que o diretório existe
                os.makedirs(DOWNLOAD_PATH, exist_ok=True)
                
                # Salvar PDF
                with open(filename, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # Atualizar banco de dados
                with db_lock:
                    ObterDadosIpvaDB.updateValor(valorIpva, filename, self.idVeiculo)
                
                escreveLog_threadsafe(f"[Thread-{self.thread_id}] PDF baixado: {filename}")
                return True
            else:
                escreveLog_threadsafe(f"[Thread-{self.thread_id}] Erro no download: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            escreveLog_threadsafe(f"[Thread-{self.thread_id}] Erro no download da guia: {e}")
            return False
    
    def _close_driver(self):
        """Fecha o driver de forma segura"""
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass

def process_veiculos_parallel(veiculos: List[Tuple], max_workers: int = MAX_THREADS):
    """Processa múltiplos veículos em paralelo"""
    escreveLog_threadsafe(f"Iniciando processamento paralelo com {max_workers} threads")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Mapear cada veículo para um futuro
        future_to_veiculo = {}
        thread_counter = 0
        
        for veiculo in veiculos:
            thread_counter += 1
            processor = VeiculoProcessor(veiculo, thread_counter % max_workers)
            future = executor.submit(processor.process)
            future_to_veiculo[future] = veiculo
        
        # Processar resultados conforme completam
        resultados = {
            'sucesso': 0,
            'falha': 0,
            'total': len(veiculos)
        }
        
        for future in as_completed(future_to_veiculo):
            veiculo = future_to_veiculo[future]
            renavam = veiculo[0]
            
            try:
                success = future.result(timeout=300)  # 5 minutos timeout por veículo
                if success:
                    resultados['sucesso'] += 1
                    escreveLog_threadsafe(f"✅ Veículo {renavam} processado com sucesso")
                else:
                    resultados['falha'] += 1
                    escreveLog_threadsafe(f"❌ Falha no processamento do veículo {renavam}")
                    
            except concurrent.futures.TimeoutError:
                resultados['falha'] += 1
                escreveLog_threadsafe(f"⏰ Timeout no processamento do veículo {renavam}")
            except Exception as e:
                resultados['falha'] += 1
                escreveLog_threadsafe(f"⚠️ Erro inesperado no veículo {renavam}: {e}")
            
            # Log progressivo
            progresso = (resultados['sucesso'] + resultados['falha']) / resultados['total'] * 100
            escreveLog_threadsafe(f"📊 Progresso: {progresso:.1f}% | Sucessos: {resultados['sucesso']} | Falhas: {resultados['falha']}")
    
    return resultados

def main():
    """Função principal"""
    try:
        escreveLog_threadsafe("🚀 Iniciando execução do processo SEFAZ-IPVA com multithreading")
        
        # Buscar veículos no banco
        veiculos = ObterDadosIpvaDB.RetornoVeiculosIpva()
        
        if not veiculos:
            escreveLog_threadsafe("❌ Nenhum veículo encontrado no banco")
            return
        
        escreveLog_threadsafe(f"📋 Total de veículos encontrados: {len(veiculos)}")
        
        # Processar veículos em paralelo
        resultados = process_veiculos_parallel(veiculos)
        
        # Resumo final
        escreveLog_threadsafe("=" * 50)
        escreveLog_threadsafe("📋 RESUMO DO PROCESSAMENTO")
        escreveLog_threadsafe("=" * 50)
        escreveLog_threadsafe(f"Total de veículos: {resultados['total']}")
        escreveLog_threadsafe(f"Processados com sucesso: {resultados['sucesso']}")
        escreveLog_threadsafe(f"Falhas: {resultados['falha']}")
        escreveLog_threadsafe(f"Taxa de sucesso: {resultados['sucesso']/resultados['total']*100:.1f}%")
        
    except Exception as e:
        escreveLog_threadsafe(f"💥 Erro crítico na execução principal: {e}")
        escreveLog_threadsafe(traceback.format_exc())

if __name__ == "__main__":
    main()