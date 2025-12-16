import pandas as pd
import sweetviz as sv

# Carregar o dataset
df = pd.read_csv("datasets/Netflix Movies and TV Shows/netflix_titles.csv")

# Gerar o relatório Sweetviz
report = sv.analyze(df)

# Salvar o relatório como um arquivo HTML
report.show_html("netflix_eda_report.html")


## Deu erro no python 3.12