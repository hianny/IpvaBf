import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import os 

server_smtp = "smtp-lob.office365.com"
port = 587
sender_mail = "rpa@bomfuturo.com.br"
password = "7BchvtSg0ZV6"

#Environment = "protheus"

#destinatarios = ["WILSON.PALHARES@bomfuturo.com.br", "hianny.urt@bomfuturo.com.br","SHERMAN.VENDRAMINI@bomfuturo.com.br","grupopatrimoniomultastransito@bomfuturo.com.br"]
destinatarios = ["hianny.urt@bomfuturo.com.br"]
#                       final_placa, len(resultadoVeiculos),numeroCsErro,numeroCsvSucesso,numeroCsvDebito,arquivoCsvSucesso,arquivoCsvErro,arquivoCsvSemDebito
def ResultadoFinalEmail(finalPlaca,qtdVeiculos,qtdVeiculosErro,qtdVeiculosSucesso,qtdVeiculosSDebito,arquivoCsvSucesso,arquivoCsvErro,arquivoCsvSemDebito):

    try:
        data = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        
        server_smtp = "smtp-lob.office365.com"
        port = 587
        sender_mail = "rpa@bomfuturo.com.br"
        password = "7BchvtSg0ZV6"

        subject = fr"FINALIZAÇÃO DA PLACA DE FINAL: {finalPlaca} "
        body = f"""\
        <h1>O robô de Multas terminou a execução</h1>
        <p>###########################################################</p>
        <p>Data de finalização: {data} </p>
        <p>Final de placa: {finalPlaca}</p>
        <p>###########################################################</p>
        <p>Quantidade total de veiculos que rodaram: {qtdVeiculos}</p>
        <p>Quantidade de veiculos que deram erro: {qtdVeiculosErro}</p>
        <p>Quantidade de veiculos sem debito: {qtdVeiculosSDebito}</p>
        <p>Quantidade de veiculos que tem pendencias: {qtdVeiculosSucesso}</p>
        <p>###########################################################</p>
        """
        arquivos_csv = [
            arquivoCsvSucesso,
            arquivoCsvErro,
            arquivoCsvSemDebito
        ]
        message = MIMEMultipart()
        message["From"] = sender_mail
        message["To"] = ", ".join(destinatarios)
        message["Subject"] = subject
        # Corpo do e-mail em HTML
        message.attach(MIMEText(body, "html"))
        # Anexo (CSV)
        for caminho in arquivos_csv:
            with open(caminho, "rb") as f:
                dados = f.read()
                part = MIMEApplication(dados, _subtype="octet-stream")  # Tipo genérico para garantir compatibilidade
                part.add_header("Content-Disposition", "attachment", filename=caminho)  # caminho completo como nome
                message.attach(part)
        # Envio
        server = smtplib.SMTP(server_smtp, port)
        server.starttls()
        server.login(sender_mail, password)
        server.sendmail(sender_mail, destinatarios, message.as_string())
        server.quit()
        print('--------------------------------')
        print('Email de finalizacao enviado com sucesso')
        print('--------------------------------')
    except Exception as e:
        print('--------------------------------')
        print('ERRO AO ENVIAR O EMAIL DE FINALIZAÇÃO')
        print('ERRO: ', e)
        print('--------------------------------')


    return

def ResultadoErro(erro,finalPlaca,qtdVeiculos,qtdVeiculosErro,qtdVeiculosSucesso,qtdVeiculosSDebito,arquivoCsvSucesso,arquivoCsvErro,arquivoCsvSemDebito):
    try:
        data = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        #destinatarios = ["WILSON.PALHARES@bomfuturo.com.br", "hianny.urt@bomfuturo.com.br"]
        
        server_smtp = "smtp-lob.office365.com"
        port = 587
        sender_mail = "rpa@bomfuturo.com.br"
        password = "7BchvtSg0ZV6"

        subject = fr"ERRO NA FINALIZAÇÃO DA PLACA DE FINAL: {finalPlaca} "
        body = f"""\
        <h1>Erro na execução</h1>
        <p>###########################################################</p>
        <p>Ocorreu um erro durante a execucao do Robô, o erro causou a interrupção do robô.</p>
        <p>Erro: {erro}</p>
        <p>O roboô vai passar para a Proximo de placa, os veiculos que não rodaram pela interrupção do erro serão rodadas depois da finalização dos veiculos com final de placa: 0</p>
        <p>###########################################################</p>
        <p>Data de finalização: {data} </p>
        <p>Final de placa: {finalPlaca}</p>
        <p>###########################################################</p>
        <p>Quantidade total de veiculos que rodaram: {qtdVeiculos}</p>
        <p>Quantidade de veiculos que deram erro: {qtdVeiculosErro}</p>
        <p>Quantidade de veiculos sem debito: {qtdVeiculosSDebito}</p>
        <p>Quantidade de veiculos que tem pendencias: {qtdVeiculosSucesso}</p>
        <p>###########################################################</p>
        """
        arquivos_csv = [
            arquivoCsvSucesso,
            arquivoCsvErro,
            arquivoCsvSemDebito
        ]
        message = MIMEMultipart()
        message["From"] = sender_mail
        message["To"] = ", ".join(destinatarios)
        message["Subject"] = subject
        # Corpo do e-mail em HTML
        message.attach(MIMEText(body, "html"))
        # Anexo (CSV)
        for caminho in arquivos_csv:
            with open(caminho, "rb") as f:
                nome_arquivo = os.path.basename(caminho)  # Só o nome, sem o caminho
                part = MIMEApplication(f.read(), _subtype="csv")
                part.add_header("Content-Disposition", "attachment", filename=nome_arquivo)
                message.attach(part)
        # Envio
        server = smtplib.SMTP(server_smtp, port)
        server.starttls()
        server.login(sender_mail, password)
        server.sendmail(sender_mail, destinatarios, message.as_string())
        server.quit()
        print('--------------------------------')
        print('Email de finalizacao enviado com sucesso')
        print('--------------------------------')
    except Exception as e:
        print('--------------------------------')
        print('ERRO AO ENVIAR O EMAIL DE FINALIZAÇÃO')
        print('ERRO: ', e)
        print('--------------------------------')
    return

if __name__ == "__main__":
    ResultadoErro('','','','','','','','')
    ResultadoFinalEmail('','','','','','','')