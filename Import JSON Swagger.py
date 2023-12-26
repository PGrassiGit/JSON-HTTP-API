import requests #lidar com http api etc
import os #dir folders e arquivos etc
import json
import logging
from tkinter import *
from tkinter import Tk, filedialog # Import tkinter
import subprocess
# Função para abrir a box de selecionar a pasta
def seleciona_dir():
    root = Tk()
    root.withdraw()  
    folder_selected = filedialog.askdirectory(title="Selecione a Pasta com os arquivos")  # abre a box pra selecionar a pasta
    return folder_selected

base_url = ('url da api/swagger')

# MODULO DE ARQUIVO LOG
LOG = 'log_importacao.txt'
logging.basicConfig(filename=(f'{LOG}'), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',encoding='utf-8')
logging.info('Log de importação JSON')


####### Faz um teste de acesso na API
requisicao_teste = requests.get(f'{base_url}/api/Health/Check')
print ('Check de acesso')

# Se estiver ok retorna (status code 200)
if requisicao_teste.status_code == 200:
    print (f'API acessada: {requisicao_teste.status_code} - {requisicao_teste.text}')
    logging.info (f'API acessada: {requisicao_teste.status_code} - {requisicao_teste.text}')#log
else:
    # Se não, verificar acesso manualmente
    print(f"Error: {requisicao_teste.status_code} - {requisicao_teste.text}")
    logging.error(f'Teste de acesso: {requisicao_teste}')  # log do teste

######PARTE DE LOGIN E GERAÇÃO DE TOKEN#######
# Login
login_data = {
    "email": "login",
    "password": "senha"
}
# Faz um POST request para inserir os dados de login e extrair o token
login_response = requests.post(f'{base_url}/api/auth/login', json=login_data)

# Verifica se fez o login (status code 200)
if login_response.status_code == 200:    
    # Extrai e printa o token de acesso
    auth_token = login_response.text.strip('"')  # Verificar a necessidade das ' ""'
    print (f'Token Armazenado: {auth_token}')
    logging.info(f'Token Armazenado: {auth_token}') #log
    if auth_token:
        print(f'Token Utilizado: {auth_token}') 
        logging.info(f'Token Utilizado: {auth_token}') #log
     # Insere o token no campo de validação
        headers = {        
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',  # Ajustar se necessario
        }
    else:
        print("Token não encontrado nos HEADERS ou Responde Body")
        logging.error("Token não encontrado nos HEADERS ou Responde Body")
else:
    # Erros durante o Login/teste token
    print(f"Erro: {login_response.status_code} - {login_response.text}")
    logging.error(f"Erro: {login_response.status_code} - {login_response.text}") #log

######IMPORTAÇÃO#############SELECIONAR PASTA########
pasta_selecionada = seleciona_dir()

if pasta_selecionada:
    # lista todos arquivos do dir
    files = os.listdir(pasta_selecionada)  # lista os arquivos da pasta
    print(f'Arquivos listados: {files}')  # printa os arquivos da pasta
    logging.info(f'Arquivos listados: {files}') #log
    
    for file in files:
        file_path = os.path.join(pasta_selecionada, file)  # caminho de cada arquivo
        print(f'Caminho do arquivo {file}: {file_path}')
        logging.info(f'Caminho do arquivo {file}: {file_path}')
        # Verifica se é um arquivo válido
        if os.path.isfile(file_path):
            # Lê o contéudo do JSON
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    json_payload = json.load(file)

                    # Arquivos separados
                    if login_response.status_code == 200:
                        # Extrai o token lá de cima na parte de login
                        auth_token = login_response.text.strip('"')  # Verificar a necessidade das ' ""'

                        # Coloca o token novamente para autorizar a /importacao
                        headers = {
                            'Authorization': f'Bearer {auth_token}',
                            'Content-Type': 'application/json',  # Ajustar se necessário
                        }

                        # Faz um POST request com o conteúdo do JSON
                        import_response = requests.post(f'{base_url}/api/Import/import', json=json_payload, headers=headers)

                        # Verifica se foi importado com sucesso ou deu erro (status code 200)
                        if import_response.status_code == 200:
                            print(f"Arquivo '{file}' importado com sucesso. Response:")
                            print(import_response.json())
                            logging.info(f"Arquivo '{file}' importado com sucesso. Response:")
                            logging.info(import_response.json())
                        elif import_response.status_code == 400:
                            print(f"Importação do arquivo '{file}' falhou. Response:")
                            print(import_response.json())
                            logging.error(import_response.json())
                        else:
                            # Outros erros
                            print(f"Erro ao importar o arquivo '{file}': {import_response.status_code} - {import_response.text}")
                            logging.error(f"Erro ao importar o arquivo '{file}': {import_response.status_code} - {import_response.text}")

                # erro na leitura ou carregamento durante a lista de arquivos
                except json.JSONDecodeError as e:
                    print(f"Erro ao carregar o arquivo JSON '{file}': {e}")
                    logging.error(f"Erro ao carregar o arquivo JSON '{file}': {e}")
subprocess.run(["notepad.exe" if os.name == "nt" else "gedit", LOG])
os.startfile(LOG)