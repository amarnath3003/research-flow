import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import os


df = pd.read_csv("data/cleaned/final_dataset.csv")


# PUBLICATION TREND
trend = df.groupby("year").size()

plt.figure(figsize=(10, 5))
plt.plot(trend.index, trend.values, marker='o')
plt.xlabel("Year")
plt.ylabel("Publications")
plt.title("Publication Trend")
plt.grid(True)

plt.savefig("outputs/figures/publication_trend.png")


# TOP JOURNALS
journal_counts = df["journal"].value_counts().head(20)

journal_counts.to_csv("outputs/stats/top_journals.csv")


# TOP KEYWORDS
all_keywords = []

for kws in df["keywords"]:

    if pd.isna(kws):
        continue

    split_kws = [k.strip() for k in kws.split(";")]

    all_keywords.extend(split_kws)

keyword_counts = Counter(all_keywords)

keywords_df = pd.DataFrame(
    keyword_counts.items(),
    columns=["keyword", "count"]
)

keywords_df = keywords_df.sort_values(
    by="count",
    ascending=False
)

keywords_df.to_csv(
    "outputs/stats/top_keywords.csv",
    index=False
)


print("Analysis complete")
