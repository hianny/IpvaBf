import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

server_smtp = "smtp-lob.office365.com"
port = 587
sender_mail = "rpa@bomfuturo.com.br"
password = "7BchvtSg0ZV6"

#Environment = "protheus"

#destinatarios = ["WILSON.PALHARES@bomfuturo.com.br", "hianny.urt@bomfuturo.com.br"]
destinatarios = ["hianny.urt@bomfuturo.com.br"]

def ResultadoFinalEmail(finalPlaca,qtdVeiculos,qtdVeiculosErro,qtdVeiculosSucesso,qtdVeiculosSDebito,arquivo_csv):

    try:
        destinatarios = ["hianny.urt@bomfuturo.com.br"]
        
        server_smtp = "smtp-lob.office365.com"
        port = 587
        sender_mail = "rpa@bomfuturo.com.br"
        password = "7BchvtSg0ZV6"

        subject = fr"O robô Multas Finalizou o final de placa {finalPlaca} "
        body = f"""\
        <h1>O robo de Multas terminou a execução</h1>>
        <p>Final de placa: {finalPlaca}</p>
        <p></p>
        <p>###########################################################</p>
        <p>Quantidade total de veiculos que rodaram: {qtdVeiculos}</p>
        <p>###########################################################</p>
        <p>Quantidade de veiculos que deram erro: {qtdVeiculosErro}</p>
        <p>###########################################################</p>
        <p>Quantidade de veiculos sem debito: {qtdVeiculosSDebito}</p>
        <p>###########################################################</p>
        <p>Quantidade de veiculos que tem pendencias: {qtdVeiculosSucesso}</p>
        <p>###########################################################</p>
        """
        message = MIMEMultipart()
        message["From"] = sender_mail
        message["To"] = ", ".join(destinatarios)
        message["Subject"] = subject
        # Corpo do e-mail em HTML
        message.attach(MIMEText(body, "html"))
        # Anexo (CSV)
        with open(arquivo_csv, "rb") as f:
            part = MIMEApplication(f.read(), _subtype="csv")
            part.add_header("Content-Disposition", "attachment", filename=arquivo_csv)
            message.attach(part)
        # Envio
        server = smtplib.SMTP(server_smtp, port)
        server.starttls()
        server.login(sender_mail, password)
        server.sendmail(sender_mail, destinatarios, message.as_string())

        print('--------------------------------')
        print('Email de finalizacao enviado com sucesso')
        print('--------------------------------')
        server.quit()
    except Exception as e:
        print(f'Ocorreu um erro: {e}')

    return


def ResultadoErro(finalPlaca,qtdVeiculos,qtdVeiculosErro,qtdVeiculosSucesso,qtdVeiculosSDebito, mensagemErro):
    try:

        subject = "ERRO NO DOCKER_TIR"
        body = f"""\
        <p>OCORREU UM ERRO NO MEIO DA EXECUCAO QUE INTERROMPEU O FLUXO DE VEICULOS</p>
        <p>Final de placa: {finalPlaca}</p>
        <p>ERRO:{mensagemErro}</p>>
        <p></p>
        <p>###########################################################</p>
        <p>Quantidade total de veiculos que rodaram: {qtdVeiculos}</p>
        <p>###########################################################</p>
        <p>Quantidade de veiculos que deram erro: {qtdVeiculosErro}</p>
        <p>###########################################################</p>
        <p>Quantidade de veiculos sem debito: {qtdVeiculosSDebito}</p>
        <p>###########################################################</p>
        <p>Quantidade de veiculos que tem pendencias: {qtdVeiculosSucesso}</p>
        <p>###########################################################</p>
        """
        message = MIMEMultipart()
        message["From"] = sender_mail
        message["To"] = ", ".join(destinatarios)  # Concatena os destinatários em uma string separada por vírgulas
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        server = smtplib.SMTP(server_smtp, port)
        server.starttls()
        server.login(sender_mail, password)
        server.sendmail(sender_mail, destinatarios, message.as_string())  # Passa a lista de destinatários
        print('--------------------------------')
        print('Email error enviado com sucesso')
        print('--------------------------------')

        server.quit()
    except Exception as e:
        print(f'Ocorreu um erro: {e}')
    return

def enviar_temp_exc(finalPlaca,qtdVeiculos,qtdVeiculosErro,qtdVeiculosSucesso,qtdVeiculosSDebito):
    try:
        server_smtp = "smtp-lob.office365.com"
        port = 587
        sender_mail = "rpa@bomfuturo.com.br"
        password = "7BchvtSg0ZV6"

        subject = "TEMPO EXECUÇÃO ELEVADO"
        body = f"""\
        <h1>O robo de Multas terminou a execução</h1>>
        <p>Final de placa: {finalPlaca}</p>
        <p></p>
        <p>###########################################################</p>
        <p>Quantidade total de veiculos que rodaram: {qtdVeiculos}</p>
        <p>###########################################################</p>
        <p>Quantidade de veiculos que deram erro: {qtdVeiculosErro}</p>
        <p>###########################################################</p>
        <p>Quantidade de veiculos sem debito: {qtdVeiculosSDebito}</p>
        <p>###########################################################</p>
        <p>Quantidade de veiculos que tem pendencias: {qtdVeiculosSucesso}</p>
        <p>###########################################################</p>
        """
        message = MIMEMultipart()
        message["From"] = sender_mail
        message["To"] = ", ".join(destinatarios)  # Concatena os destinatários em uma string separada por vírgulas
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        server = smtplib.SMTP(server_smtp, port)
        server.starttls()
        server.login(sender_mail, password)
        server.sendmail(sender_mail, destinatarios, message.as_string())  # Passa a lista de destinatários
        print('--------------------------------')
        print('Email tempo enviado com sucesso')
        print('--------------------------------')
        server.quit()
    except Exception as e:
        print(f'Ocorreu um erro: {e}')
    return


if __name__ == "__main__":
    ResultadoErro()
    ResultadoFinalEmail('','','','','','')