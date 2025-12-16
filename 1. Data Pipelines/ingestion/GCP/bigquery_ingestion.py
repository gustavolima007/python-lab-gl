# Para instalar as dependências necessárias, use o seguinte comando:
# pip install google-cloud-bigquery google-auth

from google.cloud import bigquery
from google.oauth2 import service_account
import warnings
import os

# Opcional: Suprimir o aviso sobre o BigQuery Storage
warnings.filterwarnings("ignore", category=UserWarning)

# 1. Configurar autenticação - carregar chave de serviço a partir de uma variável de ambiente
credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if credentials_path is None:
    raise ValueError("A variável de ambiente 'GOOGLE_APPLICATION_CREDENTIALS' não está definida. Por favor, defina o caminho para o arquivo JSON da chave de serviço.")

credentials = service_account.Credentials.from_service_account_file(credentials_path)

# 2. Inicializar o cliente BigQuery
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# 3. Nome dos datasets e tabelas
dataset_id = 'LAND'

# 4. Configurar o job para sobrescrever as tabelas
job_config = bigquery.LoadJobConfig(
    write_disposition="WRITE_TRUNCATE",  # Sobrescreve a tabela se ela já existir
)

# 5. Carregar df_final_pandas para LAND.importacao_xml_v1
table_id = f"{credentials.project_id}.{dataset_id}.importacao_xml_v1"
job = client.load_table_from_dataframe(df_final_pandas, table_id, job_config=job_config)
job.result()  # Espera o job terminar

# Mensagem genérica de sucesso
print("✅ **Tabela carregada com sucesso!** 🚀")
