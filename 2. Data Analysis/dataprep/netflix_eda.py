"""
Gera relatório exploratório da base netflix_titles usando dataprep.
Carrega o CSV e abre o relatório no navegador para revisão rápida.

Author: Gustavo F. Lima
License: MIT
Created: 2025
"""

from dataprep.eda import create_report
import pandas as pd

df = pd.read_csv("netflix_titles.csv")

report = create_report(df)
report.show_browser()


## Deu erro no python 3.12