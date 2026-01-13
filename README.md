# Documentação do Projeto IPVABF

## 📋 Visão Geral

O projeto **IPVABF** é um sistema de automação para consulta e extração de informações sobre veículos, incluindo dados de IPVA (Imposto sobre Propriedade de Veículos Automotores), Licenciamento e Multas. O projeto utiliza web scraping, APIs, e integração com banco de dados Oracle para automatizar processos que antes eram manuais.

**Principais características:**
- Coleta de dados de múltiplas fontes (SEFAZ, DETRAN)
- Armazenamento em banco de dados Oracle
- Processamento paralelo com threads
- Tratamento de CAPTCHAs
- Geração de logs detalhados para auditoria

---

## 🏗️ Estrutura do Projeto

```
IPVABF/
├── ObterDados/          # Etapa 1: Busca dados básicos dos veículos
├── Ipva/                # Etapa 2: Consulta IPVA da SEFAZ/MT
├── Licenciamento/       # Etapa 3: Consulta Licenciamento e Multas no DETRAN
├── Multas/              # Módulo complementar para processamento de multas
└── __init__.py
```

---

## 📂 Detalhamento das Pastas

### 1. **ObterDados/** - Extração de Dados Base

#### 🎯 Objetivo
Esta pasta é responsável pela **primeira etapa do fluxo**: buscar informações básicas dos veículos a partir de uma tabela-fonte no banco de dados Oracle (tabela PROTHEUS11.AV_BENSMTI) e inserir esses dados em uma tabela nova e vazia (IPVA_LICENCIAMENTO).

#### 📁 Arquivos Principais

| Arquivo | Função |
|---------|--------|
| `MainObterDados.py` | Script principal que orquestra o fluxo |
| `ObterDadosMultasDB.py` | Conexão com Oracle e operações no banco de dados |
| `ObterDadosDBbkp.py` | Backup do arquivo original |
| `ObterDadosMultasDB.py` | Operações de INSERT/UPDATE no banco |

#### 🔄 Fluxo de Funcionamento

```
1. MainObterDados() é chamado com um dígito de placa (finalPlaca='1')
   ↓
2. RetornoVeiculosBen() busca veículos da tabela AV_BENSMTI
   - Filtra por último dígito da placa
   - Exclui veículos que já existem em IPVA_LICENCIAMENTO
   ↓
3. Para cada veículo encontrado:
   a) veiculoIndividual() - Verifica o ID do veículo
   b) InserirDadosTabela() - Insere na tabela IPVA_LICENCIAMENTO
   c) RetornoVeiculosIpva() - Busca dados de IPVA anterior (se existir)
   ↓
4. Resultado: Tabela IPVA_LICENCIAMENTO preenchida com dados básicos
   (PLACA, RENAVAM, CHASSIS, GRUPO, NUM_DOCUMENTO, ID)
```

#### 💾 Dados Envolvidos

**Origem (Tabela PROTHEUS11.AV_BENSMTI):**
- N1_PLACA - Placa do veículo
- N1_RENAVAN - Número RENAVAN
- N1_CHASSIS - Número do chassis
- N1_GRUPO - Grupo do veículo

**Destino (Tabela RPA.IPVA_LICENCIAMENTO):**
- PLACA
- RENAVAM
- CHASSIS
- GRUPO
- ID (gerado automaticamente)
- NUM_DOCUMENTO (preenchido a partir da tabela antiga)

#### ⚙️ Configuração
```python
tabela_ipva = 'ipva_licenciamento_2026'  # Tabela destino
```

#### 🔑 Variáveis de Ambiente Necessárias
```
usernameBd    # Usuário Oracle
passwordBd    # Senha Oracle
dsn           # String de conexão (ex: oracle.com:1521/ORCL)
```

---

### 2. **Ipva/** - Consulta IPVA SEFAZ/MT

#### 🎯 Objetivo
Esta pasta é responsável pela **segunda etapa do fluxo**: consultar informações de IPVA (Imposto sobre Propriedade de Veículos Automotores) junto à SEFAZ (Secretaria de Estado da Fazenda) de Mato Grosso.

#### 📁 Arquivos Principais

