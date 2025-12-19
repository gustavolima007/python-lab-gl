"""
Registra um evento único no BigQuery via insert_rows_json com credenciais em base64.
Carrega o serviço do GCP e publica o log de status para a tabela logs_processos_python.

Author: Gustavo F. Lima
License: MIT
Created: 2025
"""

import base64
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from google.cloud import bigquery
from google.oauth2 import service_account

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(os.path.dirname(ROOT_DIR), ".env")
UTC_MINUS_3 = timezone(timedelta(hours=-3))


def _load_env_value(path: str, key: str) -> str:

    if not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            name, _, value = line.partition("=")
            if name.strip() == key:
                return value.strip()
    return ""


GCP_SERVICE_ACCOUNT_JSON_B64 = _load_env_value(ENV_PATH, "GCP_SERVICE_ACCOUNT_JSON_B64")
if not GCP_SERVICE_ACCOUNT_JSON_B64:
    raise ValueError("GCP_SERVICE_ACCOUNT_JSON_B64 not found in .env")

credentials_json = json.loads(base64.b64decode(GCP_SERVICE_ACCOUNT_JSON_B64).decode("utf-8"))
credentials = service_account.Credentials.from_service_account_info(credentials_json)

PROJECT_ID = "analytics-prd"
DATASET_ID = "REFINED"
TABLE_LOGS = "logs_processos_python" # Nome da tabela no GCP
PROCESSO = "repo-modelo" # Nome do repositorio ou do processo
TIPO = "python_script" # Tipo do processo

client = bigquery.Client(project=PROJECT_ID, credentials=credentials)


def enviar_log(
    status: str,
    mensagem: str,
    dt_inicio: Optional[datetime] = None,
    dt_fim: Optional[datetime] = None,
) -> None:

    base_ts = datetime.now(UTC_MINUS_3)
    dt_inicio = dt_inicio or base_ts
    dt_fim = dt_fim or base_ts

    # A tabela do GCP tem que ter essas colunas
    row = {
        "processo": PROCESSO,
        "tipo": TIPO,
        "status": status,
        "mensagem": mensagem,
        "dt_inicio": dt_inicio.isoformat(),
        "dt_fim": dt_fim.isoformat(),
    }

    table_id = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_LOGS}"
    errors = client.insert_rows_json(table_id, [row])
    if errors:
        raise RuntimeError(f"BigQuery insert_rows_json returned errors: {errors}")


if __name__ == "__main__":
    enviar_log("SUCESSO", "Log de exemplo criado para testes")
    print("Log enviado ao BigQuery com sucesso.")
