"""Apply manual classifications to refine the dataset."""
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from settings import load, BASE_DIR

cfg = load()
RESEARCH_TITLE = cfg["research"]["title"]


def run():
    class_path = os.path.join(BASE_DIR, "outputs", "stats", "topic_classification.csv")
    dataset_path = os.path.join(BASE_DIR, "data", "processed", "topic_dataset.csv")
    out_path = os.path.join(BASE_DIR, "data", "processed", "final_curated_dataset.csv")

    if not os.path.exists(class_path):
        print("Classification file not found. Run export_classification first and fill the CSV.")
        return

    class_df = pd.read_csv(class_path)
    class_df["keep/remove"] = class_df["keep/remove"].str.strip().str.lower()
    keep_topics = class_df[class_df["keep/remove"] == "keep"]["topic_id"].tolist()

    if not keep_topics:
        print("No topics marked as 'keep'. Check your CSV.")
        return

    df = pd.read_csv(dataset_path)
    initial = len(df)
    refined = df[df["topic"].isin(keep_topics)]
    refined.to_csv(out_path, index=False)

    print(f"Initial: {initial} -> Final: {len(refined)} ({((initial-len(refined))/initial)*100:.1f}% removed)")
    print(f"Methodology: Multi-stage semantic filtering conducted to preserve alignment with '{RESEARCH_TITLE}'")
