"""
API para extração de TODOS os usuários do GLPI.

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

CSV_PATH = os.path.join(DATA_DIR, "glpi_usuarios.csv")

CSV_FIELDS = [
    "usuario",
    "ultimo_nome",
    "email",
    "celular",
    "localizacao",
    "ativo",
    "grupos",
    "nome",
    "numero_adm",
    "entidade_padrao",
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

    usuarios = []
    start = 0
    total: Optional[int] = None

    try:
        print("Extraindo usuários do GLPI...\n")

        while True:
            end = start + PAGE_SIZE - 1

            resp = requests.get(
                f"{GLPI_URL}/User",
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

            for u in batch:
                usuarios.append({
                    "usuario": u.get("name"),
                    "ultimo_nome": u.get("realname"),
                    "email": u.get("email"),
                    "celular": u.get("mobile"),
                    "localizacao": u.get("locations_id"),
                    "ativo": bool_to_sim_nao(u.get("is_active")),
                    "grupos": u.get("groups_id"),
                    "nome": u.get("firstname"),
                    "numero_adm": u.get("registration_number"),
                    "entidade_padrao": u.get("entities_id"),
                    "id": u.get("id"),
                })

            start += len(batch)

            if total:
                print(f"{start}/{total} usuários")
            else:
                print(f"{start} usuários")

        print(f"\nTotal extraído: {len(usuarios)}")

        # -------------------------
        # CSV
        # -------------------------
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(usuarios)

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
