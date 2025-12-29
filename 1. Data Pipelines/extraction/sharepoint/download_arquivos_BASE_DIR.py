"""
Define o diretório base do projeto e o caminho local para download de arquivos.

Author: Gustavo F. Lima
License: MIT
Created: 2025
"""

from pathlib import Path

# =========================
# CAMINHOS
# =========================

# Diretório base do projeto (dois níveis acima deste arquivo)
BASE_DIR = Path(__file__).resolve().parent.parent

# Caminho para a pasta "data"
LOCAL_DOWNLOAD_PATH = BASE_DIR / "data"
