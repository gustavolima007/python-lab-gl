"""
Insere df_final_pandas em uma tabela SQL Server usando SQLAlchemy.
Substitui a tabela destino e aproveita fast_executemany para performance.

Author: Gustavo F. Lima
License: MIT
Created: 2025
"""

# Para instalar as dependências necessárias, use o seguinte comando:
# pip install pyodbc sqlalchemy pandas

import os
import warnings
from sqlalchemy import create_engine

# Opcional: suprimir warnings
warnings.filterwarnings("ignore", category=UserWarning)

# =========================================================
# 1. Configurações via variáveis de ambiente
# =========================================================
SQLSERVER_USER = os.getenv("SQLSERVER_USER")
SQLSERVER_PASSWORD = os.getenv("SQLSERVER_PASSWORD")
SQLSERVER_HOST = os.getenv("SQLSERVER_HOST")
SQLSERVER_PORT = os.getenv("SQLSERVER_PORT", "1433")
SQLSERVER_DATABASE = os.getenv("SQLSERVER_DATABASE")
SQLSERVER_DRIVER = os.getenv(
    "SQLSERVER_DRIVER",
    "ODBC Driver 18 for SQL Server"
)

if not all([SQLSERVER_USER, SQLSERVER_PASSWORD, SQLSERVER_HOST, SQLSERVER_DATABASE]):
    raise ValueError(
        "Variáveis de ambiente do SQL Server não estão completamente definidas. "
        "Verifique: SQLSERVER_USER, SQLSERVER_PASSWORD, "
        "SQLSERVER_HOST, SQLSERVER_DATABASE"
    )

# =========================================================
# 2. Criar conexão com SQL Server
# =========================================================
connection_url = (
    f"mssql+pyodbc://{SQLSERVER_USER}:{SQLSERVER_PASSWORD}"
    f"@{SQLSERVER_HOST}:{SQLSERVER_PORT}/{SQLSERVER_DATABASE}"
    f"?driver={SQLSERVER_DRIVER.replace(' ', '+')}"
    f"&Encrypt=yes&TrustServerCertificate=yes"
)

engine = create_engine(connection_url, fast_executemany=True)

# =========================================================
# 3. Configuração de schema e tabela
# =========================================================
schema_name = "dbo"
table_name = "NOME_TABELA"

# =========================================================
# 4. Carga do DataFrame no SQL Server
# =========================================================
df_final_pandas.to_sql(
    name=table_name,
    con=engine,
    schema=schema_name,
    if_exists="replace",   # equivalente ao WRITE_TRUNCATE
    index=False,
    chunksize=1000
)

# =========================================================
# 5. Mensagem genérica de sucesso
# =========================================================
print("✅ **Tabela carregada com sucesso!** 🚀")
