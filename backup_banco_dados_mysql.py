import os
import json
from datetime import datetime
import subprocess
import zipfile
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Variável para armazenar o diretório do script
diretorio_script = os.path.dirname(os.path.abspath(__file__))

# Configuração do log
arquivo_log = os.path.join(diretorio_script, 'backup.log')
logging.basicConfig(
    filename=arquivo_log,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    encoding='utf-8'
)

# Lê as configurações do arquivo configuracoes.cfg
caminho_configuracoes = os.path.join(diretorio_script, 'configuracoes.json')
with open(caminho_configuracoes, 'r') as arquivo_configuracoes:
    configuracoes = json.load(arquivo_configuracoes)

# Recupera os valores das configurações
host = configuracoes['mysql']['host']
usuario = configuracoes['mysql']['usuario']
senha = configuracoes['mysql']['senha']
bancos_dados = configuracoes['mysql']['bancos_dados']
diretorio_backup = configuracoes['backup'].get('diretorio_backup', '').strip()

# Configuração do e-mail
servidor_smtp = configuracoes['email']['servidor_smtp']
porta_smtp = configuracoes['email']['porta_smtp']
usuario_smtp = configuracoes['email']['usuario_smtp']
senha_smtp = configuracoes['email']['senha_smtp']
email_remetente = configuracoes['email']['email_remetente']
email_destinatario = configuracoes['email']['email_destinatario']
assunto = configuracoes['email']['assunto']

# Define o diretório de salvamento
if not diretorio_backup:
    diretorio_backup = diretorio_script

# Cria o diretório se ele não existir
if not os.path.exists(diretorio_backup):
    os.makedirs(diretorio_backup)
    logging.info(f"Diretório de backup criado: {diretorio_backup}")

def enviar_email(mensagem):
    try:
        msg = MIMEMultipart()
        msg['From'] = email_remetente
        msg['To'] = email_destinatario
        msg['Subject'] = assunto

        msg.attach(MIMEText(mensagem, 'plain'))

        with smtplib.SMTP(servidor_smtp, porta_smtp) as servidor:
            servidor.starttls()
            servidor.login(usuario_smtp, senha_smtp)
            servidor.sendmail(email_remetente, email_destinatario, msg.as_string())
        logging.info(f"E-mail enviado para {email_destinatario}")
    except Exception as e:
        logging.error(f"Erro ao enviar e-mail: {str(e)}")

# Itera sobre a lista de bancos de dados e realiza o backup
for banco_dados in bancos_dados:
    # Define o nome do arquivo de backup com base na data e hora atuais
    arquivo_backup = os.path.join(diretorio_backup, f"{banco_dados}_backup_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.sql")
    arquivo_zip = arquivo_backup + '.zip'

    # Constrói o comando mysqldump
    comando_dump = [
        'mysqldump',
        '--host', host,
        '--user', usuario,
        f'--password={senha}',
        banco_dados,
        '--result-file', arquivo_backup
    ]

    logging.info(f"Iniciando backup do banco de dados '{banco_dados}' com comando: {' '.join(comando_dump)}")

    # Executa o comando mysqldump
    try:
        resultado = subprocess.run(comando_dump, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.info(f"Backup do banco de dados '{banco_dados}' concluído com sucesso. Arquivo salvo como {arquivo_backup}")

        # Compacta o arquivo de backup em .zip
        with zipfile.ZipFile(arquivo_zip, 'w', zipfile.ZIP_DEFLATED) as arquivo_zip:
            arquivo_zip.write(arquivo_backup, os.path.basename(arquivo_backup))
        logging.info(f"Arquivo de backup compactado como {arquivo_zip}")

        # Remove o arquivo SQL não compactado
        os.remove(arquivo_backup)
        logging.info(f"Arquivo SQL não compactado removido: {arquivo_backup}")

        # Envia e-mail de sucesso
        mensagem_email = f"O backup do banco de dados '{banco_dados}' foi concluído com sucesso. Arquivo compactado: {arquivo_zip}"
        enviar_email(mensagem_email)

    except subprocess.CalledProcessError as e:
        mensagem_erro = f"Erro ao fazer o backup do banco de dados '{banco_dados}': {e.stderr}"
        logging.error(mensagem_erro)
        enviar_email(mensagem_erro)
    except Exception as e:
        mensagem_erro = f"Erro inesperado ao processar o banco de dados '{banco_dados}': {str(e)}"
        logging.error(mensagem_erro)
        enviar_email(mensagem_erro)