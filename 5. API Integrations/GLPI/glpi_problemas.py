"""
API para extração de TODOS os Problemas do GLPI, que são chamados de "Issues".

Autor: Gustavo F. Lima
Licença: MIT
Criado: 2026
"""
import os, csv, requests
from typing import Optional

def load_env(path=".env"):
    if os.path.isfile(path):
        for l in open(path):
            if "=" in l:
                k,v = l.strip().split("=",1)
                os.environ[k]=v

load_env()

GLPI_URL=os.environ["GLPI_URL"].rstrip("/")
APP_TOKEN=os.environ["GLPI_APP_TOKEN"]
USER_TOKEN=os.environ["GLPI_USER_TOKEN"]

STATUS = {
    1:"novo",2:"em_analise",3:"aceito",4:"em_progresso",
    5:"solucionado",6:"fechado"
}

CSV_PATH="data/glpi_problemas.csv"

def main():
    s = requests.get(f"{GLPI_URL}/initSession",
        headers={"App-Token":APP_TOKEN,"Authorization":f"user_token {USER_TOKEN}"}
    ).json()["session_token"]

    headers={"App-Token":APP_TOKEN,"Session-Token":s}
    start=0
    data=[]

    while True:
        r=requests.get(f"{GLPI_URL}/Problem",headers=headers,params={"range":f"{start}-{start+199}"})
        if r.status_code==400: break
        batch=r.json()
        if not batch: break

        for p in batch:
            data.append({
                "id":p["id"],
                "titulo":p["name"],
                "entidade":p["entities_id"],
                "status":STATUS.get(p["status"],"desconhecido"),
                "data_abertura":p["date"],
                "ultima_atualizacao":p["date_mod"],
                "requerente":p["users_id_recipient"],
                "categoria":p["itilcategories_id"],
                "impacto":p["impact"],
                "urgencia":p["urgency"],
                "prioridade":p["priority"],
                "data_solucao":p["solvedate"],
                "tempo_para_solucao":p["time_to_resolve"]
            })

        start+=len(batch)

    with open(CSV_PATH,"w",newline="",encoding="utf8") as f:
        w=csv.DictWriter(f,fieldnames=data[0].keys())
        w.writeheader()
        w.writerows(data)

if __name__=="__main__":
    main()