| Arquivo | Função |
|---------|--------|
| `MainIpvaRequests.py` | **Script principal** - Orquestra todo o fluxo IPVA |
| `ObterDadosIpvaDB.py` | Operações de banco de dados (SELECT, UPDATE) |
| `captchaIPVA.py` | Resolução automática de CAPTCHAs |
| `escreveLog.py` | Geração de logs estruturados |
| `main_ipva_threads.py` | Versão anterior com threads (backup) |
| `MainIpvaOld.py` | Versão antiga (referência/backup) |
| `logIpva/` | Diretório com histórico de logs de execução |
| `img/` | Imagens capturadas durante o processo (debug) |

#### 🔄 Fluxo de Funcionamento

```
MainIpvaRequests.main()
│
├─ 1. BUSCAR VEÍCULOS NO BANCO
│  └─ ObterDadosIpvaDB.RetornoVeiculosIpva()
│     Retorna veículos onde:
│     • NUM_DOCUMENTO NOT NULL
│     • RENAVAM > 1 caractere
│     • STATUS_IPVA = NULL ou NÃO QUITADO/A PAGAR
│     • GRUPO NÃO IN ('0306','0309','0406')  [grupos isentos]
│
├─ 2. PARA CADA VEÍCULO (loop)
│  │
│  ├─ a) CONFIGURAR CHROME (Nova sessão por veículo)
│  │     └─ Headless, prefs de download, user-agent realista
│  │
│  ├─ b) ACESSAR SEFAZ/MT
│  │     └─ driver.get("https://www.sefaz.mt.gov.br/...")
│  │
│  ├─ c) PREENCHER DADOS
│  │     ├─ Número de Documento (CPF/CNPJ)
│  │     ├─ RENAVAM
│  │     └─ Resolver CAPTCHA (se necessário)
│  │
│  ├─ d) EXTRAIR INFORMAÇÕES
│  │     ├─ Status IPVA (QUITADO/A PAGAR/VENCIDO)
│  │     ├─ Valor a pagar
│  │     └─ Data de vencimento
│  │
│  └─ e) ATUALIZAR BANCO DE DADOS
│     └─ ObterDadosIpvaDB.update(status, idVeiculo)
│        ou updateErro(msg_erro, idVeiculo)
│
└─ 3. FINALIZAR
   └─ Registrar sucesso/erro nos logs
```

#### 🌐 Tecnologias Utilizadas

| Tecnologia | Objetivo |
|-----------|----------|
| **Selenium** | Automação do navegador Chrome |
| **undetected-chromedriver** | Bypass de detecção de automação |
| **Chrome (Headless)** | Navegador em modo sem interface |
| **Requests** | Requisições HTTP (se necessário) |

#### ⚙️ Configurações do Chrome

```python
chrome_options = webdriver.ChromeOptions()
# - Modo headless (sem interface gráfica)
# - Download automático (PDF) - configurado para SEFAZ
# - Desabilita notificações, popups, extensões
# - Modo sandbox desabilitado (para Linux/Docker)
# - GPU desabilitada
# - Resolução: 1920x1080
```

#### 📊 Dados Processados

**Entrada (do Banco):**
- RENAVAM
- NUM_DOCUMENTO (CPF/CNPJ)
- CHASSIS
- ID (identificador único)

**Saída (atualização no banco):**
- STATUS_IPVA: 'QUITADO', 'A PAGAR', 'VENCIDO', 'ERRO - ...'
- VALOR_IPVA: Valor numérico com até 5 casas decimais
- ARQUIVO_IPVA: Caminho do arquivo PDF baixado
- DT_ULT_CONSULTA_SEFAZ: Data/hora da consulta (SYSDATE)

#### ⚠️ Tratamento de Erros

```
Erros comuns e como são tratados:
├─ CAPTCHA não resolvido → 'ERRO - CAPTCHA não resolvido'
├─ Timeout na SEFAZ → 'ERRO - Timeout ao conectar SEFAZ'
├─ Dados inválidos → 'ERRO - Dados não encontrados na SEFAZ'
├─ Erro ao fazer download → 'ERRO - Falha ao baixar arquivo'
└─ Erro geral → updateErro(mensagemErro, idVeiculo)
```

#### 📝 Geração de Logs

Os logs são gerados em `logIpva/` com formato:
```
log_execucao2026-01-06T09_46.txt

Conteúdo:
[2026-01-06 09:46:23] INICIANDO PROCESSO IPVA
[2026-01-06 09:46:24] Veículo 1/150: RENAVAM:12345678, CPF:123.456.789-10
[2026-01-06 09:46:45] Status IPVA: QUITADO
[2026-01-06 09:46:50] Veículo processado com sucesso
...
```

