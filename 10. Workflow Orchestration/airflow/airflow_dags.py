"""
Dispara DAG no Composer via executeAirflowCommand da API do Google.
Autentica com service account e envia o comando 'dags trigger' com payload.

Author: Gustavo F. Lima
License: MIT
Created: 2025
"""

import json
import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests

def trigger_dag():
    """Dispara uma DAG no Cloud Composer via API oficial do Google."""
    PROJECT_ID = "analytics-prd"
    LOCATION = "us-east4"
    ENVIRONMENT = "analytics-prd-composer-v2"
    DAG_ID = "datamart_id"

    BASE_URL = f"https://composer.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/environments/{ENVIRONMENT}:executeAirflowCommand"

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "config", "prd-big-query.json")

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(Request())
    token = credentials.token

    payload = {
        "command": "dags",
        "subcommand": "trigger",
        "parameters": [DAG_ID]
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(BASE_URL, headers=headers, json=payload)

    if response.status_code in (200, 201):
        print("DAG disparada com sucesso!")
        return True
    else:
        print("Erro ao disparar DAG")
        # print("Status:", response.status_code)
        # print("Detalhes:", response.text)
        return False


def main():
    trigger_dag()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erro durante a execução principal. DAG não será disparada.\nDetalhes: {e}")
