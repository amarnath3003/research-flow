"""Figure 1: Publication Growth Timeline."""
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from settings import load, BASE_DIR

cfg = load()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
ANNOTATIONS = cfg["visualizations"].get("annotations", {})


def run():
    df = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "topic_dataset.csv"))
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    counts = df.groupby("year").size().reset_index(name="count")

    start = cfg["research"]["start_year"]
    end = cfg["research"]["end_year"]
    counts = counts[(counts["year"] >= start) & (counts["year"] <= end)]

    plt.figure(figsize=(12, 6))
    plt.plot(counts["year"], counts["count"], marker="o", color="#1f77b4", linewidth=3, markersize=8, label="Annual Publications")
    plt.fill_between(counts["year"], counts["count"], color="#1f77b4", alpha=0.1)

    custom_anns = ANNOTATIONS.get("custom", []) if ANNOTATIONS.get("enabled", True) else []
    if custom_anns:
        for ann in custom_anns:
            y = ann["year"]
            if y in counts["year"].values:
                plt.axvline(x=y, color="#d62728", linestyle="--", alpha=0.7)
                val = counts[counts["year"] == y]["count"].values[0]
                plt.text(y + 0.2, val + counts["count"].max() * 0.02, ann["label"], color="#d62728", fontweight="bold", fontsize=9)
    else:
        counts["yoy"] = counts["count"].diff()
        if not counts["yoy"].isna().all():
            peak = counts["yoy"].idxmax()
            py = int(counts.loc[peak, "year"])
            pg = int(counts.loc[peak, "yoy"])
            if pg > 0:
                plt.axvline(x=py, color="#d62728", linestyle="--", alpha=0.7)
                plt.text(py + 0.2, counts.loc[peak, "count"] + counts["count"].max() * 0.02,
                         f"Highest Growth +{pg}", color="#d62728", fontweight="bold", fontsize=9)

    plt.title(f"Publication Growth Timeline ({start}-{end})", fontsize=16, fontweight="bold", pad=20)
    plt.xlabel("Year")
    plt.ylabel("Publications")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.ylim(0, counts["count"].max() * 1.3)
    plt.legend()

    figs_dir = os.path.join(OUTPUTS_DIR, "figures")
    os.makedirs(figs_dir, exist_ok=True)
    plt.savefig(os.path.join(figs_dir, "figure1_growth_timeline.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("Figure 1 generated")
