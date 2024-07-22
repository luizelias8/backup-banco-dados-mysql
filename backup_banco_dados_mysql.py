import os
import json
from datetime import datetime
import subprocess

# Variável para armazenar o diretório do script
diretorio_script = os.path.dirname(os.path.abspath(__file__))

# Lê as configurações do arquivo configuracoes.cfg
caminho_configuracoes = os.path.join(diretorio_script, 'configuracoes.json')
with open(caminho_configuracoes, 'r') as arquivo_configuracoes:
    configuracoes = json.load(arquivo_configuracoes)

# Recupera os valores das configurações
host = configuracoes['mysql']['host']
usuario = configuracoes['mysql']['usuario']
senha = configuracoes['mysql']['senha']
banco_dados = configuracoes['mysql']['banco_dados']
diretorio_backup = configuracoes['backup'].get('diretorio_backup', '').strip()

# Define o diretório de salvamento
if not diretorio_backup:
    diretorio_backup = diretorio_script

# Cria o diretório se ele não existir
if not os.path.exists(diretorio_backup):
    os.makedirs(diretorio_backup)

# Define o nome do arquivo de backup com base na data e hora atuais
arquivo_backup = os.path.join(diretorio_backup, f"{banco_dados}_backup_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.sql")

# Constrói o comando mysqldump
comando_dump = [
    'mysqldump',
    '--host', host,
    '--user', usuario,
    f'--password={senha}',
    banco_dados,
    '--result-file', arquivo_backup
]

# Executa o comando mysqldump
try:
    resultado = subprocess.run(comando_dump, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(f"Backup concluído com sucesso. Arquivo salvo como {arquivo_backup}")
except subprocess.CalledProcessError as e:
    print(f"Erro ao fazer o backup: {e.stderr}")