import pandas as pd
import os
import json
from collections import Counter

# =========================
# PATHS
# =========================
DATASET_PATH = "data/processed/topic_dataset.csv"
TOPIC_INFO_PATH = "outputs/stats/topic_info.csv"
OUTPUT_DIR = "share_pipeline"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# LOAD DATA
# =========================
print("Loading datasets...")
df = pd.read_csv(DATASET_PATH)
topic_df = pd.read_csv(TOPIC_INFO_PATH)

# =========================
# BASIC DATASET STATS
# =========================
stats = {
    "raw_paper_count": int(len(df)),
    "year_min": int(df["year"].min()),
    "year_max": int(df["year"].max()),
    "unique_journals": int(df["journal"].nunique()),
    "unique_topics": int(df["topic"].nunique()),
}

# =========================
# TOP KEYWORDS
# =========================
all_keywords = []
for kws in df["keywords"]:
    if pd.isna(kws):
        continue
    split_kws = [k.strip().lower() for k in kws.split(";")]
    all_keywords.extend(split_kws)

keyword_counts = Counter(all_keywords)
top_keywords = keyword_counts.most_common(100)
top_keywords_df = pd.DataFrame(top_keywords, columns=["keyword", "count"])

# =========================
# SAMPLE TITLES
# =========================
sample_titles = []
# TOPIC-WISE SAMPLE TITLES
for topic_id in df["topic"].unique():
    topic_subset = df[df["topic"] == topic_id]
    samples = topic_subset.head(5)
    for _, row in samples.iterrows():
        sample_titles.append({
            "topic": int(topic_id),
            "title": row["title"],
            "year": row["year"],
        })

sample_titles_df = pd.DataFrame(sample_titles)

# =========================
# TOP JOURNALS
# =========================
top_journals = (
    df["journal"]
    .value_counts()
    .head(30)
    .reset_index()
)
top_journals.columns = ["journal", "count"]

# =========================
# TOP TOPICS
# =========================
top_topics = topic_df.head(20)

# =========================
# PUBLICATION TREND
# =========================
publication_trend = (
    df.groupby("year")
    .size()
    .reset_index(name="count")
)

# =========================
# SAVE FILES
# =========================
print("Saving diagnostic exports...")

# STATS
with open(f"{OUTPUT_DIR}/dataset_stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=4)

# CSV EXPORTS
top_keywords_df.to_csv(f"{OUTPUT_DIR}/top_keywords.csv", index=False)
sample_titles_df.to_csv(f"{OUTPUT_DIR}/sample_titles.csv", index=False)
top_journals.to_csv(f"{OUTPUT_DIR}/top_journals.csv", index=False)
top_topics.to_csv(f"{OUTPUT_DIR}/top_topics.csv", index=False)
publication_trend.to_csv(f"{OUTPUT_DIR}/publication_trend.csv", index=False)

# =========================
# SUMMARY PRINT
# =========================
print("\n===== DIAGNOSTIC EXPORT COMPLETE =====\n")
print("Generated files:")
print("- dataset_stats.json")
print("- top_keywords.csv")
print("- sample_titles.csv")
print("- top_journals.csv")
print("- top_topics.csv")
print("- publication_trend.csv")
print("\nShare ONLY these files/results for diagnosis.")
