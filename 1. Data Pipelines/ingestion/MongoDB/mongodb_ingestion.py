"""
Substitui documentos na coleção MongoDB com os dados de df_final_pandas.
Limpa a coleção antes e converte o DataFrame em documentos para insert_many.

Author: Gustavo F. Lima
License: MIT
Created: 2025
"""

# Para instalar as dependências necessárias, use o seguinte comando:
# pip install pymongo pandas

import os
import warnings
from pymongo import MongoClient

# Opcional: suprimir warnings
warnings.filterwarnings("ignore", category=UserWarning)

# =========================================================
# 1. Configurações via variáveis de ambiente
# =========================================================
MONGO_URI = os.getenv("MONGO_URI")  # ex: mongodb://user:password@host:27017
MONGO_DATABASE = os.getenv("MONGO_DATABASE")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

if not all([MONGO_URI, MONGO_DATABASE, MONGO_COLLECTION]):
    raise ValueError(
        "Variáveis de ambiente do MongoDB não estão completamente definidas. "
        "Verifique: MONGO_URI, MONGO_DATABASE, MONGO_COLLECTION"
    )

# =========================================================
# 2. Criar conexão com MongoDB
# =========================================================
client = MongoClient(MONGO_URI)
db = client[MONGO_DATABASE]
collection = db[MONGO_COLLECTION]

# =========================================================
# 3. Limpar coleção (equivalente ao TRUNCATE)
# =========================================================
collection.delete_many({})

# =========================================================
# 4. Converter DataFrame para lista de documentos
# =========================================================
records = df_final_pandas.to_dict(orient="records")

if not records:
    raise ValueError("O DataFrame está vazio. Nenhum dado foi enviado ao MongoDB.")

# =========================================================
# 5. Inserir dados no MongoDB
# =========================================================
collection.insert_many(records)

# =========================================================
# 6. Mensagem genérica de sucesso
# =========================================================
print("✅ **Tabela carregada com sucesso!** 🚀")
