"""
API para extração de TODAS as categorias do GLPI.

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

CSV_PATH = os.path.join(DATA_DIR, "glpi_categorias.csv")

CSV_FIELDS = [
    "categoria",
    "entidade",
    "grupo",
    "visivel_interface_simplificada",
    "visivel_incidente",
    "visivel_requisicao",
    "visivel_problema",
    "visivel_mudanca",
    "codigo_chamado",
    "id",
]

# =========================================================
# UTILS
# =========================================================

def bool_to_sim_nao(v):
    if v in (1, "1", True):
        return "sim"
    return "nao"

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

    categorias = []
    start = 0
    total: Optional[int] = None

    try:
        print("Extraindo categorias do GLPI...\n")

        while True:
            end = start + PAGE_SIZE - 1

            resp = requests.get(
                f"{GLPI_URL}/ITILCategory",
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

            # Total real
            if total is None:
                cr = resp.headers.get("Content-Range", "")
                if "/" in cr:
                    try:
                        total = int(cr.split("/", 1)[1])
                    except:
                        pass

            for c in batch:
                categorias.append({
                    "categoria": c.get("name"),
                    "entidade": c.get("entities_id"),
                    "grupo": c.get("groups_id"),
                    "visivel_interface_simplificada": bool_to_sim_nao(c.get("is_helpdeskvisible")),
                    "visivel_incidente": bool_to_sim_nao(c.get("is_incident")),
                    "visivel_requisicao": bool_to_sim_nao(c.get("is_request")),
                    "visivel_problema": bool_to_sim_nao(c.get("is_problem")),
                    "visivel_mudanca": bool_to_sim_nao(c.get("is_change")),
                    "codigo_chamado": c.get("code"),
                    "id": c.get("id"),
                })

            start += len(batch)

            if total:
                print(f"{start}/{total} categorias")
            else:
                print(f"{start} categorias")

        print(f"\nTotal extraído: {len(categorias)}")

        # -------------------------
        # CSV
        # -------------------------
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(categorias)

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
