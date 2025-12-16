import pandas as pd
from ydata_profiling import ProfileReport

df = pd.read_csv(
    "datasets/Netflix Movies and TV Shows/netflix_titles.csv"
)

profile = ProfileReport(
    df,
    title="Netflix Movies and TV Shows - EDA",
    explorative=True
)

profile.to_file("netflix_profile_report.html")

print("✅ EDA report generated successfully!")
