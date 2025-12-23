
"""
API para extração de um chamado específico do GLPI.

Author: Gustavo F. Lima
License: MIT
Created: 2025
"""
import os
import requests

def load_env(path="codigo.py.env"):
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

# Somente ticket especifico
TICKET_ID = 5347

STATUS_MAP = {
    1: "Novo",
    2: "Em atendimento (atribuído)",
    3: "Em atendimento (planejado)",
    4: "Pendente",
    5: "Solucionado",
    6: "Fechado",
}

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

    try:
        # 2) get ticket
        ticket_url = f"{GLPI_URL}/Ticket/{TICKET_ID}/"  
        headers = {
            "Content-Type": "application/json",
            "App-Token": APP_TOKEN,
            "Session-Token": session_token,
        }
        t = requests.get(ticket_url, headers=headers, timeout=30)

        if t.status_code == 404:
            print(f"Ticket {TICKET_ID} não encontrado (404): {t.text}")
            return

        t.raise_for_status()
        ticket = t.json()

        status_code = int(ticket.get("status", -1))
        status_label = STATUS_MAP.get(status_code, f"Desconhecido({status_code})")

        print(f"ID: {ticket.get('id')}")
        print(f"Título: {ticket.get('name')}")
        print(f"Status: {status_code} - {status_label}")
        print(f"Última atualização: {ticket.get('date_mod')}")
        print(f"Data criação: {ticket.get('date_creation')}")

    finally:
        # 3) kill session (boa prática)
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
