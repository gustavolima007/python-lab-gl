"""
API para extração de TODAS as GMUDs (Mudanças) do GLPI.

Autor: Gustavo F. Lima
Licença: MIT
Criado: 2026
"""

import os
import csv
import requests
from typing import Optional

# =========================================================
# ENV
# =========================================================

def load_env(path=".env"):
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(".env")

GLPI_URL = os.environ["GLPI_URL"].rstrip("/")
APP_TOKEN = os.environ["GLPI_APP_TOKEN"]
USER_TOKEN = os.environ["GLPI_USER_TOKEN"]

# =========================================================
# CONFIG
# =========================================================

PAGE_SIZE = 200

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DATA_DIR = os.path.join(ROOT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

CSV_PATH = os.path.join(DATA_DIR, "glpi_mudancas.csv")

CSV_FIELDS = [
    "id",
    "titulo",
    "entidade",
    "status",
    "ultima_atualizacao",
    "requerente_id",
    "data_abertura",
    "categoria",
    "tempo_para_solucao",
    "aprovacao_status",
    "aprovador_id",
    "data_aprovacao",
]

# =========================================================
# DICIONÁRIOS
# =========================================================

CHANGE_STATUS = {
    1: "novo",
    2: "avaliacao",
    3: "aprovacao",
    4: "planejado",
    5: "em_execucao",
    6: "concluido",
    7: "cancelado",
}

VALIDATION_STATUS = {
    0: "nao_sujeita",
    1: "aguardando",
    2: "recusada",
    3: "concedida",
}

# =========================================================
# MAIN
# =========================================================

def main():
    # -------------------------
    # Init session
    # -------------------------
    init_headers = {
        "Content-Type": "application/json",
        "App-Token": APP_TOKEN,
        "Authorization": f"user_token {USER_TOKEN}",
    }

    r = requests.get(f"{GLPI_URL}/initSession", headers=init_headers, timeout=30)
    r.raise_for_status()
    session_token = r.json()["session_token"]

    headers = {
        "Content-Type": "application/json",
        "App-Token": APP_TOKEN,
        "Session-Token": session_token,
    }

    mudancas = []
    start = 0
    total: Optional[int] = None

    try:
        print("Extraindo GMUDs do GLPI...\n")

        while True:
            end = start + PAGE_SIZE - 1

            resp = requests.get(
                f"{GLPI_URL}/Change",
                headers=headers,
                params={"range": f"{start}-{end}"},
                timeout=60,
            )

            if resp.status_code == 400 and "ERROR_RANGE_EXCEED_TOTAL" in resp.text:
                break

            if resp.status_code not in (200, 206):
                print(resp.text)
                resp.raise_for_status()

            batch = resp.json()
            if not batch:
                break

            if total is None:
                cr = resp.headers.get("Content-Range", "")
                if "/" in cr:
                    try:
                        total = int(cr.split("/", 1)[1])
                    except:
                        pass

            for c in batch:
                mudancas.append({
                    "id": c.get("id"),
                    "titulo": c.get("name"),
                    "entidade": c.get("entities_id"),
                    "status": CHANGE_STATUS.get(int(c.get("status", 0)), "desconhecido"),
                    "ultima_atualizacao": c.get("date_mod"),
                    "requerente_id": c.get("users_id_recipient"),
                    "data_abertura": c.get("date"),
                    "categoria": c.get("itilcategories_id"),
                    "tempo_para_solucao": c.get("time_to_resolve"),
                    "aprovacao_status": VALIDATION_STATUS.get(
                        int(c.get("global_validation", 0)), "desconhecido"
                    ),
                    "aprovador_id": c.get("validation_users_id"),
                    "data_aprovacao": c.get("validation_date"),
                })

            start += len(batch)

            if total:
                print(f"{start}/{total} mudanças")
            else:
                print(f"{start} mudanças")

        print(f"\nTotal extraído: {len(mudancas)}")

        # -------------------------
        # CSV
        # -------------------------
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(mudancas)

        print(f"CSV gerado em: {CSV_PATH}")

    finally:
        # -------------------------
        # Kill session
        # -------------------------
        try:
            requests.get(
                f"{GLPI_URL}/killSession",
                headers={
                    "Content-Type": "application/json",
                    "App-Token": APP_TOKEN,
                    "Session-Token": session_token,
                },
                timeout=15,
            )
        except:
            pass


if __name__ == "__main__":
    main()