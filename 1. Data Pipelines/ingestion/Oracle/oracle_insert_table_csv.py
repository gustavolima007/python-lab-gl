"""
Lê um CSV local e envia o conteúdo para uma tabela no Oracle.
Conecta via SQLAlchemy/oracledb e usa if_exists replace para sobrescrever.

Author: Gustavo F. Lima
License: MIT
Created: 2025
"""

# pip install oracledb pandas sqlalchemy

import os
import pandas as pd
from sqlalchemy import create_engine

# Ler CSV
df_final_pandas = pd.read_csv("dados.csv")

# Oracle (env vars)
engine = create_engine(
    f"oracle+oracledb://{os.getenv('ORACLE_USER')}:{os.getenv('ORACLE_PASSWORD')}"
    f"@{os.getenv('ORACLE_HOST')}:{os.getenv('ORACLE_PORT', '1521')}"
    f"/?service_name={os.getenv('ORACLE_SERVICE')}"
)

# Enviar para Oracle
df_final_pandas.to_sql(
    name="NOME_TABELA",
    con=engine,
    schema="LAND",
    if_exists="replace",
    index=False
)

print("✅ **Tabela carregada com sucesso!** 🚀")
