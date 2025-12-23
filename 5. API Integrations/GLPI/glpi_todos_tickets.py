"""
API para extração de todos os chamados do GLPI, filtrando por categorias específicas.

Author: Gustavo F. Lima
License: MIT
Created: 2025
"""

import os
import json
import csv
import requests

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

# .env na raiz do projeto
load_env(".env")

GLPI_URL = os.environ["GLPI_URL"].rstrip("/")
APP_TOKEN = os.environ["GLPI_APP_TOKEN"]
USER_TOKEN = os.environ["GLPI_USER_TOKEN"]

STATUS_MAP = {
    1: "Novo",
    2: "Em atendimento (atribuído)",
    3: "Em atendimento (planejado)",
    4: "Pendente",
    5: "Solucionado",
    6: "Fechado",
}

# =========================
# FILTRO DE CATEGORIAS (HML)
# =========================
CATEGORY_DISPLAY = 2   # TV sem conteúdo
CATEGORY_STATUS  = 3   # Player offline/desatualizado

ALLOWED_CATEGORIES = {CATEGORY_DISPLAY, CATEGORY_STATUS}

# Se for PRD, troque para:
# CATEGORY_DISPLAY = 464
# CATEGORY_STATUS  = 465
# ALLOWED_CATEGORIES = {CATEGORY_DISPLAY, CATEGORY_STATUS}

# Ajustes
PAGE_SIZE = 200
PRINT_EACH = True
SAVE_JSON = False
SAVE_CSV = True

def main():
    # 1) init session
    init_url = f"{GLPI_URL}/initSession"
    init_headers = {
        "Content-Type": "application/json",
        "App-Token": APP_TOKEN,
        "Authorization": f"user_token {USER_TOKEN}",
    }
    r = requests.get(init_url, headers=init_headers, timeout=30)
    r.raise_for_status()
    session_token = r.json()["session_token"]

    headers = {
        "Content-Type": "application/json",
        "App-Token": APP_TOKEN,
        "Session-Token": session_token,
    }

    tickets_all = []  # só se SAVE_JSON=True
    csv_file = None
    csv_writer = None

    try:
        if SAVE_CSV:
            csv_file = open("tickets_filtrados.csv", "w", newline="", encoding="utf-8")
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([
                "id",
                "itilcategories_id",
                "status_code",
                "status_label",
                "name",
                "date_creation",
                "date_mod",
            ])

        start = 0

        while True:
            end = start + PAGE_SIZE - 1
            url = f"{GLPI_URL}/Ticket/"
            params = {"range": f"{start}-{end}"}

            resp = requests.get(url, headers=headers, params=params, timeout=60)

            # ✅ Oculta erro específico de range (encerra o loop)
            if resp.status_code == 400 and "ERROR_RANGE_EXCEED_TOTAL" in resp.text:
                break

            if resp.status_code >= 400:
                print(f"Erro ao listar tickets ({resp.status_code}): {resp.text}")
                resp.raise_for_status()

            batch = resp.json()
            if not batch:
                break

            for t in batch:
                # ✅ ID real do ticket (não é índice do loop)
                tid = t.get("id")

                # ✅ categoria do ticket
                cat_id = t.get("itilcategories_id")

                # ✅ aplica filtro: só categorias 2 e 3 (ou 464/465 no PRD)
                if cat_id not in ALLOWED_CATEGORIES:
                    continue

                sc = int(t.get("status", -1))
                sl = STATUS_MAP.get(sc, f"Desconhecido({sc})")
                name = t.get("name")
                dc = t.get("date_creation")
                dm = t.get("date_mod")

                if PRINT_EACH:
                    print(f"{tid} | cat={cat_id} | {sl} | {name}")

                if SAVE_CSV and csv_writer:
                    csv_writer.writerow([tid, cat_id, sc, sl, name, dc, dm])

                if SAVE_JSON:
                    tickets_all.append(t)

            # ✅ última página
            if len(batch) < PAGE_SIZE:
                break

            start += PAGE_SIZE

        print("\n✅ Finalizado: tickets filtrados pelas categorias foram coletados.")
        if SAVE_CSV:
            print("📄 CSV gerado: tickets_filtrados.csv")
        if SAVE_JSON:
            with open("tickets_filtrados.json", "w", encoding="utf-8") as f:
                json.dump(tickets_all, f, ensure_ascii=False, indent=2)
            print("📄 JSON gerado: tickets_filtrados.json")

    finally:
        if csv_file:
            csv_file.close()

        # 3) kill session
        kill_url = f"{GLPI_URL}/killSession"
        kill_headers = {
            "Content-Type": "application/json",
            "App-Token": APP_TOKEN,
            "Session-Token": session_token,
        }
        try:
            requests.get(kill_url, headers=kill_headers, timeout=15)
        except Exception:
            pass

if __name__ == "__main__":
    main()

