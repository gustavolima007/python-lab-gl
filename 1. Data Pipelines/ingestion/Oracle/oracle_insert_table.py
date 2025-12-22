"""
Codigo para inserir dados em uma tabela no banco Oracle de HML.

Author: Gustavo F. Lima
License: MIT
Created: 2025
"""

import os
import oracledb
from dotenv import load_dotenv


def init_oracle():
    """
    Inicializa o Oracle Client (Thick Mode)
    """
    # Instalar o oracle cliente e incluir na path: C:\oracle\instantclient_23_9

    if os.name == "nt":  # Windows
        lib_dir = r"C:\oracle\instantclient_23_9"
    else:  # Linux / Docker
        lib_dir = "/opt/oracle/instantclient_23_26"

    oracledb.init_oracle_client(lib_dir=lib_dir)


def get_connection():
    load_dotenv()

    user = os.getenv("DW_C5DBSTDY_CONSINCO_HML_USER")
    pwd = os.getenv("DW_C5DBSTDY_CONSINCO_HML_PWD")
    host = os.getenv("DW_C5DBSTDY_CONSINCO_HML_HOST")
    port = os.getenv("DW_C5DBSTDY_CONSINCO_HML_PORT")
    service = os.getenv("DW_C5DBSTDY_CONSINCO_HML_SERVICE")

    dsn = f"{host}:{port}/{service}"

    return oracledb.connect(
        user=user,
        password=pwd,
        dsn=dsn
    )


def insert_example_rows():
    # Inicializa Oracle Client (UMA vez por processo)
    init_oracle()

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("ALTER SESSION SET CURRENT_SCHEMA = DW")

            sql = """
                INSERT INTO DW.EXEMPLO_TABELA (NOME, DESCRICAO)
                VALUES (:nome, :descricao)
            """

            rows = [
                ("Linha 1", "Primeira linha inserida via Python"),
                ("Linha 2", "Segunda linha inserida via Python"),
                ("Linha 3", "Terceira linha inserida via Python"),
            ]

            cursor.executemany(sql, rows)

            print(f"✅ {cursor.rowcount} linhas inseridas com sucesso!")

        connection.commit()

    except oracledb.DatabaseError as e:
        error, = e.args
        print("❌ Erro Oracle:", error.message)

    finally:
        connection.close()


if __name__ == "__main__":
    insert_example_rows()
