"""
API para extração dos COMPUTADORES do GLPI.

Autor: Gustavo F. Lima
Licença: MIT
Criado: 2026
"""

import os
import csv
import requests

# ==============================
# Carrega variáveis do .env
# ==============================
def load_env():
    if not os.path.exists(".env"):
        raise RuntimeError("Arquivo .env não encontrado na raiz do projeto")

    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ[k] = v

load_env()

# ==============================
# Configurações
# ==============================
GLPI_URL = os.environ["GLPI_URL"].rstrip("/")
APP_TOKEN = os.environ["GLPI_APP_TOKEN"]
USER_TOKEN = os.environ["GLPI_USER_TOKEN"]

CSV_PATH = "data/glpi_computadores.csv"
PAGE_SIZE = 200

FIELDS = [
    "id", "tipo_ativo", "nome", "entidade", "localizacao", "categoria",
    "fabricante", "modelo", "numero_serie", "patrimonio",
    "status", "usuario", "data_compra", "data_garantia", "data_fim_garantia"
]

# ==============================
# Paginação GLPI
# ==============================
def get_all(endpoint, headers):
    start = 0
    data = []

    while True:
        r = requests.get(
            f"{GLPI_URL}/{endpoint}",
            headers=headers,
            params={"range": f"{start}-{start + PAGE_SIZE - 1}"}
        )

        if r.status_code == 400:
            break

        batch = r.json()
        if not batch:
            break

        data.extend(batch)
        start += len(batch)

    return data

# ==============================
# Programa principal
# ==============================
def main():

    # Cria pasta data automaticamente
    os.makedirs("data", exist_ok=True)

    # Inicia sessão no GLPI
    session = requests.get(
        f"{GLPI_URL}/initSession",
        headers={
            "App-Token": APP_TOKEN,
            "Authorization": f"user_token {USER_TOKEN}"
        }
    ).json()["session_token"]

    headers = {
        "App-Token": APP_TOKEN,
        "Session-Token": session
    }

    ativos = []

    print("Extraindo COMPUTADORES...")

    for a in get_all("Computer", headers):
        ativos.append({
            "id": a.get("id"),
            "tipo_ativo": "computador",
            "nome": a.get("name"),
            "entidade": a.get("entities_id"),
            "localizacao": a.get("locations_id"),
            "categoria": a.get("itilcategories_id"),
            "fabricante": a.get("manufacturers_id"),
            "modelo": a.get("models_id"),
            "numero_serie": a.get("serial"),
            "patrimonio": a.get("otherserial"),
            "status": a.get("states_id"),
            "usuario": a.get("users_id"),
            "data_compra": a.get("buy_date"),
            "data_garantia": a.get("warranty_date"),
            "data_fim_garantia": a.get("warranty_end_date")
        })

    # Salva CSV
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(ativos)

    print(f"\nTotal de computadores: {len(ativos)}")
    print(f"CSV salvo em {CSV_PATH}")

    # Finaliza sessão
    requests.get(
        f"{GLPI_URL}/killSession",
        headers={"App-Token": APP_TOKEN, "Session-Token": session}
    )

# ==============================
if __name__ == "__main__":
    main()
