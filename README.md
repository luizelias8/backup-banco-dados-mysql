# Script de Backup MySQL

Este projeto fornece um script Python para realizar backups de múltiplos bancos de dados MySQL. Os arquivos de backup são compactados no formato `.zip` para economizar espaço e facilitar o armazenamento e a transferência.

## Pré-requisitos

- Python 3.x
- MySQL (mysqldump deve estar instalado e disponível no PATH)

## Instalação

1. Clone o repositório para sua máquina local:
```
git clone https://github.com/luizelias8/backup-banco-dados-mysql.git
cd backup-banco-dados-mysql
```

## Uso

1. Configure o arquivo de configuração:

Copie o arquivo **configuracoes-exemplo.json** para **configuracoes.json** e ajuste os valores conforme necessário.

2. Execute o script de backup:
```
python backup_banco_dados_mysql.py
```

## Contribuição

Contribuições são bem-vindas!

## Autor

- [Luiz Elias](https://github.com/luizelias8)