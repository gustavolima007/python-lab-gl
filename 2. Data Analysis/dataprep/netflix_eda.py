from dataprep.eda import create_report
import pandas as pd

df = pd.read_csv("netflix_titles.csv")

report = create_report(df)
report.show_browser()


## Deu erro no python 3.12