#### 🔑 Variáveis de Ambiente
```
usernameBd    # Usuário Oracle
passwordBd    # Senha Oracle
dsn           # String de conexão Oracle
```

---

### 3. **Licenciamento/** - Consulta Licenciamento e Multas DETRAN

#### 🎯 Objetivo
Esta pasta realiza a **terceira etapa do fluxo**: consultar informações de Licenciamento e Multas do veículo junto ao DETRAN/MT (Departamento Estadual de Trânsito de Mato Grosso).

#### 📁 Arquivos Principais

| Arquivo | Função |
|---------|--------|
| `MainLicenciamento.py` | **Script principal** - Orquestra consulta DETRAN |
| `escreveLog.py` | Sistema de logs |
| `teste.py` | Script de testes |
| `database/` | Módulos de banco de dados |
| `captcha/` | Resolução de CAPTCHAs DETRAN |
| `email/` | Envio de e-mails com resultados |
| `logLicenciamento/` | Histórico de logs |
| `ps1/` | Scripts PowerShell auxiliares |
| `ResultadoCsv/` | Geração de relatórios CSV |

#### 📂 Subpastas Detalhadas

##### **database/**
```
├── ObterDadosLicenciamentoDB.py     # Buscar veículos da tabela
├── ObterResultadoFinalDB.py         # Atualizar status no banco
└── __pycache__/
```

**Principais funções:**
- `RetornoVeiculosLicenciamento()` - Busca veículos por dígito da placa
- `RetornoVeiculosErro()` - Busca veículos com erro em consultas anteriores
- `RetornoVeiculosSucesso()` - Retorna veículos processados com sucesso
- `updateErro()` - Atualiza registro com status de erro
- `updateLicenciamento()` - Atualiza dados de licenciamento
- `updateMultas()` - Atualiza dados de multas

##### **captcha/**
```
├── captchaLicenciamento.py          # Resolução de CAPTCHA
└── __pycache__/
```

##### **email/**
```
├── ResultadoEmail.py                # Envio de relatórios por e-mail
└── __pycache__/
```

##### **ps1/**
Contém scripts PowerShell para automação adicional (triggers, agendamentos).

##### **ResultadoCsv/**
Armazena arquivos CSV com resultados das consultas.

#### 🔄 Fluxo de Funcionamento

```
MainLicenciamento.main(final_placa)
│
├─ 0. DEFINIR QUAL LOTE PROCESSAR
│  ├─ Se final_placa == 'erro': processa veículos com erro
│  └─ Senão: processa veículos com dígito final = final_placa
│
├─ 1. BUSCAR VEÍCULOS NO BANCO
│  └─ ObterDadosLicenciamentoDB.RetornoVeiculosLicenciamento(final_placa)
│     Retorna: (ID, PLACA, RENAVAM, CHASSIS, NUM_DOCUMENTO)
│
├─ 2. PARA CADA VEÍCULO (loop)
│  │
│  ├─ a) CONFIGURAR NAVEGADOR (Chrome Undetected)
│  │     ├─ Headless mode
│  │     ├─ Selenium-stealth (anti-detecção)
│  │     └─ Download path configurado
│  │
│  ├─ b) ACESSAR DETRAN
│  │     └─ driver.get("https://www.detran.mt.gov.br/consulte-seu-veiculo")
│  │
│  ├─ c) EXECUTAR FUNÇÃO DE CONSULTA
│  │     └─ realizandoLicenciamento(driver, placa, renavam, num_doc, idVeiculo)
│  │        ├─ Aguardar carregamento da página
│  │        ├─ Localizar campos de entrada
│  │        ├─ Preencher: PLACA, RENAVAM, CPF/CNPJ
│  │        ├─ Resolver CAPTCHA (se necessário)
│  │        ├─ Submeter formulário
│  │        ├─ Extrair informações:
│  │        │  ├─ Status do Licenciamento (ATIVO/VENCIDO/CANCELADO)
│  │        │  ├─ Multas (quantidade e valor)
│  │        │  └─ Detalhes de débitos
│  │        └─ Fazer download de documentos (se disponível)
│  │
│  ├─ d) ATUALIZAR BANCO DE DADOS
│  │     ├─ Se sucesso: ObterResultadoFinalDB.updateLicenciamento(...)
│  │     ├─ Se erro geral: updateErro(msg_lic, msg_multas, idVeiculo)
│  │     └─ DT_ULT_CONSULTA_DETRAN = SYSDATE
│  │
│  └─ e) REGISTRAR EM LOG
│     └─ escreveLog(f"Processado: {placa}")
│
└─ 3. FINALIZAR
   ├─ Fechar navegador
   ├─ Gerar relatórios CSV (se configurado)
   └─ Enviar e-mail com resultados (se configurado)
```

