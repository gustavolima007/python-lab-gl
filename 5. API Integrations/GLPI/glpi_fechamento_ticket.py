"""
Codigo para fechamento automático de ticket no GLPI.

Autor: Gustavo F. Lima
Licença: MIT
Criado: 2026
"""

import requests
import json
import os
from dotenv import load_dotenv

# =========================================================
# CONFIGURAÇÃO
# =========================================================

load_dotenv()

GLPI_URL = os.getenv("GLPI_URL").rstrip("/")
APP_TOKEN = os.getenv("GLPI_APP_TOKEN")
USER_TOKEN = os.getenv("GLPI_USER_TOKEN")

TICKET_ID = 2512160043

USR_REQUERENTE_PADRAO = 33        # MSign
GRP_SUPORTE_PLAYER = 43          # Suporte Player
USR_TECNICO_TEMP = 33            # Técnico temporário

DESCRICAO = """Player restaurado com sucesso.

O player foi sincronizado novamente com o servidor MSign,
atualizado para a versão mais recente e validado.
"""

# =========================================================
# HEADERS
# =========================================================

HEADERS = {
    "Content-Type": "application/json",
    "App-Token": APP_TOKEN,
    "Authorization": f"user_token {USER_TOKEN}"
}

# =========================================================
# FUNÇÕES
# =========================================================

def glpi_get(path):
    r = requests.get(f"{GLPI_URL}{path}", headers=HEADERS)
    r.raise_for_status()
    return r.json() if r.text.strip() else []

def glpi_post(path, payload):
    return requests.post(f"{GLPI_URL}{path}", headers=HEADERS, data=json.dumps(payload))

def glpi_put(path, payload):
    return requests.put(f"{GLPI_URL}{path}", headers=HEADERS, data=json.dumps(payload))

def glpi_delete(resource, _id):
    return requests.delete(
        f"{GLPI_URL}/{resource}/{_id}",
        headers=HEADERS,
        data=json.dumps({"input": {"id": _id}})
    )

# =========================================================
# SESSÃO
# =========================================================

r = requests.get(f"{GLPI_URL}/initSession", headers=HEADERS)
r.raise_for_status()
HEADERS["Session-Token"] = r.json()["session_token"]
print("🔑 Sessão iniciada")

# =========================================================
# NORMALIZA REQUERENTE
# =========================================================

tu_list = glpi_get(f"/Ticket/{TICKET_ID}/Ticket_User")

tem_requerente = any(row.get("type") == 1 for row in tu_list)

if not tem_requerente:
    r = glpi_post("/Ticket_User", {
        "input": {
            "tickets_id": TICKET_ID,
            "users_id": USR_REQUERENTE_PADRAO,
            "type": 1
        }
    })
    if r.status_code not in (200, 201) and "ERROR_GLPI_ADD" not in r.text:
        print("Erro ao recriar requerente:", r.text)
        raise SystemExit(1)
    print("👤 Requerente restaurado (MSign)")

# =========================================================
# REMOVE TÉCNICOS
# =========================================================

for row in tu_list:
    if row.get("type") == 2:
        glpi_delete("Ticket_User", row["id"])

print("👨‍🔧 Técnicos removidos")

# =========================================================
# NORMALIZA GRUPO
# =========================================================

gt_list = glpi_get(f"/Ticket/{TICKET_ID}/Group_Ticket")

for row in gt_list:
    if row.get("type") == 2 and row.get("groups_id") != GRP_SUPORTE_PLAYER:
        glpi_delete("Group_Ticket", row["id"])

gt_after = glpi_get(f"/Ticket/{TICKET_ID}/Group_Ticket")

if not any(row.get("type") == 2 and row.get("groups_id") == GRP_SUPORTE_PLAYER for row in gt_after):
    r = glpi_post("/Group_Ticket", {
        "input": {
            "tickets_id": TICKET_ID,
            "groups_id": GRP_SUPORTE_PLAYER,
            "type": 2
        }
    })
    if r.status_code not in (200, 201):
        print("Erro ao criar grupo:", r.text)
        raise SystemExit(1)

print("👥 Grupo Suporte Player garantido")

# =========================================================
# ATRIBUI TÉCNICO TEMP
# =========================================================

r = glpi_post("/Ticket_User", {
    "input": {
        "tickets_id": TICKET_ID,
        "users_id": USR_TECNICO_TEMP,
        "type": 2
    }
})

if r.status_code not in (200, 201) and "ERROR_GLPI_ADD" not in r.text:
    print("Erro ao atribuir técnico:", r.text)
    raise SystemExit(1)

print("👨‍🔧 Técnico temporário atribuído")

# =========================================================
# REGISTRA SOLUÇÃO
# =========================================================

r = glpi_post("/ITILSolution", {
    "input": {
        "itemtype": "Ticket",
        "items_id": TICKET_ID,
        "content": DESCRICAO
    }
})

if r.status_code not in (200, 201):
    print("Erro ao registrar solução:", r.text)
    raise SystemExit(1)

print("📝 Solução registrada")

# =========================================================
# FECHA
# =========================================================

r = glpi_put(f"/Ticket/{TICKET_ID}", {
    "input": {
        "id": TICKET_ID,
        "status": 5
    }
})

if r.status_code != 200:
    print("Erro ao fechar:", r.text)
    raise SystemExit(1)

print("✅ Ticket solucionado")

# =========================================================
# REMOVE TÉCNICO TEMP
# =========================================================

tu_after = glpi_get(f"/Ticket/{TICKET_ID}/Ticket_User")
for row in tu_after:
    if row.get("type") == 2 and row.get("users_id") == USR_TECNICO_TEMP:
        glpi_delete("Ticket_User", row["id"])

print("🧹 Técnico temporário removido")

# =========================================================
# FECHA SESSÃO
# =========================================================

requests.get(f"{GLPI_URL}/killSession", headers=HEADERS)
print("🔒 Sessão encerrada")
