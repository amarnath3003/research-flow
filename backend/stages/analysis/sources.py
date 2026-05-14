"""Top sources/journals analysis."""
import pandas as pd
import os
import sys

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

    # Drop NaN journals and fill NaN citations with 0
    df = df.dropna(subset=["journal"])
    df["citations"] = df["citations"].fillna(0)

    def h_index(citations):
        c = sorted(citations, reverse=True)
        h = 0
        for i, v in enumerate(c):
            if v >= i + 1:
                h = i + 1
            else:
                break
        return h

    grouped = df.groupby("journal").agg(
        paper_count=("title", "count"),
        total_citations=("citations", "sum"),
        citations_list=("citations", list)
    ).reset_index()
    grouped["h_index"] = grouped["citations_list"].apply(h_index)
    grouped = grouped.sort_values("h_index", ascending=False).head(50)
    sources_dir = os.path.join(OUTPUTS_DIR, "sources")
    os.makedirs(sources_dir, exist_ok=True)
    grouped.drop(columns=["citations_list"]).to_csv(
        os.path.join(sources_dir, "top_sources.csv"), index=False
    )
    print("Source analysis complete")