#### 🔍 Função Principal: realizandoLicenciamento()

Esta função contém a lógica de preenchimento do formulário DETRAN:

```python
realizandoLicenciamento(driver, placaVeiculo, renavamVeiculo, 
                       num_documentoVeiculo, idVeiculo)
│
├─ 1. Localizar campos HTML
│  └─ WebDriverWait para elementos ficarem visíveis
│
├─ 2. Preencher campos
│  ├─ Campo PLACA: placaVeiculo
│  ├─ Campo RENAVAM: renavamVeiculo
│  └─ Campo CPF/CNPJ: num_documentoVeiculo
│
├─ 3. Resolver CAPTCHA (se aparece)
│  └─ captchaLicenciamento.resolverCaptcha(driver)
│
├─ 4. Clicar em "Consultar"
│  └─ WebDriverWait até resultado aparecer
│
├─ 5. Extrair dados da tabela de resultados
│  ├─ Status Licenciamento
│  ├─ Multas (quantidade)
│  ├─ Valores a pagar
│  └─ Data da última consulta
│
└─ 6. Salvar informações extraídas
   └─ Preparar para atualizar no banco
```

#### 🌐 Tecnologias Utilizadas

| Tecnologia | Objetivo |
|-----------|----------|
| **Selenium** | Automação do navegador |
| **undetected-chromedriver** | Bypass de anti-bot do DETRAN |
| **selenium-stealth** | Mascarar automação |
| **webdriver-manager** | Gerenciar versão do Edge/Chrome |
| **OCR/CAPTCHA Solver** | Resolver desafios automáticos |

#### 📊 Dados Processados

**Entrada (do Banco):**
- ID
- PLACA
- RENAVAM
- CHASSIS
- NUM_DOCUMENTO (CPF/CNPJ)

**Saída (atualização no banco):**
```
Campos atualizados em IPVA_LICENCIAMENTO:
├─ STATUS_LICENCIAMENTO: 'ATIVO', 'VENCIDO', 'CANCELADO', ou 'ERRO - ...'
├─ STATUS_MULTAS: 'SEM MULTAS', 'COM MULTAS', ou 'ERRO - ...'
├─ MULTAS: Número inteiro (quantidade de multas) ou '0'
├─ DT_ULT_CONSULTA_DETRAN: SYSDATE
├─ DT_ULT_CONSULTA_MULTAS: SYSDATE
└─ Campos opcionais para valor total de multas
```

#### ⚠️ Tratamento de Erros

```
Possíveis erros e respostas:
├─ "PLACA NÃO ENCONTRADA" → STATUS_LICENCIAMENTO = 'ERRO - Placa não existe'
├─ "RENAVAM INVÁLIDO" → STATUS_LICENCIAMENTO = 'ERRO - RENAVAM inválido'
├─ "CPF/CNPJ INVÁLIDO" → STATUS_LICENCIAMENTO = 'ERRO - Documento inválido'
├─ Timeout do site DETRAN → 'ERRO - Timeout ao conectar DETRAN'
├─ CAPTCHA não resolvido → 'ERRO - CAPTCHA não foi resolvido'
└─ Erro conexão/rede → 'ERRO - Falha de conexão'
```

#### 📝 Geração de Logs

Formato similar ao IPVA:
```
log_execucao2026-01-06T09_46.txt

[2026-01-06 09:46:00] Processando placa: OBE3I59
[2026-01-06 09:46:05] Acessando DETRAN...
[2026-01-06 09:46:15] Preenchendo formulário...
[2026-01-06 09:46:25] Resolvendo CAPTCHA...
[2026-01-06 09:46:35] Status Licenciamento: ATIVO
[2026-01-06 09:46:40] Multas encontradas: 2
[2026-01-06 09:46:45] Veículo processado com sucesso
```

#### 📧 Envio de E-mails

