import os
import json

# Variável para armazenar o diretório do script
diretorio_script = os.path.dirname(os.path.abspath(__file__))

# Lê as configurações do arquivo configuracoes.json
caminho_configuracoes = os.path.join(diretorio_script, 'configuracoes.json')

# Carrega configurações
with open(caminho_configuracoes, 'r') as arquivo_configuracoes:
    configuracoes = json.load(arquivo_configuracoes)

# Recupera o diretório de backup e o número máximo de backups
diretorio_backup = configuracoes['backup'].get('diretorio_backup', '')
numero_maximo_backups = configuracoes['backup'].get('numero_maximo_backups', 5)

if not diretorio_backup:
    print('Diretório de backup não especificado nas configurações.')
    exit()

if not os.path.exists(diretorio_backup):
    print(f"Diretório de backup não encontrado: {diretorio_backup}")
    exit()

# Lista de arquivos no diretório de backup
arquivos = [os.path.join(diretorio_backup, f) for f in os.listdir(diretorio_backup) if os.path.isfile(os.path.join(diretorio_backup, f))]

# Filtra arquivos SQL e ZIP
arquivos_backup = [f for f in arquivos if f.endswith('.sql') or f.endswith('.zip')]

# Ordena os arquivos por data de modificação, mais recentes primeiro
arquivos_backup.sort(key=lambda x: os.path.getmtime(x), reverse=True)

# Verifica se o número de arquivos excede o máximo permitido
if len(arquivos_backup) > numero_maximo_backups:
    # Remove arquivos antigos, mantendo apenas os mais recentes
    arquivos_para_remover = arquivos_backup[numero_maximo_backups:]
    for arquivo in arquivos_para_remover:
        os.remove(arquivo)
        print(f'Backup removido: {arquivo}')