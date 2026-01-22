"""
API para extração de TODOS os Ativos do GLPI.

Autor: Gustavo F. Lima
Licença: MIT
Criado: 2026
"""

import os
import csv
import requests

def load_env():
    for l in open(".env"):
        if "=" in l:
            k,v=l.strip().split("=",1)
            os.environ[k]=v

load_env()

GLPI_URL=os.environ["GLPI_URL"].rstrip("/")
APP_TOKEN=os.environ["GLPI_APP_TOKEN"]
USER_TOKEN=os.environ["GLPI_USER_TOKEN"]

PAGE_SIZE=200

CSV_PATH="data/glpi_ativos.csv"

FIELDS=[
    "id","tipo_ativo","nome","entidade","localizacao","categoria",
    "fabricante","modelo","numero_serie","patrimonio",
    "status","usuario","data_compra","data_garantia","data_fim_garantia"
]

ENDPOINTS={
    "computador":"Computer",
    "servidor":"Server",
    "impressora":"Printer",
    "rede":"NetworkEquipment",
    "software":"Software"
}

def get_all(endpoint,headers):
    start=0
    data=[]
    while True:
        r=requests.get(f"{GLPI_URL}/{endpoint}",headers=headers,params={"range":f"{start}-{start+199}"})
        if r.status_code==400: break
        batch=r.json()
        if not batch: break
        data.extend(batch)
        start+=len(batch)
    return data

def main():
    s=requests.get(f"{GLPI_URL}/initSession",
        headers={"App-Token":APP_TOKEN,"Authorization":f"user_token {USER_TOKEN}"}
    ).json()["session_token"]

    headers={"App-Token":APP_TOKEN,"Session-Token":s}

    ativos=[]

    for tipo,endpoint in ENDPOINTS.items():
        print(f"Extraindo {tipo}...")
        for a in get_all(endpoint,headers):
            ativos.append({
                "id":a.get("id"),
                "tipo_ativo":tipo,
                "nome":a.get("name"),
                "entidade":a.get("entities_id"),
                "localizacao":a.get("locations_id"),
                "categoria":a.get("itilcategories_id"),
                "fabricante":a.get("manufacturers_id"),
                "modelo":a.get("models_id"),
                "numero_serie":a.get("serial"),
                "patrimonio":a.get("otherserial"),
                "status":a.get("states_id"),
                "usuario":a.get("users_id"),
                "data_compra":a.get("buy_date"),
                "data_garantia":a.get("warranty_date"),
                "data_fim_garantia":a.get("warranty_end_date")
            })

    with open(CSV_PATH,"w",newline="",encoding="utf8") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        w.writeheader()
        w.writerows(ativos)

    print(f"\nTotal de ativos: {len(ativos)}")
    print(f"CSV salvo em {CSV_PATH}")

    requests.get(f"{GLPI_URL}/killSession",headers={"App-Token":APP_TOKEN,"Session-Token":s})

if __name__=="__main__":
    main()
