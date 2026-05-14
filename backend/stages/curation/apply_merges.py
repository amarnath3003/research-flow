"""Apply manual theme merges to create the thematic dataset."""
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from settings import load, BASE_DIR

cfg = load()


def run():
    merge_path = os.path.join(BASE_DIR, "outputs", "stats", "topic_merging_map.csv")
    curated_path = os.path.join(BASE_DIR, "data", "processed", "final_curated_dataset.csv")
    out_path = os.path.join(BASE_DIR, "data", "processed", "final_thematic_dataset.csv")

    if not os.path.exists(merge_path):
        print("Merge map not found. Run validate_semantics first and fill the CSV.")
        return

    merge_map = pd.read_csv(merge_path)
    merge_map["new_major_theme_name"] = merge_map["new_major_theme_name"].str.strip()

    if merge_map["new_major_theme_name"].isna().all() or (merge_map["new_major_theme_name"] == "").all():
        print("Theme names not filled. Edit topic_merging_map.csv first.")
        return

    df = pd.read_csv(curated_path)
    theme_lookup = dict(zip(merge_map["original_topic_id"], merge_map["new_major_theme_name"]))
    df["new_major_theme_name"] = df["topic"].map(theme_lookup)

    # Drop any rows that didn't map
    df = df.dropna(subset=["new_major_theme_name"])
    df.to_csv(out_path, index=False)

    unique_themes = df["new_major_theme_name"].nunique()
    print(f"Thematic dataset saved: {len(df)} papers, {unique_themes} unique themes")