A pasta `email/` contém `ResultadoEmail.py` que pode enviar:
- Relatórios diários de execução
- Alertas de erros
- Resumo de veículos processados

#### 📋 Geração de Relatórios CSV

Os resultados podem ser exportados para CSV em `ResultadoCsv/`:
```
resultado_2026-01-06.csv

PLACA,RENAVAM,CHASSIS,STATUS_LICENCIAMENTO,STATUS_MULTAS,MULTAS
OBE3I59,12345678,JHDJQW2323DW23,ATIVO,SEM MULTAS,0
OBE3I60,12345679,JHDJQW2323DW24,VENCIDO,COM MULTAS,2
```

---

### 4. **Multas/** - Processamento Complementar de Multas

#### 🎯 Objetivo
Módulo complementar para processar e detalhar informações sobre multas de trânsito.

#### 📁 Arquivos Principais

| Arquivo | Função |
|---------|--------|
| `mainMultas.py` | Orquestra o processamento de multas |
| `captchaMultas.py` | Resolução de CAPTCHAs específicos para multas |
| `multasDB.py` | Operações no banco para dados de multas |

#### 🔄 Fluxo
Este módulo funciona em conjunto com o Licenciamento para:
1. Detalhar multas encontradas
2. Extrair informações como: valor, data, infração
3. Atualizar tabela com histórico detalhado

---

## 🔄 Fluxo Geral Integrado

```
┌─────────────────────────────────────────────────────┐
│              BANCO DE DADOS ORACLE                   │
│  Tabela: IPVA_LICENCIAMENTO                         │
│  (ID, PLACA, RENAVAM, CHASSIS, NUM_DOCUMENTO, ...) │
└────────────────┬────────────────────────────────────┘
                 │
         ┌───────▼────────┐
         │                │
         │  ObterDados/   │
         │                │
         │ Copia dados    │
         │ de:            │
         │ AV_BENSMTI     │
         │ para           │
         │ IPVA_LICH.     │
         │                │
         └───────┬────────┘
                 │
        ┌────────▼──────────┐
        │                   │
        │     IPVA/         │
        │                   │
        │ Consulta SEFAZ:   │
        │ - Status IPVA     │
        │ - Valor a pagar   │
        │ - Atualiza DB     │
        │                   │
        └────────┬──────────┘
                 │
        ┌────────▼──────────┐
        │                   │
        │  Licenciamento/   │
        │                   │
        │ Consulta DETRAN:  │
        │ - Status Lic.     │
        │ - Multas          │
        │ - Atualiza DB     │
        │                   │
        └────────┬──────────┘
                 │
        ┌────────▼──────────┐
        │                   │
        │    Multas/        │
        │                   │
        │ Detalha multas    │
        │ (opcional)        │
        │                   │
        └────────┬──────────┘
                 │
        ┌────────▼──────────┐
        │                   │
        │   RESULTADO       │
        │                   │
        │ - DB atualizado   │
        │ - Logs gerados    │
        │ - CSV/Email       │
        │   (opcionais)     │
        │                   │
        └───────────────────┘
```

---

## 🗄️ Estrutura do Banco de Dados

### Tabela Principal: IPVA_LICENCIAMENTO

```sql
CREATE TABLE IPVA_LICENCIAMENTO (
    ID                          NUMBER(10) PRIMARY KEY,
    PLACA                       VARCHAR2(7),
    RENAVAM                     VARCHAR2(11),
    CHASSIS                     VARCHAR2(30),
    GRUPO                       VARCHAR2(10),
    NUM_DOCUMENTO               VARCHAR2(20),
    
    -- Dados IPVA
    STATUS_IPVA                 VARCHAR2(100),
    VALOR_IPVA                  NUMBER(12,5),
    ARQUIVO_IPVA                VARCHAR2(500),
    DT_ULT_CONSULTA_SEFAZ       DATE,
    
    -- Dados Licenciamento
    STATUS_LICENCIAMENTO        VARCHAR2(100),
    MULTAS                      NUMBER(5),
    STATUS_MULTAS               VARCHAR2(100),
    DT_ULT_CONSULTA_DETRAN      DATE,
    DT_ULT_CONSULTA_MULTAS      DATE,
    
    -- Controle
    DT_CRIACAO                  DATE DEFAULT SYSDATE,
    DT_ATUALIZACAO              DATE DEFAULT SYSDATE
);
```

### Tabela Origem: PROTHEUS11.AV_BENSMTI

