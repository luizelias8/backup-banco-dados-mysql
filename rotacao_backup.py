import os
import json

def carregar_configuracoes(caminho_configuracoes):
    """Carrega as configurações do arquivo JSON."""
    with open(caminho_configuracoes, 'r') as arquivo:
        return json.load(arquivo)

def verificar_diretorio_backup(diretorio_backup):
    """Verifica se o diretório de backup existe e retorna um erro se não existir."""
    if not diretorio_backup:
        raise ValueError('Diretório de backup não especificado nas configurações.')
    if not os.path.exists(diretorio_backup):
        raise FileNotFoundError(f"Diretório de backup não encontrado: {diretorio_backup}")

def listar_arquivos_backup(diretorio_backup):
    """Lista e filtra arquivos de backup no diretório especificado."""
    arquivos = [os.path.join(diretorio_backup, f) for f in os.listdir(diretorio_backup) if os.path.isfile(os.path.join(diretorio_backup, f))]
    return [f for f in arquivos if f.endswith('.sql') or f.endswith('.zip')]

def remover_arquivos_antigos(arquivos_backup, numero_maximo_backups):
    """Remove arquivos de backup antigos, mantendo apenas os mais recentes."""
    arquivos_backup_ordenados = sorted(arquivos_backup, key=lambda x: os.path.getmtime(x))
    if len(arquivos_backup) > numero_maximo_backups:
        arquivos_para_remover = arquivos_backup_ordenados[:len(arquivos_backup_ordenados) - numero_maximo_backups]
        for arquivo in arquivos_para_remover:
            os.remove(arquivo)
            print(f'Backup removido: {arquivo}')

def main():
    """Função principal do script."""
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    caminho_configuracoes = os.path.join(diretorio_script, 'configuracoes.json')

    # Carregar as configurações
    # carregar
    configuracoes = carregar_configuracoes(caminho_configuracoes)
    diretorio_backup = configuracoes['backup'].get('diretorio_backup', '')
    numero_maximo_backups = configuracoes['backup'].get('numero_maximo_backups', 5)

    try:
        verificar_diretorio_backup(diretorio_backup)
        arquivos_backup = listar_arquivos_backup(diretorio_backup)
        remover_arquivos_antigos(arquivos_backup, numero_maximo_backups)
    except (ValueError, FileNotFoundError) as e:
        print(e)
        exit()

if __name__ == '__main__':
    main()