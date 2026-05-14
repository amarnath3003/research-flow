"""Author-level analysis."""
import pandas as pd
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from settings import load, BASE_DIR

cfg = load()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")


def run():
    path = os.path.join(BASE_DIR, "data", "processed", "final_thematic_dataset.csv")
    fallback = os.path.join(BASE_DIR, "data", "processed", "topic_dataset.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
    elif os.path.exists(fallback):
        df = pd.read_csv(fallback)
    else:
        print("No dataset found. Run Data Acquisition and Topic Modeling first.")
        return

    author_records = []
    for _, row in df.iterrows():
        if pd.isna(row["authors"]):
            continue
        for author in row["authors"].split(";"):
            author = author.strip()
            if author:
                author_records.append({"author": author, "citations": row.get("citations", 0)})

    if not author_records:
        print("No author data found.")
        return

    author_df = pd.DataFrame(author_records)
    stats = author_df.groupby("author").agg(
        paper_count=("citations", "count"),
        total_citations=("citations", "sum")
    ).reset_index().sort_values("paper_count", ascending=False)

    stats_dir = os.path.join(OUTPUTS_DIR, "stats")
    os.makedirs(stats_dir, exist_ok=True)
    stats.to_csv(os.path.join(stats_dir, "top_authors.csv"), index=False)
    print("Author analysis complete")