```sql
-- Apenas campos relevantes
N1_PLACA        -- Placa do veículo
N1_RENAVAN      -- RENAVAN
N1_CHASSIS      -- Chassis
N1_GRUPO        -- Grupo do veículo
```

---

## 🚀 Como Executar

### Execução Passo-a-Passo Completa

#### **Passo 1: ObterDados** (Inicial, uma vez ou periódico)
```bash
cd c:\IpvaBf\IPVABF\ObterDados
python MainObterDados.py
# Para final_placa específico: mainObterDados('1')
```

#### **Passo 2: IPVA** (Diário)
```bash
cd c:\IpvaBf\IPVABF\Ipva
python MainIpvaRequests.py
# Processa veículos com STATUS_IPVA = NULL
```

#### **Passo 3: Licenciamento** (Diário)
```bash
cd c:\IpvaBf\IPVABF\Licenciamento
python MainLicenciamento.py 0  # Processa placas terminando em 0
python MainLicenciamento.py 1  # Processa placas terminando em 1
# ... até 9
# Ou processar erros:
python MainLicenciamento.py erro  # Reprocessa com erro
```

#### **Opcional: Multas**
```bash
cd c:\IpvaBf\IPVABF\Multas
python mainMultas.py
```

---

## ⚙️ Configuração do Ambiente

### Variáveis de Ambiente (.env)

Arquivo necessário na raiz do projeto:
```
usernameBd=seu_usuario_oracle
passwordBd=sua_senha_oracle
dsn=host:porta/ORCL
```

### Dependências Python

```
pip install selenium
pip install oracledb
pip install pandas
pip install undetected-chromedriver
pip install webdriver-manager
pip install selenium-stealth
pip install python-dotenv
pip install requests
```

### Outros Requisitos

- **Python 3.12.10**
- **Chrome/Chromium** instalado
- **Oracle Client** ou conexão válida ao Oracle
- **Acesso à internet** para SEFAZ e DETRAN

---

## 📊 Estatísticas de Uso

### Diretório de Logs

```
Ipva/logIpva/           - 40+ logs (IPVA)
Licenciamento/logLicenciamento/  - 60+ logs (Licenciamento)
```

Cada log contém:
- Timestamp de início/fim
- Veículos processados
- Sucesso/Erros
- Tempo de execução

---

## 🐛 Troubleshooting

### Problema: "Nao foi encontrado veiculos no banco"
**Causa:** ObterDados não encontrou registros
**Solução:** Verificar se tabela AV_BENSMTI tem dados, ou se já foram processados

### Problema: CAPTCHA não resolvido
**Causa:** Falha na resolução automática
**Solução:** Ajustar configurações de captcha em `captchaIPVA.py` ou `captchaLicenciamento.py`

### Problema: Timeout ao conectar SEFAZ/DETRAN
**Causa:** Site fora do ar ou lento
**Solução:** Aumentar timeout em Selenium (WebDriverWait), tentar novamente depois

### Problema: Erro de conexão Oracle
**Causa:** Credenciais incorretas ou banco offline
**Solução:** Verificar `.env`, testar conexão com sqlplus

---

## 📝 Notas Importantes

1. **Execução Sequencial:** Os módulos devem ser executados em ordem (ObterDados → IPVA → Licenciamento)

2. **Processamento por Lote:** Licenciamento processa placas por dígito final (0-9) para distribuir carga

3. **Grupos Isentos:** Grupos '0306', '0309', '0406' não são consultados no IPVA (isentos)

4. **Atualização Incremental:** O banco mantém histórico de consultas (DT_ULT_CONSULTA_*)

5. **Logs Auditáveis:** Todos os processos geram logs para rastreamento e auditoria

6. **Tratamento de Erro:** Veículos com erro podem ser reprocessados com `final_placa='erro'`

---

## 📅 Histórico de Melhorias

- **v2.0** (MainIpvaRequests.py): Nova sessão Chrome por veículo
- **v1.0** (MainIpvaOld.py): Reutilização de sessão (mais rápido mas menos confiável)

---

## 📞 Suporte e Manutenção

Para adicionar novos módulos ou alterar o fluxo:

1. Manter padrão de estrutura de pastas
2. Usar classes/funções de banco de dados existentes
3. Gerar logs com escreveLog()
4. Documentar mudanças neste arquivo
5. Testar com pequenos lotes antes de executar em produção


