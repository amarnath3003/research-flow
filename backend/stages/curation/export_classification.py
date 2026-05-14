"""Export topic classification template for manual labelling."""
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from settings import load, BASE_DIR

cfg = load()
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")


def run():
    topic_info = pd.read_csv(os.path.join(BASE_DIR, "outputs", "stats", "topic_info.csv"))
    topic_dataset = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "topic_dataset.csv"))

    template = pd.DataFrame({"topic_id": topic_info["Topic"],
                             "name": topic_info["Name"],
                             "representative_titles": "",
                             "representative_abstracts": "",
                             "label": "",
                             "classification": "",
                             "keep/remove": ""})

    for i, row in template.iterrows():
        tid = row["topic_id"]
        subset = topic_dataset[topic_dataset["topic"] == tid]
        titles = subset["title"].dropna().head(3).tolist()
        abstracts = subset["abstract"].dropna().head(2).tolist()
        template.at[i, "representative_titles"] = " | ".join(titles)
        template.at[i, "representative_abstracts"] = " | ".join(abstracts)

    out_path = os.path.join(BASE_DIR, "outputs", "stats", "topic_classification.csv")
    template.to_csv(out_path, index=False)
    print(f"Topic classification template saved to {out_path}")
    print("Manual action: Open and fill 'classification' (CORE/SUPPORTING/NOISE) and 'keep/remove' columns.")

    # Also export a simplified version for Phase 2
    simple = template[["topic_id", "name", "label"]].copy()
    simple.to_csv(os.path.join(BASE_DIR, "outputs", "stats", "topic_info_labeled.csv"), index=False)
