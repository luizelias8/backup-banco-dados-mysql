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
with open(caminho_configuracoes, 'r', encoding='utf-8') as arquivo_configuracoes:
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

def criar_email_html(mensagem, sucesso=True):
    """
    Cria um template HTML estilizado para o e-mail

    Args:
        mensagem (str): Mensagem a ser incluída no corpo do e-mail
        sucesso (bool): Indica se o backup foi bem-sucedido

    Returns:
        str: Corpo do e-mail em HTML
    """
    status_texto = 'Sucesso' if sucesso else 'Falha'
    cor_cabecalho = '#4CAF50' if sucesso else '#F44336' # Verde para sucesso, Vermelho para falha

    # Template HTML com estilos CSS embutidos
    template_html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Relatório de Backup</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="border: 1px solid #ddd; border-radius: 5px; overflow: hidden;">
            <!-- Cabeçalho -->
            <div style="background-color: {cor_cabecalho}; color: white; padding: 15px; text-align: center;">
                <h1 style="margin: 0; font-size: 24px;">Relatório de Backup - {status_texto}</h1>
            </div>

            <!-- Conteúdo -->
            <div style="padding: 20px;">
                <p style="margin-top: 0;"><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                <p><strong>Status:</strong> {status_texto}</p>

                <div style="background-color: #f9f9f9; border-left: 4px solid {cor_cabecalho}; padding: 15px; margin: 15px 0;">
                    <p style="margin: 0;">{mensagem}</p>
                </div>

                <p style="margin-bottom: 0;">Para mais detalhes, consulte o arquivo de log.</p>
            </div>

            <!-- Rodapé -->
            <div style="background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #777;">
                <p style="margin: 0;">Este é um e-mail automático. Por favor, não responda a esta mensagem.</p>
                <p style="margin: 5px 0 0 0;">Sistema de Backup Automático de Banco de Dados</p>
            </div>
        </div>
    </body>
    </html>
    """

    return template_html

def enviar_email(mensagem, sucesso=True):
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = email_remetente
        msg['To'] = email_destinatario
        msg['Subject'] = assunto

        # Cria a versão HTML do e-mail
        html = criar_email_html(mensagem, sucesso)

        # Anexa o conteúdo HTML ao e-mail
        msg.attach(MIMEText(html, 'html'))

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
