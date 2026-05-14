"""Generate semantic validation report and theme-merging template."""
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from settings import load, BASE_DIR

cfg = load()


def generate_validation_report():
    curated_path = os.path.join(BASE_DIR, "data", "processed", "final_curated_dataset.csv")
    topic_info_path = os.path.join(BASE_DIR, "outputs", "stats", "topic_info.csv")

    if not os.path.exists(curated_path):
        print("No curated dataset found. Run refine_dataset first.")
        return

    df = pd.read_csv(curated_path)
    topic_info = pd.read_csv(topic_info_path)

    report = ["# Semantic Validation Report\n"]
    for _, row in topic_info.iterrows():
        tid = row["Topic"]
        subset = df[df["topic"] == tid]
        if subset.empty:
            continue
        report.append(f"## Topic {tid}: {row['Name']}\n")
        report.append(f"Documents: {len(subset)}\n")
        titles = subset["title"].dropna().head(5).tolist()
        for t in titles:
            report.append(f"- {t}\n")
        abstracts = subset["abstract"].dropna().head(2).tolist()
        for a in abstracts:
            report.append(f"> {a[:300]}...\n")
        report.append("\n")

    out_path = os.path.join(BASE_DIR, "outputs", "stats", "semantic_validation_report.md")
    with open(out_path, "w") as f:
        f.writelines(report)
    print(f"Validation report saved to {out_path}")


def generate_merge_template():
    curated_path = os.path.join(BASE_DIR, "data", "processed", "final_curated_dataset.csv")

    if not os.path.exists(curated_path):
        print("No curated dataset found. Run refine_dataset first.")
        return

    df = pd.read_csv(curated_path)
    topic_ids = sorted(df["topic"].unique())
    template = pd.DataFrame({"original_topic_id": topic_ids, "new_major_theme_name": ""})
    out_path = os.path.join(BASE_DIR, "outputs", "stats", "topic_merging_map.csv")
    template.to_csv(out_path, index=False)
    print(f"Merge template saved to {out_path}")
    print("Manual action: Fill 'new_major_theme_name' for each topic (aim for 8-15 unique themes).")


def run_all():
    generate_validation_report()
    generate_merge_template()
