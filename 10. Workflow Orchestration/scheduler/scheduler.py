"""
Agenda a execução diária de meu_script.py às 02:00 por subprocess.
Verifica a existência do script e repete o loop a cada 24h reportando status.

Author: Gustavo F. Lima
License: MIT
Created: 2025
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Caminho do script que será executado
ROOT_DIR = Path(__file__).resolve().parent
SCRIPT_TO_RUN = ROOT_DIR / "meu_script.py"

# Hora alvo para execução diária
TARGET_HOUR = 2
TARGET_MINUTE = 0


def run_script():
    """Executa o script Python configurado."""
    if not SCRIPT_TO_RUN.exists():
        print(f"❌ Script não encontrado: {SCRIPT_TO_RUN}")
        return

    print(f"▶️ Executando script: {SCRIPT_TO_RUN}")
    subprocess.run(
        [sys.executable, str(SCRIPT_TO_RUN)],
        check=False
    )
    print("✅ Execução finalizada.")


def main():
    last_run_date = None
    print("⏱️ Scheduler iniciado. Aguardando 02:00...")

    while True:
        now = datetime.now()

        if (
            now.hour == TARGET_HOUR
            and now.minute == TARGET_MINUTE
            and last_run_date != now.date()
        ):
            run_script()
            last_run_date = now.date()

        time.sleep(30)  # evita loop agressivo


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("🛑 Scheduler interrompido pelo usuário.")
