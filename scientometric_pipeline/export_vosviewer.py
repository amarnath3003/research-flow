import pandas as pd


# VOSviewer likes CSV with:
# title, abstract, keywords, authors


df = pd.read_csv("data/cleaned/final_dataset.csv")

vos_df = df[[
    "title",
    "abstract",
    "authors",
    "keywords",
    "year",
    "citations"
]]

vos_df.to_csv(
    "data/exports/vosviewer_ready.csv",
    index=False
)

print("VOSviewer export ready")
