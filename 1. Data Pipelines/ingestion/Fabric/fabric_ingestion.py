"""
Envia um pandas DataFrame para uma tabela Delta no Fabric Lakehouse.
Cria sessão Spark com suporte Delta e grava a tabela configurada em overwrite.

Author: Gustavo F. Lima
License: MIT
Created: 2025
"""

# Para instalar as dependências necessárias, use o seguinte comando:
# pip install pyspark delta-spark pandas

import os
import warnings
from pyspark.sql import SparkSession

# Opcional: suprimir warnings
warnings.filterwarnings("ignore", category=UserWarning)

# =========================================================
# 1. Configurações via variáveis de ambiente
# =========================================================
FABRIC_WORKSPACE = os.getenv("FABRIC_WORKSPACE")
FABRIC_LAKEHOUSE = os.getenv("FABRIC_LAKEHOUSE")
FABRIC_TABLE = os.getenv("FABRIC_TABLE")

if not all([FABRIC_WORKSPACE, FABRIC_LAKEHOUSE, FABRIC_TABLE]):
    raise ValueError(
        "Variáveis de ambiente do Fabric não estão completamente definidas. "
        "Verifique: FABRIC_WORKSPACE, FABRIC_LAKEHOUSE, FABRIC_TABLE"
    )

# =========================================================
# 2. Inicializar Spark com suporte a Delta
# =========================================================
spark = (
    SparkSession.builder
    .appName("Fabric Ingestion")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .getOrCreate()
)

# =========================================================
# 3. Converter pandas DataFrame para Spark DataFrame
# =========================================================
spark_df = spark.createDataFrame(df_final_pandas)

# =========================================================
# 4. Caminho da tabela no OneLake (Lakehouse)
# =========================================================
table_path = (
    f"/lakehouse/default/"
    f"Tables/{FABRIC_TABLE}"
)

# =========================================================
# 5. Gravar dados (overwrite = truncate)
# =========================================================
(
    spark_df
    .write
    .format("delta")
    .mode("overwrite")  # equivalente ao WRITE_TRUNCATE
    .save(table_path)
)

# =========================================================
# 6. Mensagem genérica de sucesso
# =========================================================
print("✅ **Tabela carregada com sucesso!** 🚀")
