"""
API para extração de chamados do GLPI e exportação para CSV.

Author: Gustavo F. Lima
License: MIT
Created: 2025
"""
import os

import pandas as pd
import requests
from dotenv import load_dotenv

# ===============================
# CARREGA .ENV
# ===============================
load_dotenv()

GLPI_URL = os.getenv("GLPI_URL")
APP_TOKEN = os.getenv("GLPI_APP_TOKEN")
USER_TOKEN = os.getenv("GLPI_USER_TOKEN")

if not all([GLPI_URL, APP_TOKEN, USER_TOKEN]):
    raise RuntimeError("❌ Variáveis de ambiente do GLPI não configuradas.")

CSV_OUTPUT = "chamados_glpi.csv"

def to_int(value, default=0):
    """Parses an int safely."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def parse_int_list(name):
    """Reads a comma separated environment variable as ints."""
    value = os.getenv(name)
    if not value:
        return []
    cleaned = [part.strip() for part in value.split(",")]
    values = []
    for part in cleaned:
        if not part:
            continue
        try:
            values.append(int(part))
        except ValueError:
            continue
    return values

def parse_optional_int(name):
    """Returns an int from the environment or None."""
    value = os.getenv(name)
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None

CATEGORY_IDS = parse_int_list("GLPI_CATEGORY_IDS") or parse_int_list("GLPI_CATEGORY_ID")
REQUESTER_ID = parse_optional_int("GLPI_REQUESTER_ID")
GROUP_ASSIGN_ID = parse_optional_int("GLPI_GROUP_ASSIGN_ID")

HEADERS = {
    "Content-Type": "application/json",
    "App-Token": APP_TOKEN,
    "Authorization": f"user_token {USER_TOKEN}"
}


def ticket_matches_filters(ticket):
    """Checks whether a ticket satisfies the optional filters."""
    if CATEGORY_IDS:
        if to_int(ticket.get("itilcategories_id")) not in CATEGORY_IDS:
            return False
    if REQUESTER_ID is not None:
        if to_int(ticket.get("users_id_recipient")) != REQUESTER_ID:
            return False
    if GROUP_ASSIGN_ID is not None:
        if to_int(ticket.get("groups_id_assign")) != GROUP_ASSIGN_ID:
            return False
    return True

# ===============================
# SESSÃO
# ===============================
def init_session():
    r = requests.get(f"{GLPI_URL}/initSession", headers=HEADERS)
    r.raise_for_status()
    return r.json()["session_token"]

def kill_session(session_token):
    requests.get(
        f"{GLPI_URL}/killSession",
        headers={**HEADERS, "Session-Token": session_token}
    )

# ===============================
# BUSCA TODOS OS TICKETS
# ===============================
def get_all_tickets(session_token):
    tickets = []
    start = 0
    limit = 100

    headers = {**HEADERS, "Session-Token": session_token}

    while True:
        params = {
            "range": f"{start}-{start + limit - 1}",
            "forcedisplay[0]": "id",
            "forcedisplay[1]": "name",
            "forcedisplay[2]": "status",
            "forcedisplay[3]": "date",
            "forcedisplay[4]": "closedate",
            "forcedisplay[5]": "itilcategories_id",
            "forcedisplay[6]": "users_id_recipient",
            "forcedisplay[7]": "groups_id_assign",
        }

        r = requests.get(f"{GLPI_URL}/search/Ticket", headers=headers, params=params)
        r.raise_for_status()

        data = r.json().get("data", [])
        if not data:
            break

        tickets.extend(data)

        if len(data) < limit:
            break

        start += limit

    return tickets

# ===============================
# MAIN
# ===============================
def main():
    session_token = init_session()
    try:
        tickets = get_all_tickets(session_token)

        if not tickets:
            print("⚠️ Nenhum chamado encontrado.")
            return

        # ===============================
        # FILTROS NO PYTHON (SEGUROS)
        # ===============================
        filters_active = bool(CATEGORY_IDS or REQUESTER_ID is not None or GROUP_ASSIGN_ID is not None)
        if filters_active:
            tickets = [t for t in tickets if ticket_matches_filters(t)]

        if not tickets:
            print("⚠️ Nenhum chamado após aplicar filtros.")
            return

        df = pd.DataFrame(tickets)

        df.rename(columns={
            "id": "ID",
            "name": "Título",
            "status": "Status",
            "date": "Data de abertura",
            "closedate": "Data de fechamento",
            "itilcategories_id": "Categoria",
            "users_id_recipient": "Requester",
            "groups_id_assign": "Grupo"
        }, inplace=True)


        df.to_csv(CSV_OUTPUT, index=False, encoding="utf-8-sig")
        print(f"✅ CSV gerado com sucesso: {CSV_OUTPUT}")

    finally:
        kill_session(session_token)

# ===============================
# ENTRYPOINT
# ===============================
if __name__ == "__main__":
    main()
